from flask import Flask, render_template, request, flash, session, redirect, url_for
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

def get_locale():
    lang = session.get('lang')
    if lang in ['nl', 'en', 'pl']:
        return lang
    return request.accept_languages.best_match(['nl', 'en', 'pl'])

babel = Babel(app, locale_selector=get_locale)

@app.context_processor
def inject_locale():
    return {'get_locale': get_locale}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/over-ons')
def over_ons():
    return render_template('over-ons.html')

@app.route('/projecten')
def projecten():
    return render_template('projecten.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Handle form submission
        voornaam = request.form.get('voornaam')
        achternaam = request.form.get('achternaam')
        email = request.form.get('email')
        telefoon = request.form.get('telefoon')
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


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/set-language/<lang>')
def set_language(lang):
    if lang in ['nl', 'en', 'pl']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)