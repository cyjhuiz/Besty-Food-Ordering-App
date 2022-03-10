import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{prcoess.env.DB_USERNAME}:{prcoess.env.DB_PASSWORD}@{prcoess.env.DB_ENDPOINT_URL}/order'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost/order' # === CHANGE BEFORE DEPLOY ===
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)
CORS(app)

class Order(db.Model):
    __tablename__ = 'order'

    OrderId = db.Column(db.Integer, primary_key=True)
    FoodId = db.Column(db.Integer, primary_key=True)
    OrderItem = db.Column(db.String(20), nullable=False)
    ItemPrice = db.Column(db.Float, nullable=False)
    NetItemPrice = db.Column(db.Float, nullable=False)
    ItemQuantity = db.Column(db.Integer)
    OrderDate = db.Column(db.DateTime, nullable=False, default=datetime.now)
    UserId = db.Column(db.Integer, nullable=False)
    OrderStatus = db.Column(db.String(20), nullable=False)

    def __init__(self, OrderId, FoodId, OrderItem, ItemPrice, NetItemPrice, ItemQuantity, UserId):
        self.OrderId = OrderId
        self.FoodId = FoodId
        self.OrderItem = OrderItem
        self.ItemPrice = ItemPrice
        self.NetItemPrice = NetItemPrice
        self.ItemQuantity = ItemQuantity
        self.OrderDate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.UserId = UserId
        self.OrderStatus = "Pending"

    def json(self):
        return {
            'OrderId': self.OrderId,
            'FoodId': self.FoodId,
            'OrderItem': self.OrderItem,
            'ItemPrice': self.ItemPrice,
            'NetItemPrice': self.NetItemPrice,
            'ItemQuantity': self.ItemQuantity,
            'OrderDate': self.OrderDate,
            'UserId': self.UserId,
            'OrderStatus': self.OrderStatus
        }



@app.route("/order")
def get_all():
    if request.args.get("OrderStatus") and request.args.get("FoodId"):
        OrderStatus = request.args.get("OrderStatus", type=str)
        FoodId = request.args.get("FoodId", type=int)
        order_list = Order.query.filter_by(OrderStatus=OrderStatus, FoodId=FoodId)

    elif request.args.get("OrderStatus"):
        OrderStatus = request.args.get("OrderStatus", type=str)
        order_list = Order.query.filter_by(OrderStatus=OrderStatus)

    else:
        order_list = Order.query.all()

    if order_list or len(order_list) != 0:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "orders": [order.json() for order in order_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no orders."
        }
    ), 404


@app.route("/order/<string:OrderId>")
def get_order_by_id(OrderId):
    order_list = Order.query.filter_by(OrderId=OrderId)
    if order_list.first() == None:
        return jsonify(
            {
                "code": 404,
                "data": {
                    "OrderId": OrderId
                },
                "message": "Order not found."
            }
        ), 404

    return jsonify(
            {
                "code": 200,
                "data":{
                    "orders": [order.json() for order in order_list]
                }
            }
        )

@app.route("/order/<string:OrderId>/<string:FoodId>")
def get_order_item_by_id(OrderId, FoodId):
    order_item = Order.query.filter_by(OrderId=OrderId, FoodId=FoodId).first()
    if order_item == None:
        return jsonify(
            {
                "code": 404,
                "data": {
                    "OrderId": OrderId,
                    "FoodId": FoodId
                },
                "message": "Order not found."
            }
        ), 404

    return jsonify(
            {
                "code": 200,
                "data":{
                    "orders": [order_item.json()]
                }
            }
        )



@app.route("/order", methods=['POST'])
def create_order():
    data = request.get_json()
    last_order_id = Order.query.all()[-1].OrderId
    new_order_id = last_order_id + 1 if last_order_id != None else 1

    order_list = data["orders"]
    UserId = data["UserId"]

    order_objects_created = []
    for order in order_list:
        try:
            order = Order(
                OrderId=new_order_id, 
                FoodId=order["FoodId"], 
                OrderItem=order["OrderItem"], 
                ItemPrice=order["ItemPrice"],
                NetItemPrice=order["NetItemPrice"],
                ItemQuantity=order["ItemQuantity"],
                UserId=data["UserId"]
                )

            db.session.add(order)
            db.session.commit()
            order_objects_created.append(order)

        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "data": {
                        "OrderId": new_order_id
                    },
                    "message": "An error occurred while creating the order. " + str(e)
                }
            ), 500

    return jsonify(
        {
            "code": 201,
            "data": { 
                "orders": [order.json() for order in order_objects_created]
            }
        }
    ), 201

@app.route("/order/<string:OrderId>", methods=['PUT'])
def update_order(OrderId):
    order_list = Order.query.filter_by(OrderId=OrderId)

    if order_list.first() == None:
        return jsonify(
                {
                    "code": 404,
                    "data": {
                        "OrderId": OrderId
                    },
                    "message": "Order not found."
                }
            ), 404

    else: 
        data = request.get_json()

        if 'OrderStatus' in data.keys():

            for order in order_list:
                order.OrderStatus = data['OrderStatus']

        db.session.commit()
        return jsonify(
           {
            "code": 200,
            "data": {
                "orders": [order.json() for order in order_list]
            }
           }
        ), 200


@app.route("/order/<string:OrderId>/<string:FoodId>", methods=['PUT'])
def update_order_item(OrderId, FoodId):
    order_item = Order.query.filter_by(OrderId=OrderId, FoodId=FoodId).first()

    if order_item == None:
        return jsonify(
                {
                    "code": 404,
                    "data": {
                        "OrderId": OrderId,
                        "FoodId": FoodId
                    },
                    "message": "Order Item not found."
                }
            ), 404

    else: 
        data = request.get_json()

        if 'OrderStatus' in data.keys():
            order_item.OrderStatus = data['OrderStatus']

        db.session.commit()
        return jsonify(
           {
            "code": 200,
            "data": {
                "orders": [order_item.json()]
            }
           }
        ), 200

@app.route("/order/<string:OrderId>", methods=['DELETE'])
def delete_order(OrderId):
        order_list = Order.query.filter_by(OrderId=OrderId)
        if order_list.first() == None:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "OrderId": OrderId
                    },
                    "message": "Order Item not found."
                }
            ), 404

        for order in order_list:
            try:
                db.session.delete(order)
                db.session.commit()

            except Exception as e:
                return jsonify(
                    {
                        "code": 500,
                        "data": {
                            "OrderId": OrderId
                        },
                        "message": "An error occurred while deleting the order. " + str(e)
                    }
                ), 500


        return jsonify(
            {
                "code": 200,
                "data": {
                    "OrderId": OrderId
                },
                "message": "The order has been successfully deleted."
            }
        ),200
    

@app.route("/order/<string:OrderId>/<string:FoodId>", methods=['DELETE'])
def delete_order_item(OrderId, FoodId):
        order_item = Order.query.filter_by(OrderId=OrderId, FoodId=FoodId).first()
        if order_item == None:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "OrderId": OrderId,
                        "FoodId": FoodId
                    },
                    "message": "Order Item not found."
                }
            ), 404


        try:
            db.session.delete(order_item)
            db.session.commit()

        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "data": {
                        "OrderId": OrderId
                    },
                    "message": "An error occurred while deleting the order. " + str(e)
                }
            ), 500


        return jsonify(
            {
                "code": 200,
                "data": {
                    "OrderId": OrderId
                },
                "message": "The order item has been successfully deleted."
            }
        ),200
    

if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage orders ...")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5003)), debug=True)
     
     
