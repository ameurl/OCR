import pandas as pd
import streamlit as st
import requests
#from sklearn.preprocessing import MinMaxScaler
#from sklearn.impute import SimpleImputer
#from sklearn import preprocessing

import json
from urllib.request import urlopen
#import ast
from datetime import date, timedelta




def request_prediction(model_uri, data):
    headers = {"Content-Type": "application/json"}

    
    #st.write(data['SK_ID_CURR'])
    
    st.write(data)
    #data = data.tolist()
    data_json = {'data': data}
    
    response = requests.request(
        method='POST', headers=headers, url=model_uri, json=data_json)

    if response.status_code != 200:
        raise Exception(
            "Request failed with status {}, {}".format(response.status_code, response.text))

    return response.json()

def load_data ():
    data = pd.read_csv('data/data_sampled.csv')
    data.fillna(0, inplace=True)
    
    
    return data

def calculate_age(born):
    born = date.today() + timedelta(born)
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def calculate_anciennete(anciennete):
    anciennete = date.today() + timedelta(anciennete)
    return anciennete.strftime("%m-%Y")

def calculate_deltadate(delta):
    delta_m = delta/30
    if delta_m < -12 :
        delta_y = int(delta_m /12)
        delta_m = int(delta_m % 12)
        delta_r = '-{} mois et {} année(s)'.format(delta_m, -delta_y)
    else :
        delta_r = '{} mois'.format(int(delta_m))
        
    return delta_r
   
age_moyenne = 40
revenu_moyen = 165612
anciennete_moyenne = -1815

def calculate_info(Dict):
    age = calculate_age(Dict[0]["DAYS_BIRTH"])
    revenu = Dict[0]["AMT_INCOME_TOTAL"]
    anciennete = calculate_anciennete(Dict[0]["DAYS_EMPLOYED"])
    delta_age = age-40
    delta_revenu = revenu-165612
    delta_anciennete = Dict[0]["DAYS_EMPLOYED"]-(-1815)
    return age, revenu, anciennete, delta_age, delta_revenu, delta_anciennete
    

def main():
    MLFLOW_URI = 'http://127.0.0.1:5000/credit/'

    

    st.title('Demande de crédit')

    data = load_data()
    

  
    
    id_client = st.selectbox('Identifiant client', data['SK_ID_CURR'])


    predict_btn = st.button('Résultat')

            
    if predict_btn:
        data_id = data.loc[data['SK_ID_CURR'] == int(id_client)]
        #API_url = "http://127.0.0.1:5000/credit/" + str(id_client)
        API_url = "http://ameurl.pythonanywhere.com/credit/" + str(id_client)
       
        json_url = urlopen(API_url)

        API_data = json.loads(json_url.read())
        
        #st.write(API_data)
        #convertedDict = json.loads(API_data)
        
        Dict = json.loads(API_data)
        
        age, revenu, anciennete, delta_age, delta_revenu, delta_anciennete = calculate_info(Dict)
        

        
        if Dict[0]["PREDICTION"] <0.51 :
            st.success('CRÉDIT ACCEPTÉ '+str(Dict[0]["PREDICTION"]))
        else :
            st.error('CRÉDIT REFUSÉ')
        
        st.slider('Score',min_value=0.0, max_value=1.0, value=Dict[0]["PREDICTION"],disabled=True)
        st.subheader('Informations Client :')
        
        col1, col2, col3 = st.columns(3)
        
        col1.metric("Age :", age, delta_age)
        col2.metric("Sexe :", Dict[0]["CODE_GENDER"])
        col3.metric("Status marital :", Dict[0]["NAME_FAMILY_STATUS"])
        
        st.subheader('Informations Pro :')
        
        col1, col2= st.columns(2)
        
        col1.metric("Revenu :",revenu, delta_revenu)
        col2.metric("Ancienneté pro :", anciennete, calculate_deltadate(-delta_anciennete))
        
        
        
        
        



if __name__ == '__main__':
    main()
