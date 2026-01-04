# Testing Guide - The Elysium Archive

This document describes the testing strategy, automated test suite, and manual testing procedures for The Elysium Archive project. The test suite covers all core functionality and grows as new features are added.

---

## Automated Tests

### Running Tests

The project uses **pytest 9.0.2** with **pytest-django 4.11.1** for automated testing.

**Run all tests:**

```bash
pytest
```

**Run with verbose output:**

```bash
pytest -v
```

**Run specific test file:**

```bash
pytest accounts/tests/test_profile.py -v
```

**Run specific test class:**

```bash
pytest products/tests/test_access_control.py::TestProductAccessControl -v
```

**Run specific test:**

```bash
pytest orders/tests.py::TestWebhookHandling::test_webhook_idempotent_same_event_twice -v
```

**Show print statements:**

```bash
pytest -v -s
```

### Test Configuration

Tests use a dedicated test settings module (`elysium_archive/settings_test.py`) that:

- Uses simple `StaticFilesStorage` instead of manifest-based storage.
- Disables WhiteNoise for cleaner test isolation.
- Uses in-memory email backend (no real emails sent).
- Uses fast MD5 password hasher for speed.

Configuration is in `pytest.ini`:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = elysium_archive.settings_test
python_files = tests.py test_*.py *_tests.py
```

### Automated Test Coverage by Feature

#### Authentication and Account Management

**Files:** `accounts/tests/test_auth_pages.py` (5 tests), `accounts/tests/test_email_gate.py` (11 tests), `accounts/tests/test_profile.py` (14 tests)

**User Authentication:**

- Login page access (GET)
- Signup page access (GET)
- Logout flow (POST with redirect)
- Login/signup accessibility when already authenticated

**Email Verification Gate:**

- Unverified users cannot access dashboard/archive/profile (302 redirect)
- Anonymous users redirected to login
- Verified users can access protected pages
- My Archive displays purchased products for verified users
- Dashboard form POST updates display_name successfully

**User Profile Management:**

- Profile view requires authentication (302 redirect to login)
- Profile displays username and email read-only
- display_name form shows on profile page
- display_name POST updates stored in database
- display_name can be empty (optional field)
- display_name respects max_length (20 chars)
- Account deletion requires confirmation page
- Account deletion removes user and associated profile
- Account deletion logs out user and redirects home
- Success message shown on deletion

**Key assertions:** Status codes (200/302), email gate enforcement, template rendering, form handling, database state changes, messages

---

#### Product Catalog and Access Control

**Files:** `products/tests/test_access_control.py` (12 tests), `products/tests.py` (4 tests)

**Coverage:**

- Active products visible to anonymous and authenticated users
- Inactive products return 404 for non-owners
- Inactive products visible to staff/superusers
- Inactive products visible to users with AccessEntitlement (purchased products)
- Product list shows only active products
- Product detail displays title, price, content correctly
- Featured products appear in list
- CRUD operations (create, read, update, delete)

**Key assertions:** Access control logic, status codes (200/404), content display, database state

---

#### Archive Reading Pages and Content Separation

**File:** `products/tests/test_archive_read.py` (12 tests)

**Coverage:**

- Anonymous users redirected to login when accessing reading page
- Authenticated users without entitlement receive 403 error
- Users with unverified email redirected to email verification
- Owners with entitlement can access reading page (200 status)
- Reading page displays full archive content
- Preview page never displays full content, even for owners
- Preview page shows "Read Full Archive" button for owners
- Preview page shows purchase CTA for non-owners
- My Archive links directly to reading page, not preview
- Reading page includes navigation back to My Archive
- Reading page includes link to product preview page

**Key assertions:** Access control enforcement, content separation, navigation links, permission denied handling

---

#### Shopping Cart and Session Behavior

**File:** `cart/tests.py` (11 tests)

**Coverage:**

- Adding product to cart redirects to product detail
- Products stored in session as `{product_id: quantity}` dictionary
- Cart view displays items and shows empty state
- Removing products from cart updates session
- Cart persists across page visits
- Adding nonexistent/inactive products handled gracefully
- Cart operations require verified email (add_to_cart has email gate)
- Cart totals calculated correctly (single/multiple items)

**Key assertions:** Session state management, redirects, total calculations

---

#### Checkout and Payment Integration (Stripe)

**File:** `checkout/tests.py` (13 tests)

**Coverage:**

- Unverified users cannot access checkout (302 to email gate)
- Verified users can access checkout and get Stripe redirect
- Anonymous users redirected to login
- Checkout creates Order record in database
- Checkout creates OrderLineItem for each cart item
- Order total calculated from cart
- Empty cart shows warning message
- Success page displays order details
- Success page updates order status to paid
- Cancel page shows cancellation message

**Test setup:** Uses `@patch('stripe.checkout.Session.create')` to mock Stripe without real API calls

**Key assertions:** Access control, order creation, Stripe session creation, redirects, order status transitions

---

#### Webhook Handling and Access Entitlements

**File:** `orders/tests.py` (16 tests)

**Coverage:**

- Webhook `checkout.session.completed` creates AccessEntitlements
- Webhook updates order status to paid
- Webhook stores Stripe session ID and customer ID
- **Idempotency:** Same webhook event twice creates only one AccessEntitlement (verified using `get_or_create`)
- Payment failure webhook sets order status to failed
- Invalid webhook signature rejected (signature verification)
- POST only (GET not allowed)
- Missing order handled gracefully
- Order number generated as UUID on save
- Order number is unique
- Default order status is pending
- Order timestamps (created_at/updated_at) work correctly
- AccessEntitlement is unique per (user, product) pair
- AccessEntitlement deleted when product deleted (cascade delete)

**Test setup:** Uses `@patch('stripe.Webhook.construct_event')` to mock webhook verification without real Stripe calls

**Key assertions:** Database state integrity, webhook idempotency, signature validation, cascade deletes

---

#### Reviews and User-Generated Content

**File:** `reviews/tests.py` (19 tests)

**Coverage:**

- Non-buyers cannot see or post reviews
- Buyers (users with AccessEntitlement) can see review form and post reviews
- Anonymous users cannot post reviews
- User cannot post duplicate review for same product (unique constraint enforced)
- Reviews appear on product detail page
- Multiple reviews display correctly on product
- Review rating is valid range (1-5)
- Review title is optional (blank=True)
- Review deleted when user deleted (cascade delete)
- Review deleted when product deleted (cascade delete)
- **Edit Reviews:** Users can edit their own reviews via dedicated edit page
- **Edit Permission:** Users cannot edit other users' reviews (ownership verification)
- **Edit Form:** GET request to edit page shows pre-filled form with current values
- **Delete Reviews:** Users can delete their own reviews
- **Delete Permission:** Users cannot delete other users' reviews (ownership verification)
- **Delete Method:** Delete requires POST method (405 on GET)

**Key assertions:** Access control based on purchase history, unique constraints, content display, cascade deletes, ownership verification for edit/delete

---

#### Admin Interface and Safety Protections

**File:** `home/tests.py` (13 tests)

**Coverage:**

- Anonymous users cannot access Django admin (403/302)
- Regular users cannot access Django admin (403/302)
- Staff/superusers can access Django admin (200)
- Admins can delete products without entitlements
- Admins **cannot** delete products with AccessEntitlements (safety protection)
- Bulk delete blocked if ANY product has entitlements (all-or-nothing protection)
- Admins can mark products as featured via bulk action
- Admins can remove featured status via bulk action
- Regular users cannot toggle featured status (action not visible)
- Admins can edit product details (title, description, price) via form
- Admins can deactivate products (set `is_active=False`)
- Admins can view order list and order details
- Regular users cannot view orders (staff-only)

**Test setup:** Uses actual Django admin form submission (no mocking needed)

**Key assertions:** Staff-only access control, delete protection logic, admin bulk actions, form validation

---

## Manual Testing Procedures

Manual tests verify user-facing functionality that automated tests may not fully cover (UI/UX, visual rendering, real Stripe integration).

### Test Environment Setup

1. **Create test user:**

   ```bash
   python manage.py createsuperuser
   # Username: testadmin
   # Email: admin@example.com
   # Password: (your choice)
   ```

2. **Create test products:**

   ```bash
   python manage.py shell
   >>> from products.models import Category, Product
   >>> from decimal import Decimal
   >>> cat = Category.objects.create(name="Test", slug="test")
   >>> Product.objects.create(
   ...     title="Test Product",
   ...     slug="test-product",
   ...     description="Test description",
   ...     tagline="Test tagline",
   ...     image_alt="Test image",
   ...     price=Decimal("9.99"),
   ...     category=cat
   ... )
   ```

3. **Run development server:**

   ```bash
   python manage.py runserver
   ```

### Manual Test Checklist

#### Authentication and Email Verification

- [ ] Anonymous user visits /accounts/login/ → page loads
- [ ] Anonymous user visits /accounts/signup/ → page loads
- [ ] New user signs up with email → receives verification email (check console in dev)
- [ ] User clicks email verification link → redirected to confirm
- [ ] Unverified user tries to access /accounts/dashboard/ → redirected to /accounts/email/
- [ ] Verified user accesses /accounts/dashboard/ → dashboard loads

#### User Profile Management

- [ ] Verified user accesses /accounts/profile/ → profile page loads
- [ ] User updates display_name form → displays success message
- [ ] User accesses /accounts/delete_account/ → confirmation page with delete button
- [ ] User confirms deletion → account deleted, redirected to home, success message

#### Product Catalog

- [ ] Anonymous user visits /archive/ → lists only active products
- [ ] Product detail page shows title, image, description, price
- [ ] Active product accessible to anonymous user
- [ ] Staff user can edit product in admin → changes save
- [ ] Staff user marks product as inactive → removed from catalog for regular users
- [ ] Staff user can toggle featured status → appears/disappears in featured list

#### Shopping Cart

- [ ] Verified user adds product to cart → success message shown
- [ ] Cart persists across page visits
- [ ] Cart shows product title, price, quantity
- [ ] User removes product from cart → removed from display
- [ ] User views empty cart → "empty" message or CTA to browse

#### Checkout

- [ ] Verified user with items in cart accesses /checkout/
- [ ] Redirects to Stripe hosted checkout (test mode)
- [ ] User enters test Stripe card (4242 4242 4242 4242, exp 12/34, CVC 567)
- [ ] Stripe redirects to success page after payment
- [ ] Order appears in user's My Archive
- [ ] Admin can view order in Django admin with order details

#### Reviews

- [ ] User who purchased product can post review on product detail page
- [ ] User without purchase cannot see/post review form
- [ ] Posted review appears on product detail page
- [ ] User cannot post second review for same product (form disabled or error message)

#### Admin Interface

- [ ] Staff user accesses /admin/ → Django admin loads
- [ ] Regular user tries to access /admin/ → 403 Forbidden
- [ ] Admin bulk delete product with entitlements → error message, not deleted
- [ ] Admin bulk mark/remove featured → appears/disappears in featured list
- [ ] Admin edits product form → saves changes
- [ ] Admin deactivates product → removed from catalog for users

#### Archive Reading Experience

- [ ] Owner clicks "Read" in My Archive → opens reading page with full content
- [ ] Owner clicks "Read Full Archive" on preview page → opens reading page
- [ ] Preview page never shows full content, even for owners
- [ ] Anonymous user tries to access `/archive/<slug>/read/` → redirected to login
- [ ] Non-owner tries to access reading page → 403 Forbidden
- [ ] Reading page displays hero image, title, and complete archive text
- [ ] Reading page has "Back to My Archive" link
- [ ] Reading page has "View Details" link to preview page

#### Review Management

- [ ] Buyer submits review → appears on product page with "Verified purchase" badge
- [ ] User sees "Edit Review" and "Delete Review" buttons on their own review
- [ ] User clicks "Edit Review" → opens edit page with pre-filled form
- [ ] User edits review and saves → changes appear immediately on product page
- [ ] User clicks "Delete Review" → confirmation prompt appears
- [ ] User confirms deletion → review removed from product page
- [ ] User tries to edit another user's review → access denied
- [ ] User tries to delete another user's review → access denied

---

## Known Issues

None. All 128 automated tests pass.

---

## CI/CD & Continuous Integration

For production, tests should run in CI/CD pipeline:

- **GitHub Actions:** Add workflow file (example: `.github/workflows/test.yml`)
- **Pre-commit:** Run `pytest` before allowing commits
- **Deployment:** Require all tests to pass before deploying

### Example GitHub Actions Workflow

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.14'
      - run: pip install -r dev-requirements.txt
      - run: pytest --tb=short
```

