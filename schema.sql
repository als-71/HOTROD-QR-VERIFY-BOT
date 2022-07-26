CREATE TABLE tokens (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    userid VARCHAR(255) NOT NULL,
    token VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(255),
    mfa boolean NOT NULL,
    nitro boolean NOT NULL,
    billing json
);