PRAGMA foreign_keys = 0;

CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                          FROM training_cards;

DROP TABLE training_cards;

CREATE TABLE training_cards (
    training_card_id INTEGER     PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER,
    card_id          INTEGER     REFERENCES cards (card_id),
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
                             FROM sqlitestudio_temp_table;

DROP TABLE sqlitestudio_temp_table;

DROP TRIGGER IF EXISTS create_training_cards;

CREATE TRIGGER create_training_cards
         AFTER INSERT
            ON cards
      FOR EACH ROW
BEGIN
    INSERT INTO training_cards (
                                   card_id,
                                   user_id,
                                   direction
                               )
                               VALUES (
                                   NEW.card_id,
                                   NEW.user_id,
                                   '0'
                               );
    INSERT INTO training_cards (
                                   card_id,
                                   user_id,
                                   direction
                               )
                               VALUES (
                                   NEW.card_id,
                                   NEW.user_id,
                                   '1'
                               );
END;

PRAGMA foreign_keys = 1;