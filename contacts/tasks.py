import logging
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)

@shared_task
def send_good_morning_message():
    User       = get_user_model()
    users      = User.objects.filter(is_active=True).exclude(email='')
    sent_count = 0

    for user in users:
        try:
            send_mail(
                subject='Good Morning! — Contact Book',
                message=(
                    f'Good Morning, {user.get_full_name()}!'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            sent_count += 1
            logger.info('Good morning email sent to %s', user.email)

        except Exception as exc:
            logger.error(
                'Failed to send good morning email to %s: %s',
                user.email, exc
            )

    logger.info('Good morning task complete: %d emails sent', sent_count)
    return f'Good morning emails sent to {sent_count} users'