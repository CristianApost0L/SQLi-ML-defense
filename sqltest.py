import sqlite3

# Creare una connessione al database
conn = sqlite3.connect("file:preCC_SQL_injection.db", uri=True)

# Creare un cursore per eseguire comandi SQL
cursor = conn.cursor()

user = "ciaooooo"
passw = "cosaooo') ; DELETE FROM players WHERE 1=1; -- "
team = "4"
query = "INSERT INTO players (username, password, teamID) VALUES ('" + user + "','" + team + "','"+ passw + ")"
print(query)

# Eseguire una query sulla tabella sqlite_master
#cursor.executescript(query)
cursor.execute("SELECT * FROM players")

# Recuperare e stampare i risultati
tables = cursor.fetchall()
for table in tables:
    print(table)
    print()
    print()

# Chiudere la connessione
conn.close()