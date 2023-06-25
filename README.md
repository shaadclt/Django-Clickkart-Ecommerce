# Django Clickkart E-Commerce Website
This is an E-commerce website built using Django, a Python web framework. It provides a platform for users to browse and purchase products, while also offering various features for both users and administrators.

## Features
### User Side
* User Registration and Login: Users can create an account and log in to access their personalized features.
* User Verification using OTP (Twilio): Users are verified using a one-time password sent to their registered phone number via Twilio API.
* Change Password: Users can change their account password for security purposes.
* Cart Management: Users can add products to their cart, update quantities, and remove items.
* Coupon Codes: Users can apply coupon codes during checkout to avail discounts on their purchases.
* Product Search: Users can search for products using keywords or specific criteria.
* Product Review: Users can leave reviews and ratings for products they have purchased.
* User Profile: Users can view and update their profile information, such as name, email, and contact details.
* Address Management: Users can add, edit, and delete their shipping addresses for orders.
* Order Management: Users can view their order history, including details of past and current orders.
* Razorpay Payment Integration: Payment gateway integration with Razorpay to facilitate secure and convenient online transactions.

### Admin Side
* Login: Administrators can log in to access the admin panel.
* Change Password: Administrators can change their password for security purposes.
* User Management: Administrators can manage user accounts, including viewing user details, updating information, and disabling accounts if necessary.
* Product Management: Administrators can add, edit, and delete products from the website's catalog, including details such as name, description, price, and images.
* Product Variation Management: Administrators can manage product variations, such as sizes, colors, or other customizable options.
* Product Category Management: Administrators can create and manage product categories to organize products into different sections.
* Order Management: Administrators can view and manage customer orders, including order details, status updates, and tracking information.
* Coupon Management: Administrators can create and manage coupon codes, including setting discount percentages, expiry dates, and usage limits.
* Sales and Product Reports: Administrators can generate reports to analyze sales data, product popularity, and other relevant metrics.

## Installation
1. Clone the repository:

```shell
git clone https://github.com/shaadclt/Django-Clickkart-Ecommerce.git
```

2. Navigate to the project directory:

```shell
cd Django-Clickkart-Ecommerce
```

3. Install the required dependencies:
4. 
```shell
pip install -r requirements.txt
```

4. Set up the database:
   
```shell
python manage.py migrate
```

5. Create a superuser (admin) account:

```shell
python manage.py runserver
```

6. Open your web browser and go to **http://localhost:8000** to access the E-commerce website.

## Technologies Used
* Django: Web framework for building the E-commerce website.
* Twilio API: Integration for user verification via OTP.
*Razorpay: Payment gateway integration for secure online transactions.

## License
This project is licensed under the MIT License.

## Contributing
Contributions are welcome! If you have any suggestions, improvements, or bug fixes, please open an issue or submit a pull request.
