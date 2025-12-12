import requests
import json
from django.conf import settings


def send_otp_sms(mobile, code):
    """
    ارسال پیامک کد تایید با استفاده از وب‌سرویس ملی پیامک (Rest)
    """
    username = settings.MELIPAYAMAK_USERNAME
    password = settings.MELIPAYAMAK_PASSWORD

    # آدرس API ملی پیامک
    url = "https://rest.payamak-panel.com/api/SendSMS/SendSMS"

    data = {
        "username": username,
        "password": password,
        "to": mobile,
        "from": "50002710096112",  # شماره اختصاصی یا عمومی پنل
        "text": f"کد ورود شما به دیجی‌شاپ:\n{code}",
        "isFlash": False
    }

    try:
        response = requests.post(url, json=data, timeout=5)
        result = response.json()

        if result['Value'] > 15:
            return True
        else:
            print(f"SMS Error: {result['RetStatus']}")  # چاپ خطا در کنسول برای دیباگ
            return False
    except Exception as e:
        print(f"Connection Error: {str(e)}")
        return False