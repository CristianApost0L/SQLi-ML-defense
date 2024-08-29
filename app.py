from flask import Flask, request, render_template, flash, session, url_for, send_from_directory, redirect, jsonify
import sqlite3
import os
from flags import flags
import logging
import ml # importazione del modello di machine learning

# creazione di un dizionario dalla directory sol, sono le challange da fare
solves = {}
for file in os.listdir("./sol"):
    with open("./sol/" + file) as f:
        solves[file] = f.read()

app = Flask(__name__)
app.secret_key = 'security_homework_tanto_è_lunga'  # Necessario per gestire le sessioni e i messaggi flash

# Specifica che il server non è in modalità sicura
safe_mode = True

# Variabile per mostrare l'attacco di second order
second_order = True

# Cartella dove verranno salvate le immagini dei profili
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# se siamo nella root verrà renderizzata la pagina di index
@app.route('/')
def home():
    return render_template('index.html', safe_mode=safe_mode)

# icona del sito
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


# per ogni root /exec, dopo aver cliccato il bottone ricerca, verrà reinderizzata la stessa pagina ed eseguita una query verso il DBMS
@app.route('/exec', methods=['POST'])
def search():

    search_type = request.form.get('searchType') # tipo di ricerca da effettuare, teams o players

    if search_type == 'teams':
        # Query da eseguire, si compone di una SELECT sulla tabella Teams con una ricerca basata sul nome dato in input dall'utente.
        query = "SELECT id, name, points FROM teams WHERE name = '" + request.form['query'] + "'"
    elif search_type == 'players':
        # Query da eseguire, si compone di una SELECT sulla tabella Players, Teams e Ranking con una ricerca basata sul nome del player dato in input dall'utente.
        query = "SELECT players.username, teams.name, ranking.position FROM ranking JOIN players JOIN teams WHERE  ranking.playerID = player.ID AND ranking.teamID = team.id AND players.teamID == teams.id AND name = '" + request.form['query'] + "'"
    else:
        # Se il tipo di ricerca non è valido, verrà stampato un messaggio di errore e l'utente verrà reindirizzato alla pagina principale
        flash('Tipo di ricerca non valido.', 'danger')
        return redirect(url_for('index'))

    conn = sqlite3.connect("file:preCC_SQL_injection.db?mode=ro", uri=True) # inizializzazione della connessione con il database in sola lettura

    cursor = conn.cursor() # ci permette di eseguire la query nel nostro DB

    # Logging configuration
    logging.basicConfig(filename='app.log', level=logging.INFO)
    logging.info(f"Query: {query}")

    with open('./ML/output.txt', 'a') as file:
        # Scrivi una stringa nel file
        file.write(f'Query: {query}\n')
        file.write(f'Predicted: {ml.prediction(query)}\n')

    try:
        cursor.execute(query) # esecuzione della query
        results = cursor.fetchall() # caricamento del risultato della query in results
        # Questa variabile conterrà una lista di tuple, dove ogni tupla rappresenta una riga del risultato della query. 
        # Ogni elemento della tupla corrisponde a una colonna della tabella selezionata nella query.

        str_res = str(results)  # conversione della results in una stringa

        cols = []   # colonne della nostra query
        if cursor.description:
            # ricerca della colonne che dovranno essere stampate da cursor descriptor
            for name in cursor.description:
                cols.append(name[0].upper())

        # Serve solo per stampare il risultato della challange, ricerca le parole chivi dal dizionario solves, costruito precedentemente, su str_res
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

# Endpoint per la registrazione
@app.route('/register', methods=['POST','GET'])
def register():

    # Se il metodo è POST, significa che l'utente ha inviato i dati del form di registrazione
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        
        if safe_mode:
            # Prapeared Statement per evitare SQL Injection
            query = "INSERT INTO users (username, password) VALUES (?, ?)"
            params = (username, password)

            # Costruzione della query completa
            query_completa = query.replace("?", "{}").format(*map(repr, params))

            with open('./ML/output.txt', 'a') as file:
            # Scrive la predizione nel file
                file.write(f'Query: {query_completa}\n')
                file.write(f'Predicted: {ml.prediction(query_completa)}\n')
        else:
            # Query vulnerabile a SQL Injection
            query = "INSERT INTO users (username, password) VALUES ('" + username + "','" + password + "')"

            with open('./ML/output.txt', 'a') as file:
            # Scrive la predizione nel file
                file.write(f'Query: {query}\n')
                file.write(f'Predicted: {ml.prediction(query)}\n')

        # Logging configuration
        logging.basicConfig(filename='app.log', level=logging.INFO)
        # Log username and password
        logging.info(f"Username: {username}, Password: {password}")

        conn = sqlite3.connect("file:preCC_SQL_injection.db", uri=True) # connessione al database
        cursor = conn.cursor()  # cursore per eseguire le query
        
        try:
            if safe_mode:
                # Esecuzione corretta perché la query è un prepared statement
                cursor.execute(query, params)
            else :
                # Permette di esequire più statement come ');DELETE FROM users WHERE 1=1; INSERT INTO users VALUES ('sei stato','fregato') --
                cursor.executescript(query)

            # Commit delle modifiche al database
            conn.commit()
            conn.close()
            flash('Registrazione completata con successo! Ora puoi effettuare il login.', 'success')
            return render_template('index.html') 
        
        except Exception as e:
            # Se viene lanciata un'eccezione, viene stampata a schermo e il database viene chiuso
            conn.close()
            print('Sqlite3 error : ' + str(e))
            flash('Nome utente già esistente. Scegli un altro nome utente.', 'danger')
    
    return render_template('register.html') 

