import sqlite3

conn = sqlite3.connect("preCC_SQL_injection.db")
cursor = conn.cursor()
cursor.execute("""
    SELECT name FROM teams UNION SELECT Username FROM players
""")
print(cursor.fetchall())
print()

cursor.execute("""
    SELECT ranking, ranking.username FROM ranking JOIN teams ON ranking.teamID == teams.id JOIN players on ranking.playerID == players.id
""")
print(cursor.fetchall())



conn.close()