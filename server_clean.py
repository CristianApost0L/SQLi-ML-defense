import sqlite3


# Collegamento al database
conn = sqlite3.connect('preCC_SQL_injection.db')
cursor = conn.cursor()

# Funzione per cancellare tutti i dati da tutte le tabelle
def clear_all_tables():
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table_name in tables:
        cursor.execute(f'DELETE FROM {table_name[0]};')
        conn.commit()
        print(f'Dati cancellati dalla tabella {table_name[0]}')

# Eseguire la funzione
clear_all_tables()

# Chiudere la connessione
conn.close()


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
        password TEXT NOT NULL,
        profile_pic BLOB DEFAULT NULL
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

player_data = [["Giulia", "1"],
                ["Loldemort", "2"],
                ["matpro", "3"],
                ["C0mm4nd_", "4"],
                ["dp_1", "5"],
                ["Chino", "6"],
                ["ricchi24", "7"],
                ["maitai", "8"]]


user_data = [["salvatoreabello@gmail.com", "ADNSKNFNkan"],
                ["cristian@gmail.com", "QNNEWJ0J9jojq"],
                ["admin","unadminsolitario1234"]]

ranking_data = [
    ["20", "Loldemort", "2", "2"],
    ["5", "Giulia", "1", "1"],
    ["15", "matpro", "3", "3"],
    ["10", "C0mm4nd_", "4", "4"],
    ["25", "dp_1", "5", "5"],
    ["30", "Chino", "6", "6"],
    ["35", "ricchi24", "7", "7"],
    ["40", "maitai", "8", "8"],
    ["22", "Giulia", "1", "2"],
    ["50", "matpro", "3", "10"],  
    ["60", "C0mm4nd_", "4", "12"],  
    ["65", "dp_1", "5", "13"],    
    ["70", "Chino", "6", "14"],   
    ["75", "ricchi24", "7", "15"],
]

for i in team_data:
    cursor.execute("""
        INSERT INTO teams (code, name, glob_pos, nat_pos, points)
        VALUES (?, ?, ?, ?, ?)
    """, i)

for i in player_data:
    cursor.execute("""
        INSERT INTO players (username, teamID)
        VALUES (?, ?)
    """, i)

for i in ranking_data:
    cursor.execute("""
        INSERT INTO rankings (position, username, playerID, teamID)
        VALUES (?, ?, ?, ?)
    """, i)

for i in user_data:
    cursor.execute("""
        INSERT INTO users (username, password)
        VALUES (?, ?)
    """, i)

# Da notare che tra le tabelle presenti nel DB è presente sqlite_sequence che tiene traccia delle tabelle che usano
# AUTOINCREMENT,  per tracciare l'ultimo valore utilizzato delle colonne autoincrementali  

conn.commit()
conn.close()