# Endpoint per il login
@app.route('/login', methods=['POST','GET'])
def login():
    # Se il metodo è POST, significa che l'utente ha inviato i dati del form di login
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("file:preCC_SQL_injection.db?mode=ro", uri=True) # connessione al database in sola lettura
        cursor = conn.cursor() # cursore per eseguire le query

        if safe_mode:
            # Prepared Statement per evitare SQL Injection
            query = "SELECT * FROM users WHERE username = ? AND password = ?"
            params = (username, password)

            # Costruzione della query completa
            query_completa = query.replace("?", "{}").format(*map(repr, params))

            with open('./ML/output.txt', 'a') as file:
            # Scrive la predizione nel file
                file.write(f'Query: {query_completa}\n')
                file.write(f'Predicted: {ml.prediction(query_completa)}\n')
        else:
            # Query vulnerabile a SQL Injection
            query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"

            with open('./ML/output.txt', 'a') as file:
                # Scrive la predizione nel file
                file.write(f'Query: {query}\n')
                file.write(f'Predicted: {ml.prediction(query)}\n')

        # Logging configuration
        logging.basicConfig(filename='app.log', level=logging.INFO)

        # Log username and password
        logging.info(f"Username: {username}, Password: {password}")

        try:
            if safe_mode:
                # Esecuzione corretta perché la query è un prepared statement
                cursor.execute(query, params)
            else:
                # Esecuzione della query vulnerabile a SQL Injection
                cursor.execute(query)

            user = cursor.fetchone() # restituisce la prima riga del risultato della query
            conn.close() # chiusura della connessione al database

            logging.info(f"User: {user}")
        
            # Se l'utente è presente nel database, viene effetuato il login
            if user is not None:
                session['username'] = user[0]
                session['profile_pic'] = user[2]
                flash('Login effettuato con successo!', 'success')
                
                # Se l'utente è l'amministratore, viene impostata la sessione admin
                if user[0] == 'admin':
                    session['admin'] = True
            else : 
                flash('Nome utente o password errati.', 'danger')

        # Se viene lanciata un'eccezione, viene stampata a schermo e il database viene chiuso
        except Exception as e:
            conn.close()
            print('Sqlite3 error : ' + str(e))
            flash('Nome utente o password errati.', 'danger')
    
    return render_template('index.html')

# Endpoint per l'impostazione della modalità sicura
@app.route('/toggle_mode', methods=['POST'])
def toggle_mode():
    global safe_mode
    data = request.json
    safe_mode = data.get('adminMode', False)
    session['adminMode'] = safe_mode

    # Logging configuration
    logging.basicConfig(filename='app.log', level=logging.INFO)
    logging.info(f" Safe_mode: {safe_mode}")
    
    return jsonify(success=True)

# Endpoint per il logout
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    session.pop('admin', None)
    flash('Logout effettuato con successo.', 'success')
    return render_template('index.html')

# Endpoint per la visualizzazione del profilo
@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):

    conn = sqlite3.connect("file:preCC_SQL_injection.db", uri=True) # connessione al database
    cursor = conn.cursor() # cursore per eseguire le query

    # Se il metodo è POST, significa che l'utente ha inviato i dati del form di modifica del profilo
    if request.method == 'POST':
        # Gestione del caricamento della foto profilo
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename != '':
                try:
                    filename = file.filename  # Ottieni il nome del file
                    # Salva il file nella directory 'static/uploads'
                    filepath = os.path.join('static/uploads', filename)
                    file.save(filepath)

                    # Aggiorna la foto profilo dell'utente
                    session['profile_pic'] = filename
                    
                    # Aggiorna il nome del file nel database
                    cursor.execute("UPDATE users SET profile_pic = ? WHERE username = ?", (filename, username))
                    conn.commit()
                    conn.close()
                    flash('Foto profilo aggiornata con successo!', 'success')

                # Se viene lanciata un'eccezione, viene stampata a schermo e il database viene chiuso
                except sqlite3.OperationalError as e:
                    print(f"Database error: {e}")

    try :   
        if safe_mode and not second_order:
            # Prepared Statement per evitare SQL Injection
            query = "SELECT username FROM users WHERE username = ?"
            params = (username,)
            
            # Costruzione della query completa
            query_completa = query.replace("?", "{}").format(*map(repr, params))

            with open('./ML/output.txt', 'a') as file:
            # Scrive la predizione nel file
                file.write(f'Query: {query_completa}\n')
                file.write(f'Predicted: {ml.prediction(query_completa)}\n')

            cursor.execute(query, params)
        else:
            # Per fare un attacco di tipo SQLi di secondo ordine è fondamentale avere una fare di registrazione e di login correttamente implementate
            query = "SELECT username FROM users WHERE username = '" + session['username'] + "'"
            cursor.execute(query)

            with open('./ML/output.txt', 'a') as file:
            # Scrive la predizione nel file
                file.write(f'Query: {query}\n')
                file.write(f'Predicted: {ml.prediction(query)}\n')

    # Se viene lanciata un'eccezione, viene stampata a schermo e il database viene chiuso
    except Exception as e:
        print('Sqlite3 error : ' + str(e))
        conn.close()
        return "User not found", 404

    # Forzatura nella generazione del username
    users = cursor.fetchall()
    username = ' '.join(user[0] for user in users)

    if users:
        return render_template('profile.html', username=username, profile_pic=session['profile_pic'])
    else:
        return "User not found", 404

if __name__ == '__main__':
    app.run(debug=True)