# Tests for ContactGroup and Contact models
import os
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
# SimpleUploadedFile → creates a fake uploaded file for testing ImageField
from faker import Faker
from model_bakery import baker
from contacts.models import ContactGroup, Contact

fake = Faker()


def make_image():
    return SimpleUploadedFile(
        name='test.jpg',
        content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\xff\x00\x2c'
                b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x00\x3b',
        content_type='image/gif'
    )


class ContactGroupModelTest(TestCase):
    def test_contact_group_can_be_created(self):
        group = ContactGroup.objects.create(name='Family')
        self.assertIsNotNone(group.pk)

    def test_str_returns_name(self):
        group = ContactGroup.objects.create(name='Work')
        self.assertEqual(str(group), 'Work')

    def test_name_is_unique(self):
        from django.db import IntegrityError
        ContactGroup.objects.create(name='Friends')
        with self.assertRaises(IntegrityError):
            ContactGroup.objects.create(name='Friends')

    def test_groups_are_ordered_alphabetically(self):
        ContactGroup.objects.create(name='Work')
        ContactGroup.objects.create(name='Family')
        ContactGroup.objects.create(name='Friends')
        groups = ContactGroup.objects.all()
        names  = [g.name for g in groups]
        self.assertEqual(names, sorted(names))

    def test_baker_can_create_contact_group(self):
        group = baker.make(ContactGroup)
        self.assertIsNotNone(group.pk)

    def test_contact_group_name_max_length(self):
        from django.core.exceptions import ValidationError
        group = ContactGroup(name='A' * 51)
        with self.assertRaises(ValidationError):
            group.full_clean()


class ContactModelTest(TestCase):

    def setUp(self):
        self.group = ContactGroup.objects.create(name='Test Group')
        # create a group to assign to contacts in tests

    def make_contact(self, **kwargs):
        defaults = {
            'name':          fake.name(),
            'phone_number':  fake.numerify('##########'),
            # numerify() → replaces # with random digits
            'email':         fake.email(),
            'contact_picture': make_image(),
            'contact_group': self.group,
        }
        defaults.update(kwargs)
        # update() → overrides any defaults with provided kwargs
        return Contact.objects.create(**defaults)

    def test_contact_can_be_created(self):
        contact = self.make_contact()
        self.assertIsNotNone(contact.pk)

    def test_str_returns_name(self):
        contact = self.make_contact(name='John Doe')
        self.assertEqual(str(contact), 'John Doe')

    def test_email_is_optional(self):
        # contacts can be created without an email address
        contact = self.make_contact(email=None)
        self.assertIsNone(contact.email)

    def test_phone_number_is_unique(self):
        from django.db import IntegrityError
        phone = '1234567890'
        self.make_contact(phone_number=phone)
        with self.assertRaises(IntegrityError):
            self.make_contact(phone_number=phone)

    def test_email_is_unique(self):
        from django.db import IntegrityError
        email = fake.email()
        self.make_contact(email=email)
        with self.assertRaises(IntegrityError):
            self.make_contact(email=email)

    def test_contacts_are_ordered_alphabetically(self):
        self.make_contact(name='Zara')
        self.make_contact(name='Alice')
        self.make_contact(name='Mike')
        contacts = Contact.objects.all()
        names    = [c.name for c in contacts]
        self.assertEqual(names, sorted(names))

    def test_contact_belongs_to_group(self):
        contact = self.make_contact()
        self.assertEqual(contact.contact_group, self.group)

    def test_deleting_group_deletes_contacts(self):
        # CASCADE → deleting a group should delete all its contacts
        self.make_contact()
        self.assertEqual(Contact.objects.count(), 1)
        self.group.delete()
        self.assertEqual(Contact.objects.count(), 0)

    def test_contact_picture_is_deleted_on_contact_delete(self):
        contact  = self.make_contact()
        pic_path = contact.contact_picture.path
        contact.delete()
        self.assertFalse(os.path.exists(pic_path))

    def test_old_picture_deleted_when_updated(self):
        contact      = self.make_contact()
        old_pic_path = contact.contact_picture.path
        contact.contact_picture = make_image()
        contact.save()
        self.assertFalse(os.path.exists(old_pic_path))
