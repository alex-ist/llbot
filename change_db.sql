PRAGMA foreign_keys = 0;

CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                          FROM users;

DROP TABLE users;

CREATE TABLE users (
    user_id               INTEGER     PRIMARY KEY,
    chat_id               INTEGER,
    state                 INTEGER,
    m1_msg_id             INTEGER,
    o_param               INTEGER     DEFAULT (2),
    foreign_lang          TEXT (2)    NOT NULL,
    use_audio_examples    INTEGER (1) DEFAULT (1),
    use_examples          INTEGER (1) DEFAULT (1),
    min_trening_interval  INTEGER,
    min_cards_for_trening INTEGER,
    max_cards_for_trening INTEGER,
    first_access          INTEGER,
    last_access           INTEGER,
    shown_words_count     INTEGER     DEFAULT (0),
    current_forget_rate   REAL        DEFAULT (0.1),
    username              TEXT,
    first_name            TEXT,
    lang_code             TEXT,
    is_premium            INTEGER (1) 
);

INSERT INTO users (
                      user_id,
                      chat_id,
                      state,
                      m1_msg_id,
                      o_param,
                      foreign_lang,
                      use_audio_examples,
                      use_examples,
                      min_trening_interval,
                      min_cards_for_trening,
                      max_cards_for_trening,
                      first_access,
                      last_access,
                      shown_words_count,
                      current_forget_rate
                  )
                  SELECT user_id,
                         chat_id,
                         state,
                         m1_msg_id,
                         o_param,
                         foreign_lang,
                         use_audio_examples,
                         use_examples,
                         min_trening_interval,
                         min_cards_for_trening,
                         max_cards_for_trening,
                         first_access,
                         last_access,
                         shown_words_count,
                         current_forget_rate
                    FROM sqlitestudio_temp_table;

DROP TABLE sqlitestudio_temp_table;

PRAGMA foreign_keys = 1;
