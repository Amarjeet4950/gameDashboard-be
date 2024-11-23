-- init.sql
CREATE TABLE items (
    rid SERIAL PRIMARY KEY, -- Unique identifier
    id INTEGER
    examine TEXT,          -- Description of the item
    members BOOLEAN,       -- Whether the item is members-only
    lowalch INTEGER,       -- Low alchemy value
    item_limit INTEGER,    -- Trade limit for the item
    value INTEGER,         -- Base value of the item
    highalch INTEGER,      -- High alchemy value
    icon TEXT,             -- Name of the item's icon file
    name VARCHAR(255),      -- Name of the item
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);