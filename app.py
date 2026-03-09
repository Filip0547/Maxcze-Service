from flask import Flask, render_template, request, flash
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this to a real secret key

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
        dienst = request.form.get('dienst')
        bericht = request.form.get('bericht')
        locatie = request.form.get('locatie')
        akkoord = request.form.get('akkoord')
        
        # Here you would process the form, e.g., send email, save to database
        # For now, just flash a message
        flash('Bedankt voor uw aanvraag! Wij nemen binnen één werkdag contact met u op.', 'success')
        
        return render_template('contact.html')
    return render_template('contact.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)