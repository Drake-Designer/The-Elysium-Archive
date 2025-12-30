![Code Institute Project](documentation/code-institute-img.png)

<h1 align="center">
  Milestone Project 4: The Elysium Archive
</h1>

![The Elysium Archive homepage screenshot](documentation/validation/am-i-responsive.webp)

[Live Site: Coming soon](#)

The Elysium Archive is a dark fantasy ecommerce site where each purchase unlocks a private archive page you can only access on the website. No downloads. No loose files. Just secrets.


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

Each product represents an archive entry, a forbidden text stored inside a private, vampire-only archive. After a successful Stripe (test) payment, the entry unlocks a hidden page within the site and becomes part of your personal archive. The content can be read online at any time, but it is never downloadable, reinforcing the idea of secrecy and exclusivity.

I built this project as my Code Institute Milestone Project 4 using Django and PostgreSQL. Inspired by gothic vampire lore and secret societies, I designed The Elysium Archive to feel like a real place: an ancient library reserved for invited members only, where every unlocked page reveals a fragment of a hidden world.

### The Story Behind The Elysium Archive

The Elysium Archive is inspired by gothic vampire lore and the idea of a hidden society that exists alongside the ordinary world. Rather than presenting content as a traditional online shop, the project is designed as a private collection of forbidden texts, accessible only to invited members.

The dark fantasy theme is not purely aesthetic. It supports the core logic of the platform by providing a clear narrative reason for:

- User accounts, as each archive is tied to a specific member
- Access permissions, where only verified buyers can unlock protected pages
- Clear business rules, with content unlocking instantly after a successful payment

### What You Get

- A themed product catalog (digital content)
- Secure account system (register, login, logout)
- Stripe checkout in test mode
- Order confirmation and order history
- A private “My Archive” area with unlocked entries
- Protected archive pages (accessible only after purchase)
- Verified buyer reviews (only after purchase)
- Profile management and full account deletion
- Dark UI using Bootstrap with custom styling

### Who It Is For

- Visitors who enjoy dark fantasy themes and want to browse teasers before buying  
- Members who want a clean “buy once, access forever” experience on the site  
- People who enjoy exploring a complete Django project that is structured, realistic, and built step by step with care  

Refunds are not supported by design. Archive entries are treated as top-secret content that unlocks immediately after purchase.


## How The Elysium Archive Works

1. Visitors can browse the catalog and view product teasers without an account.
2. Users create an account to buy and access content.
3. Checkout happens via Stripe in test mode.
4. After a successful payment, the product is marked as unlocked for that user.
5. The unlocked entry appears in “My Archive”.
6. Only verified buyers can leave a review for a product.
7. Users can edit their profile or delete their account permanently.


## Feature Summary

### Catalog and Purchases

- Browse products with title, price, and short description
- View a product detail page with a clear purchase flow
- Stripe test checkout and order confirmation

### Archive Access Control

- Private “My Archive” area for unlocked entries
- Each entry has its own protected page
- Users cannot access archive pages unless they purchased them

### Reviews (Verified Buyers Only)

- Leave a review only after purchasing the product
- Reviews are visible on the product detail page
- Simple validation to keep feedback clean and readable

### Profiles

- Edit account details
- View purchase history and order details
- Delete account permanently


## User Experience Design

To keep this section simple and easy to scan, it is organized in the following order:
1. User Stories (tracked on GitHub Projects)
2. Site Structure
3. Wireframes
4. Color Palette and Typography

### User Stories

User stories are planned and tracked using GitHub Projects.

[GitHub Project board](https://github.com/users/Drake-Designer/projects/5)

### Site Structure

The site structure of The Elysium Archive was designed to support a clear and intuitive user journey, from public browsing to protected content access.

The platform is divided into public and restricted areas:

**Public areas**
- Homepage
- Product catalog (archive entries preview)
- Product detail pages
- Registration and login pages

These pages are accessible without authentication and allow visitors to explore the concept and available archive entries before committing to a purchase.

**Restricted areas**
- Shopping cart
- Checkout
- Order confirmation
- Personal “My Archive” area
- Protected archive entry pages
- User profile and order history

Restricted areas require authentication and, where applicable, a verified purchase.  
Direct URL access to protected content is blocked to prevent unauthorized viewing.

This structure ensures a smooth transition from visitor to registered user, and from customer to archive member, while keeping private content secure.

### Wireframes

Wireframes were created during the planning phase to define the layout, structure, and user flow of the application before development began.

The goal of the wireframes was to focus on usability and content hierarchy rather than visual design. All wireframes were created using Balsamiq and cover both desktop and mobile experiences.

#### Desktop Wireframes

The desktop wireframes were designed for a Windows PC with a 27" display (QHD 2560x1440).  
They show the main homepage layout, including navigation, hero section, featured archive entries, and the access flow explanation.

![Desktop Wireframe](documentation/wireframes/desktop.png)

#### Mobile Wireframes

Mobile wireframes were created to ensure a clear and consistent user experience across different devices.  
Layouts were tested and adapted for the following screen sizes:

- iPhone 15 Pro (6.1")
- iPad Pro (12.9")
- Samsung Galaxy S24 (6.2")

The mobile designs prioritize readability, vertical scrolling, and simplified navigation using a hamburger menu where appropriate.

![Mobile Wireframe](documentation/wireframes/mobile.png)


## Features

This section will be expanded as features are built milestone by milestone.


## Technical Overview

The Elysium Archive is built using a modular Django architecture.  
Each Django app is responsible for a specific area of functionality and is directly linked to the user stories defined during the UX planning phase.

This approach keeps the codebase organized, readable, and aligned with real-world development practices. It also makes it easier to develop, test, and maintain each feature independently.

### Django Apps Structure

The project is divided into the following Django apps:

#### `home`
Handles the public-facing structure of the site, including the homepage, static content, layout, and general navigation.  
This app provides the core presentation layer of the project.

#### `accounts`
Manages user authentication and account-related features, including:
- User registration
- Login and logout
- Profile management
- Account deletion

All features related to user identity and access control are handled here.

#### `products`
Responsible for the product catalog and protected archive content.  
This app includes:
- Product listing and product detail pages
- Product data and relationships
- Protected archive entry pages unlocked after purchase
- Access control to ensure only verified buyers can view archive content

#### `cart`
Handles the shopping cart functionality.  
Users can add, remove, and update products in their cart before proceeding to checkout.  
This app manages cart state and ensures the checkout flow only starts when the cart contains items.

#### `checkout`
Manages the payment process using Stripe in test mode.  
This includes:
- Creating Stripe checkout sessions
- Handling payment success and cancellation
- Validating payment completion before granting access

#### `orders`
Stores and manages completed orders.  
This app is responsible for:
- Order confirmation pages
- Order history for logged-in users
- Linking purchased products to user accounts

#### `reviews`
Handles product reviews submitted by verified buyers.  
Only users who have purchased a product can leave a review, ensuring feedback is genuine and relevant.

### User Stories and App Mapping

Each user story is linked to one primary Django app and tracked using GitHub Projects.  
This ensures a clear connection between planning, implementation, and final features.


## Technologies Used

- HTML, CSS, JavaScript
- Python and Django
- PostgreSQL
- Stripe (test mode)
- Bootstrap


## Database Design


## Testing and Bug Fixes

For detailed testing documentation, see [TESTING.md](TESTING.md).


## Running the Project Locally


## Deployment

This project will be deployed on Heroku. Deployment steps will be documented here, including:
- environment variables
- PostgreSQL configuration
- automatic DEBUG switching for local vs production


## Behind the Scenes: My Development Journey


## Future Improvements


## Credits
