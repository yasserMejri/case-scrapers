
-- run us_states.sql prior to this script
CREATE EXTENSION "uuid-ossp";


CREATE TYPE court_type AS ENUM ('court');
CREATE TYPE status_type AS ENUM('open','closed');
CREATE TYPE result_type as ENUM('succeeded','failed');

CREATE TABLE scraper_info (
    scraper_info_pk serial NOT NULL PRIMARY KEY,
    jurisdiction varchar(64),
    court court_type,
    us_state us_states,
    UNIQUE (jurisdiction,court, us_state)
);

CREATE TABLE scrape_results (
scrape_results_pk serial NOT NULL PRIMARY KEY,
status status_type,
result result_type,
dob DATE,
lname varchar(64),
fname varchar(64),
query_key uuid DEFAULT uuid_generate_v4(),
query_tz TIMESTAMPTZ default current_timestamp,
result_tz TIMESTAMPTZ,
result_set jsonb,
scraper_info_fk INTEGER REFERENCES scraper_info(scraper_info_pk)
);
