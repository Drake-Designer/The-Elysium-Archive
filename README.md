![Code Institute Project](documentation/code-institute-img.png)

<h1 align="center">
  Milestone Project 4: The Elysium Archive
</h1>

![The Elysium Archive homepage screenshot](documentation/validation/am-i-responsive.webp)

[Live Site: Coming soon](#)

The Elysium Archive is a dark fantasy ecommerce site where each purchase unlocks a private archive page you can only access on the website.  
No downloads. No loose files. Just secrets.


## Contents

- [Project Overview](#project-overview)
- [How The Elysium Archive Works](#how-the-elysium-archive-works)
- [Feature Summary](#feature-summary)
- [User Experience Design](#user-experience-design)
- [Features](#features)
- [Technical Overview](#technical-overview)
- [Technologies Used](#technologies-used)
- [Database Design](#database-design)
- [Testing and Bug Fixes](#testing-and-bug-fixes)
- [Running the Project Locally](#running-the-project-locally)
- [Deployment](#deployment)
- [Behind the Scenes: My Development Journey](#behind-the-scenes-my-development-journey)
- [Future Improvements](#future-improvements)
- [Credits](#credits)


## Project Overview

**The Elysium Archive** is a story-driven, dark fantasy ecommerce project where you do not buy a file, you buy access.

Each product represents an archive entry, a forbidden text stored inside a private, vampire-only archive. After a successful Stripe (test) payment, the entry unlocks a hidden page within the site and becomes part of your personal archive.

The content can be read online at any time, but it is never downloadable, reinforcing the idea of secrecy and exclusivity.

I built this project as my Code Institute Milestone Project 4 using Django and PostgreSQL. Inspired by gothic vampire lore and secret societies, The Elysium Archive is designed to feel like a real place: an ancient library reserved for invited members only.


### The Story Behind The Elysium Archive

The project is inspired by gothic vampire lore and the idea of a hidden society that exists alongside the ordinary world.

Rather than presenting content as a traditional online shop, the platform is designed as a private collection of forbidden texts, accessible only to verified members.

The dark fantasy theme supports the core logic of the platform by providing a narrative reason for:

- User accounts tied to a personal archive
- Access permissions based on verified purchases
- Immediate content unlocking after payment


### What You Get

- A themed product catalog (digital content)
- Secure account system (register, login, logout)
- Stripe checkout in test mode
- Order confirmation and order history
- A private “My Archive” area with unlocked entries
- Protected archive pages
- Verified buyer reviews
- Profile management and full account deletion


### Who It Is For

- Visitors who enjoy dark fantasy themes and want to browse teasers
- Members who want a buy once, access forever experience
- Developers exploring a complete and structured Django project

Refunds are not supported by design. Archive entries unlock immediately after purchase.


## How The Elysium Archive Works

1. Visitors browse the catalog without an account.
2. Users register to purchase content.
3. Checkout is handled via Stripe in test mode.
4. After payment, the product is unlocked for the user.
5. The entry appears in “My Archive”.
6. Only verified buyers can leave reviews.
7. Users can manage or delete their account.


## Feature Summary

### Catalog and Purchases

- Browse products with title, price, and description
- Product detail pages with a clear purchase flow
- Stripe test checkout and confirmation


### Archive Access Control

- Private “My Archive” area
- Individual protected archive pages
- Direct URL access is blocked


### Reviews (Verified Buyers Only)

- Reviews available only after purchase
- Displayed on product pages
- Simple validation for clean feedback


### Profiles

- Edit account details
- View order history
- Delete account permanently


## User Experience Design

To keep this section simple and easy to scan, it is organized in the following order:

1. [User Stories](#user-stories)
2. [Site Structure](#site-structure)
3. [Wireframes](#wireframes)
4. [Color Palette and Typography](#color-palette-and-typography)


### User Stories

User stories are planned and tracked using GitHub Projects.

[GitHub Project board](https://github.com/users/Drake-Designer/projects/5)


### Site Structure

The site structure was designed to support a clear journey from public browsing to protected content access.

**Public areas**
- Homepage
- Product catalog
- Product detail pages
- Registration and login pages

**Restricted areas**
- Shopping cart
- Checkout
- Order confirmation
- My Archive area
- Protected archive pages
- User profile and order history

Restricted areas require authentication and verified purchases.


### Wireframes

Wireframes define layout and user flow before development.  
They focus on structure and usability rather than visual design.

All wireframes were created using Balsamiq.

#### Desktop Wireframes

Designed for a 27 inch QHD display (2560x1440).

![Desktop Wireframe](documentation/wireframes/desktop.png)

#### Mobile Wireframes

Optimized for common mobile and tablet devices.

![Mobile Wireframe](documentation/wireframes/mobile.png)


### Color Palette and Typography

The visual identity supports the dark fantasy theme while remaining readable and accessible.

#### Color Palette

- **Void Black (`#0b0b0f`)**  
  Main background color.

- **Obsidian Grey (`#14141b`)**  
  Secondary background color for sections and cards.

- **Ash White (`#e6e6eb`)**  
  Primary text color.

- **Blood Crimson (`#8b1e2d`)**  
  Accent color for call-to-action elements.

- **Relic Gold (`#c2a14d`)**  
  Premium accent color for archive highlights.

All color combinations were tested for WCAG contrast compliance.

![Color Palette](documentation/color-palette.png)


#### Typography

The project uses the following Google Fonts:

- **Playfair Display**  
  Used for headings and section titles.

- **Inter**  
  Used for body text and UI elements.

- **Cinzel**  
  Considered as an alternative decorative heading font.

Typography rules:

- Serif fonts are used only for headings.
- Sans-serif fonts are used for body text and UI.
- No more than two font families are used at the same time.
- Readability is always prioritised.

![Google Fonts](documentation/google-fonts.png)


## Features

This section will be expanded milestone by milestone.


## Technical Overview

The project uses a modular Django architecture.  
Each app handles a specific area of functionality.

### Django Apps Structure

- `home` – Public-facing pages and layout
- `accounts` – Authentication and profile management
- `products` – Product catalog and protected archive content
- `cart` – Shopping cart logic
- `checkout` – Stripe checkout handling
- `orders` – Order storage and history
- `reviews` – Verified buyer reviews


## Technologies Used

- HTML, CSS, JavaScript
- Python and Django
- PostgreSQL
- Stripe (test mode)
- Bootstrap


## Database Design

This project uses a relational database designed to support secure access control, verified purchases, and protected premium content.

### Business Rules

- Users can register and authenticate.
- Users can purchase products via Stripe checkout.
- A successful payment unlocks access to premium on-site content.
- Content is accessible only within the website and is never downloadable.
- Access is granted per product and linked to the purchasing user.
- Only verified buyers can leave a review for a product.

### Core Entities

- **User**  
  Django built-in authentication user.

- **UserProfile**  
  One-to-one extension of the User model for profile-related data.

- **Product**  
  Represents a premium archive entry available for purchase.

- **Order**  
  Stores checkout and payment-related information.

- **OrderLineItem**  
  Links products to an order and records purchased items.

- **AccessEntitlement**  
  Represents granted access to a product for a specific user after payment.

- **Review**  
  Product review linked to a verified purchase.

Each entity and relationship is designed to be Django-friendly and simple to reason about, avoiding unnecessary complexity while supporting all required functionality.

### Data Model Overview

The database follows a relational structure implemented using Django ORM and PostgreSQL.

Each model uses Django’s default primary key. Relationships are defined using foreign keys and one-to-one fields where appropriate.

**Key design choices:**
- Users are managed using Django’s built-in authentication system.
- Profile data is stored separately using a one-to-one UserProfile model.
- Products represent premium archive entries.
- Orders and OrderLineItems store purchase history.
- Access to premium content is controlled via an explicit AccessEntitlement model.
- Reviews are restricted to verified buyers only.

### Core Relationships

- **User to UserProfile**: One-to-one relationship for profile data.
- **User to Order**: One-to-many relationship to track purchase history.
- **Order to OrderLineItem**: One-to-many relationship for purchased items.
- **User to Product**: Many-to-many relationship implemented via AccessEntitlement.
- **AccessEntitlement**: Grants access to a specific product for a specific user after payment.
- **Product to Review**: One-to-many relationship for verified buyer reviews.

This structure keeps access control simple, auditable, and aligned with Django best practices.

### ERD (Entity Relationship Diagram)

The Entity Relationship Diagram (ERD) below illustrates the structure of the database used in this project.

It shows the main entities, their primary and foreign keys, and how they relate to each other.  
The diagram reflects the relational data model implemented using Django ORM and PostgreSQL.

The ERD was created using **[Mermaid Live](https://mermaid.live/)**, a diagramming tool that allows database relationships to be defined using clear, readable syntax and exported as an image.

Key aspects highlighted in the ERD:
- One-to-one relationship between User and UserProfile.
- One-to-many relationships for orders and order line items.
- Explicit many-to-many relationship between users and products via AccessEntitlement.
- Access-based control of premium content.
- Reviews linked to verified purchases only.

![ERD Diagram](documentation/erd.png)




## Testing and Bug Fixes

For detailed testing, see [TESTING.md](TESTING.md).


## Running the Project Locally

This project uses environment variables for environment specific configuration and to keep secrets out of version control.

Local development uses a file called `env.py` in the project root.  
This file sets environment variables for local development only and is loaded automatically by the Django settings if present.

The `env.py` file must never be committed.

### Local setup

1. Create and activate a virtual environment.
2. Install production dependencies:
   - `pip install -r requirements.txt`
3. Optional: install development dependencies:
   - `pip install -r dev-requirements.txt`
4. Create an `env.py` file in the project root.
5. Run the development server:
   - `python manage.py runserver`

### Example `env.py`

Create a file named `env.py` in the project root (same level as `manage.py`):

```python
import os

os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("SECRET_KEY", "local-dev-secret-key-change-me")
os.environ.setdefault("ALLOWED_HOSTS", "127.0.0.1,localhost")
```

### DEBUG auto-switch

DEBUG is controlled by an environment variable:

- If `DEBUG` is not set, the project defaults to DEBUG True in local development.
- On Heroku, DEBUG is set to False using a config var.


## Deployment

The project will be deployed on Heroku.

Production configuration uses Heroku Config Vars, which become environment variables at runtime.  
The production environment does not use `env.py`.

### Required config vars

The following values are required on Heroku:

- `DEBUG=False`
- `SECRET_KEY`
- `DATABASE_URL`

More config vars are added as the project grows (Stripe keys, webhook secret, and other settings).

### DEBUG auto-switch in production

Production must always set:

- `DEBUG=False`

This keeps Django debug mode disabled in production while keeping local development convenient.


## Behind the Scenes: My Development Journey


## Future Improvements


## Credits
