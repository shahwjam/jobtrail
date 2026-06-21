-- JobTrail database schema
-- Tables created in dependency order: a table must exist before it can be referenced.

CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name     VARCHAR(120),
    created_at    TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE applications (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company         VARCHAR(200) NOT NULL,
    position        VARCHAR(200) NOT NULL,
    status          VARCHAR(50) NOT NULL DEFAULT 'Applied',
    job_description TEXT,
    applied_date    DATE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE contacts (
    id             SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    name           VARCHAR(120) NOT NULL,
    title          VARCHAR(120),
    email          VARCHAR(255),
    phone          VARCHAR(30),
    notes          TEXT,
    created_at     TIMESTAMP NOT NULL DEFAULT NOW()
);
