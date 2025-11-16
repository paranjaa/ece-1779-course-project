CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    item_name TEXT NOT NULL UNIQUE,
    item_quantity INTEGER NOT NULL
);

CREATE TABlE IF NOT EXISTS users (
    uid SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'user'
);

-- DEV BUILD ONLY -- REMOVE BEFORE DEPLOYING
INSERT INTO users (username, hashed_password) VALUES ('manager', '5fc2ca6f085919f2f77626f1e280fab9cc92b4edc9edc53ac6eee3f72c5c508e869ee9d67a96d63986d14c1c2b82c35ff5f31494bea831015424f59c96fff664', 'admin'), ('staff', '9040a19ce8acee009516b4ea917066e06a5deb15f5879c5645bf3e9b7c8877e512be42bccdc08b2370194d9427adcf1855fce60036fa73f689a281d898fb1a48', 'user');

-- For testing, adding in a couple "starter items" for display
INSERT INTO inventory (item_name, item_quantity) VALUES
('Apples', 10),
('Oranges', 15);
