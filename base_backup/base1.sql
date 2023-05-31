--
-- Файл сгенерирован с помощью SQLiteStudio v3.4.4 в Вс май 28 11:10:00 2023
--
-- Использованная кодировка текста: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Таблица: cards
DROP TABLE IF EXISTS cards;

CREATE TABLE IF NOT EXISTS cards (
    card_id      INTEGER  PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER,
    foreign_w    TEXT,
    native_w     TEXT,
    foreign_lang TEXT (2) NOT NULL,
    native_lang  TEXT (2) NOT NULL,
    example      TEXT
);

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      370,
                      5800537837,
                      'neighbor',
                      'сосед',
                      'en',
                      'ru',
                      'Hey, neighbor, could you watch my cat this weekend?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      371,
                      5800537837,
                      'apartment',
                      'квартира',
                      'en',
                      'ru',
                      'I can''t believe how quickly the apartment across from mine got rented.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      372,
                      5800537837,
                      'community',
                      'сообщество',
                      'en',
                      'ru',
                      'Our community is planning a yard sale next month'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      373,
                      5800537837,
                      'house',
                      'дом',
                      'en',
                      'ru',
                      'Did you see the paint color they chose for the house down the street?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      374,
                      5800537837,
                      'issue',
                      'проблема',
                      'en',
                      'ru',
                      'We need to talk about a serious issue.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      375,
                      5800537837,
                      'pet',
                      'домашнее животное',
                      'en',
                      'ru',
                      'Your pet is adorable! What''s its name?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      376,
                      5800537837,
                      'parking',
                      'парковка',
                      'en',
                      'ru',
                      'Parking is such a nightmare after 5 PM here.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      377,
                      5800537837,
                      'party',
                      'вечеринка',
                      'en',
                      'ru',
                      'We had a little party last night, hope we didn''t disturb you.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      378,
                      5800537837,
                      'invite',
                      'пригласить',
                      'en',
                      'ru',
                      'I''d like to invite you to our BBQ this weekend.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      379,
                      5800537837,
                      'adorable',
                      'очаровательный',
                      'en',
                      'ru',
                      'Your new puppy is absolutely adorable! How old is he?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      380,
                      5800537837,
                      'garden',
                      'сад',
                      'en',
                      'ru',
                      'Your garden is the best on the block!'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      381,
                      5800537837,
                      'maintenance',
                      'обслуживание',
                      'en',
                      'ru',
                      'The maintenance guy said he''d fix the lights in the hallway tomorrow'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      382,
                      5800537837,
                      'complaint',
                      'жалоба',
                      'en',
                      'ru',
                      'Who do I speak with about a noise complaint?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      383,
                      5800537837,
                      'garbage',
                      'мусор',
                      'en',
                      'ru',
                      'Sorry about the garbage cans blocking the driveway, I''ll move them.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      384,
                      5800537837,
                      'quiet',
                      'тихо',
                      'en',
                      'ru',
                      'It''s usually so quiet around here in the mornings.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      385,
                      5800537837,
                      'rules',
                      'правила',
                      'en',
                      'ru',
                      'Are there any specific rules about using the pool?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      386,
                      5800537837,
                      'property',
                      'собственность',
                      'en',
                      'ru',
                      'Who owns the property at the end of the street?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      387,
                      5800537837,
                      'fence',
                      'забор',
                      'en',
                      'ru',
                      'Our fence got damaged in the storm last night.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      388,
                      5800537837,
                      'shared',
                      'общий',
                      'en',
                      'ru',
                      'The basement laundry is a shared space, isn''t it?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      389,
                      5800537837,
                      'courtesy',
                      'вежливость',
                      'en',
                      'ru',
                      'Just as a courtesy, I thought I''d let you know we''re having people over tonight.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      390,
                      5800537837,
                      'security',
                      'безопасность',
                      'en',
                      'ru',
                      'The security in our building is excellent.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      391,
                      5800537837,
                      'meeting',
                      'собрание',
                      'en',
                      'ru',
                      'Is the homeowners association meeting happening this Tuesday?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      392,
                      5800537837,
                      'mail',
                      'почта',
                      'en',
                      'ru',
                      'Your mail got delivered to us by mistake.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      393,
                      5800537837,
                      'package',
                      'посылка',
                      'en',
                      'ru',
                      'There''s a package for you in the lobby.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      394,
                      5800537837,
                      'environment',
                      'окружающая среда',
                      'en',
                      'ru',
                      'We should do something about the environment, like organizing a clean-up.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      395,
                      5800537837,
                      'lawn',
                      'газон',
                      'en',
                      'ru',
                      'Your lawn looks incredible! How do you keep it so green?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      396,
                      5800537837,
                      'to meet',
                      'встретить',
                      'en',
                      'ru',
                      'Great to meet you, we just moved in next door.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      397,
                      5800537837,
                      'to greet',
                      'поприветствовать',
                      'en',
                      'ru',
                      'I just wanted to greet our new neighbors and introduce ourselves.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      398,
                      5800537837,
                      'to borrow',
                      'одолжить',
                      'en',
                      'ru',
                      'Could I borrow your lawn mower this weekend?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      399,
                      5800537837,
                      'housewarming party',
                      'праздник новоселья',
                      'en',
                      'ru',
                      'We wanted to invite you to our housewarming party.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      400,
                      5800537837,
                      'to complain',
                      'пожаловаться',
                      'en',
                      'ru',
                      'I hate to complain, but your dog has been barking early in the morning.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      401,
                      5800537837,
                      'to assist',
                      'помочь',
                      'en',
                      'ru',
                      'Would you be able to assist me in moving this furniture?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      402,
                      5800537837,
                      'to share',
                      'разделить (обязанности)',
                      'en',
                      'ru',
                      'We should share responsibilities for cleaning the stairs.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      403,
                      5800537837,
                      'to respect',
                      'уважать',
                      'en',
                      'ru',
                      'It''s important to respect each other''s privacy.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      404,
                      5800537837,
                      'disposal',
                      'утилизация, вывоз (мусора)',
                      'en',
                      'ru',
                      'We need to discuss the issue with trash disposal.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      405,
                      5800537837,
                      'to apologize',
                      'извиниться',
                      'en',
                      'ru',
                      'I want to apologize for the loud music last night.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      406,
                      5800537837,
                      'to maintain',
                      'поддерживать',
                      'en',
                      'ru',
                      'We all need to maintain the cleanliness of our shared spaces.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      407,
                      5800537837,
                      'to cooperate',
                      'сотрудничать',
                      'en',
                      'ru',
                      'If we cooperate, we can make this a great place to live.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      408,
                      5800537837,
                      'to resolve',
                      'решить',
                      'en',
                      'ru',
                      'We need to resolve this issue as soon as possible.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      409,
                      5800537837,
                      'nearby',
                      'рядом',
                      'en',
                      'ru',
                      'There''s a grocery store nearby.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      410,
                      5800537837,
                      'safe',
                      'безопасно',
                      'en',
                      'ru',
                      'I feel really safe in this neighborhood.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      411,
                      5800537837,
                      'recycling',
                      'переработка(отходов)',
                      'en',
                      'ru',
                      'I think we should start recycling, it''s important for the environment.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      412,
                      5800537837,
                      'stomping',
                      'топот',
                      'en',
                      'ru',
                      'We can hear stomping from your apartment, it''s a bit disturbing.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      413,
                      5800537837,
                      'clean up',
                      'убрать',
                      'en',
                      'ru',
                      'Could you please clean up after your dog in the garden?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      414,
                      5800537837,
                      'ceiling',
                      'потолок',
                      'en',
                      'ru',
                      'There''s a water leak from my ceiling, I think it''s coming from your apartment.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      415,
                      5800537837,
                      'renovation',
                      'ремонт',
                      'en',
                      'ru',
                      'Could you wait to start your renovation until after 9 am?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      416,
                      5800537837,
                      'concern',
                      'беспокойство',
                      'en',
                      'ru',
                      'I understand your concern about the noise.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      417,
                      5800537837,
                      'tranquility',
                      'спокойствие(глубокое)',
                      'en',
                      'ru',
                      'We moved here for the tranquility, it''s so peaceful.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      418,
                      5800537837,
                      'upstairs',
                      'наверху',
                      'en',
                      'ru',
                      'Every time the upstairs neighbors drop something, I half expect a bowling ball to come through the ceiling.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      419,
                      5800537837,
                      'downstairs',
                      'внизу',
                      'en',
                      'ru',
                      'I think my downstairs neighbors might be vampires, they''re only active after midnight!'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      420,
                      484679683,
                      'neighbor',
                      'сосед',
                      'en',
                      'ru',
                      'Hey, neighbor, could you watch my cat this weekend?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      421,
                      484679683,
                      'apartment',
                      'квартира',
                      'en',
                      'ru',
                      'I can''t believe how quickly the apartment across from mine got rented.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      422,
                      484679683,
                      'community',
                      'сообщество',
                      'en',
                      'ru',
                      'Our community is planning a yard sale next month'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      423,
                      484679683,
                      'house',
                      'дом',
                      'en',
                      'ru',
                      'Did you see the paint color they chose for the house down the street?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      424,
                      484679683,
                      'issue',
                      'проблема',
                      'en',
                      'ru',
                      'We need to talk about a serious issue.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      425,
                      484679683,
                      'pet',
                      'домашнее животное',
                      'en',
                      'ru',
                      'Your pet is adorable! What''s its name?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      426,
                      484679683,
                      'parking',
                      'парковка',
                      'en',
                      'ru',
                      'Parking is such a nightmare after 5 PM here.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      427,
                      484679683,
                      'party',
                      'вечеринка',
                      'en',
                      'ru',
                      'We had a little party last night, hope we didn''t disturb you.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      428,
                      484679683,
                      'invite',
                      'пригласить',
                      'en',
                      'ru',
                      'I''d like to invite you to our BBQ this weekend.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      431,
                      484679683,
                      'maintenance',
                      'обслуживание',
                      'en',
                      'ru',
                      'The maintenance guy said he''d fix the lights in the hallway tomorrow'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      432,
                      484679683,
                      'complaint',
                      'жалоба',
                      'en',
                      'ru',
                      'Who do I speak with about a noise complaint?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      433,
                      484679683,
                      'garbage',
                      'мусор',
                      'en',
                      'ru',
                      'Sorry about the garbage cans blocking the driveway, I''ll move them.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      434,
                      484679683,
                      'quiet',
                      'тихо',
                      'en',
                      'ru',
                      'It''s usually so quiet around here in the mornings.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      435,
                      484679683,
                      'rules',
                      'правила',
                      'en',
                      'ru',
                      'Are there any specific rules about using the pool?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      436,
                      484679683,
                      'property',
                      'собственность',
                      'en',
                      'ru',
                      'Who owns the property at the end of the street?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      437,
                      484679683,
                      'fence',
                      'забор',
                      'en',
                      'ru',
                      'Our fence got damaged in the storm last night.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      438,
                      484679683,
                      'shared',
                      'общий',
                      'en',
                      'ru',
                      'The basement laundry is a shared space, isn''t it?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      440,
                      484679683,
                      'security',
                      'безопасность',
                      'en',
                      'ru',
                      'The security in our building is excellent.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      441,
                      484679683,
                      'meeting',
                      'собрание',
                      'en',
                      'ru',
                      'Is the homeowners association meeting happening this Tuesday?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      442,
                      484679683,
                      'mail',
                      'почта',
                      'en',
                      'ru',
                      'Your mail got delivered to us by mistake.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      443,
                      484679683,
                      'package',
                      'посылка',
                      'en',
                      'ru',
                      'There''s a package for you in the lobby.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      444,
                      484679683,
                      'environment',
                      'окружающая среда',
                      'en',
                      'ru',
                      'We should do something about the environment, like organizing a clean-up.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      445,
                      484679683,
                      'lawn',
                      'газон',
                      'en',
                      'ru',
                      'Your lawn looks incredible! How do you keep it so green?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      446,
                      484679683,
                      'to meet',
                      'встретить',
                      'en',
                      'ru',
                      'Great to meet you, we just moved in next door.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      447,
                      484679683,
                      'to greet',
                      'поприветствовать',
                      'en',
                      'ru',
                      'I just wanted to greet our new neighbors and introduce ourselves.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      448,
                      484679683,
                      'to borrow',
                      'одолжить',
                      'en',
                      'ru',
                      'Could I borrow your lawn mower this weekend?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      449,
                      484679683,
                      'housewarming party',
                      'праздник новоселья',
                      'en',
                      'ru',
                      'We wanted to invite you to our housewarming party.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      450,
                      484679683,
                      'to complain',
                      'пожаловаться',
                      'en',
                      'ru',
                      'I hate to complain, but your dog has been barking early in the morning.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      451,
                      484679683,
                      'assist2',
                      'помочь',
                      'en',
                      'ru',
                      'Would you be able to assist me in moving this furniture?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      452,
                      484679683,
                      'to share',
                      'разделить (обязанности)',
                      'en',
                      'ru',
                      'We should share responsibilities for cleaning the stairs.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      453,
                      484679683,
                      'to respect',
                      'уважать',
                      'en',
                      'ru',
                      'It''s important to respect each other''s privacy.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      454,
                      484679683,
                      'disposal',
                      'утилизация, вывоз (мусора)',
                      'en',
                      'ru',
                      'We need to discuss the issue with trash disposal.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      455,
                      484679683,
                      'to apologize',
                      'извиниться',
                      'en',
                      'ru',
                      'I want to apologize for the loud music last night.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      456,
                      484679683,
                      'to maintain',
                      'поддерживать',
                      'en',
                      'ru',
                      'We all need to maintain the cleanliness of our shared spaces.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      457,
                      484679683,
                      'to cooperate',
                      'сотрудничать',
                      'en',
                      'ru',
                      'If we cooperate, we can make this a great place to live.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      458,
                      484679683,
                      'to resolve',
                      'решить2',
                      'en',
                      'ru',
                      'We need to resolve this issue as soon as possible.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      459,
                      484679683,
                      'nearby',
                      'рядом',
                      'en',
                      'ru',
                      'There''s a grocery store nearby.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      460,
                      484679683,
                      'safe',
                      'безопасно',
                      'en',
                      'ru',
                      'I feel really safe in this neighborhood.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      461,
                      484679683,
                      'recycling',
                      'перераб',
                      'en',
                      'ru',
                      'I think we should start recycling, it''s important for the environment.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      462,
                      484679683,
                      'stomping',
                      'топот',
                      'en',
                      'ru',
                      'We can hear stomping from your apartment, it''s a bit disturbing.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      463,
                      484679683,
                      'clean up',
                      'убрать',
                      'en',
                      'ru',
                      'Could you please clean up after your dog in the garden?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      464,
                      484679683,
                      'ceiling',
                      'потолок2',
                      'en',
                      'ru',
                      'There''s a water leak from my ceiling, I think it''s coming from your apartment.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      465,
                      484679683,
                      'renovation',
                      'ремонт',
                      'en',
                      'ru',
                      'Could you wait to start your renovation until after 9 am?'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      467,
                      484679683,
                      'tranquility',
                      'спокойствие (глубокое)',
                      'en',
                      'ru',
                      'We moved here for the tranquility, it''s so peaceful.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      468,
                      484679683,
                      'upstairs',
                      'наверху',
                      'en',
                      'ru',
                      'Every time the upstairs neighbors drop something, I half expect a bowling ball to come through the ceiling.'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      470,
                      484679683,
                      'edit',
                      'редактировать',
                      'en',
                      'ru',
                      'please, edit menu for our guests'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      471,
                      484679683,
                      'echo',
                      'эхо',
                      'en',
                      'ru',
                      'Listen echo'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      472,
                      484679683,
                      'table',
                      'стол',
                      'en',
                      'ru',
                      'breakfast  in the table'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      473,
                      484679683,
                      'hi',
                      'привет',
                      'en',
                      'ru',
                      ''
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      474,
                      484679683,
                      'test',
                      'тест',
                      'en',
                      'ru',
                      ''
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      475,
                      484679683,
                      'test2',
                      'тест2',
                      'en',
                      'ru',
                      ''
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      477,
                      484679683,
                      'cosmos',
                      'космос',
                      'en',
                      'ru',
                      ''
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      478,
                      484679683,
                      'test',
                      'test43',
                      'en',
                      'ru',
                      ''
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      479,
                      484679683,
                      'current2',
                      'тек2',
                      'en',
                      'ru',
                      ''
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      481,
                      484679683,
                      'ttt',
                      'ttt',
                      'en',
                      'ru',
                      ''
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      482,
                      484679683,
                      'tess',
                      'tess',
                      'en',
                      'ru',
                      ''
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      483,
                      484679683,
                      'watch',
                      'смотреть',
                      'en',
                      'ru',
                      ''
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      485,
                      484679683,
                      'qwer',
                      'вуцуц',
                      'en',
                      'ru',
                      ''
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      486,
                      5800537837,
                      'arise',
                      'возникать',
                      'en',
                      'ru',
                      ''
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      487,
                      484679683,
                      'hi',
                      'привет',
                      'en',
                      'ru',
                      ''
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      488,
                      484679683,
                      'tomic',
                      'dsaw',
                      'en',
                      'ru',
                      ''
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      489,
                      484679683,
                      'buy',
                      'купить',
                      'en',
                      'ru',
                      'I buy home'
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      490,
                      5800537837,
                      'to require',
                      'требовать',
                      'en',
                      'ru',
                      ''
                  );

