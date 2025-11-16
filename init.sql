CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    item_name TEXT NOT NULL UNIQUE,
    item_quantity INTEGER NOT NULL
);

-- For testing, adding in a couple "starter items" for display 
INSERT INTO inventory (item_name, item_quantity) VALUES
('Apples', 10),
('Oranges', 15);


-- Adding a table for users, for managing login
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR DEFAULT 'user'
);
-- This needs to get the password hashed in order to work
--INSERT INTO users (username, password, role) VALUES
--('user1','pass1', 'user');
