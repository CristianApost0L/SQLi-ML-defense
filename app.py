from flask import Flask, request, render_template, flash, session, url_for, send_from_directory, redirect
import sqlite3
import os
from flags import flags
import logging

# Importazione delle librerie necessarie per l'ML
import joblib
import re
import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
import string
import pickle
from tqdm import tqdm
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

# Carica il modello salvato
loaded_model = joblib.load('./ML/sclf.pkl')

def lemmatize_sentence(query):
    preprocessed_query = []
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))

    sentance = re.sub('[^A-Za-z0-9]+', ' ', query)  # replaces all characters that are not letters or numbers with a space.
    tokenization = nltk.word_tokenize(sentance)  # splits the sentence into tokens
    sentance = ' '.join([lemmatizer.lemmatize(w) for w in tokenization])  # lemmatization
    sentance = ' '.join(e.lower() for e in sentance.split() if e.lower() not in stop_words)  # remove stopwords
    preprocessed_query.append(sentance.strip())
  
    return preprocessed_query

def prediction(sentences):
    preprocessed_query = lemmatize_sentence(sentences)
    print(preprocessed_query)

    # Tokenization and padding
    tokenizer_obj = Tokenizer()
    tokenizer_obj.fit_on_texts(preprocessed_query)
    sequences = tokenizer_obj.texts_to_sequences(preprocessed_query)
    query_pad = pad_sequences(sequences, maxlen=500)
    
    # Prediction
    predictions = loaded_model.predict(query_pad)
    print("shape of query_pad", query_pad.shape)

    # Return predictions
    if predictions.any() >= 0.90:
        pred = 'SQL Injection Attack is there'
    else:
        pred = "No SQL injection is there"
    
    return pred
# Fine ML

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


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


# per ogni root /exec, dopo aver cliccato il bottone ricerca, verrà reinderizzata la stessa pagina eseguita una query verso il DBMS
@app.route('/exec', methods=['POST'])
def search():

    search_type = request.form.get('searchType') # ricerca del tipo di ricerca da effettuare

    if search_type == 'teams':
        # Query da eseguire, si compone di una SELECT sulla tabella Teams con una ricerca basata sul nome dato in input dall'utente.
        query = "SELECT id, name, points FROM teams WHERE name = '" + request.form['query'] + "'"
    elif search_type == 'players':
        # Query da eseguire, si compone di una SELECT sulla tabella Players con una ricerca basata sul nome dato in input dall'utente.
        query = "SELECT players.username, teams.name FROM players JOIN teams WHERE  players.teamID == teams.id AND name = '" + request.form['query'] + "'"
    else:
        flash('Tipo di ricerca non valido.', 'danger')
        return redirect(url_for('index'))

    # Logging configuration
    logging.basicConfig(filename='app.log', level=logging.INFO)
    
    logging.info(f" Query: {query}")

    res = prediction(query)

    logging.info(f" Status query: {res}")
    
    conn = sqlite3.connect("file:preCC_SQL_injection.db?mode=ro", uri=True) # inizializzazione della connessione con il database
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

        # Esecuzione errata perché permette l'esecuzione di più statament
        query = "INSERT INTO users (username, password) VALUES ('" + username + "','" + password + "')"

        # Esecuzione corretta perché evita l'esecuzione di più statament
        #query = "INSERT INTO users (username, password) VALUES (?, ?)"
        #params = (username, password)

        # Logging configuration
        logging.basicConfig(filename='app.log', level=logging.INFO)

        # Log username and password
        logging.info(f"Username: {username}, Password: {password}")

        # Query execution
        logging.info(f"Query: {query}")

        res = prediction(query)

        logging.info(f" Status query: {res}")

        conn = sqlite3.connect("file:preCC_SQL_injection.db", uri=True)
        cursor = conn.cursor()
        
        try:
            # Permette di esequire più statement come ');DELETE FROM users WHERE 1=1; INSERT INTO users VALUES ('sei stato','fregato') --
            cursor.executescript(query)

            # Esecuzione corretta perché evita l'esecuzione di più statament
            #cursor.execute(query, params)

            conn.commit()
            conn.close()
            flash('Registrazione completata con successo! Ora puoi effettuare il login.', 'success')
            return render_template('index.html') 
        except Exception as e:
            conn.close()
            print('Sqlite3 error : ' + str(e))
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

        #query = 'SELECT * FROM users WHERE username = ? AND password = ?', (username, password)
        query = "INSERT INTO users (username, password) VALUES ('" + username + "','" + password + "')"

        # Logging configuration
        logging.basicConfig(filename='app.log', level=logging.INFO)

        # Log username and password
        logging.info(f"Username: {username}, Password: {password}")

        # Query execution
        logging.info(f"Query: {query}")

        res = prediction(str(query))

        logging.info(f" Status query: {res}")

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