# GreatKart

> A complete e-commerce web application built with **Django** — product catalog, variations, cart, checkout, order tracking, customer reviews, and a hardened admin panel.

![Django](https://img.shields.io/badge/Django-6.0.7-092E20?style=flat-square&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![Database](https://img.shields.io/badge/Database-SQLite%20(default)-003B57?style=flat-square&logo=sqlite&logoColor=white)

---

## Features

### Storefront
- Browse products by category, keyword **search**, **size filter**, and **price range** with pagination
- Product pages with **image gallery**, color/size **variations** (stock-aware), and **star reviews**
- Shopping cart for guests and logged-in users (add / remove / quantity)
- Checkout → order placement → **demo payment** → order confirmation with **email receipt**
- **My Orders** history with full order detail (invoice style)
- Auth: register with **email activation**, login, forgot / reset password, dashboard, edit profile, change password

### Admin (Django admin)
- Manage categories, products, variations, orders, and payments
- Product **image gallery** inline with thumbnail previews
- Approve / reject customer reviews
- Auto-created user profile with picture upload

### Security
- Secrets kept in `.env` (gitignored) via `python-decouple`
- **Admin honeypot** — `/admin/` is a decoy login that never works; the real panel lives at `/securelogin/`
- **Session auto-expiry** (1 hour) with `django-session-timeout`
- Django CSRF protection, password validators, and authenticated-only order/review actions

---

## Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.12 |
| Framework | Django 6.0.7 |
| Database | SQLite (default) — PostgreSQL ready (see below) |
| Packages | Pillow, python-decouple, django-admin-thumbnails, django-session-timeout, django-honeypot-admin |
| Frontend | Bootstrap 4, jQuery, Font Awesome (all served locally) |

---

## Getting Started

### Prerequisites
- Python 3.12+

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/AyyazKanani/Great_Kart.git
cd Great_Kart

# 2. Create and activate a virtual environment
python -m venv env
env\Scripts\activate          # Windows
# source env/bin/activate     # Mac / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your local config (IMPORTANT: do this before the first run)
copy .env.example .env        # Windows — Mac / Linux: cp .env.example .env

# 5. Create the database
python manage.py migrate

# 6. Load the demo catalog (14 products, categories, variations)
python manage.py loaddata fixtures/catalog.json

# 7. Create your admin account
python manage.py createsuperuser

# 8. Run the server
python manage.py runserver
```

Open **http://127.0.0.1:8000/** for the store.

### Admin panel
- Real admin login: **http://127.0.0.1:8000/securelogin/**
- `/admin/` is a **decoy** page — logins there are rejected (honeypot)

### Emails in development
`.env` ships with empty email credentials, so Django uses the **console backend** — activation links and order receipts are **printed in the terminal** where `runserver` is running. To send real email, fill `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` (Gmail app password) in `.env`.

---

## Using PostgreSQL (optional)

SQLite works out of the box — no setup needed. To run on PostgreSQL instead:

```bash
pip install psycopg2-binary
```

1. Create a database:

```sql
CREATE DATABASE greatkart;
```

2. Replace the `DATABASES` block in `greatkart/settings.py` (`config` is already imported):

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='greatkart'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
```

3. Add to `.env`:

```env
DB_NAME=greatkart
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

4. Rebuild and seed:

```bash
python manage.py migrate
python manage.py loaddata fixtures/catalog.json
python manage.py createsuperuser
```

**Moving existing data** from SQLite to PostgreSQL:

```bash
# before switching DATABASES
python manage.py dumpdata --natural-foreign -e contenttypes -e auth.permission -e sessions -o backup.json
# after switching + migrate
python manage.py loaddata backup.json
```

---

## Project Structure

```
Great_Kart/
├── greatkart/            # project config (settings, root urls)
├── accounts/             # register, login, profile, password reset, order history
├── category/             # product categories
├── store/                # products, variations, reviews, image gallery, search
├── carts/                # cart add/remove, checkout
├── orders/               # order placement, demo payment, confirmation emails
├── templates/            # all HTML templates
├── greatkart/static/      # CSS, JS, fonts, images (served locally)
├── media/                # uploaded product / category / profile images
├── fixtures/catalog.json # demo catalog data (loaddata)
├── .env.example          # config template — copy to .env
├── requirements.txt
└── manage.py
```

---

## Manual Test Checklist

- [ ] Store → category pages → search → size / price filters → pagination
- [ ] Register → activation link appears in terminal → login works
- [ ] Product page: gallery switcher, color/size selection, reviews
- [ ] Cart → checkout → **Pay Now (Demo)** → order complete + email receipt in terminal
- [ ] My Orders → order detail page
- [ ] Dashboard → edit profile → change password
- [ ] `/admin/` shows the decoy, `/securelogin/` reaches the real panel
- [ ] Session expires automatically after 1 hour

---

## Contact

Built by **Ayyaz Kanani** — ayyazkanani@gmail.com · +91 95102-59595 · Mumbai, India
