CREATE TABLE dictionary_links (
    foreign_w TEXT,
    link TEXT,
    lang_code TEXT,
    date INTEGER,
    UNIQUE (foreign_w, lang_code)
);