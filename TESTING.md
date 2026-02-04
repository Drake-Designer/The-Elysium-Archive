# Testing Guide - The Elysium Archive

This document describes the current automated test suite and manual testing procedures for the repository as it stands.

## Current Test Status

**120 tests passing**

All automated tests run successfully with pytest. See the [Automated Tests](#automated-tests) section for details.

![pytest Results](documentation/testing/pytest.png)

---

## Evidence Status (Testing and Quality Checklist)

- Automated test suite documented: **Yes** (120 tests, all passing)
- Manual testing checklist provided: **Yes**
- Python style/lint checks completed: **Yes** (black, isort, flake8, pylint, djlint, bandit)
- Security audit completed: **Yes** (Bandit scan clean, 0 issues)
- HTML validation results recorded: **Yes** (all tested pages valid, see HTML Validation section)
- CSS validation results recorded: **Yes** (local styles valid; remaining errors are from external CDN libraries)
- JavaScript validation completed: **Yes** (JSHint, 0 errors)
- Responsiveness testing results recorded: **Yes** (mobile, tablet, and smart display tested)
- Accessibility testing results recorded: **In progress** (Lighthouse completed, manual checks pending)
- Best practices testing: **Yes** (Lighthouse Home - Mobile)
- SEO testing: **Yes** (Lighthouse Home - Mobile)
- Browser compatibility testing: **Yes**
- Performance testing: **Yes** (Lighthouse Home - Mobile)

This checklist is used to track the current state of testing, validation, and quality evidence within the repository.

---

## Automated Tests

### Tooling

- pytest 9.0.2
- pytest-django 4.11.1
- Tests are a mix of pytest-style functions and Django TestCase classes (notably in reviews).

### Automated Coverage Summary (Core Application Features)

The automated suite covers:

- CRUD workflows for products, reviews, and orders (model + view behaviour)
- Authentication and email-verification gates (allauth flows and protected pages)
- Payment flow logic (Stripe checkout session creation, webhooks, and entitlement creation)
- Data management and access control (entitlements, inactive product access rules)
- **Review system** (create, edit, delete with character limits and optional fields)
- **My Archive** (display of unlocked products with review/edit buttons)
- **Dashboard functionality** (profile, archive, orders, reviews tabs with review delete modal)

### Test Configuration

Pytest configuration lives in `pyproject.toml` under `[tool.pytest.ini_options]`:

- `DJANGO_SETTINGS_MODULE = "elysium_archive.settings_test"`
- `python_files = ["test_*.py", "*_test.py", "tests.py"]`
- `testpaths = ["TESTS"]`
- `addopts = "-ra"`

`elysium_archive/settings_test.py` overrides:

- `STATICFILES_STORAGE` uses `StaticFilesStorage`
- `STORAGES` uses `FileSystemStorage` for media and `StaticFilesStorage` for static
- `EMAIL_BACKEND` uses `django.core.mail.backends.locmem.EmailBackend`
- `ACCOUNT_EMAIL_HTML = True`
- `PASSWORD_HASHERS` uses `MD5PasswordHasher`

### Running Tests

Run all tests:

```bash
pytest
```

Verbose output:

```bash
pytest -v
```

Run a specific test file:

```bash
pytest TESTS/accounts/test_profile.py -v
```

Run a specific test class:

```bash
pytest TESTS/products/test_access_control.py::TestProductAccessControl -v
```

Run a specific test:

```bash
pytest TESTS/orders/test_orders.py::TestWebhookHandling::test_webhook_idempotent_same_event_twice -v
```

Show print output:

```bash
pytest -v -s
```

### Test Inventory Summary

**Total Tests:** 120

**Test Distribution by App:**

- Accounts: 20 tests (authentication, email verification, profile management, account deletion)
- Products: 29 tests (access control, archive reading, CRUD operations, product removal)
- Cart: 12 tests (cart operations, validation, totals)
- Checkout: 3 tests (checkout flow, Stripe integration, order reuse)
- Orders: 15 tests (webhook handling, order status, entitlements)
- Home: 18 tests (admin access, product management, deal banner visibility)
- Reviews: 10 tests (review creation, dashboard integration, removed products)
- Webhooks: 13 tests (idempotency, payment status, error handling)

Test discovery (under `TESTS/`) is controlled by `pyproject.toml`. Run `pytest --collect-only` to confirm the current test count.

---

## Automated Test Coverage by App

### Accounts

Files:

- `TESTS/accounts/test_auth_pages.py`
- `TESTS/accounts/test_email_gate.py`
- `TESTS/accounts/test_profile.py`

Coverage:

- Email verification gates for dashboard, profile, and my-archive; anonymous users redirected to login
- Dashboard tab rendering (My Orders, My Reviews) for verified users; display_name form updates
- Account deletion with confirmation, logout, redirect, and profile cascade removal

### Products

Files:

- `TESTS/products/test_access_control.py`
- `TESTS/products/test_archive_read.py`
- `TESTS/products/test_products.py`

Coverage:

- Active/inactive visibility by user role; entitlement required for read page access (403 without)
- Preview vs reading page content separation; email verification enforced for unpublished products
- Product model CRUD and navigation links; archive card layout validation

### Cart

File:

- `TESTS/cart/test_cart.py`

Coverage:

- Add/remove to cart with session persistence; verified email required for add-to-cart
- Validation for missing/inactive products; cart totals for single and multiple items

### Checkout

File:

- `TESTS/checkout/test_checkout.py`

Coverage:

- Verified email gate; Stripe session creation and mocked redirect; order/OrderLineItem from cart
- Double-submit safety (pending order reuse prevents duplicates); success fallback finalises payment if webhook delayed
- Cart clearing after success; wrong-user success page access blocked

### Orders and Webhooks

File:

- `TESTS/orders/test_orders.py`

Coverage:

- Webhook handling for `checkout.session.completed` (paid/unpaid), `payment_intent.payment_failed`, `checkout.session.expired`
- Idempotent entitlement creation (`get_or_create` on replay); atomic locking prevents duplicate orders
- Signature validation and POST-only enforcement; missing order ID/user gracefully handled

### Reviews

File:

- `TESTS/reviews/test_reviews.py`

Coverage:

- Form visibility for buyers only; create with optional title (50 chars) and body (1000 chars), mandatory rating (1-5 stars)
- Duplicate review prevention; cascade delete for user and product
- Edit/delete permissions enforced; delete requires POST and modal confirmation

### Home

File:

- `TESTS/home/test_home.py`

Coverage:

- Admin access restricted to staff (anonymous/regular users get 403 or redirect)
- Admin delete/bulk delete and featured flag toggle; staff-only order list/detail access

## Manual Testing Procedures

Manual tests validate user-facing behaviour, page rendering, and third-party flows not fully covered by automated tests.

### Critical User Journeys

| Journey | Steps | Expected Result |
|---------|-------|-----------------|
| **Sign Up & Email Verification** | Create account → verify email from console → login | Verified user can access dashboard |
| **Browse Archive** | Visit `/archive/` as anon/verified → click product | Active products listed; inactive hidden from non-staff |
| **Cart & Checkout** | Add product → checkout with Stripe test card → complete | Order marked paid; entitlement created; cart cleared |
| **Access Protected Content** | Entitled user visits `/archive/<slug>/read/` | Full content accessible; non-entitled users get 403 |
| **Create Review** | Buyer submits rating + optional title/body on product detail | Review displays with verified badge; non-buyers see no form |
| **Edit/Delete Review** | Click edit → update; click delete → confirm modal | Edit succeeds; delete requires POST + modal confirmation |

### Key Edge Cases (Manual Verification)

- [ ] Unverified user visits `/accounts/dashboard/` → redirected to `/accounts/email/`
- [ ] Unverified user tries checkout → redirected to email verification
- [ ] Non-entitled user visits read page → 403 Forbidden
- [ ] Wrong user accesses success page → redirected with error
- [ ] Review delete modal shows "Are you sure?" → "Stay" cancels, "Delete" removes review
- [ ] Rapid double-click checkout → only one pending order created (no duplicate)

### Test Data Setup

Create a superuser:

```bash
python manage.py createsuperuser
```

Create a test product:

```bash
python manage.py shell
>>> from products.models import Category, Product
>>> from decimal import Decimal
>>> cat = Category.objects.create(name="Test", slug="test")
>>> Product.objects.create(
...     title="Test Product",
...     slug="test-product",
...     description="Test description",
...     content="<p>Test premium content.</p>",
...     image_alt="Test image",
...     price=Decimal("9.99"),
...     category=cat,
...     is_active=True,
... )
```

Start the dev server:

```bash
python manage.py runserver
```

Note: Email is sent to console backend in DEBUG. Use verification link from terminal output.

### Stripe Test Mode

Webhook endpoint: `/checkout/webhook/`

Stripe CLI listener:

```bash
stripe listen --forward-to http://127.0.0.1:8000/checkout/webhook/
```

Test card: `4242 4242 4242 4242` with any future expiry and CVC

## Responsiveness Testing

The application has been tested across multiple device sizes to ensure responsive design and proper layout at all breakpoints. The project uses Bootstrap 5's responsive grid system with standard breakpoints.

### Breakpoints Covered

The application follows Bootstrap 5 breakpoints. Coverage is based on the devices tested and listed in the Device Test Results table below:

- Mobile portrait (320px - 575px)
- Mobile landscape (576px - 767px)
- Tablet (768px - 991px)
- Smart display/desktop (992px+)

### Device Test Results

| Device | Resolution | Orientation | Browser | Status | Evidence |
| --- | --- | --- | --- | --- | --- |
| iPhone SE | 375x667px | Portrait | Safari (iOS) | ✅ Tested | [Screenshot](documentation/testing/responsiveness-iphone-se.png) |
| Samsung Galaxy S20 | 360x800px | Portrait | Chrome (Android) | ✅ Tested | [Screenshot](documentation/testing/responsiveness-samsung-s20.png) |
| iPhone 14 Pro Max | 430x932px | Portrait | Safari (iOS) | ✅ Tested | [Screenshot](documentation/testing/responsiveness-iphone-14promax.png) |
| iPad Pro | 1024x1366px | Portrait | Safari (iPadOS) | ✅ Tested | [Screenshot](documentation/testing/responsiveness-ipad-pro.png) |
| Google Nest Hub Max | 1280x800px | Landscape | Chrome (Cast OS) | ✅ Tested | [Screenshot](documentation/testing/responsiveness-nesthubmax.png) |

### Device Coverage Summary

All tested mobile and tablet devices show consistent layout and usability.

#### iPhone SE

![iPhone SE Responsiveness](documentation/testing/responsiveness-iphone-se.png)

- Screen size: 375x667px
- Browser: Safari (iOS)
- Status: ✅ Tested and verified

#### Samsung Galaxy S20

![Samsung Galaxy S20 Responsiveness](documentation/testing/responsiveness-samsung-s20.png)

- Screen size: 360x800px
- Browser: Chrome (Android)
- Status: ✅ Tested and verified

#### Apple iPhone 14 Pro Max

![iPhone 14 Pro Max Responsiveness](documentation/testing/responsiveness-iphone-14promax.png)

- Screen size: 430x932px
- Browser: Safari (iOS)
- Status: ✅ Tested and verified

#### Apple iPad Pro

![iPad Pro Responsiveness](documentation/testing/responsiveness-ipad-pro.png)

- Screen size: 1024x1366px
- Browser: Safari (iPadOS)
- Status: ✅ Tested and verified

#### Google Nest Hub Max (Smart Display)

![Google Nest Hub Max Responsiveness](documentation/testing/responsiveness-nesthubmax.png)

- Screen size: 1280x800px
- Browser: Chrome (Cast OS)
- Status: ✅ Tested and verified

### Testing Summary

Key responsive features verified across tested devices:

- Mobile-first navigation (hamburger menu on mobile)
- Flexible grid layouts with appropriate column spans
- Typography scaling with viewport width
- Touch-friendly button/link sizing on mobile devices
- Proper spacing and padding at all breakpoints
- Image optimisation for different screen densities
- Form inputs properly sized for mobile interaction

**Status:** Tested mobile (360-430px), tablet (1024px), and smart display (1280px) breakpoints.

---

## Accessibility Testing

**Status:** In progress

Lighthouse Accessibility audit (Mobile, Moto G Power, Slow 4G throttling):

- Home page: **92** - ![Lighthouse Accessibility - Home](documentation/testing/lighthouse/accessibility-home.png)
- Archive page: **100** - ![Lighthouse Accessibility - Archive](documentation/testing/lighthouse/accessibility-archive.png)
- Product detail page: **96** - ![Lighthouse Accessibility - Product detail](documentation/testing/lighthouse/accessibility-product-detail.png)
- Shopping cart page: **96** - ![Lighthouse Accessibility - Cart](documentation/testing/lighthouse/accessibility-cart.png)
- Checkout success page: **94** - ![Lighthouse Accessibility - Checkout success](documentation/testing/lighthouse/accessibility-checkout-success.png)
- User dashboard page: **100** - ![Lighthouse Accessibility - Dashboard](documentation/testing/lighthouse/accessibility-dashboard.png)
- Lore page: **100** - ![Lighthouse Accessibility - Lore](documentation/testing/lighthouse/accessibility-lore.png)

Home page minor warnings:
- Minor contrast warnings on primary buttons (tracked; overall score acceptable)
- Carousel control button sizing for touch targets
- Video captions already present (accessibility compliance satisfied)

**Remaining tasks:** Keyboard navigation and screen reader smoke tests pending.

---

## Lighthouse Testing

Lighthouse 13.0.1, Mobile emulation, Slow 4G throttling, Single page session, Initial page load.

**URL tested:** https://the-elysium-archive-a51393fa9431.herokuapp.com/

**Latest Home (Mobile) results:**

- Performance: **92**
- First Contentful Paint (FCP): **2.7s**
- Largest Contentful Paint (LCP): **2.8s**
- Total Blocking Time (TBT): **0ms**
- Cumulative Layout Shift (CLS): **0.013**
- Speed Index (SI): **2.7s**

Scores can vary slightly between runs due to network throttling, server load, caching, and third‑party resources. Results above are from the latest run.

| Category | Score | Evidence |
| --- | --- | --- |
| Performance | 92 | ![Lighthouse Performance - Home Mobile](documentation/testing/lighthouse/performance-home.png) |
| Best Practices | 100 | ![Lighthouse Best Practices - Home Mobile](documentation/testing/lighthouse/best-practices-home.png) |
| SEO | 100 | ![Lighthouse SEO - Home Mobile](documentation/testing/lighthouse/seo-home.png) |

---

## Validation and Code Quality

### HTML Validation (W3C)

All key pages have been validated using the W3C HTML Validator and conform to HTML5 standards.

#### HTML Validation Results

**Public Pages:**

- [Home](https://validator.w3.org/nu/?doc=https%3A%2F%2Fthe-elysium-archive-a51393fa9431.herokuapp.com%2F) - ✅ Valid
- [Archive Listing](https://validator.w3.org/nu/?doc=https%3A%2F%2Fthe-elysium-archive-a51393fa9431.herokuapp.com%2Farchive%2F) - ✅ Valid
- [Product Detail (The Biological Purge)](https://validator.w3.org/nu/?doc=https%3A%2F%2Fthe-elysium-archive-a51393fa9431.herokuapp.com%2Farchive%2Fthe-biological-purge-viral-extermination-protocols%2F) - ✅ Valid
- [Lore Page](https://validator.w3.org/nu/?doc=https%3A%2F%2Fthe-elysium-archive-a51393fa9431.herokuapp.com%2Flore%2F) - ✅ Valid
- [Cart](https://validator.w3.org/nu/?doc=https%3A%2F%2Fthe-elysium-archive-a51393fa9431.herokuapp.com%2Fcart%2F) - ✅ Valid
- [Privacy Policy](https://validator.w3.org/nu/?doc=https%3A%2F%2Fthe-elysium-archive-a51393fa9431.herokuapp.com%2Fprivacy-of-the-covenant%2F) - ✅ Valid
- [Terms of Service](https://validator.w3.org/nu/?doc=https%3A%2F%2Fthe-elysium-archive-a51393fa9431.herokuapp.com%2Fterms-of-the-archiver%2F) - ✅ Valid
- [Contact](https://validator.w3.org/nu/?doc=https%3A%2F%2Fthe-elysium-archive-a51393fa9431.herokuapp.com%2Fcontact-the-lore%2F) - ✅ Valid

**Dashboard Pages (Authenticated):**

- [Dashboard - Profile Tab](https://validator.w3.org/nu/?doc=https%3A%2F%2Fthe-elysium-archive-a51393fa9431.herokuapp.com%2Faccounts%2Fdashboard%2F) - ✅ Valid
- [Dashboard - My Archive Tab](https://validator.w3.org/nu/?doc=https%3A%2F%2Fthe-elysium-archive-a51393fa9431.herokuapp.com%2Faccounts%2Fdashboard%2F%3Ftab%3Dmy-archive) - ✅ Valid
- [Dashboard - My Orders Tab](https://validator.w3.org/nu/?doc=https%3A%2F%2Fthe-elysium-archive-a51393fa9431.herokuapp.com%2Faccounts%2Fdashboard%2F%3Ftab%3Dmy-orders) - ✅ Valid
- [Dashboard - My Reviews Tab](https://validator.w3.org/nu/?doc=https%3A%2F%2Fthe-elysium-archive-a51393fa9431.herokuapp.com%2Faccounts%2Fdashboard%2F%3Ftab%3Dmy-reviews) - ✅ Valid
- [Dashboard - Delete Account Tab](https://validator.w3.org/nu/?doc=https%3A%2F%2Fthe-elysium-archive-a51393fa9431.herokuapp.com%2Faccounts%2Fdashboard%2F%3Ftab%3Ddelete) - ✅ Valid

**Authentication Pages:**

- [Login](https://validator.w3.org/nu/?doc=https%3A%2F%2Fthe-elysium-archive-a51393fa9431.herokuapp.com%2Faccounts%2Flogin%2F) - ✅ Valid
- [Signup](https://validator.w3.org/nu/?doc=https%3A%2F%2Fthe-elysium-archive-a51393fa9431.herokuapp.com%2Faccounts%2Fsignup%2F) - ✅ Valid
- [Email Verification](https://validator.w3.org/nu/?doc=https%3A%2F%2Fthe-elysium-archive-a51393fa9431.herokuapp.com%2Faccounts%2Femail%2F) - ✅ Valid

#### Summary

All tested pages conform to W3C HTML5 standards with no validation errors or warnings.

---

### CSS Validation (Jigsaw)

All custom CSS files were validated using the [W3C CSS Validation Service (Jigsaw)](https://jigsaw.w3.org/css-validator/).

Files validated:

- `static/css/base.css`
- `static/css/components/dashboard.css`
- `static/css/components/deal-banner.css`
- `static/css/components/products.css`
- `static/css/pages/home.css`
- `static/css/pages/lore.css`
- `static/css/pages/footer-pages.css`
- `static/css/admin/admin.css` (and modules)

**Status:** All project CSS files validated and passed. Remaining errors in full-page reports originate from external CDN libraries (Font Awesome, Bootstrap) and cannot be fixed in this repository.

**Evidence:** Validation screenshots stored in `documentation/testing/css-validation/`

### JavaScript Validation (JSHint)

All custom JavaScript files were validated with JSHint and returned no errors. Metrics warnings relate to complexity only.

Validated files:

- `static/js/admin/image-alt-counter.js`
- `static/js/checkout-status.js`
- `static/js/dashboard.js`
- `static/js/effects-toggle.js`
- `static/js/messages.js`
- `static/js/review-form.js`

### Python Style/Lint Checks

Available via `dev-requirements.txt`:

- `python -m black --check .`
- `python -m isort --check-only .`
- `flake8`
- `pylint`
- `bandit -c bandit.yaml -r accounts cart checkout home orders products reviews elysium_archive manage.py`
- `djlint --check .`

Results:

- `black --check .`: ✅ Passed after formatting
- `isort --check-only .`: ✅ Passed after formatting
- `flake8 .`: ✅ Passed with exclusions for `.venv` and migrations via `.flake8`
- `pylint accounts cart checkout home orders products reviews elysium_archive manage.py`: ✅ No output reported
- `bandit -c bandit.yaml -r accounts cart checkout home orders products reviews elysium_archive manage.py`: ✅ No issues reported
- `djlint --check .`: ✅ Passed (0 files would be updated)

#### Bandit Security Audit Details

Bandit is a security linter that scans Python code for common security issues. The project uses a custom configuration file (`bandit.yaml`) to focus scans on application code and skip false positives.

**Configuration (`bandit.yaml`):**

```yaml
# Bandit configuration
# Exclude test folders and generated assets.
exclude:
  - .venv
  - node_modules
  - staticfiles
  - migrations
  - TESTS
  - tests
skips:
  - B101  # assert_used - acceptable in test code
  - B308  # mark_safe - reviewed, only static HTML without user input
```

**Excluded Directories:**

- `.venv`, `node_modules`, `staticfiles`: third-party code and generated assets
- `migrations`, `TESTS`, `tests`: auto-generated code and test files

**Skipped Checks:**

- **B101** (assert_used): Acceptable in test code; excluded globally since tests are already excluded
- **B308** (mark_safe): All uses reviewed and confirmed safe (static HTML only, no user input)

**Security Improvements Implemented:**

1. **XSS Prevention:**
   - Replaced `mark_safe()` with `format_html()` in admin display methods where variables are interpolated
   - Retained `mark_safe()` only for completely static HTML (reviewed and documented)

2. **Password Security:**
   - Removed all hardcoded passwords from test fixtures
   - Implemented runtime password generation using `django.utils.crypto.get_random_string()`

3. **Secret Key Management:**
   - Removed hardcoded development secret key
   - Added `get_random_secret_key()` fallback for local development
   - Production validation ensures `SECRET_KEY` comes from environment

4. **Exception Handling:**
   - Added logging to all try/except blocks that previously used `pass`
   - Exceptions are now logged with `logger.warning()` and `exc_info=True`

**Scan Results:**

- **Lines Scanned:** 5,146 (application code only)
- **Issues Found:** 0 (Low: 0, Medium: 0, High: 0)
- **Status:** ✅ Clean

### Security Headers

With `DEBUG=False`, confirm response headers include:

- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`

## Browser Compatibility Testing

### Chrome Desktop (Windows)

Google Chrome desktop browser was used to verify that core user journeys and ecommerce flows operate correctly without layout, JavaScript, or navigation issues.

#### Test Results

| Item Tested | Result |
| --- | --- |
| Home page loads and renders correctly | PASS |
| Archive listing and product detail pages | PASS |
| Login and dashboard access (verified user) | PASS |
| Add to cart and cart display | PASS |
| Stripe checkout cancel flow | PASS |
| Cart persistence after cancel | PASS |
| Archive reading page (entitled user) | PASS |
| JavaScript console errors | None |

#### Environment

**OS:** Windows 11

**Browser:** Google Chrome

**Version:** 144.0.7559.133 (64-bit)

#### Evidence

**Checkout Cancelled Page:**

![Checkout Cancelled page](documentation/testing/checkout-cancelled.png)

**Shopping Cart After Cancellation:**

![Shopping Cart after cancellation](documentation/testing/shopping-cart.png)

### Firefox Desktop (Windows)

Mozilla Firefox desktop browser was used to verify that core user journeys and ecommerce flows operate correctly without layout, JavaScript, or navigation issues.

#### Test Results

| Item Tested | Result |
| --- | --- |
| Home page loads and renders correctly | PASS |
| Archive listing and product detail pages | PASS |
| Login and dashboard access (verified user) | PASS |
| Add to cart and cart display | PASS |
| Stripe checkout cancel flow | PASS |
| Cart persistence after cancel | PASS |
| Archive reading page (entitled user) | PASS |
| JavaScript console errors | None |

#### Environment

**OS:** Windows 11
**Browser:** Mozilla Firefox
**Version:** 147.0.2 (64-bit)

#### Evidence

Same evidence screenshots as Chrome Desktop:

- Checkout Cancelled page
- Shopping Cart after cancellation

---

## Known Issues

None recorded in this document yet. Update this section if issues are discovered during testing.
