# Design rationale and interaction plan

## Rationale

Truck Print Studio is designed for UK road-transport enthusiasts who want to
find a design quickly, select an appropriate clothing size and complete a
made-to-order purchase without unnecessary account creation. The catalogue,
bag and checkout are therefore the primary journey. Accounts, wishlists,
reviews and order history provide optional value after the first purchase.

The application is original coursework created for this target audience. It
does not copy a walkthrough project. Bootstrap, Font Awesome, Stripe,
Cloudinary, WhiteNoise and Django are external dependencies; application
models, views, templates, CSS, tests and business rules are project code.

## Information architecture



The navigation keeps the high-priority actions visible: categories, shop, bag
and account actions. Product pages provide the decision-making information
(image, description, price and size) before the add-to-bag action.

## Page wireframes

### Catalogue and product

```text
+----------------------------------------------------------+
| Logo | Categories | Shop | Bag | Account                 |
+----------------------------------------------------------+
| Search and filters                                       |
| [Product card] [Product card] [Product card]             |
| image, name, price, View design                         |
+----------------------------------------------------------+

+----------------------------------------------------------+
| Product image | Name, description, price                 |
|               | Size selector (clothing only)            |
|               | [Add to bag] [Wishlist]                  |
|               | Reviews and feedback                     |
+----------------------------------------------------------+
```

### Bag and checkout

```text
+----------------------------------------------------------+
| Bag                                                     |
| image | product | size | quantity | remove              |
|                                                     total|
| [Continue shopping]                         [Checkout]  |
+----------------------------------------------------------+

+----------------------------------------------------------+
| Delivery form                 | Order summary            |
| labelled fields + errors      | image, size, total       |
| [Continue to payment]         |                          |
+----------------------------------------------------------+
```

## UX, accessibility and control decisions

- Semantic `nav`, `main`, `section`, headings, labels and `address` elements
  create an understandable document structure.
- Product images have descriptive alternative text; decorative icon text is
  hidden from assistive technology where appropriate.
- Forms use CSRF protection, server-side validation and visible error messages.
- Bootstrap responsive layout and a collapsible navigation support mobile and
  desktop use.
- Django messages confirm successful actions and explain checkout, payment,
  authentication and validation failures.
- There are no autoplay media elements or aggressive pop-ups.
- A missing URL is handled by the custom 404 handler and returns the visitor
  to the shop with an explanatory message.
- Guest checkout avoids requesting account details that are not required.
- External social links open in a new tab with `noopener noreferrer`.

The use of a compact, product-first interface is intentional: it reduces
choice overload for the target audience while keeping order, wishlist and
account controls available after sign-in.

## Data and front-end relationship

Views validate request data and coordinate workflows, models enforce
relationships and database constraints, and templates render the resulting
state. The session bag is converted into `OrderItem` records at checkout;
Stripe's webhook then updates the order payment state. This keeps the browser
from being the source of truth for payment or order status.

## Manual distinction evidence


