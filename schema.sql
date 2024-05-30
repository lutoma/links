CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
	NEW.updated_at = NOW();
	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE EXTENSION citext;
CREATE TABLE lists (
	id SERIAL PRIMARY KEY,
	slug CITEXT NOT NULL,
	parent_id INTEGER REFERENCES lists(id),
	created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	title TEXT NOT NULL,
	description TEXT
);

CREATE UNIQUE INDEX lists_slug_unique ON lists (lower(slug));
CREATE TRIGGER lists_set_timestamp BEFORE UPDATE ON lists
	FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();

CREATE TABLE links (
	id SERIAL PRIMARY KEY,
	list_id INTEGER NOT NULL REFERENCES lists(id),
	created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	url TEXT NOT NULL,
	domain CITEXT NOT NULL,
	title TEXT,
	description TEXT
);

CREATE TRIGGER links_set_timestamp BEFORE UPDATE ON links
	FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();
