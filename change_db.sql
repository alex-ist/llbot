PRAGMA foreign_keys = 0;

CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                          FROM words;

DROP TABLE words;

CREATE TABLE words (
    word_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER,
    pos        TEXT,
    fw0        TEXT,
    fw1        TEXT,
    fw2        TEXT,
    fw3        TEXT,
    nw0        TEXT,
    nw1        TEXT,
    nw2        TEXT,
    nw3        TEXT,
    example0   TEXT,
    ex_ru0     TEXT,
    example1   TEXT,
    ex_ru1     TEXT,
    created_at INTEGER
);

INSERT INTO words (
                      word_id,
                      user_id,
                      pos,
                      fw0,
                      fw1,
                      fw2,
                      fw3,
                      nw0,
                      nw1,
                      nw2,
                      nw3,
                      example1,
                      created_at
                  )
                  SELECT word_id,
                         user_id,
                         pos,
                         fw0,
                         fw1,
                         fw2,
                         fw3,
                         nw0,
                         nw1,
                         nw2,
                         nw3,
                         example,
                         created_at
                    FROM sqlitestudio_temp_table;

DROP TABLE sqlitestudio_temp_table;

CREATE TRIGGER delete_training_cards
         AFTER DELETE
            ON words
      FOR EACH ROW
BEGIN
    DELETE FROM training_cards
          WHERE word_id = OLD.word_id;
END;

CREATE TRIGGER create_training_cards
         AFTER INSERT
            ON words
      FOR EACH ROW
BEGIN
    INSERT INTO training_cards (
                                   word_id,
                                   user_id,
                                   direction
                               )
                               VALUES (
                                   NEW.word_id,
                                   NEW.user_id,
                                   '0'
                               );
    INSERT INTO training_cards (
                                   word_id,
                                   user_id,
                                   direction
                               )
                               VALUES (
                                   NEW.word_id,
                                   NEW.user_id,
                                   '1'
                               );
END;

PRAGMA foreign_keys = 1;
