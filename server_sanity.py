import sqlite3

conn = sqlite3.connect("preCC_SQL_injection.db")
cursor = conn.cursor()
cursor.execute("""
    SELECT name FROM teams UNION SELECT Username FROM players
""")
print(cursor.fetchall())

print()

cursor.execute("""
    SELECT rankings.position, rankings.username FROM rankings JOIN teams ON rankings.teamID == teams.id JOIN players on rankings.playerID == players.id
""")
print(cursor.fetchall())

print()

cursor.execute("""
    SELECT username FROM users
""")
print(cursor.fetchall())



conn.close()