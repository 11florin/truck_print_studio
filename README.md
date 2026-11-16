# Truck Print Studio

## About the project

I created Truck Print Studio as an online shop for people who are interested
in trucks and road transport in the United Kingdom. The products are
made-to-order clothing and mugs with designs inspired by life on the road.

I wanted a visitor to understand the purpose of the shop immediately, find a
product and reach checkout without being forced to create an account. For
returning customers, I added accounts, wishlists, reviews and order history.

The application is built with Django and uses a relational database. I split
the functionality into the `shop`, `orders` and `accounts` applications so
that each part has a clear responsibility.

## Contents

- [Purpose and target audience](#purpose-and-target-audience)
- [Features](#features)
- [Design and UX](#design-and-ux)
- [Technologies](#technologies)
- [Project structure](#project-structure)
- [Database schema](#database-schema)
- [User stories](#user-stories)
- [Local installation](#local-installation)
- [Testing](#testing)
- [Bugs found and fixed during testing](#bugs-found-and-fixed-during-testing)
- [Deployment to Heroku](#deployment-to-heroku)
- [Security](#security)
- [Git and development process](#git-and-development-process)
- [Limitations and next steps](#limitations-and-next-steps)

## Purpose and target audience

The main audience is made up of drivers, dispatchers and people interested in
UK road transport. I chose this subject because it has a recognisable visual
identity and gives the shop a clear audience rather than making it a generic
store.

The main journey I designed is:

```text
Homepage -> Catalogue -> Product details -> Bag -> Checkout -> Stripe -> Confirmation
```

Visitors can browse and buy as guests. After signing in, customers can save
products, write reviews and view their orders.

## Features

- A homepage that explains the purpose of the shop clearly.
- A Bootstrap carousel for featured products.
- Dynamic categories: Hoodie, Sweatshirt, Mugs and T-Shirts.
- Search by product name and description.
- Filtering by category and product type.
- Product detail pages with images, descriptions, prices and reviews.
- Sizes `S`, `M`, `L`, `XL` and `XXL` for T-shirts and Hoodies.
- A session-based bag.
- Product images, sizes, quantities and totals in the bag.
- Guest checkout.
- Stripe Checkout.
- A Stripe webhook for confirming the actual payment result.
- Pending, paid, failed, cancelled and expired payment states.
- The transaction ID shown in the order confirmation.
- Payment confirmation emails through Resend or Gmail SMTP.
- Registration, login, logout and password reset.
- Wishlist functionality.
- Review create, update and delete functionality.
- Order history and order details.
- Django Admin for managing application data.
- Cloudinary for production images.
- WhiteNoise for static files.
- Controlled handling of unknown URLs.

## Design and UX

I kept the interface simple and focused on the product. On the homepage I
placed the main message and a button leading to the catalogue. In the
navigation I kept the actions I consider most important: categories, shop,
bag and account.

On the product page, information is presented in the order in which I expect
a customer to need it: image, name, description, price, size and then the
add-to-bag action.

I used:

- semantic elements such as `nav`, `main`, `section`, headings and labels;
- alternative text for product images;
- visible messages after important actions;
- server-side form validation;
- a responsive Bootstrap layout;
- labelled carousel controls;
- no autoplay audio or aggressive pop-ups;
- external links opened in a separate tab with `noopener noreferrer`.

I documented the visual structure and design decisions in
[docs/design.md](./docs/design.md). The relational diagram is in
[docs/erd.md](./docs/erd.md).

## Technologies

- Python 3.12
- Django 6.1.2
- Django ORM and migrations
- SQLite for local development
- PostgreSQL for production
- HTML5 and Django templates
- CSS3
- Bootstrap 5
- Stripe Checkout and Stripe webhooks
- Cloudinary
- Resend or Gmail SMTP
- Gunicorn
- WhiteNoise
- Heroku
- Git and GitHub

The exact versions are kept in [requirements.txt](./requirements.txt).

## Project structure

```text
truck_print_studio/
├── accounts/
│   ├── email_backend.py
│   ├── forms.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── docs/
│   ├── design.md
│   ├── erd.md
│   ├── screenshots.md
│   └── user-stories.md
├── orders/
│   ├── email_service.py
│   ├── forms.py
│   ├── models.py
│   ├── stripe_service.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── shop/
│   ├── context_processors.py
│   ├── forms.py
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── static/
│   ├── css/
│   └── images/
├── templates/
│   ├── accounts/
│   ├── orders/
│   ├── registration/
│   └── shop/
├── truck_print_config/
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   ├── asgi.py
│   └── wsgi.py
├── manage.py
├── Procfile
├── README.md
└── requirements.txt
```

`shop` contains the catalogue, bag, wishlist and reviews. `orders` contains
checkout, orders and the Stripe integration. `accounts` contains
authentication and password-reset emails.

## Database schema

The complete schema is available in [docs/erd.md](./docs/erd.md).

### Category

Stores the name and slug of a category. One category can contain many
products.

### Product

Stores the name, slug, product type, design theme, description, price, image,
`active`, `featured` and `made_to_order` flags, and creation date.

### Order

Stores the authenticated customer when there is one, checkout email, delivery
address, total, payment status, Stripe Checkout Session ID, Stripe Payment
Intent ID, payment date and confirmation-email status.

### OrderItem

Links a product to an order and stores the quantity, purchase price and
selected size. I keep the price in `OrderItem` so that a later catalogue
change does not alter older orders.

### Review

Links a user to a product and stores the rating, comment and timestamps. A
user can only update or delete their own review.

### Wishlist

Links a user to a product. A unique database constraint prevents the same
product from being saved twice by the same user.

### Coupon

Stores the code, discount percentage, active status and optional expiry date.

### Important relationships

- `Category` has many `Product` records.
- `User` can have many `Order`, `Review` and `Wishlist` records.
- `Product` can have many `Review` and `Wishlist` records.
- `Order` has one or more `OrderItem` records.
- `OrderItem` refers to the purchased product.
- Database constraints prevent invalid prices, quantities and discounts.

## User stories

### Catalogue

- As a visitor, I want to understand immediately what the shop offers.
- As a visitor, I want to see active and featured products.
- As a visitor, I want to search by name or description.
- As a visitor, I want to filter by category and product type.
- As a visitor, I want to see the image, description, price and sizes.

### Bag and checkout

- As a guest, I want to choose a size for clothing.
- As a guest, I want to buy products without sizes, such as mugs.
- As a guest, I want to see the image, size, quantity and total in my bag.
- As a guest, I want to remove a specific bag variant.
- As a customer, I want to submit delivery details and pay through Stripe.
- As a customer, I want feedback when payment succeeds or fails.
- As a customer, I want to see the order number and transaction ID.

### Accounts

- As a visitor, I want to create an account with a valid email address.
- As a user, I want to sign in and sign out.
- As a user, I want to reset my password.
- As an authenticated user, I want to see only my own orders.
- As an authenticated user, I want to manage my own reviews.
- As an authenticated user, I want to save products to a wishlist.

The extended user-story list is in
[docs/user-stories.md](./docs/user-stories.md).

## Local installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

For local development I use a `.env` file, which must not be committed to
Git:

```env
SECRET_KEY=replace-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000
DATABASE_URL=optional-local-postgresql-url
STRIPE_SECRET_KEY=sk_test_replace-me
STRIPE_WEBHOOK_SECRET=whsec_replace-me
STRIPE_CURRENCY=gbp
CLOUDINARY_URL=cloudinary://replace-me
```

For email I can configure Resend:

```env
EMAIL_BACKEND=accounts.email_backend.ResendEmailBackend
RESEND_API_KEY=re_replace-me
DEFAULT_FROM_EMAIL=Truck Print Studio <verified-sender@example.com>
```

or Gmail SMTP:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-account@gmail.com
EMAIL_HOST_PASSWORD=your-google-app-password
DEFAULT_FROM_EMAIL=Truck Print Studio <your-account@gmail.com>
```

I use a Gmail App Password rather than the normal account password.

## Testing

I keep the tests beside each application:

- [shop/tests.py](./shop/tests.py) covers the catalogue, categories, search,
  bag, quantities, wishlist and reviews;
- [orders/tests.py](./orders/tests.py) covers checkout, orders, Stripe,
  webhooks, transaction IDs and emails;
- [accounts/tests.py](./accounts/tests.py) covers registration, login,
  password reset and access protection.

I run the tests with:

```bash
python manage.py test
```

The current result is:

```text
50 tests executed
50 tests passed
0 failures
0 errors
```

I also use:

```bash
python manage.py check
DEBUG=False python manage.py check --deploy
python manage.py makemigrations --check
python manage.py collectstatic --no-input
```

The tests include invalid input, corrupted sessions, missing products,
access to another user's orders, unauthorised reviews, duplicate wishlists,
incomplete Stripe events and unknown-URL redirection.

For manual testing I use the checklist in
[docs/screenshots.md](./docs/screenshots.md). I still need to add evidence
for desktop, mobile, checkout, Stripe, email, password reset, Cloudinary,
admin and 404 behaviour before submission.

## Bugs Found and Fixed During Testing

During development and testing I found the following bugs and corrected them
before the current test run.

### Invalid bag data

An old session could contain an invalid product ID, quantity or size. I added
validation before session data is used.

### Inactive products

A disabled product should not be addable from an old session. The bag now
checks that the product is still active and available.

### Stripe webhook

I found cases where the Stripe payload was incomplete or the payment had
failed, expired or been cancelled. The webhook now validates the event,
handles each status separately and prevents duplicate emails.

### Transaction ID

At first, the customer could see payment confirmation but not the transaction
identifier. I added `stripe_payment_intent_id` to `Order` and display it in
the order confirmation and order details.

### Resend and Gmail

Email delivery initially depended on a Resend-specific check. I moved sending
to the configured Django email backend so the same logic works with Resend or
Gmail SMTP.

### Legacy categories

I removed the old categories from the navigation and added migrations to
normalise the final categories. The products and menu now use database data
rather than hard-coded links.

### Missing pages

I added a 404 handler. An unknown URL returns the visitor to the shop with an
explanatory message, while ownership errors remain 404 responses so that
details about another customer's order or review are not exposed.

### Production media

Files uploaded locally are not persistent on Heroku. I configured Cloudinary
for media and WhiteNoise for static files.

These fixes are covered by the automated tests where appropriate. I will also
record the manual browser checks and any remaining issues in the evidence
listed in [docs/screenshots.md](./docs/screenshots.md).

## Deployment to Heroku

The Procfile is:

```text
web: gunicorn truck_print_config.wsgi:application
```

My deployment process is:

1. Connect the GitHub repository to Heroku and use the `develop` branch.
2. Add PostgreSQL through Heroku Postgres or configure an external
   `DATABASE_URL`.
3. Configure Config Vars for `SECRET_KEY`, `DEBUG=False`,
   `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `DATABASE_URL`,
   `CLOUDINARY_URL`, Stripe and email.
4. Run:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. Add the categories and products through `/admin/`.
6. Mark the homepage products as `Featured`.
7. Upload the images through Admin so that they are stored in Cloudinary.
8. Configure the Stripe webhook at:

   ```text
   /orders/stripe/webhook/
   ```

9. Make a test payment and check that the webhook returns HTTP 200, the order
   becomes `Paid` and the email is received.

I use SQLite only locally. In production I use PostgreSQL, Cloudinary and
WhiteNoise.

The live application is:

<https://truck-print-studio-d34dbb49183c.herokuapp.com/>

## Security

- I do not keep secrets in the repository.
- `.env`, the SQLite database, media and collected static files are in
  `.gitignore`.
- `SECRET_KEY`, Stripe, Cloudinary and email passwords are environment
  variables.
- Production runs with `DEBUG=False`.
- HTTPS redirect, HSTS and secure cookies are configured.
- Stripe webhooks are checked with the signing secret.
- Django validates passwords during registration.
- Account, wishlist, review and order pages require authentication.
- A user cannot view or modify another user's data.
- Django Admin is protected from non-staff users.

## Git and development process

I used Git to keep a record of the project. I worked on separate features,
including authentication, the catalogue and bag, Stripe, password reset and
emails.

I added focused tests for the main features and ran the complete suite before
deployment. The history shows incremental development, but it cannot
retrospectively prove the exact `red-green-refactor` order for every feature.
In my report I will describe the commits and test results accurately rather
than claim evidence that the history cannot support.

The database configuration is centralised in
[truck_print_config/settings.py](./truck_print_config/settings.py). When
`DATABASE_URL` exists, the application uses PostgreSQL; otherwise it uses
SQLite locally.

## Limitations and next steps

Before submission I still need to complete:

- manual screenshots from the evidence checklist;
- HTML and CSS validation;
- Lighthouse and accessibility checks;
- browser-console checks;
- complete testing of the deployed version;
- uploading the final images and products to production;
- committing and pushing the final local changes.

As future improvements, I could add catalogue pagination, more complete
coupon management and automated accessibility checks in CI.

## Supporting documentation

- [Design, rationale and wireframes](./docs/design.md)
- [Entity relationship diagram](./docs/erd.md)
- [User stories](./docs/user-stories.md)
- [Screenshot checklist](./docs/screenshots.md)

## Author

**Florin Albu**
