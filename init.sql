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
INSERT INTO users (username, password, role) VALUES ('admin', 'scrypt:32768:8:1$yiCv2YnQotBzMb3l$39086d72aa7a4e3392447ffc502cd33a46b74adb25a9c431702744d873e4de8efd52d6f3ab838d2bea36d5ee136ea7ed3386e39dadbcc190eeabab235c7d76bd', 'admin');

-- For testing, adding in a couple "starter items" for display
INSERT INTO inventory (item_name, item_quantity) VALUES
('Apples', 10),
('Oranges', 15);

-- Adding a function that handles notifications
CREATE OR REPLACE FUNCTION notify_database_change()
RETURNS TRIGGER AS $$
DECLARE 
  payload JSON;
BEGIN
  payload = json_build_object(
    -- should just be inventory
    'table', TG_TABLE_NAME,
    'action', TG_OP,
    -- had to add this, since it'll change when there's a new item or one is deleted
    -- TODO?: also need to add function for changing IDs
    'id', COALESCE(OLD.id, NEW.id)
  );

  PERFORM pg_notify('inventory_events', payload::text);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;



-- Create trigger on INSERT/UPDATE/DELETE/CREATE
-- whenever those happen, try and run the function
CREATE TRIGGER inventory_trigger
AFTER CREATE OR INSERT OR UPDATE OR DELETE ON inventory
FOR EACH ROW EXECUTE FUNCTION notify_database_change();


