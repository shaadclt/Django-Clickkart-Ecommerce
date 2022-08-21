# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
from django.conf import settings

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
def sentOTP(mobile):
    phone = "+91" + str(mobile)
    account_sid = settings.ACCOUNT_SID
    auth_token = settings.AUTH_TOKEN
    client = Client(account_sid, auth_token)

    verification = client.verify.services(
        settings.SERVICES_KEY_OTP
    ).verifications.create(to=phone, channel="sms")

    print(verification.status)


def checkOTP(mobile, otp):
    account_sid = settings.ACCOUNT_SID
    auth_token = settings.AUTH_TOKEN
    client = Client(account_sid, auth_token)

    verification_check = client.verify.services(
        settings.SERVICES_KEY_OTP
    ).verification_checks.create(to="+91" + mobile, code=otp)

    if verification_check.status == "approved":
        return True
    else:
        return False
