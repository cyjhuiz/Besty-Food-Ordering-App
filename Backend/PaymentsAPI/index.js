const app = require('./controller/app.js');
const port = process.prcoess.env.PORT || 5005;

app.listen(port, () => {
  console.log(`Server started on port http://localhost:${port}`);
})