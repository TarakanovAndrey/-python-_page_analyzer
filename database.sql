DROP TABLE IF EXISTS urls;

CREATE TABLE IF NOT EXISTS urls (
id bigint primary key generated always as identity,
name varchar(255) unique,
created_at timestamp DEFAULT CURRENT_TIMESTAMP);


DROP TABLE IF EXISTS url_checks;

CREATE TABLE IF NOT EXISTS url_checks (
id bigint primary key generated always as identity,
url_id bigint REFERENCES urls (id),
status_code varchar(255), h1 text, title text,
description text, created_at timestamp DEFAULT CURRENT_TIMESTAMP);
