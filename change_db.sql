PRAGMA foreign_keys = 0;

CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                          FROM users;

DROP TABLE users;

CREATE TABLE users (
    user_id               INTEGER     PRIMARY KEY,
    chat_id               INTEGER,
    username              TEXT,
    first_name            TEXT,
    name                  TEXT,
    lang_code             TEXT,
    is_premium            INTEGER (1),
    o_param               INTEGER     DEFAULT (2),
    foreign_lang          TEXT (2)    NOT NULL,
    use_audio_examples    INTEGER (1) DEFAULT (1),
    use_examples          INTEGER (1) DEFAULT (1),
    min_trening_interval  INTEGER,
    min_cards_for_trening INTEGER,
    max_cards_for_trening INTEGER,
    cur_cards_for_trening INTEGER,
    first_access          INTEGER,
    last_access           INTEGER,
    shown_words_count     INTEGER,
    current_forget_rate   REAL,
    status                TEXT (1)    DEFAULT A,
    sent_nid              INTEGER     DEFAULT (0),
    auto_play_audio       INTEGER (1) DEFAULT (1),
    prof_level            TEXT (3) 
);

INSERT INTO users (
                      user_id,
                      chat_id,
                      username,
                      first_name,
                      name,
                      lang_code,
                      is_premium,
                      o_param,
                      foreign_lang,
                      use_audio_examples,
                      use_examples,
                      min_trening_interval,
                      min_cards_for_trening,
                      max_cards_for_trening,
                      cur_cards_for_trening,
                      first_access,
                      last_access,
                      shown_words_count,
                      current_forget_rate,
                      status,
                      sent_nid,
                      auto_play_audio
                  )
                  SELECT user_id,
                         chat_id,
                         username,
                         first_name,
                         name,
                         lang_code,
                         is_premium,
                         o_param,
                         foreign_lang,
                         use_audio_examples,
                         use_examples,
                         min_trening_interval,
                         min_cards_for_trening,
                         max_cards_for_trening,
                         cur_cards_for_trening,
                         first_access,
                         last_access,
                         shown_words_count,
                         current_forget_rate,
                         status,
                         sent_nid,
                         auto_play_audio
                    FROM sqlitestudio_temp_table;

DROP TABLE sqlitestudio_temp_table;

PRAGMA foreign_keys = 1;

UPDATE users SET prof_level = 'A2' WHERE user_id=5800537837;
UPDATE users SET prof_level = 'B1' WHERE user_id=484679683;
