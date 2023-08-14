CREATE TABLE urls (
id bigint primary key generated always as identity,
name varchar(255) unique, created_at date CURRENT_DATE);


CREATE TABLE url_checks (
id bigint primary key generated always as identity,
url_id bigint REFERENCES urls (id),
status_code varchar(255), h1 text, title text,
description text, created_at date CURRENT_DATE);


