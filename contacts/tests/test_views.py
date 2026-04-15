from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from faker import Faker

from contacts.models import ContactGroup, Contact

User = get_user_model()
fake = Faker()


def make_image(name='test.gif'):
    return SimpleUploadedFile(
        name=name,
        content=(
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\xff\x00\x2c'
            b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x00\x3b'
        ),
        content_type='image/gif'
    )


def make_user(role='regular_user', password='StrongPass99!'):
    user = User.objects.create_user(
        email=fake.unique.email(),
        password=password
    )
    user.role = role
    user.save()
    return user


def make_contact(group):
    return Contact.objects.create(
        name=fake.name(),
        phone_number=fake.unique.numerify('##########'),
        email=fake.unique.email(),
        contact_picture=make_image(),
        contact_group=group,
    )


class ContactListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('contact_list')
        self.user = make_user('regular_user')

    def test_unauthenticated_user_is_redirected(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_authenticated_user_can_access(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_correct_template_is_used(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'contacts/contact_list.html')

    def test_form_is_in_context(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertIn('form', response.context)

    def test_groups_are_in_context(self):
        self.client.force_login(self.user)
        ContactGroup.objects.create(name='Family')
        response = self.client.get(self.url)
        self.assertIn('groups', response.context)


class ContactCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('contact_create')
        self.group = ContactGroup.objects.create(name='Test')
        self.regular = make_user('regular_user')
        self.admin = make_user('admin')
        self.super_admin = make_user('super_admin')

    def get_valid_data(self):
        return {
            'name': fake.name(),
            'phone_number': fake.unique.numerify('##########'),
            'email': fake.unique.email(),
            'contact_group': self.group.pk,
            'contact_picture': make_image(),
        }

    def test_unauthenticated_user_returns_401(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['success'], False)
        self.assertEqual(response.json()['message'], 'Login required.')

    def test_regular_user_returns_403(self):
        self.client.force_login(self.regular)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['success'], False)

    def test_admin_can_create_contact(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url, self.get_valid_data())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_super_admin_can_create_contact(self):
        self.client.force_login(self.super_admin)
        response = self.client.post(self.url, self.get_valid_data())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_valid_data_creates_contact(self):
        self.client.force_login(self.admin)
        self.client.post(self.url, self.get_valid_data())
        self.assertEqual(Contact.objects.count(), 1)

    def test_valid_data_returns_success_json(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url, self.get_valid_data())
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('message', data)

    def test_invalid_data_returns_400(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url, {
            'name': '',
            'phone_number': '',
            'contact_group': self.group.pk,
        })
        self.assertEqual(response.status_code, 400)

    def test_invalid_data_returns_errors_in_json(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url, {'name': ''})
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('errors', data)

    def test_invalid_data_does_not_create_contact(self):
        self.client.force_login(self.admin)
        self.client.post(self.url, {'name': ''})
        self.assertEqual(Contact.objects.count(), 0)


class ContactGetViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.group = ContactGroup.objects.create(name='Test')
        self.contact = make_contact(self.group)
        self.url = reverse('contact_get', args=[self.contact.pk])
        self.admin = make_user('admin')
        self.super_admin = make_user('super_admin')
        self.regular = make_user('regular_user')

    def test_unauthenticated_user_returns_401(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['success'], False)
        self.assertEqual(response.json()['message'], 'Login required.')

    def test_regular_user_returns_403(self):
        self.client.force_login(self.regular)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['success'], False)

    def test_admin_gets_contact_json(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['id'], self.contact.pk)

    def test_super_admin_gets_contact_json(self):
        self.client.force_login(self.super_admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], self.contact.pk)

    def test_response_contains_all_fields(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        data = response.json()
        for field in ['id', 'name', 'phone_number', 'email', 'contact_group', 'picture_url']:
            self.assertIn(field, data)

    def test_nonexistent_contact_returns_404(self):
        self.client.force_login(self.admin)
        url = reverse('contact_get', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ContactUpdateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.group = ContactGroup.objects.create(name='Test')
        self.contact = make_contact(self.group)
        self.url = reverse('contact_update', args=[self.contact.pk])
        self.admin = make_user('admin')
        self.regular = make_user('regular_user')
        self.super_admin = make_user('super_admin')

    def get_valid_data(self):
        return {
            'name': 'Updated Name',
            'phone_number': fake.unique.numerify('##########'),
            'email': fake.unique.email(),
            'contact_group': self.group.pk,
            'contact_picture': make_image('updated.gif'),
        }

    def test_unauthenticated_user_returns_401(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['success'], False)
        self.assertEqual(response.json()['message'], 'Login required.')

    def test_regular_user_returns_403(self):
        self.client.force_login(self.regular)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['success'], False)

    def test_admin_can_update_contact(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url, self.get_valid_data())
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])

    def test_update_changes_contact_name_in_database(self):
        self.client.force_login(self.admin)
        self.client.post(self.url, self.get_valid_data())
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.name, 'Updated Name')

    def test_invalid_data_returns_400(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url, {'name': ''})
        self.assertEqual(response.status_code, 400)

    def test_invalid_data_returns_errors_in_json(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url, {'name': ''})
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('errors', data)

    def test_super_admin_can_update_contact(self):
        self.client.force_login(self.super_admin)
        response = self.client.post(self.url, self.get_valid_data())
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])


class ContactDeleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.group = ContactGroup.objects.create(name='Test')
        self.contact = make_contact(self.group)
        self.url = reverse('contact_delete', args=[self.contact.pk])
        self.super_admin = make_user('super_admin')
        self.admin = make_user('admin')
        self.regular = make_user('regular_user')

    def test_unauthenticated_user_returns_401(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['success'], False)
        self.assertEqual(response.json()['message'], 'Login required.')

    def test_regular_user_returns_403(self):
        self.client.force_login(self.regular)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['success'], False)

    def test_admin_returns_403(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['success'], False)

    def test_super_admin_can_delete_contact(self):
        self.client.force_login(self.super_admin)
        response = self.client.post(self.url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])

    def test_delete_removes_contact_from_database(self):
        self.client.force_login(self.super_admin)
        pk = self.contact.pk
        self.client.post(self.url)
        self.assertFalse(Contact.objects.filter(pk=pk).exists())

    def test_delete_response_contains_contact_name(self):
        self.client.force_login(self.super_admin)
        contact_name = self.contact.name
        response = self.client.post(self.url)
        data = response.json()
        self.assertIn(contact_name, data['message'])

    def test_delete_nonexistent_contact_returns_404_for_super_admin(self):
        self.client.force_login(self.super_admin)
        url = reverse('contact_delete', args=[9999])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)