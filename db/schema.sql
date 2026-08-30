PRAGMA user_version = 1;

CREATE TABLE users (
    user_id                INTEGER PRIMARY KEY,
    chat_id                INTEGER,
    username               TEXT,
    first_name             TEXT,
    name                   TEXT,
    lang_code              TEXT,
    is_premium             INTEGER,
    o_param                INTEGER DEFAULT 2,
    foreign_lang           TEXT NOT NULL,
    use_audio_examples     INTEGER DEFAULT 1,
    use_examples           INTEGER DEFAULT 1,
    min_trening_interval   INTEGER,
    min_cards_for_trening  INTEGER,
    max_cards_for_trening  INTEGER,
    cur_cards_for_trening  INTEGER,
    first_access           INTEGER,
    last_access            INTEGER,
    shown_words_count      INTEGER,
    current_forget_rate    REAL,
    status                 TEXT DEFAULT 'A',
    sent_nid               INTEGER DEFAULT 0,
    auto_play_audio        INTEGER DEFAULT 1,
    prof_level             TEXT
);

CREATE TABLE words (
    word_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER,
    pos         TEXT,
    fw0         TEXT,
    fw1         TEXT,
    fw2         TEXT,
    fw3         TEXT,
    nw0         TEXT,
    nw1         TEXT,
    nw2         TEXT,
    nw3         TEXT,
    example0    TEXT,
    ex_ru0      TEXT,
    example1    TEXT,
    ex_ru1      TEXT,
    created_at  INTEGER
);

CREATE TABLE training_cards (
    training_card_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id           INTEGER,
    word_id           INTEGER REFERENCES words (word_id),
    direction         INTEGER NOT NULL,
    next_training_t   INTEGER DEFAULT -1,
    last_training_t   INTEGER DEFAULT -1
);

CREATE TRIGGER create_training_cards
AFTER INSERT ON words
FOR EACH ROW
BEGIN
    INSERT INTO training_cards (word_id, user_id, direction)
    VALUES (NEW.word_id, NEW.user_id, 0);

    INSERT INTO training_cards (word_id, user_id, direction)
    VALUES (NEW.word_id, NEW.user_id, 1);
END;

CREATE TRIGGER delete_training_cards
AFTER DELETE ON words
FOR EACH ROW
BEGIN
    DELETE FROM training_cards WHERE word_id = OLD.word_id;
END;

CREATE TABLE maintenance_data (
    user_id         INTEGER PRIMARY KEY,
    chat_id         INTEGER,
    msg_id1         INTEGER,
    msg_id2         INTEGER,
    state           TEXT,
    sub_state       TEXT,
    reminder        INTEGER DEFAULT -1,
    reminder_count  INTEGER DEFAULT 0
);

CREATE TABLE dictionary_links (
    foreign_w  TEXT,
    link       TEXT,
    lang_code  TEXT,
    date       INTEGER,
    UNIQUE (foreign_w, lang_code)
);

CREATE TABLE user_notifications (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    ch_msg_id  INTEGER
);

CREATE TABLE word_set (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    f_word     TEXT NOT NULL,
    f_lang     TEXT NOT NULL DEFAULT 'en',
    f_example  TEXT,
    topic      TEXT,
    tr1_lang   TEXT,
    tr1        TEXT
);

CREATE UNIQUE INDEX unique_word_lang_topic
ON word_set (f_word, f_lang, topic);

CREATE TABLE c_dict (
    fw          TEXT,
    source_url  TEXT,
    is_pron     INTEGER
);

CREATE TABLE c_dict_pron (
    fw         TEXT NOT NULL,
    hw         TEXT NOT NULL,
    pos        TEXT NOT NULL,
    entry_num  INTEGER NOT NULL,
    region     TEXT NOT NULL,
    ipa        TEXT,
    fn         TEXT
);
