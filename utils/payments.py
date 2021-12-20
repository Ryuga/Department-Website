import requests
import json
import PaytmChecksum

paytmParams = dict()

paytmParams["body"] = {
    "requestType": "Payment",
    "mid": "YOUR_MID_HERE",
    "websiteName": "YOUR_WEBSITE_NAME",
    "orderId": "ORDERID_98765",
    "callbackUrl": "https://<callback URL to be used by merchant>",
    "txnAmount": {
        "value": "1.00",
        "currency": "INR",
    },
    "userInfo": {
        "custId": "CUST_001",
    },
}

# Generate checksum by parameters we have in body
# Find your Merchant Key in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
checksum = PaytmChecksum.generateSignature(json.dumps(paytmParams["body"]), "YOUR_MERCHANT_KEY")

paytmParams["head"] = {
    "signature": checksum
}

post_data = json.dumps(paytmParams)

# for Staging
url = "https://securegw-stage.paytm.in/theia/api/v1/initiateTransaction?mid=YOUR_MID_HERE&orderId=ORDERID_98765"

# for Production
# url = "https://securegw.paytm.in/theia/api/v1/initiateTransaction?mid=YOUR_MID_HERE&orderId=ORDERID_98765"
response = requests.post(url, data = post_data, headers = {"Content-type": "application/json"}).json()
print(response)
