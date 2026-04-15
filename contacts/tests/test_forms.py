# Tests for ContactForm validation

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker
from model_bakery import baker
from contacts.forms import ContactForm
from contacts.models import ContactGroup, Contact

fake = Faker()


def make_image():
    return SimpleUploadedFile(
        name='test.jpg',
        content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\xff\x00\x2c'
                b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x00\x3b',
        content_type='image/gif'
    )


class ContactFormTest(TestCase):

    def setUp(self):
        self.group = ContactGroup.objects.create(name='Test Group')

    def get_valid_data(self):
        # returns valid form POST data
        return {
            'name':          'John Doe',
            'phone_number':  '+1234567890',
            'email':         fake.email(),
            'contact_group': self.group.pk,
        }

    def get_valid_files(self):
        # returns valid file data for the form
        return {'contact_picture': make_image()}

    #  Valid Scenarios 

    def test_valid_form_is_valid(self):
        form = ContactForm(data=self.get_valid_data(), files=self.get_valid_files())
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_form_without_email_is_valid(self):
        # email is optional in ContactForm
        data = self.get_valid_data()
        data['email'] = ''
        form = ContactForm(data=data, files=self.get_valid_files())
        self.assertTrue(form.is_valid())

    def test_form_saves_contact_to_database(self):
        form = ContactForm(data=self.get_valid_data(), files=self.get_valid_files())
        self.assertTrue(form.is_valid())
        contact = form.save()
        self.assertIsNotNone(contact.pk)

    #  Name Validation 

    def test_empty_name_is_invalid(self):
        data = self.get_valid_data()
        data['name'] = ''
        form = ContactForm(data=data, files=self.get_valid_files())
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_single_character_name_is_invalid(self):
        # name must be at least 2 characters
        data = self.get_valid_data()
        data['name'] = 'A'
        form = ContactForm(data=data, files=self.get_valid_files())
        self.assertFalse(form.is_valid())

    def test_two_character_name_is_valid(self):
        data = self.get_valid_data()
        data['name'] = 'Jo'
        form = ContactForm(data=data, files=self.get_valid_files())
        self.assertTrue(form.is_valid())

    def test_whitespace_only_name_is_invalid(self):
        data = self.get_valid_data()
        data['name'] = '   '
        form = ContactForm(data=data, files=self.get_valid_files())
        self.assertFalse(form.is_valid())

    #  Phone Number Validation 

    def test_empty_phone_number_is_invalid(self):
        data                 = self.get_valid_data()
        data['phone_number'] = ''
        form = ContactForm(data=data, files=self.get_valid_files())
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)

    def test_valid_phone_with_country_code_is_valid(self):
        data                 = self.get_valid_data()
        data['phone_number'] = '+91 9876543210'
        form = ContactForm(data=data, files=self.get_valid_files())
        self.assertTrue(form.is_valid())

    def test_phone_with_dashes_is_valid(self):
        data                 = self.get_valid_data()
        data['phone_number'] = '123-456-7890'
        form = ContactForm(data=data, files=self.get_valid_files())
        self.assertTrue(form.is_valid())

    def test_too_short_phone_is_invalid(self):
        # phone must be at least 7 characters
        data                 = self.get_valid_data()
        data['phone_number'] = '123'
        form = ContactForm(data=data, files=self.get_valid_files())
        self.assertFalse(form.is_valid())

    def test_duplicate_phone_number_is_invalid(self):
        phone   = '+1234567890'
        Contact.objects.create(
            name='Existing',
            phone_number=phone,
            contact_group=self.group,
            contact_picture=make_image()
        )
        data                 = self.get_valid_data()
        data['phone_number'] = phone
        form = ContactForm(data=data, files=self.get_valid_files())
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)

    def test_duplicate_phone_excluded_on_update(self):
        contact = Contact.objects.create(
            name='Test',
            phone_number='+1234567890',
            contact_group=self.group,
            contact_picture=make_image()
        )
        data = self.get_valid_data()
        data['phone_number'] = '+1234567890'
        form = ContactForm(data=data, files=self.get_valid_files(), instance=contact)
        # instance=contact → tells the form we are editing this existing contact
        self.assertTrue(form.is_valid())

    #  Email Validation

    def test_invalid_email_format_is_invalid(self):
        data = self.get_valid_data()
        data['email'] = 'notanemail'
        form = ContactForm(data=data, files=self.get_valid_files())
        self.assertFalse(form.is_valid())

    #  Group Validation 

    def test_missing_contact_group_is_invalid(self):
        data                   = self.get_valid_data()
        data['contact_group']  = ''
        form = ContactForm(data=data, files=self.get_valid_files())
        self.assertFalse(form.is_valid())
        self.assertIn('contact_group', form.errors)

    def test_nonexistent_group_id_is_invalid(self):
        data                  = self.get_valid_data()
        data['contact_group'] = 9999
        # 9999 → ID that does not exist in the database
        form = ContactForm(data=data, files=self.get_valid_files())
        self.assertFalse(form.is_valid())

    #  Picture Validation 

    def test_missing_picture_is_invalid(self):
        form = ContactForm(data=self.get_valid_data(), files={})
        self.assertFalse(form.is_valid())
        self.assertIn('contact_picture', form.errors)

    def test_empty_form_is_invalid(self):
        form = ContactForm(data={}, files={})
        self.assertFalse(form.is_valid())