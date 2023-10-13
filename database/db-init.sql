-- Set the password for the default postgres user
ALTER USER postgres WITH PASSWORD 'postgres';

-- Create a new database named db
CREATE DATABASE IF NOT EXISTS db;

-- Connect to the new database
\c db;

-- Create a new table to store questions and outputs
CREATE TABLE IF NOT EXISTS qa (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    output TEXT NOT NULL
);

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE db TO postgres;
GRANT ALL PRIVILEGES ON TABLE qa TO postgres;