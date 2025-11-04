from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import base64
import os
import requests
from models import db, SaleTransaction
import pytz

EAT = pytz.timezone("Africa/Nairobi")

# 🔵 Blueprint
mpesa_bp = Blueprint("mpesa", __name__, url_prefix="/mpesa")

# 🔐 Config (from environment variables)
MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE") 
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY")
MPESA_BASE_URL = os.getenv("MPESA_BASE_URL")


# 🔑 Get M-Pesa access token
def get_access_token():
    try:
        resp = requests.get(
            f"{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials",
            auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET),
            timeout=10
        )
        resp.raise_for_status()
        return resp.json().get("access_token")
    except Exception as e:
        current_app.logger.error(f"Failed to get M-Pesa token: {e}")
        return None


# 💳 STK Push request
@mpesa_bp.route("/stkpush", methods=["POST"])
def lipa_na_mpesa():
    data = request.get_json() or {}
    phone = str(data.get("phone", "")).strip()
    amount = float(data.get("amount", 0))
    sale_id = data.get("sale_id")

    if not phone or not amount:
        return jsonify({"error": "Missing phone or amount"}), 400

    token = get_access_token()
    if not token:
        return jsonify({"error": "Unable to get M-Pesa access token"}), 500

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        (MPESA_SHORTCODE + MPESA_PASSKEY + timestamp).encode("utf-8")
    ).decode("utf-8")

    callback_url = f"{request.host_url}mpesa/callback"
    account_ref = f"FIDPOS-{sale_id or 'NOREF'}"

    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": MPESA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": callback_url,
        "AccountReference": account_ref,
        "TransactionDesc": "FidPOS Checkout Payment"
    }

    try:
        resp = requests.post(
            f"{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers=headers,
            timeout=15
        )
        res_json = resp.json()
        current_app.logger.info(f"STKPush Response: {res_json}")
        return jsonify(res_json), resp.status_code
    except Exception as e:
        current_app.logger.error(f"STK Push failed: {e}")
        return jsonify({"error": str(e)}), 500


# 📬 Handle M-Pesa callback (confirmation)
@mpesa_bp.route("/callback", methods=["POST"])
def mpesa_callback():
    data = request.get_json() or {}
    try:
        body = data.get("Body", {})
        callback = body.get("stkCallback", {})
        result_code = callback.get("ResultCode")
        result_desc = callback.get("ResultDesc")
        checkout_id = callback.get("CheckoutRequestID")

        if result_code == 0:
            metadata = callback["CallbackMetadata"]["Item"]
            amount = next(item["Value"] for item in metadata if item["Name"] == "Amount")
            phone = next(item["Value"] for item in metadata if item["Name"] == "PhoneNumber")

            # Update DB
            transaction = SaleTransaction.query.filter_by(id=checkout_id).first()
            if transaction:
                transaction.status = "paid"
                transaction.paymenyt_method = "mpesa"
                transaction.paid_at = datetime.now(EAT)
                db.session.commit()

            current_app.logger.info(f"✅ Payment success: {phone} paid {amount}")
        else:
            current_app.logger.warning(f"❌ Payment failed: {result_desc}")

    except Exception as e:
        current_app.logger.error(f"[Callback Error] {e}")

    return jsonify({"ResultCode": 0, "ResultDesc": "Received"})

@mpesa_bp.route("/status/<sale_id>", methods=["GET"])
def check_mpesa_status(sale_id):
    transaction = SaleTransaction.query.filter_by(id=sale_id).first()
    if not transaction:
        return jsonify({"error": "Sale not found"}), 404

    if transaction.status == "paid":
        return jsonify({"status": "Success"}), 200
    elif transaction.status == "failed":
        return jsonify({"status": "Failed"}), 200
    else:
        return jsonify({"status": "Pending"}), 200
