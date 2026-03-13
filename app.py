from flask import Flask, render_template, request, flash, redirect
from flask_babel import Babel, _
from flask_mail import Mail as FlaskMail, Message as FlaskMessage
from dotenv import load_dotenv
import os
import polib
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from sendgrid import SendGridAPIClient  # type: ignore[import-not-found]
from sendgrid.helpers.mail import Mail as SendGridMail, Email as SendGridEmail  # type: ignore[import-not-found]

# Load environment variables from .env file
# Make sure to create a .env file with your email credentials
# See .env.example for the required variables
load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO').upper())
logger = logging.getLogger(__name__)

app.secret_key = os.getenv('SECRET_KEY')
if not app.secret_key:
    # Use a random fallback in development, but warn because this rotates each restart.
    app.secret_key = os.urandom(32)
    logger.warning('SECRET_KEY is not configured. Using a temporary key; set SECRET_KEY in .env for stable sessions.')


def _normalize_mail_provider(provider):
    normalized = (provider or '').strip().lower()
    aliases = {
        'outlook': 'smtp',
        'hotmail': 'smtp',
        'microsoft': 'smtp',
        'office365': 'smtp',
    }
    if normalized in aliases:
        return aliases[normalized]
    if normalized in ('smtp', 'sendgrid'):
        return normalized
    return ''


def _as_bool(value, default=False):
    if value is None:
        return default
    normalized = str(value).strip().lower()
    if normalized in ('1', 'true', 'yes', 'y', 'on'):
        return True
    if normalized in ('0', 'false', 'no', 'n', 'off'):
        return False
    return default

# --- Flask-Mail configuration ---
# Load email credentials from environment variables
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp-mail.outlook.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = _as_bool(os.getenv('MAIL_USE_TLS', 'True'), default=True)
app.config['MAIL_TIMEOUT'] = int(os.getenv('MAIL_TIMEOUT', 10))
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Required: your email address
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Required: your email password
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))
app.config['MAIL_RECIPIENT'] = os.getenv('MAIL_RECIPIENT', os.getenv('MAIL_USERNAME', ''))
app.config['SENDGRID_API_KEY'] = os.getenv('SENDGRID_API_KEY', '')
app.config['SENDGRID_FROM_EMAIL'] = os.getenv('SENDGRID_FROM_EMAIL', app.config['MAIL_DEFAULT_SENDER'] or app.config['MAIL_USERNAME'])
app.config['EMAIL_SEND_ASYNC'] = _as_bool(os.getenv('EMAIL_SEND_ASYNC', 'False'), default=False)
app.config['EMAIL_SEND_WORKERS'] = max(1, int(os.getenv('EMAIL_SEND_WORKERS', 2)))
app.config['EMAIL_REQUEST_TIMEOUT'] = max(5, int(os.getenv('EMAIL_REQUEST_TIMEOUT', 20)))

provider_from_env = _normalize_mail_provider(os.getenv('MAIL_PROVIDER', ''))
if provider_from_env:
    app.config['MAIL_PROVIDER'] = provider_from_env
elif app.config['SENDGRID_API_KEY']:
    app.config['MAIL_PROVIDER'] = 'sendgrid'
else:
    app.config['MAIL_PROVIDER'] = 'smtp'

if app.config['MAIL_PROVIDER'] == 'sendgrid' and (app.config.get('SENDGRID_FROM_EMAIL') or '').endswith('@gmail.com'):
    logger.warning('SENDGRID_FROM_EMAIL uses gmail.com. This often fails unless the sender is verified in SendGrid.')

mail = FlaskMail(app)

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


def load_po_translations(lang):
    if lang == 'nl':
        return {}

    po_path = os.path.join(app.root_path, 'translations', lang, 'LC_MESSAGES', 'messages.po')
    if not os.path.exists(po_path):
        return {}

    catalog = {}
    for entry in polib.pofile(po_path):
        if entry.obsolete or not entry.msgid:
            continue
        if entry.msgstr:
            catalog[entry.msgid] = entry.msgstr
    return catalog


