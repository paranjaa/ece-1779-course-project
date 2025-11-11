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

//adding CRUD operations
app.get("/items", async (req, res) => {
  try {
    //like the test page, get every item in the database
    const result = await pool.query("SELECT * FROM items ORDER BY id ASC");
    res.json(result.rows);
  } catch (err) {
    console.error("Error fetching items:", err);
    res.status(500).json({ error: "Database error" });
  }
});


//Add a new item
app.post("/items", async (req, res) => {
  // get the required files from the request  
  const { name, quantity } = req.body;
  if (!name) {
    //make an error if they aren't there
    return res.status(400).json({ error: "Item name is required" });
  }

  try {
    //if they're present, make an SQL query with the pieces
    const result = await pool.query(
      "INSERT INTO items (name, quantity) VALUES ($1, $2) RETURNING *",
      //default to 0 if not specified?
      [name, quantity || 0]
    );
    //return the newly added item
    res.status(201).json(result.rows[0]);
  } catch (err) {
    console.error("Error adding item:", err);
    res.status(500).json({ error: "Database error" });
  }
});

//Update, change an item by ID
app.put("/items/:id", async (req, res) => {
    //1. Retrieve the existing task from postgresql
    const id = req.params.id;
    //and the parts to change in the request
    const { name, quantity } = req.body;

  try {
    // try getting the corresponding values in the database
    const result = await pool.query(
      "UPDATE items SET name = $1, quantity = $2 WHERE id = $3 RETURNING *",
      [name, quantity, id]
    );
    // if the query doesn't return a result with any rows, return an error
    if (result.rowCount === 0) {
      return res.status(404).json({ error: "Item not found" });
    }
    
    //if not, then pass in the new values    
    res.json(result.rows[0]);
    //need to add logic for partial updates, like with A2
  } catch (err) {
    //errors for if something else goes wrong
    console.error("Error updating item:", err);
    res.status(500).json({ error: "Database error" });
  }
});

// delete, get rid of an item by ID
app.delete("/items/:id", async (req, res) => {
  
  //get the item from postgresql  
  const { id }  = req.params;

  try {
    //run a query
    const result = await pool.query("DELETE FROM items WHERE id = $1", [id]);

    //if there isn't a result in the response, there wasn't an item    
    if (result.rowCount === 0) {
      return res.status(404).json({ error: "Item not found" });
    }
    //if no error, then just send 204 (need to add in the Redis part next)
    res.status(204).send();
  } catch (err) {
    console.error("Error deleting item:", err);
    res.status(500).json({ error: "Database error" });
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
