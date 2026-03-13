# Maxcze-Service

This is a small Flask website for a Dutch construction business.  The project
includes:

* A contact/offerte form with backend email example
* A privacy policy page
* Internationalization support (Dutch, English, Polish) via Flask-Babel

---

## Setup

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

2. Initialize translation catalogs (run whenever you add new `_()` strings):

   ```bash
   # extract all messages from Python and templates
   pybabel extract -F babel.cfg -o messages.pot .

   # create language directories for each supported locale
   pybabel init -i messages.pot -d translations -l nl
   pybabel init -i messages.pot -d translations -l en
   pybabel init -i messages.pot -d translations -l pl

   # after editing the `.po` files, compile them:
   pybabel compile -d translations
   ```

3. Run the app:

   ```bash
   flask run
   ```

## Notes

* Language is selected using `?lang=nl`, `?lang=en` or `?lang=pl` query
  parameter; the base template provides a switcher.
* Templates extend `base.html` and wrap all human‑visible text in `_()` so they
  can be translated.

### Email delivery

The contact form supports 2 providers:

* `MAIL_PROVIDER=smtp` (default when no SendGrid key is set)
* `MAIL_PROVIDER=sendgrid` (recommended if Microsoft SMTP auth is blocked)

Recommended shared settings:

```dotenv
SECRET_KEY=replace-with-a-long-random-string
MAIL_RECIPIENT=your-email@domain.com
EMAIL_SEND_ASYNC=False
```

Minimal SMTP `.env` values:

```dotenv
MAIL_PROVIDER=smtp
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@outlook.com
```

Minimal SendGrid `.env` values:

```dotenv
MAIL_PROVIDER=sendgrid
MAIL_RECIPIENT=your-email@domain.com
SENDGRID_API_KEY=SG.your_api_key
SENDGRID_FROM_EMAIL=verified-sender@yourdomain.com
```

