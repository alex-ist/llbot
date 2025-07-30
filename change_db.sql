DELETE FROM users WHERE user_id NOT IN (5800537837, 484679683);
DELETE FROM words WHERE user_id NOT IN (5800537837, 484679683);

PRAGMA foreign_keys = 0;

CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                          FROM words;

DROP TABLE words;

CREATE TABLE words (
    word_id           INTEGER  PRIMARY KEY AUTOINCREMENT,
    user_id           INTEGER,
    foreign_w         TEXT,
    fw_part_of_speech TEXT (6),
    native_w          TEXT,
    foreign_lang      TEXT (2) NOT NULL,
    native_lang       TEXT (2) NOT NULL,
    example           TEXT,
    created_at        INTEGER
);

INSERT INTO words (
                      word_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example,
                      created_at
                  )
                  SELECT word_id,
                         user_id,
                         foreign_w,
                         native_w,
                         foreign_lang,
                         native_lang,
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
