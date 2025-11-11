CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0
);

-- Sample data
INSERT INTO items (name, quantity)
VALUES 
  ('Apples', 10),
  ('Oranges', 5);
