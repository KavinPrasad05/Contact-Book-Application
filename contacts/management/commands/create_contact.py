from django.core.management.base import BaseCommand, CommandError
from contacts.models import Contact, ContactGroup


class Command(BaseCommand):
    help = 'Create a new contact from the command line'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, required=True, help='Contact name')
        parser.add_argument('--phone', type=str, required=True, help='Phone number')
        parser.add_argument('--email', type=str, help='Email address')
        parser.add_argument('--group', type=str, help='Contact group name')

    def handle(self, *args, **options):
        name = options['name']
        phone = options['phone']
        email = options.get('email')
        group_name = options.get('group')

        contact_group = None
        if group_name:
            contact_group, _ = ContactGroup.objects.get_or_create(name=group_name)

        try:
            contact = Contact.objects.create(
                name=name,
                phone_number=phone,
                email=email,
                contact_group=contact_group
            )
        except Exception as exc:
            raise CommandError(f'Failed to create contact: {exc}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Contact "{contact.name}" created successfully with ID {contact.id}'
            )
        )