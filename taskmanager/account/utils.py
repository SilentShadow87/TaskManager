from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_one_time_token(request, user, token, template, subject):
    """Send an email to the user with one-time token link."""
    current_site = get_current_site(request)

    # prepare email subject and message
    subject = subject
    message = render_to_string(
            template,
            {
                'request': request,
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token
            })

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email,])
