PRAGMA foreign_keys = 0;

CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                          FROM words;

DROP TABLE words;

CREATE TABLE words (
    word_id      INTEGER  PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER,
    foreign_w    TEXT,
    native_w     TEXT,
    foreign_lang TEXT (2) NOT NULL,
    native_lang  TEXT (2) NOT NULL,
    example      TEXT
);

INSERT INTO words (
                      word_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  SELECT card_id,
                         user_id,
                         foreign_w,
                         native_w,
                         foreign_lang,
                         native_lang,
                         example
                    FROM sqlitestudio_temp_table;

CREATE TABLE sqlitestudio_temp_table0 AS SELECT *
                                           FROM training_cards;

DROP TABLE training_cards;

CREATE TABLE training_cards (
    training_card_id INTEGER     PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER,
    card_id          INTEGER     REFERENCES words (word_id),
    direction        INTEGER (1) NOT NULL,
    next_training_t  INTEGER     DEFAULT ( -1),
    last_training_t  INTEGER     DEFAULT ( -1) 
);

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           SELECT training_card_id,
                                  user_id,
                                  card_id,
                                  direction,
                                  next_training_t,
                                  last_training_t
                             FROM sqlitestudio_temp_table0;

DROP TABLE sqlitestudio_temp_table0;

DROP TABLE sqlitestudio_temp_table;

CREATE TRIGGER delete_training_cards
         AFTER DELETE
            ON words
      FOR EACH ROW
BEGIN
    DELETE FROM training_cards
          WHERE card_id = OLD.word_id;
END;

CREATE TRIGGER create_training_cards
         AFTER INSERT
            ON words
      FOR EACH ROW
BEGIN
    INSERT INTO training_cards (
                                   card_id,
                                   user_id,
                                   direction
                               )
                               VALUES (
                                   NEW.word_id,
                                   NEW.user_id,
                                   '0'
                               );
    INSERT INTO training_cards (
                                   card_id,
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


PRAGMA foreign_keys = 0;

CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                          FROM training_cards;

DROP TABLE training_cards;

CREATE TABLE training_cards (
    training_card_id INTEGER     PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER,
    word_id          INTEGER     REFERENCES words (card_id),
    direction        INTEGER (1) NOT NULL,
    next_training_t  INTEGER     DEFAULT ( -1),
    last_training_t  INTEGER     DEFAULT ( -1) 
);

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               word_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           SELECT training_card_id,
                                  user_id,
                                  card_id,
                                  direction,
                                  next_training_t,
                                  last_training_t
                             FROM sqlitestudio_temp_table;

DROP TABLE sqlitestudio_temp_table;

DROP TRIGGER IF EXISTS create_training_cards;

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

DROP TRIGGER delete_training_cards;

CREATE TRIGGER delete_training_cards
         AFTER DELETE
            ON words
      FOR EACH ROW
BEGIN
    DELETE FROM training_cards
          WHERE word_id = OLD.word_id;
END;
