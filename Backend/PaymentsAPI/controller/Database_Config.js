const sql = require('mysql');

const connection = sql.createConnection({
  host: prcoess.env.DB_HOST,
  port: 3306,
  user: prcoess.env.DB_USER,
  password: '',
  database: prcoess.env.DB_NAME
});

connection.connect(function (err) {
  if (err) {
    console.log("Error connecting " + err.stack);
    return;
  }

  else {
    console.log("Connected as id " + connection.threadId);
    return;
  };
});

module.exports = connection;