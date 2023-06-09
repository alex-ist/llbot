PRAGMA foreign_keys = 0;

CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                          FROM user_config;

DROP TABLE user_config;

CREATE TABLE user_config (
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
    shown_words_count     INTEGER,
    current_forget_rate   REAL
);

INSERT INTO user_config (
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
                               forgetting_rate
                          FROM sqlitestudio_temp_table;

DROP TABLE sqlitestudio_temp_table;

PRAGMA foreign_keys = 1;
