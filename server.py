import sqlite3

conn = sqlite3.connect("preCC_SQL_injection.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        name TEXT NOT NULL,
        glob_pos INTEGER NOT NULL,
        nat_pos INTEGER NOT NULL,
        points INTEGER NOT NULL,
        UNIQUE(name)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        teamID INTEGER NOT NULL,
        FOREIGN KEY(teamID) REFERENCES teams(id)
    )
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS rankings (
        position INTEGER,
        username TEXT NOT NULL,
        playerID INTEGER NOT NULL,
        teamID INTEGER NOT NULL,
        FOREIGN KEY(teamID) REFERENCES teams(id)
        FOREIGN KEY(playerID) REFERENCES players(id)
        PRIMARY KEY (playerID, teamID)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
""")

team_data = [["a:b", "about:blankets", "22", "1", "413"], 
                ["ITA", "TeamItaly", "35", "2", "355"],
                ["PTM", "pwnthem0le", "43", "3", "333"],
                ["MadrHacks", "MadrHacks", "45", "4", "331"],
                ["mhackeroni", "mhackeroni", "55", "5", "293"],
                ["ToH", "Tower of Hanoi", "60", "6", "285"],
                ["Srdnlen", "Srdnlen", "78", "7", "264"],
                ["fibonhack", "fibonhack", "81", "8", "261"],
                ["TRX", "TheRomanXpl0it", "85", "9", "253"],
                ["b2s", "born2scan", "129", "10", "190"],
                ["RdC", "Rubi di Cubrik", "145", "11", "175"],
                ["Hackappatoi", "Hackappati", "150", "12", "173"],
                ["HackDagos", "HackDagos", "208", "13", "136"],
                ["z:h", "ZenHack", "220", "14", "133"],
                ["pwn0tt1", "Pwnzer0tt1", "230", "15", "130"]] 

player_data = [["Giulia", "1", "ubqwheewe"],
                ["Loldemort", "2", "absdubedb"],
                ["matpro", "3", "ane9uw94r"],
                ["C0mm4nd_", "4", "qojw3ur32hr"],
                ["dp_1", "5", "andsnf'"],
                ["Chino", "6", "i0s0ifd"],
                ["ricchi24", "7", "aksndaenae"],
                ["maitai", "8", "qowjqpN+ù"],
                ["salvatoreabello@gmail.com", "15", "ADNSKNFNkan"],
                ["cristian@gmal.com", "14", "QNNEWJ0J9jojq"]]

ranking_data = [["20", "Loldemort", "2", "2"]]

for i in team_data:
    cursor.execute("""
        INSERT INTO teams (code, name, glob_pos, nat_pos, points)
        VALUES (?, ?, ?, ?, ?)
    """, i)

for i in player_data:
    cursor.execute("""
        INSERT INTO players (username, teamID, password)
        VALUES (?, ?, ?)
    """, i)

for i in ranking_data:
    cursor.execute("""
        INSERT INTO rankings (position, username, playerID, teamID)
        VALUES (?, ?, ?, ?)
    """, i)

# Da notare che tra le tabelle presenti nel DB è presente sqlite_sequence che tiene traccia delle tabelle che usano
# AUTOINCREMENT,  per tracciare l'ultimo valore utilizzato delle colonne autoincrementali  

conn.commit()
conn.close()