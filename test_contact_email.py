import unittest
from unittest.mock import patch

from app import app


class ContactEmailFlowTest(unittest.TestCase):
    def setUp(self):
        app.config.update(
            TESTING=True,
            MAIL_PROVIDER='smtp',
            MAIL_SUPPRESS_SEND=True,
            MAIL_RECIPIENT='owner@example.com',
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
        self.assertIn('<html', sent_message.html.lower())
        self.assertIn('Jan', sent_message.html)
        self.assertIn('de Vries', sent_message.html)
        self.assertIn(b'Bedankt voor uw aanvraag!', response.data)


if __name__ == '__main__':
    unittest.main()
