# from django.test import TestCase, Client
# from django.urls import reverse
# from django.contrib.auth import get_user_model
# from faker import Faker

# User = get_user_model()
# fake = Faker()


# def make_user(email, password, role='regular_user', is_active=True):
#     user = User.objects.create_user(
#         email=email,
#         password=password,
#         role=role,
#         is_active=is_active,
#     )
#     return user


# class RegisterViewTest(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.url = reverse('register')

#     def test_register_page_loads_with_status_200(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200) #200 - the request was successful

#     def test_register_page_uses_correct_template(self):
#         response = self.client.get(self.url)
#         self.assertTemplateUsed(response, 'accounts/register.html')

#     def test_register_page_contains_form(self):
#         response = self.client.get(self.url)
#         self.assertIn('form', response.context)

#     def test_authenticated_user_is_redirected_from_register(self):
#         user = make_user(fake.unique.email(), 'StrongPass99!')
#         self.client.force_login(user)
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse('contact_list'))

#     def test_valid_registration_redirects_to_login(self):
#         response = self.client.post(self.url, {
#             'email': fake.unique.email(),
#             'password1': 'StrongPass99!',
#             'password2': 'StrongPass99!',
#         })
#         self.assertRedirects(response, '/accounts/login/?registered=true')

#     def test_valid_registration_creates_user_in_database(self):
#         email = fake.unique.email()
#         self.client.post(self.url, {
#             'email': email,
#             'password1': 'StrongPass99!',
#             'password2': 'StrongPass99!',
#         })
#         self.assertTrue(User.objects.filter(email=email).exists())

#     def test_valid_registration_assigns_regular_user_role(self):
#         email = fake.unique.email()
#         self.client.post(self.url, {
#             'email': email,
#             'password1': 'StrongPass99!',
#             'password2': 'StrongPass99!',
#         })
#         user = User.objects.get(email=email)
#         self.assertEqual(user.role, 'regular_user')

#     def test_invalid_registration_does_not_create_user(self):
#         self.client.post(self.url, {
#             'email': 'invalid-email',
#             'password1': 'StrongPass99!',
#             'password2': 'StrongPass99!',
#         })
#         self.assertEqual(User.objects.count(), 0)

#     def test_invalid_registration_rerenders_form_with_errors(self):
#         response = self.client.post(self.url, {
#             'email': '',
#             'password1': 'StrongPass99!',
#             'password2': 'StrongPass99!',
#         })
#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(response.context['form'].is_valid())

#     def test_mismatched_passwords_does_not_create_user(self):
#         self.client.post(self.url, {
#             'email': fake.unique.email(),
#             'password1': 'StrongPass99!',
#             'password2': 'Different99!',
#         })
#         self.assertEqual(User.objects.count(), 0)

#     def test_short_password_does_not_create_user(self):
#         self.client.post(self.url, {
#             'email': fake.unique.email(),
#             'password1': 'abc',
#             'password2': 'abc',
#         })
#         self.assertEqual(User.objects.count(), 0)

#     def test_duplicate_email_does_not_create_second_user(self):
#         email = fake.unique.email()
#         make_user(email, 'StrongPass99!')
#         self.client.post(self.url, {
#             'email': email,
#             'password1': 'StrongPass99!',
#             'password2': 'StrongPass99!',
#         })
#         self.assertEqual(User.objects.filter(email=email).count(), 1)

#     def test_empty_password_does_not_create_user(self):
#         self.client.post(self.url, {
#             'email': fake.unique.email(),
#             'password1': '',
#             'password2': '',
#         })
#         self.assertEqual(User.objects.count(), 0)


# class LoginViewTest(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.url = reverse('login')
#         self.email = fake.unique.email()
#         self.password = 'StrongPass99!'
#         self.user = make_user(self.email, self.password)

#     def test_login_page_loads_with_status_200(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)

#     def test_login_page_uses_correct_template(self):
#         response = self.client.get(self.url)
#         self.assertTemplateUsed(response, 'accounts/login.html')

#     def test_login_page_contains_form(self):
#         response = self.client.get(self.url)
#         self.assertIn('form', response.context)

#     def test_authenticated_user_is_redirected_from_login(self):
#         self.client.force_login(self.user)
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse('contact_list'))

