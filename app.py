from flask import Flask, request, render_template, flash, session, url_for, send_from_directory, redirect, jsonify
import sqlite3
import os
import logging
import ml # Importazione del modello di machine learning

# Dizionario contenente le descrizioni delle sfide
flags = {
    "0": "Identifica il numero di colonne nella tabella 'teams' usando il trucco dei NULL.",
    "1": "Trova i nomi delle altre tabelle nel database.",
    "2": "Trova i nomi delle colonne nella tabella 'players'.",
    "3": "Usando le informazioni trovate, esegui una SQL injection UNION per recuperare i dati dei giocatori.",
    "4": "Congratulazioni, hai scoperto tutti gli utenti."
}

# Connessione al database SQLite
conn = sqlite3.connect("preCC_SQL_injection.db")
cursor = conn.cursor()

# Leggi ed esegui tutte le query dal file queries.sql
with open("sol/queries.sql", "r") as query_file:
    lines = query_file.readlines()

for line in lines:
    query, _, output_file = line.partition("--")
    query = query.strip()
    output_file = output_file.strip()
    
    cursor.execute(query)
    
    # Esegui tutte le query e salva l'output nei file ./sol/
    with open("sol/" + output_file, "w") as f:
        f.write(str(cursor.fetchall()))

conn.close()

# Crea un dizionario con le soluzioni delle sfide
solves = {}
for file in os.listdir("./sol"):
    with open("./sol/" + file) as f:
        solves[file] = f.read()

app = Flask(__name__)
app.secret_key = 'security_homework_tanto_è_lunga'

# Specifica che il server non è in modalità sicura
safe_mode = False

# Variabile per mostrare l'attacco di secondo ordine
second_order = False

# Cartella dove verranno salvate le immagini del profilo
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Renderizza la pagina index quando si accede alla root
@app.route('/')
def home():
    return render_template('index.html', safe_mode=safe_mode)

# Esegui una query al DBMS dopo aver cliccato il pulsante di ricerca
@app.route('/exec', methods=['POST'])
def search():
    # Tipo di ricerca da eseguire, teams o players
    search_type = request.form.get('searchType') 

    if search_type == 'teams':
        query = "SELECT id, name, points FROM teams WHERE name = '" + request.form['query'] + "'"
    elif search_type == 'players':
        query = "SELECT players.username, teams.name, ranking.position FROM ranking JOIN players JOIN teams WHERE  ranking.playerID = player.ID AND ranking.teamID = team.id AND players.teamID == teams.id AND name = '" + request.form['query'] + "'"
    else:
        flash('Tipo di ricerca non valido.', 'danger')
        return redirect(url_for('index'))
    
    # Inizializza la connessione al database in modalità sola lettura
    conn = sqlite3.connect("file:preCC_SQL_injection.db?mode=ro", uri=True)
    cursor = conn.cursor()

    # Configurazione del logging
    logging.basicConfig(filename='.log/app.log', level=logging.INFO)
    logging.info(f"Query: {query}")

    with open('.log/predictions.log', 'a') as file:
        # Scrivi la query e la previsione nel file
        file.write(f'Query: {query}\n')
        file.write(f'Predicted: {ml.prediction(query)}\n')

    try:
        cursor.execute(query) # Esegui la query
        results = cursor.fetchall() # Carica il risultato della query in results

        str_res = str(results)  # Converte results in una stringa

        cols = []   # Colonne della nostra query
        if cursor.description:
            # Recupera le colonne da stampare dal descrittore del cursore
            for name in cursor.description:
                cols.append(name[0].upper())

        # Controlla se qualche valore in str_res è presente nel dizionario solves
        for key, value in solves.items():
            if value in str_res:
                return render_template('index.html', flag=flags[key].strip(), results=results, columns=cols)
        
        conn.close() # Chiudi la connessione al database

        # Renderizza la pagina index con i risultati della query
        return render_template('index.html', results=results, columns=cols) 
    
    # Gestisci le eccezioni sollevate dal DBMS
    except Exception as e:
        conn.close() # Chiudi la connessione al database
        return render_template('index.html', error=str(e))

