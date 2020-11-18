from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import account_activation_token


def send_confirmation_email(request, user):
    current_site = get_current_site(request)

    subject = 'Email confirmation'
    message = render_to_string(
            'account/activation_email.html', 
            {
                'request': request,
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })

    send_mail(subject, message, 'fejsov87@gmail.com', [user.email,])
