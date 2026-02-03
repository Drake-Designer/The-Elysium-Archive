"""Session helpers for the shopping cart."""

from decimal import Decimal

from products.models import Product

from .models import Cart, CartItem


def _get_or_create_user_cart(user):
    """Return the persistent cart for the user."""
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def _sync_session_to_db(session, user):
    """Sync session cart into DB for an authenticated user."""
    cart = session.get("cart", {})
    if cart is None:
        cart = {}

    db_cart = _get_or_create_user_cart(user)

    product_ids = []
    for key in list(cart.keys()):
        try:
            product_ids.append(int(key))
        except (TypeError, ValueError):
            cart.pop(key, None)

    if not product_ids:
        CartItem.objects.filter(cart=db_cart).delete()
        session["cart"] = {}
        session.modified = True
        return

    valid_products = set(
        Product.objects.filter(
            id__in=product_ids,
            is_active=True,
            is_removed=False,
        ).values_list("id", flat=True)
    )

    CartItem.objects.filter(cart=db_cart).exclude(
        product_id__in=valid_products
    ).delete()

    for pid in valid_products:
        CartItem.objects.get_or_create(
            cart=db_cart, product_id=pid, defaults={"quantity": 1}
        )

    session["cart"] = {str(pid): 1 for pid in valid_products}
    session.modified = True


def merge_db_cart_into_session(session, user):
    """Merge a user's DB cart with the current session cart and sync the result."""
    session_cart = session.get("cart", {})
    if session_cart is None:
        session_cart = {}

    db_cart = _get_or_create_user_cart(user)

    db_items = (
        CartItem.objects.filter(cart=db_cart)
        .select_related("product")
        .filter(product__is_active=True, product__is_removed=False)
    )
    db_ids = {str(item.product.pk) for item in db_items if item.product}

    merged = dict(session_cart)
    for pid_str in db_ids:
        merged[pid_str] = 1

    session["cart"] = merged
    session.modified = True

    _sync_session_to_db(session, user)


def get_cart(session):
    """Return the cart dictionary stored in the session."""
    cart = session.get("cart")
    if cart is None:
        cart = {}
        session["cart"] = cart
    return cart


def add_to_cart(session, product_id, user=None):
    """Add a product to the cart as a single purchase."""
    try:
        Product.objects.get(id=product_id, is_active=True, is_removed=False)
    except Product.DoesNotExist:
        return False

    cart = get_cart(session)
    product_id_str = str(product_id)

    if product_id_str in cart:
        return "already_in_cart"

    cart[product_id_str] = 1
    session.modified = True

    if user is not None and getattr(user, "is_authenticated", False):
        _sync_session_to_db(session, user)

    return True


def remove_from_cart(session, product_id, user=None):
    """Remove a product from the cart."""
    cart = get_cart(session)
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        session.modified = True

        if user is not None and getattr(user, "is_authenticated", False):
            _sync_session_to_db(session, user)

        return True

    return False


def get_cart_items(session, user=None):
    """Return cart items with product data."""
    cart = get_cart(session)
    if not cart:
        return []

    valid_ids = []
    for product_id_str in list(cart.keys()):
        try:
            valid_ids.append(int(product_id_str))
        except (TypeError, ValueError):
            cart.pop(product_id_str, None)

    if not valid_ids:
        session["cart"] = {}
        session.modified = True
        return []

    qs = Product.objects.filter(id__in=valid_ids, is_active=True, is_removed=False)
    products = list(qs)
    active_ids = set(qs.values_list("id", flat=True))

    removed = 0
    for product_id_str in list(cart.keys()):
        try:
            if int(product_id_str) not in active_ids:
                cart.pop(product_id_str, None)
                removed += 1
        except (TypeError, ValueError):
            continue

    if removed:
        session["cart"] = cart
        session.modified = True

        if user is not None and getattr(user, "is_authenticated", False):
            _sync_session_to_db(session, user)

    return [{"product": product} for product in products]


def get_cart_total(session, cart_items=None):
    """Return the total value of the cart with discounts applied."""
    total = Decimal("0.00")
    items = cart_items if cart_items is not None else get_cart_items(session)
    for item in items:
        total += item["product"].get_discounted_price()
    return total


def clear_cart(session, user=None):
    """Clear all cart items from the session."""
    session["cart"] = {}
    session.modified = True

    if user is not None and getattr(user, "is_authenticated", False):
        db_cart = _get_or_create_user_cart(user)
        CartItem.objects.filter(cart=db_cart).delete()
