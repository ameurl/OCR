#APP FLASK (commande : flask run)
# Partie formulaire non utilisée (uniquement appel à l'API)

from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
#from flask_wtf import Form, validators  
#from wtforms.fields import StringField
#from wtforms import TextField, BooleanField, PasswordField, TextAreaField, validators
#from wtforms.widgets import TextArea

#from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

#from toolbox.predict import *
import pandas as pd
import xgboost
import joblib
from datetime import date, timedelta
import json

import warnings
warnings.filterwarnings("ignore", category=UserWarning)


# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
#app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'



#Load Dataframe
path_df = 'data/data_sampled.csv'
path_df_general = 'data/application_train.csv'
data = pd.read_csv(path_df)
data_general = pd.read_csv(path_df_general)
data.fillna(0, inplace=True)

description = ['SK_ID_CURR','CODE_GENDER','AMT_INCOME_TOTAL','AMT_CREDIT',
              'NAME_FAMILY_STATUS','DAYS_BIRTH','DAYS_EMPLOYED']
data_general = data_general[description]


#Load Model
pipeline = joblib.load('pipeline.joblib')


data_general['DAYS_EMPLOYED'].replace({365243: 0}, inplace = True)
data_general['CODE_GENDER'].replace({'M': 'Homme', 'F':'Femme'}, inplace = True)
#data_general['ANCIENNETE'] = str(data_general['ANCIENNETE'])
print(data_general.info())
@app.route('/credit/<id_client>', methods=['GET'])
def credit(id_client):
    print('ok')

    data_id = data.loc[data['SK_ID_CURR'] == int(id_client)]
    resultat = pipeline.predict_proba(data_id)
    resultat = float(resultat[:,1])
    
    data_id_general = data_general.loc[data_general['SK_ID_CURR'] == int(id_client)]
    data_id_general['PREDICTION'] = resultat
    
    data_dict = data_id_general.to_json(orient='records')
    
    print(type(data_dict))
    print(data_dict)

    print('Nouvelle Prédiction : \n', dict_final)


    return jsonify(data_dict)


#lancement de l'application
if __name__ == "__main__":
    app.run(debug=True)