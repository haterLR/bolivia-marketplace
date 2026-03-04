import hmac
import os
from hashlib import sha256


class TigoMoneyProvider:
    def __init__(self):
        self.api_key = os.getenv('TIGO_MONEY_API_KEY', 'fake-key')
        self.secret = os.getenv('TIGO_MONEY_SECRET', 'fake-secret')

    def create_payment(self, order, callback_url):
        return {
            'provider': 'tigo_money',
            'payment_url': f'https://fake.tigo.money/pay/{order.id}',
            'reference': f'TM-{order.id}',
            'callback_url': callback_url,
        }

    def verify_callback(self, payload, signature):
        digest = hmac.new(self.secret.encode(), str(payload).encode(), sha256).hexdigest()
        return hmac.compare_digest(digest, signature)
