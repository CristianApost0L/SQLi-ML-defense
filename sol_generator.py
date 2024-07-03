# send query and save result on file
# Usage: python sol.py <query> <output_file>
# Example: python sol.py "SELECT * FROM users" users.txt

import sqlite3
import sys


#Use it too generate solution of the challanges

conn = sqlite3.connect("preCC_SQL_injection.db")
cursor = conn.cursor()

# Reads all queries from "queries.sql"
with open("sol/queries.sql", "r") as query_file:
    lines = query_file.readlines()

for line in lines:
    query, _, output_file = line.partition("--")
    query = query.strip()
    output_file = output_file.strip()
    
    cursor.execute(query)
    
    # Exec all queries and stamp the output on ./sol/i file
    with open("sol/" + output_file, "w") as f:
        f.write(str(cursor.fetchall()))

conn.close()

