# SQL Injection Attack Simulation & Machine Learning Detection

## Project Description

This project demonstrates an **inband SQL injection attack** simulation, where attackers can inject SQL commands via user inputs using techniques like **Tautology**, **End-of-line comment**, and **Piggybacked query**. It showcases how SQLi vulnerabilities can be exploited by injecting malicious queries through the same communication channel used for both sending and receiving results. The aim is to explore the risk posed by SQL injection attacks and provide a learning tool for detecting and preventing them.

To complement the SQL injection simulation, a **Machine Learning detection system** is integrated to automatically identify and block SQLi attempts. The system analyzes query patterns and applies **text processing techniques** like **Bag of Words (BoW)** and **TF-IDF** to transform the input queries into numerical features that can be processed by the ML models. Various algorithms are employed, including **XGBoost**, **LightGBM**, and **Random Forest**, to accurately detect potentially malicious SQL queries.

### Features
- **Inband SQL Injection Attacks**: Simulate SQL injection vulnerabilities using Tautology, End-of-line comments, and Piggybacked queries.
- **Real-time SQL Injection Detection**: Leverage ML models trained to identify malicious queries in real-time using advanced natural language processing techniques.
- **Interactive Web Interface**: A Flask-based web application is provided for users to interact with and understand the process of SQL injection and its detection.

---

## Installation Instructions

### Install Virtual Environment
We use `virtualenv` to create an isolated Python environment for the project. Install `virtualenv` if you don't have it:

```bash
pip install virtualenv
```

Create a virtual environment in your project directory:

```bash
virtualenv venv
```

Activate the virtual environment:

- On Windows:

    ```bash
    venv\Scripts\activate
    ```

- On Linux:

    ```bash
    source ./venv/bin/activate
    ```

## Install Flask
Once the virtual environment is activated, install Flask:

```bash
pip install Flask
```

## Install Required Libraries
Install the necessary libraries for the machine learning models and SQL injection detection:

```bash
pip install joblib numpy pandas texttable matplotlib scipy xgboost lightgbm scikit-learn
```

## Build Machine Learning Models

### Install Jupyter Notebook

If you haven't already installed Jupyter Notebook, you can do so by running:

```bash
pip install notebook
```

### Running the Notebooks
To train the models using Jupyter Notebooks, follow these steps:

1. Start Jupyter Notebook
    Navigate to the project directory in the terminal and start Jupyter:
  
    ```bash
    jupyter notebook
    ```
    This will open a new tab in your web browser, where you can navigate through the project files.

2. Open and Run the Notebooks
    In the Jupyter interface, find and open the notebook you want to run:

    - To train the models using Bag of Words (BoW), open and run ***SQLi_detection_BoW.ipynb***.
   
    - Alternatively, to train the models using TF-IDF, open and run ***SQLi_detection_TF_IDF.ipynb***.

### Running Notebooks from the Command Line
Alternatively, you can run the notebooks directly from the command line:

- For Bag of Words **(BoW)**:
  
    ```bash
    python -m ipykernel_launcher SQLi_detection_BoW.ipynb
    ```

- For **TF-IDF**:

    ```bash
    python -m ipykernel_launcher SQLi_detection_BoW.ipynb
    ```

## Start Application

To start the Flask web application, run:

```bash
python app.py
```

Once the server is running, open your browser and navigate to:  [http://localhost:5000].
