PRAGMA foreign_keys = 0;

CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                          FROM maintenance_data;

DROP TABLE maintenance_data;

CREATE TABLE maintenance_data (
    user_id   INTEGER PRIMARY KEY,
    chat_id   INTEGER,
    msg_id1   INTEGER,
    msg_id2   INTEGER,
    state     TEXT,
    sub_state TEXT
);

INSERT INTO maintenance_data (
                                 user_id,
                                 chat_id,
                                 msg_id1,
                                 msg_id2,
                                 state
                             )
                             SELECT user_id,
                                    chat_id,
                                    msg_id1,
                                    msg_id2,
                                    state
                               FROM sqlitestudio_temp_table;

DROP TABLE sqlitestudio_temp_table;

PRAGMA foreign_keys = 1;
