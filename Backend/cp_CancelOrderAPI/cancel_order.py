from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import amqp_setup
import pika
import json

import requests
from invokes import invoke_http

app = Flask(__name__)
CORS(app)
# initialize all endpoints
food_URL = os.environ.get('food_URL') or 'localhost:5001/food'
user_URL = os.environ.get('user_URL') or 'localhost:5002/user'
order_URL = os.environ.get('order_URL') or 'localhost:5003/order'
credit_URL = os.environ.get('credit_URL') or 'localhost:5004/credit'
payment_URL = os.environ.get('payment_URL') or 'localhost:5005/payment'
                                                                               

# Expected input {"OrderId": OrderId, "FoodId: FoodId"} relating to order to be cancelled
@app.route("/cancel_order", methods=['POST'])
def cancel_order():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        
        order_json = request.get_json()
        OrderId = order_json["OrderId"]
        FoodId = order_json["FoodId"]

        try:
            print("\nReceived an order cancellation:", order_json)

            # send order details
            result = process_cancel_order(order_json) 
            return jsonify(result), 200

            
        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "cancel_order.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400



# Expected input {"FoodId": FoodId } relating to order to be cancelled
@app.route("/cancel_order/FoodAvailability", methods=['POST'])
def cancel_order_by_food_availability():
    # Simple check of input format and data of the request are JSON
    if request.is_json:

        food_id_json = order_json = request.get_json()
        FoodId = food_id_json["FoodId"]
        food_result = invoke_http(food_URL + f"/{FoodId}", method='PUT', json={"FoodAvailability": "Unavailable"})
        is_unavailable = (food_result['code'] == 200)
        print('food_result:', food_result)


        if is_unavailable:
            # Find all orders with OrderStatus=Prepared and FoodId=Relevant FoodId
            OrderStatus = "Preparing"
            order_result = invoke_http(order_URL + f"?OrderStatus={OrderStatus}&FoodId={FoodId}", method='GET')
            orders = order_result["data"]["orders"]
            print('order_result:', order_result)

            final_result = {
                "orders": []
            }

            for order in orders:
                # remove UserId for cancel order
                OrderId = order["OrderId"]
                FoodId = order["FoodId"]

                order_json = {
                    "OrderId": OrderId,
                    "FoodId": FoodId,
                }

                try:
                    print("\nReceived an order cancellation:", order_json)

                    # cancel the single affected order and add the necessary deatils to the final_result varaible
                    result = process_cancel_order(order_json) 
                    order = result["data"]
                    final_result["orders"].append(order)

                    
                except Exception as e:
                    # Unexpected error in code
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
                    print(ex_str)

                    return jsonify({
                        "code": 500,
                        "message": "cancel_order.py internal error: " + ex_str
                    }), 500

            return jsonify({
                "code": 200,
                "data": final_result,
                "message": f"The cancellation of all orders for Food #{FoodId} has been processed and refunded successfully"
            }), 200

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400



def process_cancel_order(order_json):
    

    # Invoke the order microservice
    print('\n-----Invoking order microservice-----')
    OrderId = order_json["OrderId"]
    FoodId = order_json["FoodId"]
    

    # Change order status from Processing to Cancelled
    order_result = invoke_http(order_URL + f"/{OrderId}/{FoodId}", method='PUT', json={"OrderStatus": "Cancelled"})
    orders = order_result["data"]["orders"]
    print('order_result:', order_result)



    # Get total order_amount of all order items for future invocation via Payment Service
    # Get TotalCreditsToBeRefunded for future invocation via Credit Service
    OrderAmt = 0
    TotalCreditsToBeRefunded = 0
    for order in orders:
       OrderAmt += (order["NetItemPrice"] * order["ItemQuantity"])
       TotalCreditsToBeRefunded += (order["ItemPrice"] - order["NetItemPrice"]) * order["ItemQuantity"]

    # Get user details for payment and notification
        # Get UserId from order details
    UserId = orders[0]["UserId"]
    print('\n-----Invoking user microservice-----')
    user_result = invoke_http(user_URL + f"/{UserId}", method='GET', json=None)
    user = user_result["data"]
    print('user_result:', user_result)


    # Invoke Payment microservice to start Refund
    print('\n-----Invoking payments microservice-----')
    payment_result = invoke_http(
        payment_URL +f"/refundPayment", 
        method='POST',
        json={
            "OrderId": OrderId, 
            "OrderAmt": OrderAmt, 
            "UserTBankId": user["UserTBankId"],
            "UserMobile": user["UserMobile"],
            })
    print('payment_result:', payment_result)



    # === Check Payment Status ===
    # If payment fails, return error
    payment_status = payment_result["Content"]["ServiceResponse"]["ServiceRespHeader"]["ErrorText"]
    if  payment_status != "invocation successful":
        return {
            "code": 500,
            "data": {payment_status},
            "message": f"Payment failed. {payment_status}"
        }


    # Remove credits gained from creating the order
    print('\n-----Invoking credit microservice-----')
    Cancelled = orders[0]["OrderStatus"]
    credit_result = invoke_http(
        credit_URL + f"/add", 
        method='POST',
        json={
            "UserId": UserId,
            "UserCredits": TotalCreditsToBeRefunded
            }
        )
    print('credit_result:', credit_result)


    UserFirstName = user["UserFirstName"]
    notification_message_json = json.dumps({
            "UserMobile": user["UserMobile"],
            "message": f"Hey {UserFirstName}, Your order has been placed. We will notify you once the order can be collected. Regards, Team Betsy",
            "UserEmail": user["UserEmail"],
            "EmailSubject": f"Your order #{OrderId} has been confirmed",
            "EmailContent": f"Hey {UserFirstName}, Your order has been placed. We will notify you once the order can be collected. Regards, Team Betsy"
        })

    print('\n\n-----Publishing the (place_order notification) message with routing_key=cancel_order.notify-----')
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="cancel_order.notify", 
    body=notification_message_json, properties=pika.BasicProperties(delivery_mode = 2)) 

    return {
        "code": 200,
        "data": orders[0],
        "message": f"Order #{OrderId} has been cancelled and refunded successfully."
    }





# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for cancelling an order...")
    app.run(host="0.0.0.0", port=5101, debug=True)
    
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
