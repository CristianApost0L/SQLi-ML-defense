from flask import Flask
from scipy.sparse import hstack
import joblib
import pandas as pd
import re

app = Flask(__name__)

feature_extraction = 'BoW'

if feature_extraction == 'BoW':
    gbm = joblib.load('./models/BoW/gbm_model.pkl')
    ada = joblib.load('./models/BoW/ada_model.pkl')
    xgb = joblib.load('./models/BoW/xgb_model.pkl')
    lgbm = joblib.load('./models/BoW/lgbm_model.pkl')
    log_reg = joblib.load('./models/BoW/log_reg_model.pkl')
    rf = joblib.load('./models/BoW/rf_model.pkl')
    knn = joblib.load('./models/BoW/knn_model.pkl')
    dt = joblib.load('./models/BoW/dt_model.pkl')
    stacking = joblib.load('./models/BoW/stacking_model.pkl')
    imputer = joblib.load('./models/BoW/imputer.pkl')
    vectorizer = joblib.load('./models/BoW/vectorizer.pkl')
elif feature_extraction == 'ITF-IDF':
    gbm = joblib.load('./models/ITF-IDF/gbm_model.pkl')
    ada = joblib.load('./models/ITF-IDF/ada_model.pkl')
    xgb = joblib.load('./models/ITF-IDF/xgb_model.pkl')
    lgbm = joblib.load('./models/ITF-IDF/lgbm_model.pkl')
    log_reg = joblib.load('./models/ITF-IDF/log_reg_model.pkl')
    rf = joblib.load('./models/ITF-IDF/rf_model.pkl')
    knn = joblib.load('./models/ITF-IDF/knn_model.pkl')
    dt = joblib.load('./models/ITF-IDF/dt_model.pkl')
    stacking = joblib.load('./models/ITF-IDF/stacking_model.pkl')
    imputer = joblib.load('./models/ITF-IDF/imputer.pkl')
    vectorizer = joblib.load('./models/ITF-IDF/vectorizer.pkl')

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
    query_bow = vectorizer.transform([query])
    
    # Combina le caratteristiche numeriche e testuali
    query_features_combined = hstack((query_features_imputed, query_bow)).tocsr()

    # Predizioni dai modelli
    predictions = {
        'Gradient Boosting Machine': gbm.predict(query_features_combined)[0],
        'AdaBoost': ada.predict(query_features_combined)[0],
        'XGBoost': xgb.predict(query_features_combined)[0],
        'LightGBM': lgbm.predict(query_features_combined)[0],
        'Logistic Regression': log_reg.predict(query_features_combined)[0],
        'Random Forest': rf.predict(query_features_combined)[0],
        'Stacking Classifier': stacking.predict(query_features_combined)[0]
    }

    if predictions['Stacking Classifier'] == 1:
        return 'SQL Injection Detected'
    else:
        return 'No SQL Injection Detected'

# Fine ML