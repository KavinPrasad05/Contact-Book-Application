from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from contacts.models import Contact
from unittest.mock import patch
from accounts.tasks import send_welcome_email, send_otp_email


class CreateContactCommandTest(TestCase):
    def test_create_contact_command(self):
        out = StringIO()

        call_command(
            'create_contact',
            '--name', 'Kavin',
            '--phone', '9876543210',
            '--email', 'kavin@example.com',
            stdout=out
        )

        self.assertTrue(Contact.objects.filter(name='Kavin').exists())
        self.assertIn('created successfully', out.getvalue().lower())

class TaskTest(TestCase):
    @patch('accounts.tasks.send_mail')
    def test_send_welcome_email(self, mock_send_mail):
        send_welcome_email('user@example.com', 'User Name')
        self.assertTrue(mock_send_mail.called)

class OTPTaskTest(TestCase):
    @patch('accounts.tasks.send_mail')
    def test_send_otp_email(self, mock_send_mail):
        send_otp_email.run('user@example.com', '123456', 'User')
        mock_send_mail.assert_called_once()