TRANSLATIONS = {
    'en': load_po_translations('en'),
    'pl': load_po_translations('pl'),
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


def translate(message):
    lang = get_locale()
    if lang == 'nl':
        return message
    return TRANSLATIONS.get(lang, {}).get(message, message)


def _clean_value(value, fallback='Niet opgegeven'):
    cleaned = (value or '').strip()
    return cleaned or fallback


def _build_contact_payload(form_data):
    return {
        'voornaam': _clean_value(form_data.get('voornaam'), ''),
        'achternaam': _clean_value(form_data.get('achternaam'), ''),
        'email': _clean_value(form_data.get('email'), ''),
        'telefoon': _clean_value(form_data.get('telefoon')),
        'type_aanvraag': _clean_value(form_data.get('type_aanvraag')),
        'bericht': _clean_value(form_data.get('bericht'), ''),
        'akkoord': bool(form_data.get('akkoord')),
        'timestamp': datetime.now().strftime('%d-%m-%Y %H:%M'),
    }


def _send_contact_email(payload):
    _validate_email_delivery_config()

    provider = _normalize_mail_provider(app.config.get('MAIL_PROVIDER')) or 'smtp'
    if provider == 'sendgrid':
        _send_contact_email_sendgrid(payload)
        return

    _send_contact_email_smtp(payload)


def _validate_email_delivery_config():
    if not app.config.get('MAIL_RECIPIENT'):
        raise RuntimeError('MAIL_RECIPIENT is not configured')

    provider = _normalize_mail_provider(app.config.get('MAIL_PROVIDER')) or 'smtp'
    if provider == 'sendgrid':
        if not app.config.get('SENDGRID_API_KEY'):
            raise RuntimeError('SENDGRID_API_KEY is not configured')
        if not app.config.get('SENDGRID_FROM_EMAIL'):
            raise RuntimeError('SENDGRID_FROM_EMAIL is not configured')
        return

    if not app.config.get('MAIL_USERNAME'):
        raise RuntimeError('MAIL_USERNAME is not configured for SMTP delivery')
    if not app.config.get('MAIL_PASSWORD'):
        raise RuntimeError('MAIL_PASSWORD is not configured for SMTP delivery')
    if not app.config.get('MAIL_DEFAULT_SENDER'):
        raise RuntimeError('MAIL_DEFAULT_SENDER is not configured for SMTP delivery')


def _send_contact_email_smtp(payload):
    fullname = f"{payload['voornaam']} {payload['achternaam']}".strip()
    subject_name = fullname or 'Onbekende afzender'
    msg = FlaskMessage(
        subject=f'Nieuwe offerte aanvraag: {subject_name}',
        recipients=[app.config['MAIL_RECIPIENT']],
        reply_to=payload['email'] if payload['email'] else None,
    )
    msg.body = render_template('emails/offerte_notification.txt', data=payload)
    msg.html = render_template('emails/offerte_notification.html', data=payload)
    msg.extra_headers = {
        'X-Priority': '1',
        'Importance': 'High'
    }
    executor = ThreadPoolExecutor(max_workers=1)
    try:
        future = executor.submit(mail.send, msg)
        future.result(timeout=app.config.get('EMAIL_REQUEST_TIMEOUT', 20))
    except FuturesTimeoutError as exc:
        future.cancel()
        raise RuntimeError(
            f"SMTP send exceeded {app.config.get('EMAIL_REQUEST_TIMEOUT', 20)}s timeout"
        ) from exc
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


def _send_contact_email_sendgrid(payload):
    api_key = app.config.get('SENDGRID_API_KEY')

    fullname = f"{payload['voornaam']} {payload['achternaam']}".strip()
    subject_name = fullname or 'Onbekende afzender'
    text_content = render_template('emails/offerte_notification.txt', data=payload)
    html_content = render_template('emails/offerte_notification.html', data=payload)

    message = SendGridMail(
        from_email=app.config['SENDGRID_FROM_EMAIL'],
        to_emails=app.config['MAIL_RECIPIENT'],
        subject=f'Nieuwe offerte aanvraag: {subject_name}',
        plain_text_content=text_content,
        html_content=html_content,
    )

    if payload.get('email'):
        message.reply_to = SendGridEmail(payload['email'])

    try:
        response = SendGridAPIClient(api_key).send(message, request_timeout=10)
    except Exception as exc:
        status_code = getattr(exc, 'status_code', None)
        body = getattr(exc, 'body', None)
        if isinstance(body, (bytes, bytearray)):
            body = body.decode('utf-8', errors='replace')
        detail = f' status={status_code}' if status_code else ''
        if body:
            detail += f' body={body}'
        raise RuntimeError(f'SendGrid request failed.{detail}') from exc

    if response.status_code < 200 or response.status_code >= 300:
        response_body = getattr(response, 'body', None)
        if isinstance(response_body, (bytes, bytearray)):
            response_body = response_body.decode('utf-8', errors='replace')
        detail = f' status={response.status_code}'
        if response_body:
            detail += f' body={response_body}'
        raise RuntimeError(f'SendGrid send failed.{detail}')

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
        '_': translate,
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
        payload = _build_contact_payload(request.form)

        if not payload['voornaam'] or not payload['achternaam'] or not payload['email'] or not payload['bericht']:
            flash(translate('Vul alle verplichte velden in en probeer opnieuw.'), 'error')
            return render_template('contact.html')

        if not payload['akkoord']:
            flash(translate('U moet akkoord gaan met het privacybeleid.'), 'error')
            return render_template('contact.html')

        try:
            _validate_email_delivery_config()
            _send_contact_email(payload)
            flash(translate('Bedankt voor uw aanvraag! Wij nemen binnen één werkdag contact met u op.'), 'success')
        except Exception:
            logger.exception(
                'Email send failed. provider=%s recipient_set=%s from_set=%s',
                app.config.get('MAIL_PROVIDER'),
                bool(app.config.get('MAIL_RECIPIENT')),
                bool(app.config.get('SENDGRID_FROM_EMAIL') or app.config.get('MAIL_DEFAULT_SENDER')),
            )
            flash(translate('Er is een fout opgetreden bij het verzenden. Probeer het later opnieuw.'), 'error')

        return redirect(ROUTE_MAP['contact'][lang])
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