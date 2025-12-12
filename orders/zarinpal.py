import requests
import json
from django.conf import settings

# اطلاعات سندباکس زرین‌پال
MERCHANT = "41414141-4141-4141-4141-414141414141"
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
        # مبلغ باید حداقل ۱۰،۰۰۰ ریال (۱۰۰۰ تومان) باشد
        data = {
            "merchant_id": self.merchant,
            "amount": int(amount * 10),  # تبدیل تومان به ریال
            "callback_url": callback_url,
            "description": description,
            "metadata": {"email": email, "mobile": mobile}
        }

        headers = {'content-type': 'application/json', 'accept': 'application/json'}

        try:
            response = requests.post(ZP_API_REQUEST, data=json.dumps(data), headers=headers, timeout=10)
            result = response.json()

            # --- بخش دیباگ ---
            print(f"ZarinPal Request Response: {result}")
            # ------------------------------------------------

            # بررسی ایمن وجود 'data' و 'code'
            # گاهی زرین‌پال در صورت خطا data را [] برمی‌گرداند که دیکشنری نیست
            data_section = result.get('data')

            if data_section and isinstance(data_section, dict) and data_section.get('code') == 100:
                return {
                    'status': True,
                    'url': ZP_API_STARTPAY + data_section['authority'],
                    'authority': data_section['authority']
                }
            else:
                # استخراج کد خطا به صورت ایمن
                errors = result.get('errors')
                error_code = 'unknown'

                if isinstance(errors, dict):
                    error_code = errors.get('code')
                elif isinstance(errors, list):
                    # گاهی ارورها داخل لیست هستند
                    error_code = str(errors)

                return {'status': False, 'code': error_code}

        except requests.exceptions.Timeout:
            return {'status': False, 'code': 'timeout'}
        except requests.exceptions.ConnectionError:
            return {'status': False, 'code': 'connection_error'}
        except Exception as e:
            print(f"ZarinPal Exception: {str(e)}")
            return {'status': False, 'code': 'internal_error'}

    def payment_verify(self, amount, authority):
        """
        تایید نهایی پرداخت
        """
        data = {
            "merchant_id": self.merchant,
            "amount": int(amount * 10),  # ریال
            "authority": authority
        }

        headers = {'content-type': 'application/json', 'accept': 'application/json'}

        try:
            response = requests.post(ZP_API_VERIFY, data=json.dumps(data), headers=headers, timeout=10)
            result = response.json()

            # --- بخش دیباگ ---
            print(f"ZarinPal Verify Response: {result}")
            # -----------------

            data_section = result.get('data')

            if data_section and isinstance(data_section, dict):
                code = data_section.get('code')
                if code == 100:
                    return {'status': True, 'ref_id': data_section.get('ref_id')}
                elif code == 101:
                    return {'status': True, 'ref_id': data_section.get('ref_id'), 'message': 'Verified Before'}

            # در غیر این صورت خطا داریم
            return {'status': False, 'code': result.get('errors', {}).get('code', 'unknown')}

        except Exception as e:
            return {'status': False, 'code': str(e)}