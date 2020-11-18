from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationToken(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
                str(user.pk) + str(timestamp) +
                str(user.profile.is_verified)
                )

account_activation_token = AccountActivationToken()
