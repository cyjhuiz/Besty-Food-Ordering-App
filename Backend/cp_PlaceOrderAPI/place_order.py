from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
import threading
import time
import requests
from datetime import datetime, timedelta

import amqp_setup
import pika

import json

from invokes import invoke_http
from check_stripe_payment_success import check_stripe_payment_success

app = Flask(__name__)
CORS(app)
# initialize all endpoints
food_URL = os.environ.get('food_URL') or 'localhost:5001/food'
user_URL = os.environ.get('user_URL') or 'localhost:5002/user'
order_URL = os.environ.get('order_URL') or 'localhost:5003/order'
credit_URL = os.environ.get('credit_URL') or 'localhost:5004/credit'
payment_URL = os.environ.get('payment_URL') or 'localhost:5005/payment'

payment_URL_dict = {
    "Stripe": f"{payment_URL}/create-payment-intent", 
    "TBank": f"{payment_URL}/payOrder_tBank"
    } 


@app.route("/place_order", methods=['POST'])
def place_order():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            order_json = request.get_json()
            print("\nReceived an order in JSON:", order_json)


            # 1. Send order info {cart items}
            result = processPlaceOrder(order_json)
            return jsonify(result), 201

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "place_order.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

# input variable is payment type
def processPlaceOrder(order_json):
    
    UserId = order_json["UserId"]
    PaymentType = order_json["PaymentType"]
    
    print('\n-----Invoking Credit microservice for Deducting Credit-----')
    deduct_credit_result = invoke_http(
        credit_URL + f"/remove", 
        method='POST',
        json={
            "UserId": UserId
        }
        )
    print('deduct_credit_result:', deduct_credit_result)

    average_discount_per_item = 0
    num_items = 0
    for order in order_json["orders"]:
        num_items += int(order["ItemQuantity"])
    if "UserCredits" in deduct_credit_result["data"].keys():
        average_discount_per_item = round(deduct_credit_result["data"]["UserCredits"]/num_items,2)
    
    for order in order_json["orders"]:
        order["NetItemPrice"] = order["ItemPrice"] - average_discount_per_item
    
    print('\n-----Invoking Order microservice-----')
    order_result = invoke_http(order_URL, method='POST', json=order_json)
    OrderId = order_result["data"]["orders"][0]["OrderId"]
    print('order_result:', order_result)
    

    # === Get User Details ===
    print('\n-----Invoking user microservice-----')
    user_result = invoke_http(user_URL + f"/{UserId}", method='GET', json=None)
    user = user_result["data"]
    print('user_result:', user_result)


    print('\n-----Invoking Payment microservice-----')
    OrderAmt = 0

    orders = order_result["data"]["orders"]
    for order in orders:
        OrderAmt += (order["NetItemPrice"] * order["ItemQuantity"])

    payment_json_dict = {
        "TBank": {
            "UserAccId": user["UserAccId"],
            "UserTBankId": user["UserTBankId"], 
            "UserPin": user["UserPin"], 
            "OrderAmt": OrderAmt,
            "UserMobile":user["UserMobile"]
        },
        "Stripe": {
            "amt": OrderAmt * 100
        }
    }
    payment_result = invoke_http(
        payment_URL_dict[f"{PaymentType}"], 
        method='POST', 
        json=payment_json_dict[f"{PaymentType}"]
        )
    print('payment_result:', payment_result)

    if PaymentType == "Stripe":
        # run async function
        stripe_payment_json = {
            "clientSecret": payment_result,
            "user": user,
            "OrderId": OrderId
        }
        check_payment = threading.Thread(target=check_stripe_payment_success, args=(stripe_payment_json,))
        check_payment.start()
        return payment_result

    print('\n-----Invoking Order microservice-----')
    order_result = invoke_http(order_URL + f"/{OrderId}", method='PUT', json={"OrderStatus": "Preparing"})
    orders = order_result["data"]["orders"]
    print('order_result:', order_result)



    print('\n-----Invoking Credit microservice for Adding Credit-----')
    credit_bonus_rate = 0.10
    add_credit_amount = OrderAmt * credit_bonus_rate
    add_credit_result = invoke_http(
        credit_URL + f"/add", 
        method='POST', 
        json={
            "UserId": UserId, 
            "UserCredits": add_credit_amount,
            }
        )
    print('add_credit_result:', add_credit_result)

    UserFirstName = user["UserFirstName"]
    notification_message_json = json.dumps({
            "UserMobile": user["UserMobile"],
            "message": f"Hey {UserFirstName}, Your order has been placed. We will notify you once the order can be collected. Regards, Team Betsy",
            "UserEmail": user["UserEmail"],
            "EmailSubject": f"Your order #{OrderId} has been confirmed",
            "EmailContent": f"Hey {UserFirstName}, Your order has been placed. We will notify you once the order can be collected. Regards, Team Betsy"
        })

    print('\n\n-----Publishing the (place_order notification) message with routing_key=place_order.notify-----')
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="place_order.notify", 
    body=notification_message_json, properties=pika.BasicProperties(delivery_mode = 2)) 


    return {
        "code": 201,
        "data": {
            "orders": [ order for order in orders]
        },
        "message": f"The status of Order #{OrderId} has been confirmed and sent to the customer."
    }


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for placing an order...")
    app.run(host="0.0.0.0", port=5102, debug=True)
    # Check AMQP Settings
    amqp_setup.check_setup()

    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program,
    #       and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.
