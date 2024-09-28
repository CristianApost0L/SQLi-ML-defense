from flask import Flask
from scipy.sparse import hstack
import joblib
import pandas as pd
import re

app = Flask(__name__)

# Load the saved models
# Load models from the 'models/Bow' directory
gbm_bow = joblib.load('../models/Bow/gbm_model.pkl')
ada_bow = joblib.load('../models/Bow/ada_model.pkl')
xgb_bow = joblib.load('../models/Bow/xgb_model.pkl')
lgbm_bow = joblib.load('../models/Bow/lgbm_model.pkl')
log_reg_bow = joblib.load('../models/Bow/log_reg_model.pkl')
rf_bow = joblib.load('../models/Bow/rf_model.pkl')
knn_bow = joblib.load('../models/Bow/knn_model.pkl')
dt_bow = joblib.load('../models/Bow/dt_model.pkl')
stacking_bow = joblib.load('../models/Bow/stacking_model.pkl')

# Load models from the 'models/ITF-IDF' directory
gbm_tfidf = joblib.load('../models/ITF-IDF/gbm_model.pkl')
ada_tfidf = joblib.load('../models/ITF-IDF/ada_model.pkl')
xgb_tfidf = joblib.load('../models/ITF-IDF/xgb_model.pkl')
lgbm_tfidf = joblib.load('../models/ITF-IDF/lgbm_model.pkl')
log_reg_tfidf = joblib.load('../models/ITF-IDF/log_reg_model.pkl')
rf_tfidf = joblib.load('../models/ITF-IDF/rf_model.pkl')
knn_tfidf = joblib.load('../models/ITF-IDF/knn_model.pkl')
dt_tfidf = joblib.load('../models/ITF-IDF/dt_model.pkl')
stacking_tfidf = joblib.load('../models/ITF-IDF/stacking_model.pkl')

# Load the imputer and vectorizer
imputer = joblib.load('../models/Bow/imputer.pkl')
vectorizer_bow = joblib.load('../models/Bow/vectorizer.pkl')
vectorizer_tfidf = joblib.load('../models/ITF-IDF/vectorizer.pkl')

# Combined feature extraction function
def extract_features(query):
    features = {}
    features['no_sngle_quts'] = query.count("'")
    features['no_dble_quts'] = query.count('"')
    features['no_punctn'] = sum([1 for char in query if char in '!@#$%^&*()-_=+[{]};:\'",<.>/?\\|`~'])
    features['no_sgle_cmnt'] = query.count('--')
    features['no_mlt_cmnt'] = query.count('/*') + query.count('*/')
    features['no_whte_spce'] = query.count(' ')
    features['no_nrml_kywrds'] = len(re.findall(r'\b(select|from|where|insert|delete|update|join|union)\b', query, re.IGNORECASE))
    features['no_hmfl_kywrds'] = len(re.findall(r'\b(exec|shutdown|cmdshell|ascii|hex|char|concat)\b', query, re.IGNORECASE))
    features['no_prctge'] = query.count('%')
    features['no_log_oprtr'] = len(re.findall(r'\b(and|or|not)\b', query, re.IGNORECASE))
    features['no_oprtr'] = sum([1 for char in query if char in '=<>'])
    features['no_null_valus'] = query.lower().count('null')
    features['no_hexdcml_valus'] = len(re.findall(r'0x[0-9a-fA-F]+', query))
    features['no_db_info_cmnds'] = len(re.findall(r'\b(database|information_schema|version)\b', query, re.IGNORECASE))
    features['no_roles'] = len(re.findall(r'\b(admin|user|guest)\b', query, re.IGNORECASE))
    features['no_ntwr_cmnds'] = len(re.findall(r'\b(load_file|benchmark|sleep)\b', query, re.IGNORECASE))
    features['no_lanage_cmnds'] = len(re.findall(r'\b(exec|declare|open|fetch|close|deallocate|prepare|execute)\b', query, re.IGNORECASE))
    features['no_alphabet'] = len(re.findall(r'[a-zA-Z]', query))
    features['no_digits'] = len(re.findall(r'\d', query))
    features['no_spl_chrtr'] = len(re.findall(r'[^a-zA-Z0-9\s]', query))
    return pd.DataFrame([features])

def prediction(query):
    # Estrai le caratteristiche dalla query
    query_features = extract_features(query)
    
    # Gestisci i valori mancanti nelle caratteristiche della singola query utilizzando lo stesso imputer
    query_features_imputed = imputer.transform(query_features)
    
    # Trasforma il testo della query in BoW
    query_bow = vectorizer_bow.transform([query])
    
    # Combina le caratteristiche numeriche e testuali
    query_features_combined = hstack((query_features_imputed, query_bow)).tocsr()

    # Predizioni dai modelli
    predictions = {
        'Gradient Boosting Machine': gbm_bow.predict(query_features_combined)[0],
        'AdaBoost': ada_bow.predict(query_features_combined)[0],
        'XGBoost': xgb_bow.predict(query_features_combined)[0],
        'LightGBM': lgbm_bow.predict(query_features_combined)[0],
        'Logistic Regression': log_reg_bow.predict(query_features_combined)[0],
        'Random Forest': rf_bow.predict(query_features_combined)[0],
        'Stacking Classifier': stacking_bow.predict(query_features_combined)[0]
    }

    if predictions['Stacking Classifier'] == 1:
        return 'SQL Injection Detected'
    else:
        return 'No SQL Injection Detected'

# Fine ML