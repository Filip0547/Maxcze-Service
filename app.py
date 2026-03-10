from flask import Flask, render_template, request, flash, redirect, url_for
from flask_babel import Babel, _
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

# Load environment variables from .env file
# Make sure to create a .env file with your email credentials
# See .env.example for the required variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this to a real secret key

# --- Flask-Mail configuration ---
# Load email credentials from environment variables
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp-mail.outlook.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Required: your email address
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Required: your email password
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))

mail = Mail(app)

# --- internationalization / localization ---
app.config["BABEL_DEFAULT_LOCALE"] = "nl"
app.config["BABEL_TRANSLATION_DIRECTORIES"] = "translations"

SUPPORTED_LANGS = ['nl', 'en', 'pl']
ROUTE_MAP = {
    'home': {'nl': '/', 'en': '/en', 'pl': '/pl'},
    'over_ons': {'nl': '/over-ons', 'en': '/en/about-us', 'pl': '/pl/o-nas'},
    'projecten': {'nl': '/projecten', 'en': '/en/projects', 'pl': '/pl/projekty'},
    'contact': {'nl': '/contact', 'en': '/en/contact', 'pl': '/pl/contact'},
    'privacy': {'nl': '/privacy', 'en': '/en/privacy', 'pl': '/pl/prywatnosc'},
}

def get_locale():
    if request.view_args:
        lang = request.view_args.get('lang')
        if lang in SUPPORTED_LANGS:
            return lang

    first_segment = request.path.strip('/').split('/', 1)[0]
    if first_segment in ['en', 'pl']:
        return first_segment

    return 'nl'

babel = Babel(app, locale_selector=get_locale)

@app.context_processor
def inject_locale():
    def localized_url(page, lang=None):
        active_lang = lang or get_locale()
        return ROUTE_MAP[page][active_lang]

    def switch_language_url(lang):
        endpoint = request.endpoint
        if endpoint in ROUTE_MAP:
            return ROUTE_MAP[endpoint][lang]
        return ROUTE_MAP['home'][lang]

    def is_current(page):
        return request.endpoint == page

    return {
        'get_locale': get_locale,
        'localized_url': localized_url,
        'switch_language_url': switch_language_url,
        'is_current': is_current,
    }

@app.route('/', defaults={'lang': 'nl'})
@app.route('/en', defaults={'lang': 'en'})
@app.route('/pl', defaults={'lang': 'pl'})
def home(lang='nl'):
    return render_template('index.html')

@app.route('/over-ons', defaults={'lang': 'nl'})
@app.route('/en/about-us', defaults={'lang': 'en'})
@app.route('/pl/o-nas', defaults={'lang': 'pl'})
def over_ons(lang='nl'):
    return render_template('over-ons.html')

@app.route('/projecten', defaults={'lang': 'nl'})
@app.route('/en/projects', defaults={'lang': 'en'})
@app.route('/pl/projekty', defaults={'lang': 'pl'})
def projecten(lang='nl'):
    return render_template('projecten.html')

@app.route('/contact', defaults={'lang': 'nl'}, methods=['GET', 'POST'])
@app.route('/en/contact', defaults={'lang': 'en'}, methods=['GET', 'POST'])
@app.route('/pl/contact', defaults={'lang': 'pl'}, methods=['GET', 'POST'])
def contact(lang='nl'):
    if request.method == 'POST':
        # Handle form submission
        voornaam = request.form.get('voornaam')
        achternaam = request.form.get('achternaam')
        email = request.form.get('email')
        telefoon = request.form.get('telefoon')
        type_aanvraag = request.form.get('type_aanvraag')
        bericht = request.form.get('bericht')
        akkoord = request.form.get('akkoord')
        
        # Send email
        msg = Message(
            subject='Nieuwe offerte aanvraag van MaxCze Service website',
            recipients=['maxcze@hotmail.com'],
            body=f"""
Nieuwe offerte aanvraag ontvangen via de website.

Naam: {voornaam} {achternaam}
E-mail: {email}
Telefoon: {telefoon or 'Niet opgegeven'}
Type aanvraag: {type_aanvraag or 'Niet opgegeven'}

Bericht:
{bericht}

Privacy akkoord: {'Ja' if akkoord else 'Nee'}

--
Deze e-mail is automatisch verzonden vanaf de MaxCze Service website.
            """.strip()
        )
        msg.extra_headers = {
            'X-Priority': '1',
            'Importance': 'High'
        }
        try:
            mail.send(msg)
            flash(_('Bedankt voor uw aanvraag! Wij nemen binnen één werkdag contact met u op.'), 'success')
        except Exception as e:
            flash(_('Er is een fout opgetreden bij het verzenden. Probeer het later opnieuw.'), 'error')
        
        return render_template('contact.html')
    return render_template('contact.html')


@app.route('/privacy', defaults={'lang': 'nl'})
@app.route('/en/privacy', defaults={'lang': 'en'})
@app.route('/pl/prywatnosc', defaults={'lang': 'pl'})
def privacy(lang='nl'):
    return render_template('privacy.html')

@app.route('/set-language/<lang>')
def set_language(lang):
    if lang not in SUPPORTED_LANGS:
        return redirect(ROUTE_MAP['home']['nl'])

    referrer = request.referrer or ''
    for page, paths in ROUTE_MAP.items():
        for source_lang, source_path in paths.items():
            if referrer.endswith(source_path):
                return redirect(paths[lang])

    return redirect(ROUTE_MAP['home'][lang])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)