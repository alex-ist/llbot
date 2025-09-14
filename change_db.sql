PRAGMA foreign_keys = 0;

CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                          FROM c_dict_pron;

DROP TABLE c_dict_pron;

CREATE TABLE c_dict_pron (
    fw        TEXT     ,
    hw        TEXT     NOT NULL,
    pos       TEXT     NOT NULL,
    entry_num INTEGER  NOT NULL,
    region    TEXT (2) NOT NULL,
    ipa       TEXT     NOT NULL,
    fn        TEXT
);

INSERT INTO c_dict_pron (
                            hw,
                            pos,
                            entry_num,
                            region,
                            ipa,
                            fn
                        )
                        SELECT hw,
                               pos,
                               entry_num,
                               region,
                               ipa,
                               fn
                          FROM sqlitestudio_temp_table;

DROP TABLE sqlitestudio_temp_table;

PRAGMA foreign_keys = 1;



DELETE FROM c_dict
WHERE
    fw LIKE 'deprec%' OR hw LIKE 'deprec%' OR
    fw LIKE 'kick%'   OR hw LIKE 'kick%'   OR
    fw LIKE 'enga%'   OR hw LIKE 'enga%'   OR
    fw LIKE 'make%'   OR hw LIKE 'make%'   OR
    fw LIKE 'lock%'   OR hw LIKE 'lock%'   OR
    fw LIKE 'mess%'   OR hw LIKE 'mess%'   OR
    fw LIKE 'run%'    OR hw LIKE 'run%'    OR
	fw LIKE 'stem%'    OR hw LIKE 'stem%'    OR
	fw LIKE 'guide%'    OR hw LIKE 'guide%'    OR
	fw LIKE 'Beetle%'    OR hw LIKE 'Beetle%'    OR
	fw LIKE 'near%'    OR hw LIKE 'near%'    OR
	fw LIKE '%fold'    OR hw LIKE '%fold'    OR
	fw LIKE 'requir%'    OR hw LIKE 'requir%'    OR
	fw LIKE '%scope'    OR hw LIKE '%scope'    OR
    fw IN ('shame', 'indeed', 'gosh', 'bother', 'blast', 'own', 'certain', 'once') OR
    hw IN ('shame', 'indeed', 'gosh', 'bother', 'blast', 'own', 'certain', 'once');

DELETE FROM c_dict_pron
WHERE
    fw LIKE 'deprec%' OR hw LIKE 'deprec%' OR
    fw LIKE 'kick%'   OR hw LIKE 'kick%'   OR
    fw LIKE 'enga%'   OR hw LIKE 'enga%'   OR
    fw LIKE 'make%'   OR hw LIKE 'make%'   OR
    fw LIKE 'lock%'   OR hw LIKE 'lock%'   OR
    fw LIKE 'mess%'   OR hw LIKE 'mess%'   OR
    fw LIKE 'run%'    OR hw LIKE 'run%'    OR
	fw LIKE 'stem%'    OR hw LIKE 'stem%'    OR
	fw LIKE 'guide%'    OR hw LIKE 'guide%'    OR
	fw LIKE 'Beetle%'    OR hw LIKE 'Beetle%'    OR
	fw LIKE 'near%'    OR hw LIKE 'near%'    OR
	fw LIKE '%fold'    OR hw LIKE '%fold'    OR
	fw LIKE 'requir%'    OR hw LIKE 'requir%'    OR
	fw LIKE '%scope'    OR hw LIKE '%scope'    OR
    fw IN ('shame', 'indeed', 'gosh', 'bother', 'blast', 'own', 'certain', 'once') OR
    hw IN ('shame', 'indeed', 'gosh', 'bother', 'blast', 'own', 'certain', 'once');


UPDATE c_dict_pron
SET fw = (
    SELECT fw
    FROM c_dict
    WHERE c_dict.hw = c_dict_pron.hw
)
WHERE fw IS NULL
  AND hw IN (
      SELECT hw
      FROM c_dict
      GROUP BY hw
      HAVING COUNT(*) = 1
  );
  
PRAGMA foreign_keys = 0;

CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                          FROM c_dict_pron;

DROP TABLE c_dict_pron;

CREATE TABLE c_dict_pron (
    fw        TEXT     NOT NULL,
    hw        TEXT     NOT NULL,
    pos       TEXT     NOT NULL,
    entry_num INTEGER  NOT NULL,
    region    TEXT (2) NOT NULL,
    ipa       TEXT     NOT NULL,
    fn        TEXT
);

INSERT INTO c_dict_pron (
                            fw,
                            hw,
                            pos,
                            entry_num,
                            region,
                            ipa,
                            fn
                        )
                        SELECT fw,
                               hw,
                               pos,
                               entry_num,
                               region,
                               ipa,
                               fn
                          FROM sqlitestudio_temp_table;

DROP TABLE sqlitestudio_temp_table;

PRAGMA foreign_keys = 1;














====



PRAGMA foreign_keys = 0;

CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                          FROM c_dict;

DROP TABLE c_dict;

CREATE TABLE c_dict (
    fw         TEXT,
    source_url TEXT,
    is_pron    INTEGER
);

INSERT INTO c_dict (
                       fw,
                       source_url,
                       is_pron
                   )
                   SELECT fw,
                          source_url,
                          is_pron
                     FROM sqlitestudio_temp_table;

DROP TABLE sqlitestudio_temp_table;

PRAGMA foreign_keys = 1;



