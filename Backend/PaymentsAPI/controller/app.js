const express = require('express');
const app = express();
const PaynowQR = require('paynowqr');
const stripe = require("stripe")(prcoess.env.STRIPE_API_KEY);

//const database = require('./Database_Config.js');

const bodyParser = require('body-parser');
var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;

const cors = require('cors');
const {
  response
} = require('express');

app.use(bodyParser.urlencoded({
  extended: false
}));
app.use(bodyParser.json());

app.options('*', cors());
app.use(cors());

app.post("/payment/create-payment-intent", async (req, res) => {
  const requestBody = req.body;
  console.log(requestBody.amt)
  // Create a PaymentIntent with the order amount and currency
  const paymentIntent = await stripe.paymentIntents.create({
    amount: requestBody.amt,
    currency: "sgd"
  });

  res.send({
    clientSecret: paymentIntent.client_secret
  });
});

//Check for Stripe Payment Information
app.post("/payment/checkPaymentStatus", async (req, res) => {
  const requestBody = req.body;
  const paymentIntent = await stripe.paymentIntents.retrieve(requestBody.PaymentId);
  res.send(paymentIntent);
})

//generatePaynow
//Parameters required:
//OrderAmt; OrderId
//Type: x-form-urlencoded
app.post('/payment/generatePaynow', (request, response, next) => {

  const requestBody = request.body;
  console.log(requestBody)
  //Create a PaynowQR object
  let qrcode = new PaynowQR({
    uen: prcoess.env.COMPANY_UEN, //Required: UEN of company
    amount: requestBody.OrderAmt, //Specify amount of money to pay.
    editable: true, //Whether or not to allow editing of payment amount. Defaults to false if amount is specified
    expiry: '20210501', //Set an expiry date for the Paynow QR code (YYYYMMDD). If ommitted, defaults to 5 years from now.
    refNumber: requestBody.OrderId, //Reference number for Paynow Transaction. Useful if you need to track payments for recouncilation.
    company: prcoess.env.COMPANY_NAME //Company name to embed in the QR code. Optional.               
  });

  //Outputs the qrcode to a UTF-8 string format, which can be passed to a QR code generation script to generate the paynow QR
  response.status(200).send(JSON.parse("{\"result\":\"" + qrcode.output() + "\"}"));
})

//Invoke Payment on tBank to Merchant
//Parameters required:
//UserAccId (tbank); UserPin(tbank); UserTBankId (tbank); OrderAmt(App Payment amount)
//Type: x-form-urlencoded
app.post('/payment/payOrder_tBank', (request, response, next) => {
  //console.log("--payOrder_tBank is called--")
  const requestBody = request.body;
  var requestHeader = {
    "Header": {
      "serviceName": "creditTransfer",
      "userID": requestBody.UserAccId,
      "PIN": requestBody.UserPin,
      "OTP": requestBody.OTP,
    }
  }
  //console.log(requestHeader)
  var dt = new Date();
  dt.setHours(dt.getHours() + 8);

  //console.log(dt.toISOString().slice(0, 10))
  var requestContent = {
    'Content': {
      'accountFrom': requestBody.UserTBankId,
      'accountTo': prcoess.env.COMPANY_BANK_ACCOUNT,
      'transactionAmount': requestBody.OrderAmt,
      'transactionReferenceNumber': `Payment Transaction`,
      'narrative': 'KIM JONG UN - SGD' + requestBody.OrderAmt + ' @ ' + dt.toISOString().slice(0, 10)
    }
  }

  var header = JSON.stringify(requestHeader);
  var content = JSON.stringify(requestContent);

  content = encodeURIComponent(content);

  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function () {
    if (this.readyState === 4 && xmlHttp.status == 200) {
      //  console.log(this.responseText)
      response.status(200).send(this.responseText)
      sendSMS(requestBody.UserMobile, `A trxn of SGD` + requestBody.OrderAmt + ` from account ` + requestBody.UserTBankId + ` to KIM JONG UN'S DELIGHTS on ` + dt.toISOString() + ` (SGT) was completed. If unauthorised, call +65 6828 0123`)
      //sendSMS(requestBody.MobileNumber, `A trxn of SGD` + requestBody.OrderAmt + ` from account ` + requestBody.UserTBankId + ` to KIM JONG UN'S DELIGHTS on ` + dt.toISOString() + ` (SGT) was completed. If unauthorised, call +65 6828 0123`)
    }
  }

  xmlHttp.open("get", "http://tbankonline.com/SMUtBank_API/Gateway?Header=" + header + "&Content=" + content, true)
  xmlHttp.timeout = 5000;
  xmlHttp.send();
})


// To Link User with TBank account
// To Store user Accnt ID and Password
// To create beneficiary on both sides
//Parameters required:
//UserAccId (tbank); UserPin(tbank); UserAccNo (tbank accNo.); MobileNumber (customer)
//Type: x-form-urlencoded
app.post('/payment/LinkTBankAccount', (request, response, next) => {

  const requestBody = request.body;
  //console.log(requestBody)

  //ref: addBeneficiary(userID, UserPin, UserMobile, BeneificaryID, BeneficiaryDesc, response)
  //adding beneficiary to customer
  addBeneficiary(requestBody.UserAccId, requestBody.UserPin, prcoess.env.COMPANY_BENEFICIARY_ID, prcoess.env.COMPANY_BANK_ACCOUNT, prcoess.env.COMPANY_NAME)

  //adding beneficiary to Merchant
  addBeneficiary(prcoess.env.COMPANY_BANK_USER_ID, prcoess.env.COMPANY_BANK_PIN, requestBody.UserMobile, requestBody.UserAccNo, "CS " + requestBody.UserAccId, response)

})

