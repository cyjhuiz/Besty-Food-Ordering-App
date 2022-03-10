from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import boto3
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{prcoess.env.DB_USERNAME}:{prcoess.env.DB_PASSWORD}@{prcoess.env.DB_ENDPOINT_URL}/food'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

CORS(app)

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

class Food(db.Model):
    __tablename__ = 'food'

    FoodId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FoodName = db.Column(db.String(20))
    FoodPrice = db.Column(db.Float(precision=2), nullable=False)
    FoodCategory = db.Column(db.String(20), nullable=False)
    FoodImgUrl = db.Column(db.String(20), nullable=False)
    FoodAvailability = db.Column(db.String(20), nullable=False)

    def __init__(self, FoodId, FoodName, FoodPrice, FoodCategory, FoodImgUrl, FoodAvailability):
        self.FoodId = FoodId
        self.FoodName = FoodName
        self.FoodPrice = FoodPrice
        self.FoodCategory = FoodCategory
        self.FoodImgUrl = FoodImgUrl
        self.FoodAvailability = FoodAvailability

    def json(self):
        return {
            "FoodId": self.FoodId,
            "FoodName": self.FoodName,
            "FoodPrice": self.FoodPrice,
            "FoodCategory": self.FoodCategory, 
            "FoodImgUrl": self.FoodImgUrl,
            "FoodAvailability": self.FoodAvailability
            }

s3_client = boto3.client(
    's3', 
    aws_access_key_id=prcoess.env.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=prcoess.env.AWS_SECRET_KEY_ID
    )


@app.route("/food")
def get_all():
    food_list = Food.query.all()
    if len(food_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "food": [food.json() for food in food_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no food in the database."
        }
    ), 404


@app.route("/food/<string:FoodId>")
def find_by_food_id(FoodId):
    food = Food.query.filter_by(FoodId=FoodId).first()
    if food:
        return jsonify(
            {
                "code": 200,
                "data": food.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Food not found."
        }
    ), 404


@app.route("/food", methods=['POST'])
def create_food():
    data = request.form

    if (Food.query.filter_by(FoodName=data["FoodName"]).first()):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "FoodName": data["FoodName"]
                },
                "message": "Food already exists."
            }
        ), 400

    try:
        
        file = request.files["FoodImg"]

        last_food_id = Food.query.all()[-1].FoodId
        new_food_id = last_food_id + 1 if last_food_id != None else 1

        img_extension = file.filename.split(".")[1]
        img_filename = str(new_food_id) + "." + datetime.now().strftime("%Y-%m-%d.%H:%M:%S") + "." + img_extension

        # upload img to s3 bucket
        s3_client.upload_fileobj(file, Bucket='betsy-food-img', Key=img_filename, ExtraArgs={'ACL': 'public-read', 'ContentType': file.content_type})
        
        food = Food(
            FoodId=new_food_id,
            FoodName=data["FoodName"],
            FoodPrice=data["FoodPrice"],
            FoodCategory=data["FoodCategory"], 
            FoodImgUrl=f"{prcoess.env.S3_URL_ENDPOINT}/{img_filename}",
            FoodAvailability= data["FoodAvailability"]
        )

        db.session.add(food)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "FoodName": data["FoodName"]
                },
                "message": "An error occurred creating the food."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": food.json()
        }
    ), 201


@app.route("/food/<string:FoodId>", methods=['PUT'])
def update_food(FoodId):
    food = Food.query.filter_by(FoodId=FoodId).first()
    if food:

        # if request is called by cancel_order api which input is json
        if request.is_json:
            data = request.get_json()
            food.FoodAvailability = data["FoodAvailability"]            
    
        # if request is called by food management system
        else:
            data = request.form
            if "FoodName" in data.keys():
                if (Food.query.filter_by(FoodName=data["FoodName"]).first()):
                    return jsonify(
                        {
                            "code": 400,
                            "data": {
                                "FoodName": data["FoodName"]
                            },
                            "message": "Food already exists."
                        }
                    ), 400

                else:
                    food.FoodName = data["FoodName"]

            if "FoodPrice" in data.keys():
                food.FoodPrice = data["FoodPrice"]
            
            if "FoodImg" in request.files.keys():
                file = request.files["FoodImg"]

                img_filename = food.FoodImgUrl[food.FoodImgUrl.rfind("/") + 1:]
                s3_client.delete_object(Bucket='betsy-food-img', Key=img_filename)
                # updating image filename with new timestamp
                img_filename = img_filename.split(".")
                img_filename = img_filename[0] + "." + datetime.now().strftime("%Y-%m-%d.%H:%M:%S") + "." + img_filename[-1]

                # upload img to s3 bucket
                s3_client.upload_fileobj(file, Bucket='betsy-food-img', Key=img_filename, ExtraArgs={'ACL': 'public-read', 'ContentType': file.content_type})
                food.FoodImgUrl = f"https://betsy-food-img.s3.amazonaws.com/{img_filename}"

            if "FoodAvailability" in data.keys():
                food.FoodAvailability = data["FoodAvailability"]

        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": food.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "FoodId": FoodId
            },
            "message": "FoodId not found."
        }
    ), 404


@app.route("/food/<string:FoodId>", methods=['DELETE'])
def delete_food(FoodId):
    food = Food.query.filter_by(FoodId=FoodId).first()
    if food:
        s3_client.delete_object(Bucket='betsy-food-img', Key=food.FoodImgUrl[food.FoodImgUrl.rfind("/") + 1:])
        db.session.delete(food)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": {
                    "FoodId": FoodId
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "FoodId": FoodId
            },
            "message": "FoodId not found."
        }
    ), 404


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": food service")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5001)), debug=True)