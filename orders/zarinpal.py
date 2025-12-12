import requests
import json
from django.conf import settings

# اطلاعات سندباکس زرین‌پال
MERCHANT = "41414141-4141-4141-4141-414141414141"  # مرچنت کد تست زرین پال
ZP_API_REQUEST = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://sandbox.zarinpal.com/pg/StartPay/"


class ZarinPal:
    def __init__(self):
        self.merchant = MERCHANT

    def payment_request(self, amount, description, callback_url, email=None, mobile=None):
        """
        ارسال درخواست پرداخت به زرین‌پال و دریافت Authority
        """
        data = {
            "merchant_id": self.merchant,
            "amount": amount * 10,  # تبدیل تومان به ریال (زرین‌پال ریال می‌گیرد)
            "callback_url": callback_url,
            "description": description,
            "metadata": {"email": email, "mobile": mobile}
        }

        headers = {'content-type': 'application/json', 'accept': 'application/json'}

        try:
            response = requests.post(ZP_API_REQUEST, data=json.dumps(data), headers=headers, timeout=10)
            result = response.json()

            if result['data']['code'] == 100:
                return {
                    'status': True,
                    'url': ZP_API_STARTPAY + result['data']['authority'],
                    'authority': result['data']['authority']
                }
            else:
                return {'status': False, 'code': result['errors']['code']}
        except requests.exceptions.Timeout:
            return {'status': False, 'code': 'timeout'}
        except requests.exceptions.ConnectionError:
            return {'status': False, 'code': 'connection_error'}

    def payment_verify(self, amount, authority):
        """
        تایید نهایی پرداخت
        """
        data = {
            "merchant_id": self.merchant,
            "amount": amount * 10,  # ریال
            "authority": authority
        }

        headers = {'content-type': 'application/json', 'accept': 'application/json'}

        try:
            response = requests.post(ZP_API_VERIFY, data=json.dumps(data), headers=headers, timeout=10)
            result = response.json()

            if result['data']['code'] == 100:
                return {'status': True, 'ref_id': result['data']['ref_id']}
            elif result['data']['code'] == 101:
                return {'status': True, 'ref_id': result['data']['ref_id'], 'message': 'Verified Before'}
            else:
                return {'status': False, 'code': result['errors']['code']}
        except Exception as e:
            return {'status': False, 'code': str(e)}