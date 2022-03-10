const express = require('express');
const app = express();
const sgMail = require('@sendgrid/mail')

//remember to npm install amqplib
const amqp = require("amqplib/callback_api");

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

// /sendemail
//Parameters required:
//UserEmail; EmailSubject; EmailContent
//type: x-form-urlencoded
app.post('/sendemail', (request, response, next) => {
  const requestBody = request.body;
  sendEmail(requestBody.UserEmail, requestBody.EmailSubject, requestBody.EmailContent)
  response.end();
})

app.post('/sendSMS/', (request, response, next) => {
  const requestBody = request.body;
  sendSMS(requestBody.UserMobile, requestBody.message);
  response.end();
})

//---- Helper functions ----

//sendSMS
function sendSMS(UserMobile, message) {
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
        console.log("SMS Sent successfully!")
      }
      //console.log("SMS: " + this.responseText)
    }
  }
  xmlHttp.open("POST", "http://tbankonline.com/SMUtBank_API/Gateway?Header=" + header + "&Content=" + content, true)
  xmlHttp.timeout = 5000;
  xmlHttp.send();
}

//sendEmail
function sendEmail(UserEmail, EmailSubject, EmailContent) {
  sgMail.setApiKey(prcoess.env.MAIL_API_KEY)
  const msg = {
    to: UserEmail, // Change to your recipient
    from: prcoess.env.COMPANY_EMAIL, // Change to your verified sender
    subject: `${prcoess.env.COMPANY_NAME} - ` + EmailSubject,
    text: EmailContent,
    html: '<strong>' + EmailContent + '</strong>',
  }
  sgMail
    .send(msg)
    .then(() => {
      console.log('Email sent')
      return;
    })
    .catch((error) => {
      console.error(error)
      return;
    })
}

const process = require('process');
const rabbit_host = process.prcoess.env.rabbit_host;
const rabbit_port = process.prcoess.env.rabbit_port;

amqp.connect(`amqp://${rabbit_host}:${rabbit_port}`, (connectionError, connection) => {
  if (connectionError) {
    throw connectionError;
  }
  // Step 2: Create Channel
  connection.createChannel((channelError, channel) => {
    if (channelError) {
      throw channelError;
    }
    // Step 3: Assert Queue to listen to
    const queueName = 'Notification';
    channel.assertQueue(queueName);
    // Step 4: Receive Messages
    channel.consume(queueName, json_data => {
      const data = JSON.parse(json_data.content);
      sendSMS(data.UserMobile, data.Message, "NoResponseObject"); // AMQP has no response object
      sendEmail(data.UserEmail, data.EmailSubject, data.EmailContent); // Not sure about the order of the parameters for email function
      channel.ack(json_data);
    });
  });
});

module.exports = app;