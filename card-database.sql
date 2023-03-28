PRAGMA foreign_keys=OFF;
DROP TABLE IF EXISTS "Cards";
CREATE TABLE "Cards" (
    "id"            INTEGER,
    "name"          TEXT,
    "beta_name"     TEXT,
    "type"          TEXT,
    "archetype"     TEXT,
    "subtype"       TEXT,
    "attribute"     TEXT,
    "atk"           INTEGER,
    "def"           INTEGER,
    "level"         INTEGER,
    "rank"          INTEGER,
    "linkval"       INTEGER,
    "linkmarkers"   TEXT,
    "scale"         INTEGER,
    "desc"          TEXT,
    "card_images"   TEXT,
    "banlist_info"  TEXT,
    "card_prices"   TEXT,
    "misc_info"     TEXT
);
CREATE INDEX card_id ON Cards(id);