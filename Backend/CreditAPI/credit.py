import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{prcoess.env.DB_USERNAME}:{prcoess.env.DB_PASSWORD}@{prcoess.env.DB_ENDPOINT_URL}/credit'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)
CORS(app)


class Credit(db.Model):
    __tablename__ = 'credit'

    UserId = db.Column(db.Integer, primary_key=True)
    UserCredits = db.Column(db.Float, nullable=False)
    PointsDatetime = db.Column(db.DateTime, nullable=False, primary_key=True)

    def __init__(self, UserId, UserCredits):
        self.UserId = UserId
        self.UserCredits = UserCredits
        self.PointsDatetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def json(self):
        return {
            'UserId': self.UserId,
            'UserCredits': self.UserCredits,
            'PointsDatetime': self.PointsDatetime
        }


@app.route("/credit")
def get_all():
    credit_list = Credit.query.all()
    if len(credit_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "credit": [credit.json() for credit in credit_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no credit records."
        }
    ), 404


@app.route("/credit/<string:UserId>")
def get_credit(UserId):
    credit_list = Credit.query.filter_by(UserId=UserId)
    if credit_list:
        return jsonify(
            {
                "code": 200,
                "data": [credit.json() for credit in credit_list]
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "UserId": UserId
            },
            "message": "Credits not found."
        }
    ), 404


@app.route("/credit/add", methods=['POST'])
def add_credit():
    data = request.get_json()
    UserId = data["UserId"]
    
    credit = Credit(UserId=UserId, UserCredits=data["UserCredits"])

    try:
        db.session.add(credit)
        db.session.commit()

    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "UserId": UserId
                },
                "message": "An error occurred adding the credit record."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": credit.json()
        }
    ), 201


@app.route("/credit/remove", methods=['POST'])
def remove_credit():
    data = request.get_json()
    UserId = data["UserId"]
    credit_list = Credit.query.filter_by(UserId=UserId)

    UserQueryCredits = 0
    credit_from_most_recent_order = credit_list[-1].UserCredits
    if credit_from_most_recent_order != None:
        UserQueryCredits = credit_from_most_recent_order
    else:
        return jsonify(
            {
                "code": 404,
                "data": {
                    "UserId": UserId
                },
                "message": "UserId does not have sufficient credits to deduct."
            }
        ), 404

    credit = Credit(UserId=UserId, UserCredits=0)
    db.session.add(credit)
    db.session.commit()
    return jsonify(
        {
            "code": 200,
            "data": {
                "UserId": UserId,
                "UserCredits": UserQueryCredits
            },
            "message": str(UserQueryCredits) + " credits have been deducted successfully."
        }
    ), 200


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) +
          ": managing a user's credits")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5004)), debug=True)
