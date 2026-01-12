[33me1ba291[m[33m ([m[1;36mHEAD[m[33m -> [m[1;32mmain[m[33m, [m[1;31morigin/main[m[33m, [m[1;31morigin/HEAD[m[33m)[m Add signup email templates and fix email styling
[33m6df536e[m Enable HTML emails for allauth in settings.py
[33mbb04f58[m Fix email templates and add base_message.html
[33mca94a0c[m Move all tests to TESTS folder and fix test issues
[33me90f264[m Replace Home 'Coming Soon' cards with real, implemented features
[33mf225ca7[m Add admin alt text safety feature and update README on bug fixes
[33m88f1f39[m Add deal banner bar with dynamic scrolling, admin controls, and deal integration
[33mb88c412[m Add deal banner bar with dynamic scrolling, admin controls, and deal integration
[33m007f9db[m Add clickable category badges and unified tag filtering on archive
[33m77e45f7[m Fix checkout flow, account dashboard tabs, My Archive access, and email confirmation UX
[33m7049bd1[m Fix mixed content errors for Cloudinary images
[33m62f6c54[m Fix intermittent carousel image loading
[33m65dfe8a[m Fix style on 500.html error page template
[33m42dfb8c[m Add staff-only error page testing dashboard
[33mbc45362[m Add missing allauth and CKEditor 5 URL includes
[33m1979beb[m Fix static files not served on Heroku by adding collectstatic to release command
[33m3a5ff40[m Refactor account deletion template, fix cart URL in checkout, and enable superadmin archive access
[33m449606c[m Delete unstable CKEditor version and install django-ckeditor-5==0.2.19
[33m4b67644[m Configure CKEditor for product content with safe image handling
[33mccb8be2[m Add custom error pages with consistent styling, configure production security headers, validate full test suite, and updating README and testing documentation
[33mcd0441a[m Add dedicated archive reading pages, implement review edit and delete, and update tests and documentation to confirm access control and review ownership
[33m51aac42[m Add missing automated tests, ensure full test coverage, and document testing approach
[33ma8f20f8[m Add verified buyer reviews, refactor My Archive to display all purchased content with direct access, centralize entitlement checks, add Admin Power Tools, and update documentation
[33m72477d9[m Fix Stripe webhook signature exception import
[33mb1287ef[m Complete Stripe webhook flow, orders, entitlements, and documentation
[33m7d999ef[m Implement Stripe hosted checkout session with pending order creation, add checkout success and cancel pages with order summary and cart handling, and update the README with a full Stripe payments section, testing instructions, test card details, and clarification about Link appearing in the hosted checkout UI in test mode
[33m388ca5b[m Update README with email verification rules, profile features, and email styling requirements
[33m44e0a49[m fix: correct allauth email confirmation template to submit the confirmation key properly and prevent 404 errors on email verification
[33m51e6542[m Fix media storage configuration by using Cloudinary as the default file storage in production, aligning Django storage settings with environment variables and ensuring profile images are served correctly on Heroku.
[33m4f26ce0[m Improve email compatibility by inlining all account email styles, removing the unused email stylesheet and obsolete assets, and cleaning up email button content.
[33me85185c[m Improve user profile experience with profile picture support, consistent display name usage, superuser protection, better mobile responsiveness, fixed email templates, proper media handling, and code cleanup.
[33md572386[m Refactor cart to single purchase model with presence based storage, remove all quantity update functionality, add in-cart indicator on archive catalog with quick link to shopping cart for products already added
[33md53b52f[m Implement session based shopping cart with add, view, and remove functionality. Add quantity update feature to cart page with visual feedback and JavaScript enhancements. Create Order and OrderLineItem models with admin interface and implement order creation from cart data
[33m48a90c9[m Refactor templates and static assets to improve archive search markup, navigation and message layout, standardize code comments, introduce an initial checkout route with placeholder view, update email styling, and enhance CSS and JavaScript for dashboard, cart, and product layouts
[33m2674712[m Create shopping cart with session storage, add cart item management, display cart with order summary, integrate cart navigation in navbar and product detail
[33m88c7262[m Enhance lore page with images and unified styling, gate registration calls to action to anonymous users
[33m3bf34b0[m Add search functionality to archive catalog, gate registration calls-to-action to anonymous users, unlock browse entries feature for authenticated members, and link carousel featured entries directly to product detail pages
[33m0e4e8ad[m Add release phase to run migrations on deploy
[33m6866a72[m Implement complete product catalog with category model, admin interface, seed data, public list and detail views, shopping cart integration, and euro pricing display
[33mb73d2a5[m Add content and category fields to Product model, implement get_absolute_url method, configure ProductAdmin with organized fieldsets and prepopulated slug generation, and create seed_products management command that populates database with twenty Bloodlines Masquerade-inspired archive entries including ten clan archives and ten miscellaneous archives
[33m5b7fd6b[m Implement functional dashboard tab switching with inline JavaScript, remove debug code and superfluous test files, eliminate unused CSS for deprecated Bootstrap Tab implementation, and correct product CRUD test assertions for Decimal price fields
[33m1818b3e[m Add django-allauth implementation, email templates, and comprehensive documentation to README
[33m0a053fa[m Add complete allauth template overrides for password reset, change and email
[33mec7fa4e[m Test: configure pytest and remove legacy tests.py, add pytest.ini for pytest-django settings and discovery patterns, remove empty accounts/tests.py to avoid conflicts with accounts/tests/ package, keep auth page tests under accounts/tests/test_auth_pages.py (pytest -q passes)
[33m858035e[m Adopt django-allauth for authentication; expand accounts with user domain features
[33m414073e[m Integrate django-allauth for authentication with custom templates, remove old auth views, add email verification, and create pytest tests
[33m117d880[m Add reusable Django messages include, wire it into the base layout, and auto dismiss alerts after five seconds
[33m626a3cf[m Use custom authentication forms and add clear success, info, and error messages for register, login, and logout flows
[33m6de862e[m Add simple RegisterForm and LoginForm with Bootstrap styling, placeholders, and autocomplete hints for authentication forms
[33m601c5cc[m Fix the navbar brand animated border sizing on large screens, add missing navigation list classes to match styling hooks, and tidy base templates and the effects toggle script by removing duplication while keeping the same layout and behavior.