#     def test_valid_credentials_redirect_to_contact_list(self):
#         response = self.client.post(self.url, {
#             'username': self.email,
#             'password': self.password,
#         })
#         self.assertRedirects(response, reverse('contact_list'))

#     def test_valid_credentials_create_session(self):
#         self.client.post(self.url, {
#             'username': self.email,
#             'password': self.password,
#         })
#         self.assertIn('_auth_user_id', self.client.session)

#     def test_wrong_password_returns_200(self):
#         response = self.client.post(self.url, {
#             'username': self.email,
#             'password': 'WrongPassword!',
#         })
#         self.assertEqual(response.status_code, 200)

#     def test_wrong_password_shows_error_message(self):
#         response = self.client.post(self.url, {
#             'username': self.email,
#             'password': 'WrongPassword!',
#         })
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, 'Incorrect')

#     def test_unregistered_email_returns_200(self):
#         response = self.client.post(self.url, {
#             'username': 'nobody@example.com',
#             'password': 'StrongPass99!',
#         })
#         self.assertEqual(response.status_code, 200)

#     def test_unregistered_email_does_not_create_session(self):
#         self.client.post(self.url, {
#             'username': 'nobody@example.com',
#             'password': 'StrongPass99!',
#         })
#         self.assertNotIn('_auth_user_id', self.client.session)

#     def test_empty_email_returns_200(self):
#         response = self.client.post(self.url, {
#             'username': '',
#             'password': self.password,
#         })
#         self.assertEqual(response.status_code, 200)

#     def test_empty_password_returns_200(self):
#         response = self.client.post(self.url, {
#             'email': self.email,
#             'password': '',
#         })
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, 'required')

#     def test_registered_url_shows_sweetalert_flag(self):
#         response = self.client.get(self.url + '?registered=true')
#         self.assertContains(response, 'Account Created!')

#     def test_inactive_user_cannot_login(self):
#         self.user.is_active = False
#         self.user.save()
#         self.client.post(self.url, {
#             'username': self.email,
#             'password': self.password,
#         })
#         self.assertNotIn('_auth_user_id', self.client.session)


# class LogoutViewTest(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = make_user(fake.unique.email(), 'StrongPass99!')

#     def test_logout_redirects_to_login(self):
#         self.client.force_login(self.user)
#         response = self.client.post(reverse('logout'))
#         self.assertRedirects(response, reverse('login'))

#     def test_logout_destroys_session(self):
#         self.client.force_login(self.user)
#         self.client.post(reverse('logout'))
#         self.assertNotIn('_auth_user_id', self.client.session)

#     def test_logout_requires_post_not_get(self):
#         self.client.force_login(self.user)
#         response = self.client.get(reverse('logout'))
#         self.assertNotEqual(response.status_code, 200)
#         self.assertIn('_auth_user_id', self.client.session)

from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='Test@123'
        )

    def test_register_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    @patch('accounts.views.send_welcome_email.delay')
    def test_register_user(self, mock_send_email):
        response = self.client.post(reverse('register'), {
            'email': 'new@example.com',
            'password1': 'StrongPass@123',
            'password2': 'StrongPass@123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='new@example.com').exists())
        mock_send_email.assert_called_once()

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    @patch('accounts.views.send_otp_email.delay')
    def test_login_generates_otp_and_redirects(self, mock_send_otp):
        response = self.client.post(reverse('login'), {
            'username': 'user@example.com',
            'password': 'Test@123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify_otp'))
        session = self.client.session
        self.assertEqual(session.get('pending_user_id'), self.user.pk)
        mock_send_otp.assert_called_once()

    def test_verify_otp_page_without_session_redirects(self):
        response = self.client.get(reverse('verify_otp'))
        self.assertEqual(response.status_code, 302)

    def test_verify_otp_success(self):
        otp = self.user.generate_otp()
        session = self.client.session
        session['pending_user_id'] = self.user.pk
        session.save()

        response = self.client.post(reverse('verify_otp'), {
            'otp_code': otp
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('contact_list'))

    def test_verify_otp_invalid(self):
        self.user.generate_otp()
        session = self.client.session
        session['pending_user_id'] = self.user.pk
        session.save()

        response = self.client.post(reverse('verify_otp'), {
            'otp_code': '000000'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid')