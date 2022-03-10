from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import threading
import requests
import json
from time import sleep
from datetime import datetime, timedelta
from invokes import invoke_http

import amqp_setup
import pika
import json


order_URL = os.environ.get('order_URL') or 'localhost:5003/order'

payment_URL = os.environ.get('payment_URL') or 'localhost:5005/payment'


def check_stripe_payment_success(stripe_payment_json):
    user = stripe_payment_json["user"]
    OrderId = stripe_payment_json["OrderId"]
    clientSecret = stripe_payment_json["clientSecret"]

    current_time = datetime.now()
    max_time_limit = datetime.now() + timedelta(minutes = 3)
    payment_success = False

    print('\n-----Invoking Payment microservice for Checking Payment Status-----')

    while current_time <= max_time_limit and not(payment_success):
        payment_success_result = invoke_http(
            f"{payment_URL}/checkPaymentStatus", 
            method='POST',
            json={
                "PaymentId": clientSecret
            }
            )
        sleep(15)
        current_time = datetime.now()

        payment_success = (payment_success_result["code"] == 200)

    if not(payment_success):
        print('\n-----Invoking Order microservice-----')
        order_result = invoke_http(order_URL + f"/{OrderId}", method='PUT', json={"OrderStatus": "Payment Failed"})
        print('order_result:', order_result)

        return jsonify({
            "code": 400,
            "message": "Payment for order failed. Please try again"
        }), 400
    
    else:
        print('\n-----Invoking Order microservice-----')
        order_result = invoke_http(order_URL + f"/{OrderId}", method='PUT', json={"OrderStatus": "Preparing"})
        print('order_result:', order_result)


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
        "code": 200,
        "message": f"The status of Order #{OrderId} has been confirmed and sent to the customer."
    }
 

    




