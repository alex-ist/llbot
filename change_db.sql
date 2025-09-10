CREATE TABLE c_dict_pron (
    hw        TEXT,
    pos       TEXT     NOT NULL,
    entry_num INTEGER  NOT NULL,
    region    TEXT (2) NOT NULL,
    ipa       TEXT     NOT NULL,
    fn        TEXT
);

CREATE TABLE c_dict_hw (
    hw          TEXT PRIMARY KEY,
    source_url  TEXT NOT NULL,
    raw_json    TEXT NOT NULL
);
