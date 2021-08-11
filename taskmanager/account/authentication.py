import re
from django.contrib.auth.models import User
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework import authentication
from rest_framework import exceptions

from .tokens import account_activation_token


class OneTimeTokenAuthentication(authentication.BaseAuthentication):
    """Authenticate user using one time token."""
    token_generator = None
    message = None

    def authenticate(self, request):
        user = None
        uidb64 = None
        token = None

        if request.method == 'GET':
            # determine uidb64 and token from the path
            pattern = re.compile('(?:/[a-zA-Z\d\-_]+)+/(?P<uidb64>[a-zA-Z\d\-_]+)/(?P<token>[a-zA-Z\d\-_]+)/')

            parse_result = pattern.match(request.get_full_path())
            if parse_result:
                credentials = parse_result.groupdict()
                uidb64 = credentials['uidb64']
                token = credentials['token']

        elif request.method in ('POST', 'PATCH', 'PUT'):
            # get uidb64 and token from the request body
            uidb64 = request.data.get('uidb64')
            token = request.data.get('token')

        try:
            # get user instance
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

        except (AttributeError, TypeError, ValueError, OverflowError, User.DoesNotExist):
            pass

        # check if token is valid
        if not self.token_generator.check_token(user, token):
            raise exceptions.AuthenticationFailed(self.message)

        return user, token


class ActivationTokenAuthentication(OneTimeTokenAuthentication):
    token_generator = account_activation_token
    message = 'The confirmation link was invalid, possibly because it has already been used.'


class ResetPasswordTokenAuthentication(OneTimeTokenAuthentication):
    token_generator = PasswordResetTokenGenerator()
    message = 'The reset link is invalid.'
