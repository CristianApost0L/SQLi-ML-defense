## Install Virtual Environment
We use a module named virtualenv which is a tool to create isolated Python environments. virtualenv creates a folder that contains all the necessary executables to use the packages that a Python project would need.

```c
pip install virtualenv
Create Python virtual environment
```

Go to the local directory where you want to create your Flask app.

```c
virtualenv venv
```

Activate a virtual environment based on your OS

```c
For windows > venv\Scripts\activate
For linux > source ./venv/bin/activate
```

## Install Flask
Once the virtual environment is activated, install Flask:

```c
pip install Flask
```

## Install Required Libraries
Install the necessary libraries for the project:

```c
pip install re joblib numpy pandas texttable matplotlib scipy xgboost lightgbm scikit-learn
```

## Build ML Models

To build the models with BoW, run the following script:

```c
python SQLi_detection_BoW.ipynb
```
otherwise:
```c
python SQLi_detection_TF_IDF.ipynb
```

## Start Application

Run the Flask application with the following command:

```c
python app.py
```

Open your browser and follow the link  [http://localhost:5000] (http://localhost:5000).