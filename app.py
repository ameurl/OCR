#APP FLASK (commande : flask run)

from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
from flask import redirect, render_template, request, send_file, session, url_for

import pandas as pd
import xgboost
import joblib
from datetime import date, timedelta
import json

import lime
from lime import lime_tabular
import os

import warnings
warnings.filterwarnings("ignore", category=UserWarning)


# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)



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
print(data_general.info())

@app.route('/')
def hello_world():
    return 'oki'
    
@app.route('/credit/<id_client>', methods=['GET'])
def credit(id_client):
    print('ok')

    data_id = data.loc[data['SK_ID_CURR'] == int(id_client)]
    resultat = pipeline.predict_proba(data_id)
    resultat = float(resultat[:,1])
    
    data_id_general = data_general.loc[data_general['SK_ID_CURR'] == int(id_client)]
    data_id_general['PREDICTION'] = resultat
    
    explainer = lime_tabular.LimeTabularExplainer(data.values[0:100], mode="classification", feature_names= data.columns)
    explanation = explainer.explain_instance(data_id.values[0], pipeline.predict_proba)
    features_list = explanation.as_list()
    data_features = pd.DataFrame(features_list).set_index(0).squeeze()
    data_id_general = data_id_general.append(data_features)
    
    data_dict = data_id_general.to_json(orient='records')

    
    print(data_features)   


    return jsonify(data_dict)


#Application run
if __name__ == "__main__":
    app.run(debug=True)