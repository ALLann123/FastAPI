#!/usr/bin/python3
import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
import uvicorn
#---This imports handle STK pus
import base64
from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field
#---Receiving the transaction result
from fastapi import Request

# Load credentials from the .env file
load_dotenv()

app = FastAPI(title="Daraja M-PESA Tutorial")

# Sandbox base URL
BASE_URL = "https://sandbox.safaricom.co.ke"


@app.get("/")
def home():
    return {
        "message": "Daraja FastAPI is running"
    }


@app.get("/token")
def get_access_token():
    # Read our credentials securely from environment variables
    consumer_key = os.getenv("DARAJA_CONSUMER_KEY")
    consumer_secret = os.getenv("DARAJA_CONSUMER_SECRET")

    if not consumer_key or not consumer_secret:
        raise HTTPException(
            status_code=500,
            detail="Daraja credentials are missing"
        )

    # Ask Safaricom for an OAuth access token
    url = (
        f"{BASE_URL}/oauth/v1/generate"
        "?grant_type=client_credentials"
    )

    try:
        response = requests.get(
            url,
            auth=(consumer_key, consumer_secret),
            timeout=20
        )
        response.raise_for_status()
        data = response.json()

    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Could not authenticate with Daraja"
        )

    token = data.get("access_token")

    if not token:
        raise HTTPException(
            status_code=502,
            detail="Daraja did not return an access token"
        )

    # For this learning endpoint, return only whether
    # authentication succeeded. Do not expose the token.
    return {
        "authenticated": True,
        "message": "Daraja authentication successful"
    }


#-------------Here we make an STK Push------------------
# Validate the data sent to our payment endpoint
class PaymentRequest(BaseModel):
    phone: str=Field(
        pattern=r"^254[71]\d{8}$",
        description="Phone number in format 2547XXXXXXXX"
    )
    amount: int=Field(ge=1, le=250000)
    reference: str=Field(
        default="ORDER001",
        min_length=1,
        max_length=12
    )

# Endpoint to handle STK
@app.post("/stk-push")
def stk_push(payment:PaymentRequest):
    consumer_key = os.getenv("DARAJA_CONSUMER_KEY")
    consumer_secret = os.getenv("DARAJA_CONSUMER_SECRET")
    shortcode = os.getenv("DARAJA_SHORTCODE")
    passkey = os.getenv("DARAJA_PASSKEY")
    callback_url = os.getenv("DARAJA_CALLBACK_URL")

    if not all([
        consumer_key,
        consumer_secret,
        shortcode,
        passkey,
        callback_url,
    ]):
        raise HTTPException(
            status_code=500,
            detail="Daraja configuration is incomplete"
        )

    # Step 1: Get an OAuth token
    token_url = (
        f"{BASE_URL}/oauth/v1/generate"
        "?grant_type=client_credentials"
    )

    try:
        token_response=requests.get(
            token_url,
            auth=(consumer_key, consumer_secret),
            timeout=20
        )

        token_response.raise_for_status()
        access_token=token_response.json()["access_token"]

    except (requests.RequestException, KeyError):
        raise HTTPException(
            status_code=502,
            detail="Daraja authentication failed"
        )

    # Step 2: Create the timestamp in Kenya's timezone
    timestamp=datetime.now(
        ZoneInfo("Africa/Nairobi")
    ).strftime("%Y%m%d%H%M%S")

    #Step 3: Generate the STK push password
    password_string=f"{shortcode}{passkey}{timestamp}"
    # sending over the internet we encode strings
    password = base64.b64encode(
        password_string.encode("utf-8")
    ).decode("utf-8")

    # Step 4: Prepare the request
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": payment.amount,
        "PartyA": payment.phone,
        "PartyB": shortcode,
        "PhoneNumber": payment.phone,
        "CallBackURL": callback_url,
        "AccountReference": payment.reference,
        "TransactionDesc": "Order payment"
    }

    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # step 5: Send the STK push request to Safaricom
    try:
        response=requests.post(
            f"{BASE_URL}/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    except requests.HTTPError as exc:
        # Log details privately when debugging; don't expose
        # Credentials or sensitive request headers
        raise HTTPException(
            status_code=502,
            detail="Daraja rejected the STK push request"
        )from exc

    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not reach Daraja"
        )from exc


@app.post("/api/mpesa/callback")
async def mpesa_callback(request: Request):
    # Read the raw request body
    raw_body = await request.body()

    if not raw_body:
        print("Callback error: request body is empty")
        raise HTTPException(
            status_code=400,
            detail="Callback request body is empty"
        )

    # Parse the JSON body
    try:
        callback_data = await request.json()
    except ValueError:
        print(
            "Callback error: invalid JSON",
            "Content-Type:", request.headers.get("content-type"),
            "Body length:", len(raw_body)
        )
        raise HTTPException(
            status_code=400,
            detail="Request body must contain valid JSON"
        )

    # Extract the M-PESA callback
    body = callback_data.get("Body", {})
    stk_callback = body.get("stkCallback", {})

    # Log only the structure for debugging
    print("Callback top-level keys:", list(callback_data.keys()))
    print("STK callback keys:", list(stk_callback.keys()))

    result_code = stk_callback.get("ResultCode")
    checkout_id = stk_callback.get("CheckoutRequestID")

    if result_code is None or not checkout_id:
        print("Callback error: expected fields are missing")
        raise HTTPException(
            status_code=400,
            detail="Invalid M-PESA callback payload"
        )

    if result_code == 0:
        print("Callback reports successful payment:", checkout_id)
        return {
            "received": True,
            "checkout_request_id": checkout_id,
            "message": "Successful callback received"
        }

    print("Callback reports unsuccessful payment:", checkout_id)

    return {
        "received": True,
        "checkout_request_id": checkout_id,
        "result_code": result_code,
        "message": "Unsuccessful callback received"
    }

# start our server
if __name__=="__main__":
    #start our server
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