---

## Debugging Failed Tests

If a test fails during development:

1. **Run with verbose traceback:**

   ```bash
   pytest <test_name> -vv --tb=long
   ```

2. **Show print/debug output:**

   ```bash
   pytest <test_name> -vv -s
   ```

3. **Stop on first failure:**

   ```bash
   pytest -x
   ```

4. **Run in debugger (pdb):**

   ```bash
   pytest <test_name> --pdb
   ```

5. **Check database state:**

   - Automated tests use in-memory SQLite (:memory:)
   - Each test gets a fresh database
   - Use `client.get()` and `response.context` to inspect request context
   - Print queries: `from django.db import connection; print(connection.queries)`

---

## Adding New Tests

When adding new features:

1. Create test file in app's `tests/` folder or `tests.py`:

   ```text
   apps/<app_name>/tests/
   ├── __init__.py
   ├── test_feature1.py
   └── test_feature2.py
   ```

2. Use existing fixtures from `conftest.py`:

   ```python
   import pytest

   @pytest.mark.django_db
   class TestNewFeature:
       def test_something(self, client, verified_user, product_active):
           """Test description in present tense."""
           # Arrange
           client.force_login(verified_user)
           
           # Act
           response = client.get(reverse("feature_url"))
           
           # Assert
           assert response.status_code == 200
   ```

