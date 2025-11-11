const express = require("express");
const app = express();
const { Pool } = require("pg");
const port = 3000;

//adding middleware again
app.use(express.json());

//adding in some environment values to 
//need to get these from a secret file later
const pool = new Pool({
  host: process.env.DB_HOST || "db",
  port: process.env.DB_PORT || 5432,
  user: process.env.DB_USER || "postgres",
  password: process.env.DB_PASSWORD || "postgres",
  database: process.env.DB_NAME || "items_db",
});

//different route, try and display from the databse
app.get("/", async (req, res) => {
  try {
    // hopefully this works like assignment #1
    const result = await pool.query("SELECT * FROM items ORDER BY id ASC");
    let html = "<h1>Inventory</h1><ul>";
    for (const item of result.rows) {
      html += `<li>${item.name}: ${item.quantity}</li>`;
    }
    html += "</ul>";
    res.send(html);
  } catch (err) {
    console.error(err);
    res.status(500).send("Database error");
  }
});

//adding this to get files from the subfolder
//const path = require("path");
//app.use(express.static(path.join(__dirname, "public")));

//app.get("/", (req, res) => {
//  res.send("Hello from Node.js inside Docker! (modified this message)");
//});
//
app.listen(port, () => {
  console.log(`App running at http://localhost:${port}`);
});
