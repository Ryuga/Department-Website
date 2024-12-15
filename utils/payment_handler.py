import json

import requests
from django.conf import settings
from utils.paytm_checksum import generateSignature


class PaytmPaymentHandler:

    @staticmethod
    def initiate_transaction(transaction):
        params = dict()

        params["body"] = {
            "requestType": "Payment",
            "mid": settings.PAYTM_MERCHANT_ID,
            "websiteName": "Zephyrus",
            "orderId": str(transaction.id),
            "callbackUrl": settings.OAUTH_REDIRECTION_URL,
            "txnAmount": {
                "value": str(transaction.value),
                "currency": "INR",
            },
            "userInfo": {
                "custId": transaction.registration.id,

            },
        }
        params["head"] = {
            "signature": generateSignature(json.dumps(params["body"]), settings.PAYTM_MERCHANT_KEY)
        }
        url = settings.PAYTM_INITIATE_TRANSACTION_URL + "&orderId=" + str(transaction.id)
        print(url)

        return requests.post(
            url,
            json=params,
            headers={"Content-type": "application/json"}
        ).json()

    @staticmethod
    def generate_payments_page_url(transaction):
        return settings.PAYTM_SHOW_PAYMENTS_PAGE_URL + "&orderId=" + str(transaction.id)