3. Run tests to ensure they pass:

   ```bash
   pytest <new_test_file> -v
   ```

---

## Test Fixtures (conftest.py)

Available pytest fixtures in `conftest.py`:

- **`verified_user`** - User with verified email (for protected pages)
- **`unverified_user`** - User without verified email
- **`staff_user`** - Django superuser (for admin tests)
- **`category`** - Test Category object
- **`product_active`** - Active Product (is_active=True)
- **`product_inactive`** - Inactive Product (is_active=False)
- **`entitlement`** - AccessEntitlement for verified_user
- **`order_pending`** - Pending Order with line items
- **`order_paid`** - Paid Order (status='paid')
- **`client`** - Django test client (built-in pytest-django)
- **`db`** - Database access marker (built-in pytest-django)

---

## Manual Testing Checklist

### Error Pages Testing

To verify custom error pages work correctly in production:

1. **Test 404 Page:**
   - Navigate to `/nonexistent-url/`
   - Verify custom 404 page displays with dark fantasy styling
   - Check navigation links (Home, Archive, My Archive) work
   - Confirm page extends base template (has navbar, footer)

2. **Test 403 Page:**
   - Try accessing `/archive/<slug>/read/` without purchase
   - Verify custom 403 page displays
   - Check login/purchase prompts appear for non-authenticated users
   - Confirm "My Archive" link appears for authenticated users