# Endpoint per la registrazione degli utenti
@app.route('/register', methods=['POST','GET'])
def register():

    # Se il metodo è POST, l'utente ha inviato il modulo di registrazione
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        
        if safe_mode:
            # Prepared Statement per prevenire SQL Injection
            query = "INSERT INTO users (username, password) VALUES (?, ?)"
            params = (username, password)

            # Costruisci la query completa
            query_completa = query.replace("?", "{}").format(*map(repr, params))

            with open('./ML/output.txt', 'a') as file:
                # Scrivi la previsione nel file
                file.write(f'Query: {query_completa}\n')
                file.write(f'Predicted: {ml.prediction(query_completa)}\n')
        else:
            # Query vulnerabile a SQL Injection
            query = "INSERT INTO users (username, password) VALUES ('" + username + "','" + password + "')"

            with open('./ML/output.txt', 'a') as file:
                # Scrivi la previsione nel file
                file.write(f'Query: {query}\n')
                file.write(f'Predicted: {ml.prediction(query)}\n')

        # Configurazione del logging
        logging.basicConfig(filename='.log/app.log', level=logging.INFO)
        # Logga username e password
        logging.info(f"Username: {username}, Password: {password}")

        conn = sqlite3.connect("file:preCC_SQL_injection.db", uri=True) # Connetti al database
        cursor = conn.cursor()  # Cursore per eseguire le query
        
        try:
            if safe_mode:
                # Esegui correttamente perché la query è una prepared statement
                cursor.execute(query, params)
            else:
                # Permette di eseguire più istruzioni come ');DELETE FROM users WHERE 1=1; INSERT INTO users VALUES ('sei stato','fregato') --
                cursor.executescript(query)

            # Conferma le modifiche al database
            conn.commit()
            conn.close()
            flash('Registrazione avvenuta con successo! Ora puoi effettuare il login.', 'success')
            return render_template('index.html') 
        
        except Exception as e:
            # Gestisci le eccezioni e chiudi il database
            conn.close()
            print('Errore Sqlite3 : ' + str(e))
            flash('Username già esistente. Scegli un altro username.', 'danger')
    
    return render_template('register.html') 

# Endpoint per il login degli utenti
@app.route('/login', methods=['POST','GET'])
def login():
    # Se il metodo è POST, l'utente ha inviato il modulo di login
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("file:preCC_SQL_injection.db?mode=ro", uri=True) # Connetti al database in modalità sola lettura
        cursor = conn.cursor() # Cursore per eseguire le query

        if safe_mode:
            # Prepared Statement per prevenire SQL Injection
            query = "SELECT * FROM users WHERE username = ? AND password = ?"
            params = (username, password)

            # Costruisci la query completa
            query_completa = query.replace("?", "{}").format(*map(repr, params))

            with open('./ML/output.txt', 'a') as file:
                # Scrivi la previsione nel file
                file.write(f'Query: {query_completa}\n')
                file.write(f'Predicted: {ml.prediction(query_completa)}\n')
        else:
            # Query vulnerabile a SQL Injection
            query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"

            with open('./ML/output.txt', 'a') as file:
                # Scrivi la previsione nel file
                file.write(f'Query: {query}\n')
                file.write(f'Predicted: {ml.prediction(query)}\n')

        # Configurazione del logging
        logging.basicConfig(filename='.log/app.log', level=logging.INFO)

        # Logga username e password
        logging.info(f"Username: {username}, Password: {password}")

        try:
            if safe_mode:
                # Esegui correttamente perché la query è una prepared statement
                cursor.execute(query, params)
            else:
                # Esegui la query vulnerabile a SQL Injection
                cursor.execute(query)

            user = cursor.fetchone() # Recupera la prima riga del risultato della query
            conn.close() # Chiudi la connessione al database

            logging.info(f"User: {user}")
        
            # Se l'utente è presente nel database, effettua il login
            if user is not None:
                session['username'] = user[0]
                session['profile_pic'] = user[2]
                flash('Login avvenuto con successo!', 'success')
                
                # Se l'utente è l'amministratore, imposta la sessione admin
                if user[0] == 'admin':
                    session['admin'] = True
            else: 
                flash('Username o password non validi.', 'danger')

        # Gestisci le eccezioni e chiudi il database
        except Exception as e:
            conn.close()
            print('Errore Sqlite3 : ' + str(e))
            flash('Username o password non validi.', 'danger')
    
    return render_template('index.html')

