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

