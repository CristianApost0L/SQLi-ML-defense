from flask import Flask, request, render_template, flash, session
import sqlite3
import os
from flags import flags

# creazione di un dizionario dalla directory sol, sono le challange da fare
solves = {}
for file in os.listdir("./sol"):
    with open("./sol/" + file) as f:
        solves[file] = f.read()


app = Flask(__name__)
app.secret_key = 'security_homework_tanto_è_lunga'  # Necessario per gestire le sessioni e i messaggi flash


# se siamo nella root verrà renderizzata la pagina di index
@app.route('/')
def home():
    return render_template('index.html')

# per ogni root /exec, dopo aver cliccato il bottone ricerca, verrà reinderizzata la stessa pagina eseguita una query verso il DBMS
@app.route('/exec', methods=['POST'])
def search():
    # query da eseguire, si compone di una SELECT sulla tabella Teams con una ricerca basata sul nome dato in input dall'utente.
    # Rapprensenta la nostra vulnerabilità.
    query = "SELECT id, name, points FROM teams WHERE name = '" + request.form['query'] + "'"
    
    conn = sqlite3.connect("file:preCC_SQL_injection.db?mode=ro", uri=True) #inizializzazione della connessione con il database
    cursor = conn.cursor() # ci permette di eseguire la query nel nostro DB in modalità di sola lettura

    try:
        cursor.execute(query) # esecuzione della query
        results = cursor.fetchall() # caricamento del risultato della query in results
        # Questa variabile conterrà una lista di tuple, dove ogni tupla rappresenta una riga del risultato della query. 
        # Ogni elemento della tupla corrisponde a una colonna della tabella selezionata nella query.

        str_res = str(results)  # conversione della results in una stringa

        cols = []   # colonne della nostra query
        if cursor.description:
            # search columns from cursor descriptor, we need to stamp them on index page
            # ricerca della colonne che dovranno essere stamate da curso descriptor
            for name in cursor.description:
                cols.append(name[0].upper())

        # Serve solo per stampare il risultato della challange, ricerca le parole chivi dal dizionario solves, costruito 
        # precedentemente, su str_res
        for key, value in solves.items():
            # Se è stato trovato un valore in str_res presente in uno dei file in ./sol, il nome del file funge da indice nel file 
            # flags.py per stampare la prossima challange
            if value in str_res:
                return render_template('index.html', flag=flags[key].strip(), results=results, columns=cols)
        
        conn.close() # chiusura della connessione al DB

        # rendering della pagina index con tutti i risultati della query
        return render_template('index.html', results=results, columns=cols) 
    
    # se viene lanciata una eccezione da parte del DBMS, viene intercettata stampando anche su schermo l'eccezione
    except Exception as e:
        conn.close() #chiusura della connessione al database
        return render_template('index.html', error=str(e))
    
@app.route('/register', methods=['POST','GET'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        query = "INSERT INTO users (username, password) VALUES ('" + username + "','" + password + ")"

        conn = sqlite3.connect("file:preCC_SQL_injection.db", uri=True)
        cursor = conn.cursor()
        
        try:
            # realizzazione corretta perché evita l'esecuzione di più statament
            #cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            cursor.executescript(query)
            conn.commit()
            conn.close()
            flash('Registrazione completata con successo! Ora puoi effettuare il login.', 'success')
            return render_template('index.html') 
        except Exception as e:
            conn.close()
            print(e)
            flash('Nome utente già esistente. Scegli un altro nome utente.', 'danger')
            return render_template('register.html') 
    
    return render_template('register.html') 

# Endpoint per il login
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect("file:preCC_SQL_injection.db?mode=ro", uri=True)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['username'] = username
            flash('Login effettuato con successo!', 'success')
            return render_template('index.html')
        else:
            flash('Nome utente o password errati.', 'danger')
            return render_template('index.html')
    
    return render_template('index.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    flash('Logout effettuato con successo.', 'success')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)