# Endpoint per attivare/disattivare la modalità sicura
@app.route('/toggle_mode', methods=['POST'])
def toggle_mode():
    global safe_mode
    data = request.json
    safe_mode = data.get('adminMode', False)
    session['adminMode'] = safe_mode

    # Configurazione del logging
    logging.basicConfig(filename='.log/app.log', level=logging.INFO)
    logging.info(f" Safe_mode: {safe_mode}")
    
    return jsonify(success=True)

# Endpoint per il logout degli utenti
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    session.pop('admin', None)
    flash('Logout avvenuto con successo.', 'success')
    return render_template('index.html')

# Endpoint per visualizzare il profilo utente
@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):

    conn = sqlite3.connect("file:preCC_SQL_injection.db", uri=True) # Connetti al database
    cursor = conn.cursor() # Cursore per eseguire le query

    # Se il metodo è POST, l'utente ha inviato il modulo di aggiornamento del profilo
    if request.method == 'POST':
        # Gestisci il caricamento dell'immagine del profilo
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename != '':
                try:
                    filename = file.filename  # Ottieni il nome del file
                    # Salva il file nella directory 'static/uploads'
                    filepath = os.path.join('static/uploads', filename)
                    file.save(filepath)

                    # Aggiorna l'immagine del profilo dell'utente
                    session['profile_pic'] = filename
                    
                    # Aggiorna il nome del file nel database
                    cursor.execute("UPDATE users SET profile_pic = ? WHERE username = ?", (filename, username))
                    conn.commit()
                    conn.close()
                    flash('Immagine del profilo aggiornata con successo!', 'success')

                # Gestisci le eccezioni e chiudi il database
                except sqlite3.OperationalError as e:
                    print(f"Errore del database: {e}")

    try:   
        if safe_mode and not second_order:
            # Prepared Statement per prevenire SQL Injection
            query = "SELECT username FROM users WHERE username = ?"
            params = (username,)
            
            # Costruisci la query completa
            query_completa = query.replace("?", "{}").format(*map(repr, params))

            with open('./ML/output.txt', 'a') as file:
                # Scrivi la previsione nel file
                file.write(f'Query: {query_completa}\n')
                file.write(f'Predicted: {ml.prediction(query_completa)}\n')

            cursor.execute(query, params)
        else:
            # Per un attacco SQLi di secondo ordine, è essenziale avere una fase di registrazione e login correttamente implementata
            query = "SELECT username FROM users WHERE username = '" + session['username'] + "'"
            cursor.execute(query)

            with open('./ML/output.txt', 'a') as file:
                # Scrivi la previsione nel file
                file.write(f'Query: {query}\n')
                file.write(f'Predicted: {ml.prediction(query)}\n')

    # Gestisci le eccezioni e chiudi il database
    except Exception as e:
        print('Errore Sqlite3 : ' + str(e))
        conn.close()
        return "Utente non trovato", 404

    # Forza la generazione del nome utente
    users = cursor.fetchall()
    username = ' '.join(user[0] for user in users)

    if users:
        return render_template('profile.html', username=username, profile_pic=session['profile_pic'])
    else:
        return "Utente non trovato", 404

if __name__ == '__main__':
    app.run(debug=True)
