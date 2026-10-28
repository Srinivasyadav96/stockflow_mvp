# StockFlow MVP – Inventory Management System

A web-based inventory management application developed as part of the SDE Intern assessment. It helps organizations manage products, monitor stock levels, and identify low-stock items.

Live Demo: https://stockflow-mvp-bd1p.onrender.com/

GitHub: https://github.com/Srinivasyadav96/stockflow_mvp

## Features

- User registration, login, and logout.
- Organization-specific product management.
- Add, view, update, and delete products.
- Search products by name or SKU.
- Dashboard displaying total products, total stock quantity, and low-stock products.
- Configurable product-level low-stock thresholds with an organization default.
- Organization-level data isolation.

## User Flow

1. A user registers with an organization name, email, and password.
2. The application creates the user's organization.
3. After logging in, the user views the inventory dashboard.
4. The user adds products with details such as name, SKU, quantity, cost price, and selling price.
5. The user can search, edit, or delete products.
6. The dashboard displays inventory totals and highlights products at or below their low-stock threshold.
7. Each user can access only their own organization's products.

## Technology Stack

- Backend: Python, Django 4.2
- Frontend: HTML5, Bootstrap
- Database: SQLite for local development, PostgreSQL for production
- Deployment: Render, Gunicorn, WhiteNoise
- Version Control: Git, GitHub

## Run Locally

Clone the repository:

```bash
git clone https://github.com/SrinivasYadav96/stockflow_mvp.git
cd stockflow_mvp
```

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies and apply migrations:

```bash
pip install -r requirements.txt
python manage.py migrate
```

Start the application:

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ and register an account to get started.

## Author

M. Srinivas

GitHub: https://github.com/Srinivasyadav96