3. **Test 500 Page:**
   - Temporarily introduce a server error (e.g., in a view)
   - Verify custom 500 page displays with inline styles
   - Check page works even when static files fail to load
   - Confirm basic navigation links work (no Django template tags)

4. **Test 400 Page:**
   - Send malformed POST request (e.g., missing CSRF token)
   - Verify custom 400 page displays
   - Check error message is clear and user-friendly

**Note:** Error pages should only be tested with `DEBUG=False` in settings.

### Security Headers Verification

Test security headers are properly set in production:

1. Open browser DevTools → Network tab
2. Load any page on live site
3. Check Response Headers for:
   - `X-Frame-Options: DENY`
   - `X-Content-Type-Options: nosniff`
   - `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`

Use online tools like [securityheaders.com](https://securityheaders.com/) for comprehensive analysis.

---

## Performance Notes

- **Full test suite:** ~1.5 seconds (110 tests)
- **Single test file:** ~0.3-0.5 seconds
- **Stripe mocking:** Uses `@patch()` to avoid real API calls
- **Database:** In-memory SQLite (fast, isolated, no cleanup needed)
- **Email:** In-memory backend (no real emails, checked via `response.context['messages']`)

---

## Support & Questions

For test failures or questions:

1. Check test output: `pytest -vv --tb=short`
2. Review test source code in app `tests/` folders
3. Check fixtures in `conftest.py`
4. Verify app views and models match test expectations
