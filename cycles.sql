CREATE TABLE IF NOT EXISTS cycles (
	id serial PRIMARY KEY,
	cycles_id INTEGER UNIQUE NOT NULL,
	produce_blocks INTEGER NOT NULL,
	failed_blocks INTEGER NOT NULL,
    added_time TIMESTAMP
);