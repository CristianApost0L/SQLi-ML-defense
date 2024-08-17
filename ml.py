# Importazione delle librerie necessarie per l'ML
import joblib
import re
import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
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