INSERT INTO cards (
                      card_id,
                      user_id,
                      foreign_w,
                      native_w,
                      foreign_lang,
                      native_lang,
                      example
                  )
                  VALUES (
                      491,
                      484679683,
                      'Message',
                      'сообщение',
                      'en',
                      'ru',
                      ''
                  );


-- Таблица: maintenance_data
DROP TABLE IF EXISTS maintenance_data;

CREATE TABLE IF NOT EXISTS maintenance_data (
    user_id INTEGER PRIMARY KEY,
    chat_id INTEGER,
    msg_id  INTEGER,
    state   TEXT
);


-- Таблица: training_cards
DROP TABLE IF EXISTS training_cards;

CREATE TABLE IF NOT EXISTS training_cards (
    training_card_id INTEGER     PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER,
    card_id                      REFERENCES cards (card_id),
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
                           VALUES (
                               735,
                               5800537837,
                               370,
                               0,
                               1686142033,
                               1685208367
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               736,
                               5800537837,
                               370,
                               1,
                               1685788180,
                               1685090543
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               737,
                               5800537837,
                               371,
                               0,
                               1685788259,
                               1685090447
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               738,
                               5800537837,
                               371,
                               1,
                               1685607499,
                               1685262881
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               739,
                               5800537837,
                               372,
                               0,
                               1685788232,
                               1685090442
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               740,
                               5800537837,
                               372,
                               1,
                               1685339755,
                               1685208636
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               741,
                               5800537837,
                               373,
                               0,
                               1685788206,
                               1685090437
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               742,
                               5800537837,
                               373,
                               1,
                               1686141838,
                               1685208494
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               743,
                               5800537837,
                               374,
                               0,
                               1685788268,
                               1685090374
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               744,
                               5800537837,
                               374,
                               1,
                               1686141844,
                               1685208500
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               745,
                               5800537837,
                               375,
                               0,
                               1685788183,
                               1685090433
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               746,
                               5800537837,
                               375,
                               1,
                               1686141848,
                               1685208505
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               747,
                               5800537837,
                               376,
                               0,
                               1685788154,
                               1685090426
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               748,
                               5800537837,
                               376,
                               1,
                               1686141851,
                               1685208509
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               749,
                               5800537837,
                               377,
                               0,
                               1685788113,
                               1685090416
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               750,
                               5800537837,
                               377,
                               1,
                               1686141854,
                               1685208513
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               751,
                               5800537837,
                               378,
                               0,
                               1685788079,
                               1685090409
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               752,
                               5800537837,
                               378,
                               1,
                               1686141872,
                               1685208522
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               753,
                               5800537837,
                               379,
                               0,
                               1685788276,
                               1685090400
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               754,
                               5800537837,
                               379,
                               1,
                               1685788283,
                               1685090525
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               755,
                               5800537837,
                               380,
                               0,
                               1685788059,
                               1685090405
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               756,
                               5800537837,
                               380,
                               1,
                               1686141847,
                               1685208517
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               757,
                               5800537837,
                               381,
                               0,
                               1685607331,
                               1685262823
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               758,
                               5800537837,
                               381,
                               1,
                               1685788244,
                               1685090532
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               759,
                               5800537837,
                               382,
                               0,
                               1685565663,
                               1685218026
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               760,
                               5800537837,
                               382,
                               1,
                               1685648830,
                               1685044185
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               761,
                               5800537837,
                               383,
                               0,
                               1685649162,
                               1685044120
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               762,
                               5800537837,
                               383,
                               1,
                               1685787603,
                               1685090474
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               763,
                               5800537837,
                               384,
                               0,
                               1685649141,
                               1685044116
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               764,
                               5800537837,
                               384,
                               1,
                               1685787638,
                               1685090490
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               765,
                               5800537837,
                               385,
                               0,
                               1685649111,
                               1685044111
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               766,
                               5800537837,
                               385,
                               1,
                               1685787641,
                               1685090493
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               767,
                               5800537837,
                               386,
                               0,
                               1685272591,
                               1685208630
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               768,
                               5800537837,
                               386,
                               1,
                               1685649175,
                               1685044180
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               769,
                               5800537837,
                               387,
                               0,
                               1685649224,
                               1685044057
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               770,
                               5800537837,
                               387,
                               1,
                               1685787559,
                               1685090469
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               771,
                               5800537837,
                               388,
                               0,
                               1685282021,
                               1685218059
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               772,
                               5800537837,
                               388,
                               1,
                               1685648706,
                               1685044190
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               773,
                               5800537837,
                               389,
                               0,
                               1685272658,
                               1685208701
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               774,
                               5800537837,
                               389,
                               1,
                               1685649121,
                               1685044176
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               775,
                               5800537837,
                               390,
                               0,
                               1685649198,
                               1685044071
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               776,
                               5800537837,
                               390,
                               1,
                               1685787523,
                               1685090479
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               777,
                               5800537837,
                               391,
                               0,
                               1685649073,
                               1685044107
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               778,
                               5800537837,
                               391,
                               1,
                               1685787531,
                               1685090485
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               779,
                               5800537837,
                               392,
                               0,
                               1685649044,
                               1685044100
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               780,
                               5800537837,
                               392,
                               1,
                               1685787560,
                               1685090498
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               781,
                               5800537837,
                               393,
                               0,
                               1685649022,
                               1685044096
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               782,
                               5800537837,
                               393,
                               1,
                               1685787569,
                               1685090505
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               783,
                               5800537837,
                               394,
                               0,
                               1685395315,
                               1684959708
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               784,
                               5800537837,
                               394,
                               1,
                               1685384814,
                               1684959842
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               785,
                               5800537837,
                               395,
                               0,
                               1685395160,
                               1684959646
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               786,
                               5800537837,
                               395,
                               1,
                               1685513674,
                               1684999412
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               787,
                               5800537837,
                               396,
                               0,
                               1685514387,
                               1684999340
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               788,
                               5800537837,
                               396,
                               1,
                               1685384789,
                               1684959839
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               789,
                               5800537837,
                               397,
                               0,
                               1685514489,
                               1684999308
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               790,
                               5800537837,
                               397,
                               1,
                               1685705939,
                               1685208560
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               791,
                               5800537837,
                               398,
                               0,
                               1685395256,
                               1684959670
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               792,
                               5800537837,
                               398,
                               1,
                               1685385574,
                               1684959780
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               793,
                               5800537837,
                               399,
                               0,
                               1685514546,
                               1684999284
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               794,
                               5800537837,
                               399,
                               1,
                               1685513786,
                               1684999376
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               795,
                               5800537837,
                               400,
                               0,
                               1685482199,
                               1685044052
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               796,
                               5800537837,
                               400,
                               1,
                               1685513739,
                               1684999417
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               797,
                               5800537837,
                               401,
                               0,
                               1685395223,
                               1684959742
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               798,
                               5800537837,
                               401,
                               1,
                               1685385392,
                               1684959807
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               799,
                               5800537837,
                               402,
                               0,
                               1685705423,
                               1685208373
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               800,
                               5800537837,
                               402,
                               1,
                               1685513739,
                               1684999395
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               801,
                               5800537837,
                               403,
                               0,
                               1685482175,
                               1685044047
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               802,
                               5800537837,
                               403,
                               1,
                               1685513679,
                               1684999385
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               803,
                               5800537837,
                               404,
                               0,
                               1685705451,
                               1685208386
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               804,
                               5800537837,
                               404,
                               1,
                               1685384802,
                               1684959835
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               805,
                               5800537837,
                               405,
                               0,
                               1685482184,
                               1685044043
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               806,
                               5800537837,
                               405,
                               1,
                               1685513706,
                               1684999390
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               807,
                               5800537837,
                               406,
                               0,
                               1685283338,
                               1685262982
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               808,
                               5800537837,
                               406,
                               1,
                               1685705898,
                               1685208540
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               809,
                               5800537837,
                               407,
                               0,
                               1685395268,
                               1684959753
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               810,
                               5800537837,
                               407,
                               1,
                               1685384941,
                               1684959820
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               811,
                               5800537837,
                               408,
                               0,
                               1685395028,
                               1684959642
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               812,
                               5800537837,
                               408,
                               1,
                               1685513616,
                               1684999369
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               813,
                               5800537837,
                               409,
                               0,
                               1685514467,
                               1684999353
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               814,
                               5800537837,
                               409,
                               1,
                               1685513725,
                               1684999425
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               815,
                               5800537837,
                               410,
                               0,
                               1685283303,
                               1685262942
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               816,
                               5800537837,
                               410,
                               1,
                               1685513645,
                               1684999407
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               817,
                               5800537837,
                               411,
                               0,
                               1685514588,
                               1684999302
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               818,
                               5800537837,
                               411,
                               1,
                               1685513726,
                               1684999421
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               819,
                               5800537837,
                               412,
                               0,
                               1685395345,
                               1684959704
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               820,
                               5800537837,
                               412,
                               1,
                               1685513816,
                               1684999381
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               821,
                               5800537837,
                               413,
                               0,
                               1685514411,
                               1684999344
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               822,
                               5800537837,
                               413,
                               1,
                               1685385576,
                               1684959776
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               823,
                               5800537837,
                               414,
                               0,
                               1685395252,
                               1684959736
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               824,
                               5800537837,
                               414,
                               1,
                               1685638765,
                               1685044143
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               825,
                               5800537837,
                               415,
                               0,
                               1685514438,
                               1684999349
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               826,
                               5800537837,
                               415,
                               1,
                               1685371407,
                               1685262896
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               827,
                               5800537837,
                               416,
                               0,
                               1685283351,
                               1685262991
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               828,
                               5800537837,
                               416,
                               1,
                               1685705939,
                               1685208566
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               829,
                               5800537837,
                               417,
                               0,
                               1685395081,
                               1684959712
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               830,
                               5800537837,
                               417,
                               1,
                               1685513606,
                               1684999400
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               831,
                               5800537837,
                               418,
                               0,
                               1685395270,
                               1684959747
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               832,
                               5800537837,
                               418,
                               1,
                               1685647916,
                               1685044140
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               833,
                               5800537837,
                               419,
                               0,
                               1685395106,
                               1684959716
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               834,
                               5800537837,
                               419,
                               1,
                               1685482466,
                               1685044148
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               835,
                               484679683,
                               420,
                               0,
                               1684971819,
                               1684964619
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               836,
                               484679683,
                               420,
                               1,
                               1684886667,
                               1684879467
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               837,
                               484679683,
                               421,
                               0,
                               1685213277,
                               1685206077
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               838,
                               484679683,
                               421,
                               1,
-                              1,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               839,
                               484679683,
                               422,
                               0,
                               1684971791,
                               1684964591
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               840,
                               484679683,
                               422,
                               1,
                               1684972358,
                               1684965158
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               841,
                               484679683,
                               423,
                               0,
                               1685924513,
                               1685227771
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               842,
                               484679683,
                               423,
                               1,
                               1684886664,
                               1684879464
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               843,
                               484679683,
                               424,
                               0,
                               1684964283,
                               1684957083
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               844,
                               484679683,
                               424,
                               1,
-                              1,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               845,
                               484679683,
                               425,
                               0,
                               1684971803,
                               1684964603
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               846,
                               484679683,
                               425,
                               1,
                               1684972335,
                               1684965135
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               847,
                               484679683,
                               426,
                               0,
                               1684972255,
                               1684965055
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               848,
                               484679683,
                               426,
                               1,
                               1684971834,
                               1684964634
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               849,
                               484679683,
                               427,
                               0,
                               1685928025,
                               1685228956
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               850,
                               484679683,
                               427,
                               1,
                               1684886676,
                               1684879476
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               851,
                               484679683,
                               428,
                               0,
                               1685864565,
                               1685207420
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               852,
                               484679683,
                               428,
                               1,
                               1684972352,
                               1684965152
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               857,
                               484679683,
                               431,
                               0,
                               1684886651,
                               1684879451
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               858,
                               484679683,
                               431,
                               1,
                               1684971838,
                               1684964638
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               859,
                               484679683,
                               432,
                               0,
                               1685208451,
                               1685201251
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               860,
                               484679683,
                               432,
                               1,
                               1684972279,
                               1684965079
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               861,
                               484679683,
                               433,
                               0,
                               1685930875,
                               1685229903
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               862,
                               484679683,
                               433,
                               1,
                               1684972348,
                               1684965148
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               863,
                               484679683,
                               434,
                               0,
                               1684966517,
                               1684959317
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               864,
                               484679683,
                               434,
                               1,
                               1684881282,
                               1684879482
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               865,
                               484679683,
                               435,
                               0,
                               1684962785,
                               1684955585
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               866,
                               484679683,
                               435,
                               1,
                               1684886679,
                               1684879479
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               867,
                               484679683,
                               436,
                               0,
                               1685927101,
                               1685228639
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               868,
                               484679683,
                               436,
                               1,
-                              1,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               869,
                               484679683,
                               437,
                               0,
                               1684965755,
                               1684958555
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               870,
                               484679683,
                               437,
                               1,
                               1684971844,
                               1684964644
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               871,
                               484679683,
                               438,
                               0,
                               1685867571,
                               1685207305
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               872,
                               484679683,
                               438,
                               1,
                               1684971861,
                               1684964661
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               875,
                               484679683,
                               440,
                               0,
                               1684966438,
                               1684959238
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               876,
                               484679683,
                               440,
                               1,
                               1684971859,
                               1684964659
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               877,
                               484679683,
                               441,
                               0,
                               1685864568,
                               1685207416
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               878,
                               484679683,
                               441,
                               1,
                               1684971849,
                               1684964649
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               879,
                               484679683,
                               442,
                               0,
                               1685930888,
                               1685229914
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               880,
                               484679683,
                               442,
                               1,
-                              1,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               881,
                               484679683,
                               443,
                               0,
                               1685864841,
                               1685207877
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               882,
                               484679683,
                               443,
                               1,
                               1684971846,
                               1684964646
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               883,
                               484679683,
                               444,
                               0,
                               1684965694,
                               1684958494
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               884,
                               484679683,
                               444,
                               1,
-                              1,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               885,
                               484679683,
                               445,
                               0,
                               1684966962,
                               1684965162
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               886,
                               484679683,
                               445,
                               1,
                               1684972274,
                               1684965074
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               887,
                               484679683,
                               446,
                               0,
                               1684886633,
                               1684879433
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               888,
                               484679683,
                               446,
                               1,
-                              1,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               889,
                               484679683,
                               447,
                               0,
                               1685868670,
                               1685207254
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               890,
                               484679683,
                               447,
                               1,
                               1684972345,
                               1684965145
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               891,
                               484679683,
                               448,
                               0,
                               1684886639,
                               1684879439
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               892,
                               484679683,
                               448,
                               1,
                               1684972277,
                               1684965077
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               893,
                               484679683,
                               449,
                               0,
                               1686014772,
                               1685201258
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               894,
                               484679683,
                               449,
                               1,
                               1684886657,
                               1684879457
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               895,
                               484679683,
                               450,
                               0,
                               1684886637,
                               1684879437
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               896,
                               484679683,
                               450,
                               1,
-                              1,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               897,
                               484679683,
                               451,
                               0,
                               1685236989,
                               1685229789
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               898,
                               484679683,
                               451,
                               1,
-                              1,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               899,
                               484679683,
                               452,
                               0,
                               1684966964,
                               1684965164
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               900,
                               484679683,
                               452,
                               1,
                               1684966967,
                               1684965167
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               901,
                               484679683,
                               453,
                               0,
                               1684972260,
                               1684965060
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               902,
                               484679683,
                               453,
                               1,
                               1684972314,
                               1684965114
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               903,
                               484679683,
                               454,
                               0,
                               1685550004,
                               1685045806
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               904,
                               484679683,
                               454,
                               1,
                               1684971827,
                               1684964627
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               905,
                               484679683,
                               455,
                               0,
                               1685864392,
                               1685207725
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               906,
                               484679683,
                               455,
                               1,
                               1684972341,
                               1684965141
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               907,
                               484679683,
                               456,
                               0,
                               1684972245,
                               1684965045
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               908,
                               484679683,
                               456,
                               1,
                               1684971829,
                               1684964629
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               909,
                               484679683,
                               457,
                               0,
                               1684971800,
                               1684964600
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               910,
                               484679683,
                               457,
                               1,
                               1684886659,
                               1684879459
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               911,
                               484679683,
                               458,
                               0,
                               1684971794,
                               1684964594
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               912,
                               484679683,
                               458,
                               1,
                               1684972317,
                               1684965117
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               913,
                               484679683,
                               459,
                               0,
                               1686029307,
                               1685206080
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               914,
                               484679683,
                               459,
                               1,
                               1684886662,
                               1684879462
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               915,
                               484679683,
                               460,
                               0,
                               1685867593,
                               1685207303
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               916,
                               484679683,
                               460,
                               1,
                               1684972343,
                               1684965143
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               917,
                               484679683,
                               461,
                               0,
                               1685053451,
                               1685046251
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               918,
                               484679683,
                               461,
                               1,
                               1684972271,
                               1684965071
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               919,
                               484679683,
                               462,
                               0,
                               1685052964,
                               1685045764
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               920,
                               484679683,
                               462,
                               1,
                               1684886654,
                               1684879454
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               921,
                               484679683,
                               463,
                               0,
                               1684886630,
                               1684879430
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               922,
                               484679683,
                               463,
                               1,
                               1684886670,
                               1684879470
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               923,
                               484679683,
                               464,
                               0,
                               1684963984,
                               1684956784
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               924,
                               484679683,
                               464,
                               1,
                               1684971854,
                               1684964654
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               925,
                               484679683,
                               465,
                               0,
                               1684971788,
                               1684964588
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               926,
                               484679683,
                               465,
                               1,
                               1684971842,
                               1684964642
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               929,
                               484679683,
                               467,
                               0,
                               1685928017,
                               1685228948
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               930,
                               484679683,
                               467,
                               1,
                               1684972337,
                               1684965137
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               931,
                               484679683,
                               468,
                               0,
                               1685867806,
                               1685206904
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               932,
                               484679683,
                               468,
                               1,
                               1684972269,
                               1684965069
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               935,
                               484679683,
                               470,
                               0,
                               1684951356,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               936,
                               484679683,
                               470,
                               1,
                               1684951355,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               937,
                               484679683,
                               471,
                               0,
                               1684952162,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               938,
                               484679683,
                               471,
                               1,
                               1684952162,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               939,
                               484679683,
                               472,
                               0,
                               1684954313,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               940,
                               484679683,
                               472,
                               1,
                               1684954313,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               941,
                               484679683,
                               473,
                               0,
                               1684954703,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               942,
                               484679683,
                               473,
                               1,
                               1684954703,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               943,
                               484679683,
                               474,
                               0,
                               1684954806,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               944,
                               484679683,
                               474,
                               1,
                               1684954806,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               945,
                               484679683,
                               475,
                               0,
                               1684955004,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               946,
                               484679683,
                               475,
                               1,
                               1684955004,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               949,
                               484679683,
                               477,
                               0,
                               1684955542,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               950,
                               484679683,
                               477,
                               1,
                               1684955542,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               951,
                               484679683,
                               478,
                               0,
                               1684956741,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               952,
                               484679683,
                               478,
                               1,
                               1684956741,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               953,
                               484679683,
                               479,
                               0,
                               1684956857,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               954,
                               484679683,
                               479,
                               1,
                               1684956857,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               957,
                               484679683,
                               481,
                               0,
                               1684957094,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               958,
                               484679683,
                               481,
                               1,
                               1684957094,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               959,
                               484679683,
                               482,
                               0,
                               1684957283,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               960,
                               484679683,
                               482,
                               1,
                               1684957283,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               961,
                               484679683,
                               483,
                               0,
                               1684958543,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               962,
                               484679683,
                               483,
                               1,
                               1684958543,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               965,
                               484679683,
                               485,
                               0,
                               1684971816,
                               1684964616
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               966,
                               484679683,
                               485,
                               1,
                               1684972339,
                               1684965139
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               967,
                               5800537837,
                               486,
                               0,
                               1685264761,
                               1685262961
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               968,
                               5800537837,
                               486,
                               1,
                               1685626871,
                               1685208530
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               969,
                               484679683,
                               487,
                               0,
                               1684966960,
                               1684965160
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               970,
                               484679683,
                               487,
                               1,
                               1684972350,
                               1684965150
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               971,
                               484679683,
                               488,
                               0,
                               1685052971,
                               1685045771
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               972,
                               484679683,
                               488,
                               1,
-                              1,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               973,
                               484679683,
                               489,
                               0,
                               1685045887,
                               1685038687
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               974,
                               484679683,
                               489,
                               1,
-                              1,
-                              1
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               975,
                               5800537837,
                               490,
                               0,
                               1685264701,
                               1685262901
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               976,
                               5800537837,
                               490,
                               1,
                               1685272313,
                               1685262948
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               977,
                               484679683,
                               491,
                               0,
                               1685234409,
                               1685227209
                           );

INSERT INTO training_cards (
                               training_card_id,
                               user_id,
                               card_id,
                               direction,
                               next_training_t,
                               last_training_t
                           )
                           VALUES (
                               978,
                               484679683,
                               491,
                               1,
-                              1,
-                              1
                           );


-- Таблица: user_config
DROP TABLE IF EXISTS user_config;

CREATE TABLE IF NOT EXISTS user_config (
    user_id               INTEGER     PRIMARY KEY,
    chat_id               INTEGER,
    state                 INTEGER,
    m1_msg_id             INTEGER,
    o_param               INTEGER     DEFAULT (2),
    forgetting_rate       REAL        DEFAULT (0.1),
    foreign_lang          TEXT (2)    NOT NULL,
    use_audio_examples    INTEGER (1) DEFAULT (1),
    use_examples          INTEGER (1) DEFAULT (1),
    min_trening_interval  INTEGER,
    min_cards_for_trening INTEGER,
    max_cards_for_trening INTEGER,
    first_access          INTEGER,
    last_access           INTEGER
);

INSERT INTO user_config (
                            user_id,
                            chat_id,
                            state,
                            m1_msg_id,
                            o_param,
                            forgetting_rate,
                            foreign_lang,
                            use_audio_examples,
                            use_examples,
                            min_trening_interval,
                            min_cards_for_trening,
                            max_cards_for_trening,
                            first_access,
                            last_access
                        )
                        VALUES (
                            484679683,
                            484679683,
                            NULL,
                            NULL,
                            2,
                            0.1,
                            'en',
                            1,
                            1,
                            3600,
                            12,
                            24,
                            1684793519,
                            1685233049
                        );

INSERT INTO user_config (
                            user_id,
                            chat_id,
                            state,
                            m1_msg_id,
                            o_param,
                            forgetting_rate,
                            foreign_lang,
                            use_audio_examples,
                            use_examples,
                            min_trening_interval,
                            min_cards_for_trening,
                            max_cards_for_trening,
                            first_access,
                            last_access
                        )
                        VALUES (
                            5800537837,
                            5800537837,
                            NULL,
                            NULL,
                            2,
                            0.1,
                            'en',
                            1,
                            1,
                            3600,
                            12,
                            24,
                            1684824959,
                            1685262749
                        );


-- Таблица: word_set
DROP TABLE IF EXISTS word_set;

CREATE TABLE IF NOT EXISTS word_set (
    id        INTEGER  PRIMARY KEY AUTOINCREMENT,
    f_word    TEXT     NOT NULL,
    f_lang    TEXT (2) NOT NULL
                       DEFAULT en,
    f_example TEXT,
    topic     TEXT,
    tr1_lang  TEXT (2),
    tr1       TEXT
);

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         1,
                         'neighbor',
                         'en',
                         'Hey, neighbor, could you watch my cat this weekend?',
                         'neighbours',
                         'ru',
                         'сосед'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         2,
                         'apartment',
                         'en',
                         'I can''t believe how quickly the apartment across from mine got rented.',
                         'neighbours',
                         'ru',
                         'квартира'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         3,
                         'community',
                         'en',
                         'Our community is planning a yard sale next month',
                         'neighbours',
                         'ru',
                         'сообщество'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         4,
                         'house',
                         'en',
                         'Did you see the paint color they chose for the house down the street?',
                         'neighbours',
                         'ru',
                         'дом'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         5,
                         'issue',
                         'en',
                         'We need to talk about a serious issue.',
                         'neighbours',
                         'ru',
                         'проблема'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         6,
                         'pet',
                         'en',
                         'Your pet is adorable! What''s its name?',
                         'neighbours',
                         'ru',
                         'домашнее животное'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         7,
                         'parking',
                         'en',
                         'Parking is such a nightmare after 5 PM here.',
                         'neighbours',
                         'ru',
                         'парковка'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         8,
                         'party',
                         'en',
                         'We had a little party last night, hope we didn''t disturb you.',
                         'neighbours',
                         'ru',
                         'вечеринка'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         9,
                         'invite',
                         'en',
                         'I''d like to invite you to our BBQ this weekend.',
                         'neighbours',
                         'ru',
                         'пригласить'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         10,
                         'adorable',
                         'en',
                         'Your new puppy is absolutely adorable! How old is he?',
                         'neighbours',
                         'ru',
                         'очаровательный'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         11,
                         'garden',
                         'en',
                         'Your garden is the best on the block!',
                         'neighbours',
                         'ru',
                         'сад'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         12,
                         'maintenance',
                         'en',
                         'The maintenance guy said he''d fix the lights in the hallway tomorrow',
                         'neighbours',
                         'ru',
                         'обслуживание'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         13,
                         'complaint',
                         'en',
                         'Who do I speak with about a noise complaint?',
                         'neighbours',
                         'ru',
                         'жалоба'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         14,
                         'garbage',
                         'en',
                         'Sorry about the garbage cans blocking the driveway, I''ll move them.',
                         'neighbours',
                         'ru',
                         'мусор'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         15,
                         'quiet',
                         'en',
                         'It''s usually so quiet around here in the mornings.',
                         'neighbours',
                         'ru',
                         'тихо'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         16,
                         'rules',
                         'en',
                         'Are there any specific rules about using the pool?',
                         'neighbours',
                         'ru',
                         'правила'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         17,
                         'property',
                         'en',
                         'Who owns the property at the end of the street?',
                         'neighbours',
                         'ru',
                         'собственность'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         18,
                         'fence',
                         'en',
                         'Our fence got damaged in the storm last night.',
                         'neighbours',
                         'ru',
                         'забор'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         19,
                         'shared',
                         'en',
                         'The basement laundry is a shared space, isn''t it?',
                         'neighbours',
                         'ru',
                         'общий'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         20,
                         'courtesy',
                         'en',
                         'Just as a courtesy, I thought I''d let you know we''re having people over tonight.',
                         'neighbours',
                         'ru',
                         'вежливость'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         21,
                         'security',
                         'en',
                         'The security in our building is excellent.',
                         'neighbours',
                         'ru',
                         'безопасность'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         22,
                         'meeting',
                         'en',
                         'Is the homeowners association meeting happening this Tuesday?',
                         'neighbours',
                         'ru',
                         'собрание'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         23,
                         'mail',
                         'en',
                         'Your mail got delivered to us by mistake.',
                         'neighbours',
                         'ru',
                         'почта'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         24,
                         'package',
                         'en',
                         'There''s a package for you in the lobby.',
                         'neighbours',
                         'ru',
                         'посылка'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         25,
                         'environment',
                         'en',
                         'We should do something about the environment, like organizing a clean-up.',
                         'neighbours',
                         'ru',
                         'окружающая среда'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         26,
                         'lawn',
                         'en',
                         'Your lawn looks incredible! How do you keep it so green?',
                         'neighbours',
                         'ru',
                         'газон'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         27,
                         'to meet',
                         'en',
                         'Great to meet you, we just moved in next door.',
                         'neighbours',
                         'ru',
                         'встретить'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         28,
                         'to greet',
                         'en',
                         'I just wanted to greet our new neighbors and introduce ourselves.',
                         'neighbours',
                         'ru',
                         'поприветствовать'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         29,
                         'to borrow',
                         'en',
                         'Could I borrow your lawn mower this weekend?',
                         'neighbours',
                         'ru',
                         'одолжить'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         30,
                         'housewarming party',
                         'en',
                         'We wanted to invite you to our housewarming party.',
                         'neighbours',
                         'ru',
                         'праздник новоселья'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         31,
                         'to complain',
                         'en',
                         'I hate to complain, but your dog has been barking early in the morning.',
                         'neighbours',
                         'ru',
                         'пожаловаться'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         32,
                         'to assist',
                         'en',
                         'Would you be able to assist me in moving this furniture?',
                         'neighbours',
                         'ru',
                         'помочь'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         33,
                         'to share',
                         'en',
                         'We should share responsibilities for cleaning the stairs.',
                         'neighbours',
                         'ru',
                         'разделить (обязанности)'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         34,
                         'to respect',
                         'en',
                         'It''s important to respect each other''s privacy.',
                         'neighbours',
                         'ru',
                         'уважать'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         35,
                         'disposal',
                         'en',
                         'We need to discuss the issue with trash disposal.',
                         'neighbours',
                         'ru',
                         'утилизация, вывоз (мусора)'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         36,
                         'to apologize',
                         'en',
                         'I want to apologize for the loud music last night.',
                         'neighbours',
                         'ru',
                         'извиниться'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         37,
                         'to maintain',
                         'en',
                         'We all need to maintain the cleanliness of our shared spaces.',
                         'neighbours',
                         'ru',
                         'поддерживать'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         38,
                         'to cooperate',
                         'en',
                         'If we cooperate, we can make this a great place to live.',
                         'neighbours',
                         'ru',
                         'сотрудничать'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         39,
                         'to resolve',
                         'en',
                         'We need to resolve this issue as soon as possible.',
                         'neighbours',
                         'ru',
                         'решить'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         40,
                         'nearby',
                         'en',
                         'There''s a grocery store nearby.',
                         'neighbours',
                         'ru',
                         'рядом'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         41,
                         'safe',
                         'en',
                         'I feel really safe in this neighborhood.',
                         'neighbours',
                         'ru',
                         'безопасно'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         42,
                         'recycling',
                         'en',
                         'I think we should start recycling, it''s important for the environment.',
                         'neighbours',
                         'ru',
                         'переработка(отходов)'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         43,
                         'stomping',
                         'en',
                         'We can hear stomping from your apartment, it''s a bit disturbing.',
                         'neighbours',
                         'ru',
                         'топот'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         44,
                         'clean up',
                         'en',
                         'Could you please clean up after your dog in the garden?',
                         'neighbours',
                         'ru',
                         'убрать'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         45,
                         'ceiling',
                         'en',
                         'There''s a water leak from my ceiling, I think it''s coming from your apartment.',
                         'neighbours',
                         'ru',
                         'потолок'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         46,
                         'renovation',
                         'en',
                         'Could you wait to start your renovation until after 9 am?',
                         'neighbours',
                         'ru',
                         'ремонт'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         47,
                         'concern',
                         'en',
                         'I understand your concern about the noise.',
                         'neighbours',
                         'ru',
                         'беспокойство'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         48,
                         'tranquility',
                         'en',
                         'We moved here for the tranquility, it''s so peaceful.',
                         'neighbours',
                         'ru',
                         'спокойствие (глубокое)'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         49,
                         'upstairs',
                         'en',
                         'Every time the upstairs neighbors drop something, I half expect a bowling ball to come through the ceiling.',
                         'neighbours',
                         'ru',
                         'наверху'
                     );

INSERT INTO word_set (
                         id,
                         f_word,
                         f_lang,
                         f_example,
                         topic,
                         tr1_lang,
                         tr1
                     )
                     VALUES (
                         50,
                         'downstairs',
                         'en',
                         'I think my downstairs neighbors might be vampires, they''re only active after midnight!',
                         'neighbours',
                         'ru',
                         'внизу'
                     );


-- Триггер: create_training_cards
DROP TRIGGER IF EXISTS create_training_cards;
CREATE TRIGGER IF NOT EXISTS create_training_cards
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


-- Триггер: delete_training_cards
DROP TRIGGER IF EXISTS delete_training_cards;
CREATE TRIGGER IF NOT EXISTS delete_training_cards
                       AFTER DELETE
                          ON cards
                    FOR EACH ROW
BEGIN
    DELETE FROM training_cards
          WHERE card_id = OLD.card_id;
END;


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