//REFUND PAYMENT
//Parameters required:
//UserTBankId; OrderAmt; MerchMobile (merchant); UserMobile (customer)
//Type: x-form-urlencoded
app.post('/payment/refundPayment', (request, response, next) => {

  const requestBody = request.body;

  var requestHeader = {
    "Header": {
      "serviceName": "creditTransfer",
      "userID": prcoess.env.COMPANY_BANK_USER_ID,
      "PIN": prcoess.env.COMPANY_BANK_PIN,
      "OTP": OTP
    }
  }
  //console.log(requestHeader)
  var dt = new Date();
  dt.setHours(dt.getHours() + 8);

  //console.log(dt.toISOString().slice(0, 10))
  var requestContent = {
    'Content': {
      'accountFrom': prcoess.env.COMPANY_BANK_ACCOUNT,
      'accountTo': requestBody.UserTBankId,
      'transactionAmount': requestBody.OrderAmt,
      'transactionReferenceNumber': `REFUND Transaction`,
      'narrative': 'REFUNDED SGD' + requestBody.OrderAmt + ' to ' + requestBody.UserTBankId + ' @ ' + dt.toISOString().slice(0, 10)
    }
  }

  var header = JSON.stringify(requestHeader);
  var content = JSON.stringify(requestContent);

  content = encodeURIComponent(content);

  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function () {
    if (this.readyState === 4 && xmlHttp.status == 200) {
      //  console.log(this.responseText)
      sendSMS("6596386988", `A REFUND of SGD` + requestBody.OrderAmt + ` to account ` + requestBody.UserTBankId + ` on ` + dt.toISOString() + ` (SGT) was completed. If unauthorised, call +65 6828 0123`)
      sendSMS(requestBody.UserMobile, `A REFUND of SGD` + requestBody.OrderAmt + ` from KIM JONG UN'S DELIGHTS to your account ` + requestBody.UserTBankId + ` on ` + dt.toISOString() + ` (SGT) was completed. If unauthorised, call +65 6828 0123`)
      response.status(200).send(this.responseText)
    }
  }

  xmlHttp.open("get", "http://tbankonline.com/SMUtBank_API/Gateway?Header=" + header + "&Content=" + content, true)
  xmlHttp.timeout = 5000;
  xmlHttp.send();
})

//---- Helper functions ----

//Adding Beneficiary
function addBeneficiary(userID, UserPin, UserMobile, BeneificaryID, BeneficiaryDesc, response) {
  var requestHeader = {
    "Header": {
      "serviceName": "addBeneficiary",
      "userID": userID,
      "PIN": UserPin,
      "OTP": OTP
    }
  }
  var requestContent = {
    'Content': {
      'AccountID': BeneificaryID,
      'Description': BeneficiaryDesc
    }
  }

  var header = JSON.stringify(requestHeader);
  var content = JSON.stringify(requestContent);

  content = encodeURIComponent(content);

  var xmlHttp = new XMLHttpRequest();
  if (xmlHttp === null) {
    console.log("Something wrong with addBeneficiary.")
    return;
  }
  xmlHttp.onreadystatechange = function () {
    if (this.readyState === 4 && xmlHttp.status == 200) {
      console.log(this.responseText);
      //console.log(response);
      //response.status(200).send(JSON.parse(this.responseText));

      //check if it's the last linking up of accounts
      if (response != null) {
        sendSMS(UserMobile, `BETSY SERVICE - You have successfully connected to ${prcoess.env.COMPANY_BANK_ACCOUNT}. If unauthorised, call +65 6828 0123`);
        response.status(200).send("Successfully connected accounts.");
      }
    }
  }
  xmlHttp.open("POST", "http://tbankonline.com/SMUtBank_API/Gateway?Header=" + header + "&Content=" + content, true)
  xmlHttp.timeout = 5000;
  xmlHttp.send();
}

//sendSMS https://shrouded-tor-58051.herokuapp.com/payOrder_tBank
function sendSMS(UserMobile, message, response) {
  console.log(UserMobile)
  console.log(message)
  var depoHeader = {
    "Header": {
      "serviceName": "sendSMS",
      "userID": prcoess.env.COMPANY_BANK_USER_ID,
      "PIN": prcoess.env.COMPANY_BANK_PIN,
      "OTP": OTP
    }
  }

  var depoContent = {
    "Content": {
      "mobileNumber": UserMobile,
      "message": message
    }
  }

  var header = JSON.stringify(depoHeader);
  var content = JSON.stringify(depoContent);

  content = encodeURIComponent(content);
  console.log(content)
  var xmlHttp = new XMLHttpRequest();
  if (xmlHttp === null) {
    console.log("Something went wrong with sendSMS.")
    return;
  }
  xmlHttp.onreadystatechange = function () {
    if (this.readyState === 4 && xmlHttp.status == 200) {
      if (response != null) {
        response.status(200).send("Message Successfully Sent!")
      }
      //console.log("SMS: " + this.responseText)
    }
  }

  xmlHttp.open("POST", "http://tbankonline.com/SMUtBank_API/Gateway?Header=" + header + "&Content=" + content, true)
  xmlHttp.timeout = 5000;
  xmlHttp.send();
}

module.exports = app;