CREATE TABLE tokens (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    userid VARCHAR(255) NOT NULL,
    token VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(255) NOT NULL,
    address json,
    mfa boolean NOT NULL,
    nitro boolean NOT NULL,
    billing boolean NOT NULL
);