from django.test import TestCase
from django.contrib.auth import get_user_model
from faker import Faker
from accounts.forms import RegisterForm, LoginForm

User = get_user_model()
fake = Faker()


class RegisterFormTest(TestCase):
    def get_valid_data(self):
        return {
            'email': fake.email(),
            'password1': 'StrongPass99!',
            'password2': 'StrongPass99!',
        }

    # Valid Scenarios 

    def test_valid_form_is_valid(self):
        form = RegisterForm(data=self.get_valid_data())
        self.assertTrue(form.is_valid())

    def test_valid_form_creates_user(self):
        data = self.get_valid_data()
        form = RegisterForm(data=data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertIsNotNone(user.pk)

    def test_saved_user_has_correct_email(self):
        data = self.get_valid_data()
        form = RegisterForm(data=data)
        form.is_valid()
        user = form.save()
        self.assertEqual(user.email, data['email'])

    def test_saved_user_has_correct_role(self):
        data = self.get_valid_data()
        form = RegisterForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.role, 'regular_user')

    def test_saved_user_password_is_hashed(self):
        data = self.get_valid_data()
        form = RegisterForm(data=data)
        form.is_valid()
        user = form.save()
        self.assertNotEqual(user.password, data['password2'])


    #  Invalid Scenarios 

    def test_empty_email_is_invalid(self):
        data = self.get_valid_data()
        data['email'] = ''
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_email_format_is_invalid(self):
        data  = self.get_valid_data()
        data['email'] = 'not an email'
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())

    def test_duplicate_email_is_invalid(self):
        email = fake.email()
        User.objects.create_user(email=email, password='StrongPass99!')
        data = self.get_valid_data()
        data['email'] = email
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())

    def test_empty_password_is_invalid(self):
        data = self.get_valid_data()
        data['password2'] = ''
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_short_password_is_invalid(self):
        # passwords under 8 characters should fail
        data             = self.get_valid_data()
        data['password1'] = 'abc'
        data['password2'] = 'abc'
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())

    def test_numeric_only_password_is_invalid(self):
        data = self.get_valid_data()
        data['password1'] = '12345678'
        data['password2'] = '12345678'
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())

    def test_common_password_is_invalid(self):
        data = self.get_valid_data()
        data['password1'] = 'password'
        data['password2'] = 'password'
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())

    def test_mismatched_passwords_is_invalid(self):
        # confirm password must match password exactly
        data = self.get_valid_data()
        data['password2'] = 'DifferentPass99!'
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())


    def test_empty_form_is_invalid(self):
        # tests that a completely empty form fails
        form = RegisterForm(data={})
        self.assertFalse(form.is_valid())

    def test_empty_confirm_password_is_invalid(self):
        data = self.get_valid_data()
        data['password2'] = ''
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())


class LoginFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

    def test_valid_login_form_is_valid(self):
        form = LoginForm(request=None, data={
            'username': 'test@example.com',
            'password': 'testpass123',
        })
        print(form.errors)
        self.assertTrue(form.is_valid())

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@domain.co.uk',
            password='Testpass123!'
        )

    def test_login_form_accepts_valid_credentials(self):
        form = LoginForm(request=None, data={
            'username': 'user@domain.co.uk',
            'password': 'Testpass123!',
        })
        print(form.errors)
        self.assertTrue(form.is_valid())

    # Invalid Scenarios 

    def test_empty_email_is_invalid(self):
        form = LoginForm(data={'username': '', 'password': 'StrongPass99!'})
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_invalid_email_format_is_invalid(self):
        form = LoginForm(data={'username': 'notanemail', 'password': 'StrongPass99!'})
        self.assertFalse(form.is_valid())

    def test_empty_password_is_invalid(self):
        form = LoginForm(data={'username': 'user@example.com', 'password': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_empty_form_is_invalid(self):
        form = LoginForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_missing_password_field_is_invalid(self):
        form = LoginForm(data={'username': 'user@example.com'})
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_missing_email_field_is_invalid(self):
        form = LoginForm(data={'password': 'StrongPass99!'})
        self.assertFalse(form.is_valid())
