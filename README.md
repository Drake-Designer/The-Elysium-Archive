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

**The Elysium Archive** is a story-driven, dark fantasy ecommerce project where you do not buy a file. You buy access.

Each product is an “archive entry” that unlocks a private page inside the site. After a successful Stripe test payment, the entry becomes visible in your personal archive area. You can read it whenever you want, but you cannot download it.

I built this as my Code Institute Milestone Project 4 using Django and PostgreSQL. I love the dark fantasy vampire vibe, so I used that theme to make the project feel like a real place: a secret library with locked shelves and invited guests.

### The Story Behind The Elysium Archive

I have always liked gothic worlds, vampire politics, and that “hidden society” feeling. So instead of building a generic shop, I built a site that feels like a private collection of forbidden texts.

The theme is not just decoration. It gives the project a good reason for:
- user accounts (your archive follows your account)
- permissions (only buyers can access locked pages)
- clear business rules (the content unlocks instantly after payment)

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


## Features

This section will be expanded as features are built milestone by milestone.


## Technical Overview


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


