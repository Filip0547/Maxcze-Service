import unittest
from unittest.mock import patch
import time

from app import app


class ContactEmailFlowTest(unittest.TestCase):
    def setUp(self):
        app.config.update(
            TESTING=True,
            MAIL_PROVIDER='smtp',
            MAIL_SUPPRESS_SEND=True,
            EMAIL_SEND_ASYNC=False,
            MAIL_RECIPIENT='owner@example.com',
            MAIL_USERNAME='owner@example.com',
            MAIL_PASSWORD='dummy-password',
            MAIL_DEFAULT_SENDER='noreply@example.com',
            WTF_CSRF_ENABLED=False,
        )
        self.client = app.test_client()

    def test_contact_form_sends_email(self):
        payload = {
            'voornaam': 'Jan',
            'achternaam': 'de Vries',
            'email': 'jan@example.com',
            'telefoon': '06-12345678',
            'terugbericht_via': 'whatsapp',
            'type_aanvraag': 'offerte',
            'bericht': 'Ik wil graag een offerte voor kozijnen.',
            'akkoord': 'on',
        }

        with patch('app.mail.send') as mock_send:
            response = self.client.post('/contact', data=payload, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_send.call_count, 1)

        sent_message = mock_send.call_args.args[0]
        self.assertEqual(sent_message.recipients, ['owner@example.com'])
        self.assertIn('Nieuwe offerte aanvraag:', sent_message.subject)
        self.assertEqual(sent_message.reply_to, 'jan@example.com')
        self.assertIn('Ik wil graag een offerte voor kozijnen.', sent_message.body)
        self.assertIn('Terugbericht via: WhatsApp-bericht', sent_message.body)
        self.assertIn('<html', sent_message.html.lower())
        self.assertIn('Jan', sent_message.html)
        self.assertIn('de Vries', sent_message.html)
        self.assertIn(b'Bedankt voor uw aanvraag!', response.data)

    def test_contact_form_outlook_provider_uses_smtp(self):
        app.config.update(
            MAIL_PROVIDER='outlook',
            MAIL_USERNAME='owner@example.com',
            MAIL_PASSWORD='dummy-password',
            MAIL_DEFAULT_SENDER='owner@example.com',
        )
        payload = {
            'voornaam': 'Anna',
            'achternaam': 'Jansen',
            'email': 'anna@example.com',
            'telefoon': '06-00000000',
            'terugbericht_via': 'email',
            'type_aanvraag': 'advies',
            'bericht': 'Kunt u mij terugbellen?',
            'akkoord': 'on',
        }

        with patch('app.mail.send') as mock_send:
            response = self.client.post('/contact', data=payload, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_send.call_count, 1)
        self.assertIn(b'Bedankt voor uw aanvraag!', response.data)

    def test_contact_form_send_mode_setting_does_not_break_delivery(self):
        app.config.update(EMAIL_SEND_ASYNC=True, MAIL_TIMEOUT=5)
        payload = {
            'voornaam': 'Lars',
            'achternaam': 'Bakker',
            'email': 'lars@example.com',
            'telefoon': '06-99999999',
            'terugbericht_via': 'telefoon',
            'type_aanvraag': 'offerte',
            'bericht': 'Graag een offerte voor een dakkapel.',
            'akkoord': 'on',
        }

        with patch('app.mail.send') as mock_send:
            response = self.client.post('/contact', data=payload, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_send.call_count, 1)
        self.assertIn(b'Bedankt voor uw aanvraag!', response.data)

    def test_contact_form_handles_slow_mail_without_hanging(self):
        app.config.update(EMAIL_REQUEST_TIMEOUT=1)
        payload = {
            'voornaam': 'Mila',
            'achternaam': 'Pieters',
            'email': 'mila@example.com',
            'telefoon': '06-88888888',
            'terugbericht_via': 'email',
            'type_aanvraag': 'offerte',
            'bericht': 'Ik wil een offerte voor een aanbouw.',
            'akkoord': 'on',
        }

        def _slow_send(_msg):
            time.sleep(2)

        with patch('app.mail.send', side_effect=_slow_send):
            response = self.client.post('/contact', data=payload, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Er is een fout opgetreden bij het verzenden.', response.data)

    def test_contact_form_falls_back_to_sendgrid_when_smtp_fails(self):
        app.config.update(
            MAIL_PROVIDER='smtp',
            SENDGRID_API_KEY='SG.test-key',
            SENDGRID_FROM_EMAIL='verified@example.com',
        )

        payload = {
            'voornaam': 'Noah',
            'achternaam': 'Koster',
            'email': 'noah@example.com',
            'telefoon': '06-77777777',
            'terugbericht_via': 'telefoon',
            'type_aanvraag': 'offerte',
            'bericht': 'Graag een prijsindicatie voor een renovatie.',
            'akkoord': 'on',
        }

        with patch('app._send_contact_email_smtp', side_effect=RuntimeError('SMTP timeout')):
            with patch('app._send_contact_email_sendgrid') as mock_sendgrid:
                response = self.client.post('/contact', data=payload, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_sendgrid.call_count, 1)
        self.assertIn(b'Bedankt voor uw aanvraag!', response.data)


if __name__ == '__main__':
    unittest.main()
