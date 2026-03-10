from flask import Flask, render_template, request, flash
from flask_babel import Babel, _
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this to a real secret key

# --- internationalization / localization ---
app.config['BABEL_DEFAULT_LOCALE'] = 'nl'
app.config['BABEL_SUPPORTED_LOCALES'] = ['nl', 'en', 'pl']

babel = Babel(app)

@babel.localeselector
# decide which locale to use for this request
# priority: ?lang query param, then Accept-Language header
# (could be extended to use cookie or user settings)
def get_locale():
    lang = request.args.get('lang')
    if lang in app.config['BABEL_SUPPORTED_LOCALES']:
        return lang
    return request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])

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
        
        # Here you would process the form, e.g., send email, save to database
        # For now, just flash a message (translated)
        flash(_('Bedankt voor uw aanvraag! Wij nemen binnen één werkdag contact met u op.'), 'success')
        
        return render_template('contact.html')
    return render_template('contact.html')


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)