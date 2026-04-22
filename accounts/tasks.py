import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_otp_email(self, user_email, otp_code, full_name):
    """
    Sends the 6-digit OTP to the user's email address.
    Called asynchronously via Celery after credential validation.
    Emails are delivered through Mailtrap in local development.
    """
    try:
        send_mail(
            subject='Your Login OTP — Contact Book',
            message=(
                f'Hello {full_name},\n\n'
                f'Your One-Time Password (OTP) for Contact Book login is:\n\n'
                f'        {otp_code}\n\n'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        logger.info('OTP email sent to %s', user_email)
        return f'OTP email sent to {user_email}'

    except Exception as exc:
        logger.error('OTP email failed for %s: %s', user_email, exc)
        # Retry up to 3 times with a 30-second delay between attempts
        raise self.retry(exc=exc, countdown=30)


@shared_task(bind=True, max_retries=3)
def send_welcome_email(self, user_email, full_name):
    """Sends a welcome email immediately after successful registration."""
    try:
        send_mail(
            subject='Welcome to Contact Book!',
            message=(
                f'Hello {full_name},\n\n'
                f'Welcome to Contact Book! Your account has been created.\n\n'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        logger.info('Welcome email sent to %s', user_email)
        return f'Welcome email sent to {user_email}'
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)