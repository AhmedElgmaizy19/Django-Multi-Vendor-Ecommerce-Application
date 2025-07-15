 Application
A multi-vendor e-commerce platform built with Django and Django Rest Framework. The platform allows multiple vendors to register, manage their products, and sell online while customers can browse, purchase, and track orders.

🚀 Features
✅ User Features
User Registration & Login (JWT Authentication)

Profile management

Browsing products by category, vendor, tags

Product details page

Search products

Add products to cart

Checkout process

Order history & details

Product reviews and ratings

Wishlist functionality

Email notifications for order updates

✅ Vendor Features
Vendor registration and profile management

Vendor dashboard

Add / Edit / Delete products

Manage orders related to vendor’s products

View earnings

Product sales analytics

Upload product images

Manage stock and inventory

✅ Admin Features
Manage users and vendors

Manage categories and tags

View all products

Manage orders across the platform

Approve or reject vendor accounts

Manage platform-wide settings

✅ Technical Features
Django REST Framework for API backend

Token-based authentication with JWT

PostgreSQL database

Custom user model supporting vendor roles

Image upload support (Django media)

Pagination for product listing

Custom permissions for vendors/admins

Unit and integration tests

Docker support for deployment

Environment variables using python-decouple

CORS support for frontend integration

API documentation (Swagger / DRF YASG)

📂 Project Structure
Example:

bash
Copy
Edit
/ecommerce_project
    /accounts
    /products
    /orders
    /vendors
    /reviews
    manage.py
    requirements.txt
accounts → User and vendor auth, profiles

products → Product models, views, serializers

orders → Order handling, payments, invoices

vendors → Vendor-specific logic

reviews → Ratings and comments on products

⚙️ Installation
1. Clone the Repository
2. 
git clone https://github.com/AhmedElgmaizy19/Django-Multi-Vendor-Ecommerce-Application.git
cd Django-Multi-Vendor-Ecommerce-Application
3. Create Virtual Environment
On macOS/Linux:

python3 -m venv venv
source venv/bin/activate


On Windows:

python -m venv venv
venv\Scripts\activate
3. Install Dependencies

pip install -r requirements.txt
4. Configure Environment Variables
Create a .env file:


python manage.py migrate
6. Create Superuser

python manage.py createsuperuser
7. Run Server
python manage.py runserver
