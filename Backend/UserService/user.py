from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{prcoess.env.DB_USERNAME}:{prcoess.env.DB_PASSWORD}@{prcoess.env.DB_ENDPOINT_URL}/user'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

cors = CORS(app)

class User(db.Model):
    __tablename__ = 'user'

    UserId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserEmail = db.Column(db.String(40), nullable=False)
    UserPassword = db.Column(db.String(20), nullable=False)
    UserFirstName = db.Column(db.String(20), nullable=False)
    UserLastName = db.Column(db.String(20), nullable=False)
    UserMobile = db.Column(db.String(10), nullable=False)
    UserTBankId = db.Column(db.String(20), nullable= True)
    UserAccId = db.Column(db.String(20), nullable= True)
    UserPin = db.Column(db.String(20), nullable= True)

    def __init__(self, UserId, UserEmail, UserPassword, UserFirstName, UserLastName, UserMobile, UserTBankId, UserAccId, UserPin):
        self.UserId = UserId
        self.UserEmail = UserEmail
        self.UserPassword = UserPassword
        self.UserFirstName = UserFirstName
        self.UserLastName = UserLastName
        self.UserMobile = UserMobile
        self.UserTBankId = UserTBankId
        self.UserAccId = UserAccId
        self.UserPin = UserPin

    def json(self):
        return {
            "UserId": self.UserId,
            "UserEmail": self.UserEmail, 
            "UserFirstName": self.UserFirstName,
            "UserLastName": self.UserLastName,
            "UserPassword": self.UserPassword, 
            "UserMobile": self.UserMobile,
            "UserTBankId": self.UserTBankId,
            "UserAccId": self.UserAccId,
            "UserPin": self.UserPin
            }


@app.route("/user")
def get_all():
    user_list = User.query.all()
    if len(user_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "users": [user.json() for user in user_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no users."
        }
    ), 404


@app.route("/user/<string:UserId>")
def find_by_user_id(UserId):
    user = User.query.filter_by(UserId=UserId).first()
    if user:
        return jsonify(
            {
                "code": 200,
                "data": user.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "User not found."
        }
    ), 404

@app.route("/user/email/<string:UserEmail>")
def find_by_user_email(UserEmail):
    user = User.query.filter_by(UserEmail=UserEmail).first()
    if user:
        return jsonify(
            {
                "code": 200,
                "data": user.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "User not found."
        }
    ), 404

# rmbr to change from userId to Username in architecture diagram
@app.route("/user", methods=['POST'])
def create_user():
    data = request.get_json()
    #print("DATA HERE", request.get_json())
    user = User(UserId = None, **data)

    UserEmail = data["UserEmail"]
    if (User.query.filter_by(UserEmail=UserEmail).first()):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "UserEmail": UserEmail
                },
                "message": "Email already exists."
            }
        ), 400


    try:
        db.session.add(user)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "UserEmail": UserEmail
                },
                "message": "An error occurred creating the user."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": user.json()
        }
    ), 201


@app.route("/user/<string:UserId>", methods=['PUT'])
def update_user(UserId):
    user = User.query.filter_by(UserId=UserId).first()
    if user:
        data = request.get_json()

        if "UserEmail" in data.keys():
            UserEmail = data["UserEmail"]
            if (User.query.filter_by(UserEmail=UserEmail).first()):
                return jsonify(
                    {
                        "code": 400,
                        "data": {
                            "UserEmail": UserEmail
                        },
                        "message": "Email already exists."
                    }
                ), 400

            user.UserEmail = data["UserEmail"]

        if "UserPassword" in data.keys():
            user.UserPassword = data["UserPassword"]
        
        if "UserFirstName" in data.keys():
            user.UserFirstName = data["UserFirstName"]

        if "UserLastName" in data.keys():
            user.UserLastName = data["UserLastName"]
            
        if "UserMobile" in data.keys():
            user.UserMobile = data["UserMobile"]

        if "UserTBankId" in data.keys():
            user.UserTBankId = data["UserTBankId"]

        if "UserAccId" in data.keys():
            user.UserAccId = data["UserAccId"]

        if "UserPin" in data.keys():
            user.UserPin = data["UserPin"]

        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": user.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "UserId": UserId
            },
            "message": "UserId not found."
        }
    ), 404


@app.route("/user/<string:UserId>", methods=['DELETE'])
def delete_user(UserId):
    user = User.query.filter_by(UserId=UserId).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": {
                    "UserId": UserId
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "UserId": UserId
            },
            "message": "UserId not found."
        }
    ), 404


if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 5002)), debug=True, host='0.0.0.0')
