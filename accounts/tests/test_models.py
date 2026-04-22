from django.test import TestCase
from django.contrib.auth import get_user_model
from model_bakery import baker
from faker import Faker

User = get_user_model()

fake = Faker()

class CustomUserModelTest(TestCase):

    def setUp(self):
        self.password = 'StrongPass99!'
        self.user = User.objects.create_user(
            email=fake.email(),
            password=self.password,
        )
        print(self.user)

    def test_user_email_is_stored_correctly(self):
        email = 'test@example.com'
        user  = User.objects.create_user(email=email, password=self.password)
        self.assertEqual(user.email, email)

    def test_user_default_role_is_regular_user(self):
        self.assertEqual(self.user.role, 'regular_user')

    def test_user_is_active_by_default(self):
        self.assertTrue(self.user.is_active)

    def test_user_is_not_staff_by_default(self):
        self.assertFalse(self.user.is_staff)

    def test_user_is_not_superuser_by_default(self):
        self.assertFalse(self.user.is_superuser)

    def test_password_is_hashed_not_plain_text(self):
        self.assertNotEqual(self.user.password, self.password)

    def test_check_password_returns_true_for_correct_password(self):
        self.assertTrue(self.user.check_password(self.password))

    def test_check_password_returns_false_for_wrong_password(self):
        self.assertFalse(self.user.check_password('WrongPassword!'))

    def test_email_field_is_unique(self):
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email=self.user.email, password=self.password)

    # Role Tests 

    def test_regular_user_can_create_returns_false(self):
        self.assertFalse(self.user.can_create())

    def test_regular_user_can_update_returns_false(self):
        self.assertFalse(self.user.can_update())

    def test_regular_user_can_delete_returns_false(self):
        self.assertFalse(self.user.can_delete())

    def test_admin_can_create_returns_true(self):
        admin = User.objects.create_user(email=fake.email(), password=self.password)
        admin.role = 'admin'
        admin.save()
        self.assertTrue(admin.can_create())

    def test_admin_can_update_returns_true(self):
        admin = User.objects.create_user(email=fake.email(), password=self.password)
        admin.role = 'admin'
        admin.save()
        self.assertTrue(admin.can_update())

    def test_admin_can_delete_returns_false(self):
        admin = User.objects.create_user(email=fake.email(), password=self.password)
        admin.role = 'admin'
        admin.save()
        self.assertFalse(admin.can_delete())

    def test_super_admin_can_create_returns_true(self):
        super_admin = User.objects.create_user(email=fake.email(), password=self.password)
        super_admin.role = 'super_admin'
        super_admin.save()
        self.assertTrue(super_admin.can_create())

    def test_super_admin_can_update_returns_true(self):
        super_admin = User.objects.create_user(email=fake.email(), password=self.password)
        super_admin.role = 'super_admin'
        super_admin.save()
        self.assertTrue(super_admin.can_update())

    def test_super_admin_can_delete_returns_true(self):
        super_admin = User.objects.create_user(email=fake.email(), password=self.password)
        super_admin.role = 'super_admin'
        super_admin.save()
        self.assertTrue(super_admin.can_delete())

    # Manager Tests 

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password=self.password)

    def test_create_user_with_none_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password=self.password)

    def test_create_superuser_sets_is_staff_true(self):
        superuser = User.objects.create_superuser(
            email=fake.email(), password=self.password
        )
        self.assertTrue(superuser.is_staff)

    def test_create_superuser_sets_is_superuser_true(self):
        superuser = User.objects.create_superuser(
            email=fake.email(), password=self.password
        )
        self.assertTrue(superuser.is_superuser)

    def test_create_superuser_sets_role_to_super_admin(self):
        superuser = User.objects.create_superuser(
            email=fake.email(), password=self.password
        )
        self.assertEqual(superuser.role, 'super_admin')

    def test_email_is_normalized_on_creation(self):
        user = User.objects.create_user(
            email='User@EXAMPLE.COM', 
            password=self.password
        )
        self.assertEqual(user.email, 'User@example.com')

    #  Baker Tests 

    def test_baker_can_create_user(self):
        user = baker.make(User)
        self.assertIsNotNone(user.pk)

    def test_baker_can_create_multiple_users(self):
        users = baker.make(User, _quantity=5)
        self.assertEqual(len(users), 5)

    def test_generate_otp(self):
        user = User.objects.create_user(email='otp@example.com', password='Test@123')
        otp = user.generate_otp()
        self.assertEqual(len(otp), 6)
        self.assertEqual(user.otp_code, otp)

    def test_is_otp_valid(self):
        user = User.objects.create_user(email='otp2@example.com', password='Test@123')
        otp = user.generate_otp()
        self.assertTrue(user.is_otp_valid(otp))
        self.assertFalse(user.is_otp_valid('000000'))

    def test_clear_otp(self):
        user = User.objects.create_user(email='otp3@example.com', password='Test@123')
        user.generate_otp()
        user.clear_otp()
        self.assertIsNone(user.otp_code)
        self.assertTrue(user.is_otp_verified)