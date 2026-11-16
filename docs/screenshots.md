# Screenshot checklist

Capture these screens after deployment and add the images to a
`docs/screenshots/` directory:

1. Home page with featured products.
2. Catalogue with search and filters.
3. Product page with size selection.
4. Bag showing product image, quantity and size.
5. Stripe test checkout page.
6. Successful order confirmation with `Paid` status.
7. Wishlist page for an authenticated user.
8. Order history page.
9. Heroku deployment dashboard showing a healthy service.
10. Django admin showing product/category management.
11. Password reset form and confirmation message (hide the email address).
12. Stripe webhook delivery showing an HTTP 200 response.
13. Order confirmation email showing order number, total and transaction ID
    (hide personal information).
14. Missing URL showing the informative redirect back to the shop.
15. Mobile navigation and checkout layout.
16. Failed form validation and a failed/cancelled payment message.

Use descriptive filenames, for example `01-home.png` and
`06-order-paid.png`. Do not include API keys, customer data or personal
information in screenshots.

For distinction evidence, keep the screenshots together with any HTML/CSS
validator or JavaScript lint reports and record the date, environment and
result in the submission notes.
