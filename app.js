const express = require("express");
const app = express();
const port = 3000;

//adding this to get files from the subfolder
const path = require("path");
app.use(express.static(path.join(__dirname, "public")));

app.get("/", (req, res) => {
  res.send("Hello from Node.js inside Docker! (modified this message)");
});

app.listen(port, () => {
  console.log(`App running at http://localhost:${port}`);
});
