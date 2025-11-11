CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    item_name TEXT NOT NULL UNIQUE,
    item_quantity INTEGER NOT NULL
);