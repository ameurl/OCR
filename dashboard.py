import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import requests

import json
from urllib.request import urlopen
from datetime import date, timedelta
import plotly.express as px
import os

def request_prediction(model_uri, data):
    headers = {"Content-Type": "application/json"}

    
    
    st.write(data)
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

def calculate_info(Dict):
    age = calculate_age(Dict[0]["DAYS_BIRTH"])
    revenu = Dict[0]["AMT_INCOME_TOTAL"]
    montant_credit = Dict[0]["AMT_CREDIT"]
    anciennete = calculate_anciennete(Dict[0]["DAYS_EMPLOYED"])
    delta_age = age-45
    delta_revenu = revenu-170000
    delta_anciennete = Dict[0]["DAYS_EMPLOYED"]-(-1815)
    return age, revenu, anciennete, delta_age, delta_revenu, delta_anciennete, montant_credit
    

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
        
        
        Dict = json.loads(API_data)
        
        
        age, revenu, anciennete, delta_age, delta_revenu, delta_anciennete, montant_credit = calculate_info(Dict)
        

        
        if Dict[0]["PREDICTION"] <0.51 :
            st.success('CRÉDIT ACCEPTÉ, Score: '+str(Dict[0]["PREDICTION"]))
        else :
            st.error('CRÉDIT REFUSÉ')
        
        st.slider('Score',min_value=0.0, max_value=1.0, value=Dict[0]["PREDICTION"],disabled=True)
        st.subheader('Informations Client :')
        
        col1, col2, col3 = st.columns(3)
        
        col1.metric("Age :", age, delta_age)
        col2.metric("Sexe :", Dict[0]["CODE_GENDER"])
        col3.metric("Status marital :", Dict[0]["NAME_FAMILY_STATUS"])
        
        st.subheader('Informations Profesionnelles :')
        
        col1, col2= st.columns(2)
        
        col1.metric("Revenu :",revenu, delta_revenu)
        col2.metric("Ancienneté :", anciennete, calculate_deltadate(-delta_anciennete))
        st.write('Les indicateurs sous les informations Age, Revenu et Ancienneté indique la différence entre le client et la moyenne des clients')
        st.write('')
        st.write('')
        
        tab1, tab2, tab3, tab4 = st.tabs(["Montant", "Salaire", "Age", "Interprétabilité"])
        with tab1:
            st.write('Le montant de la demande de crédit : ',montant_credit)          
            fig = px.histogram(data['AMT_CREDIT'])
            fig.add_vline(x=montant_credit, line_width=5, line_color='red', annotation_text='Le client') 
            st.plotly_chart(fig, use_container_width=True)

            st.write("Description de l'ensemble des demandes de crédit")
            df_credit = pd.DataFrame({'Crédit': data['AMT_CREDIT'].describe()})
            st.table(df_credit)

        with tab2:
            st.write("Le salaire du client : ",revenu)
            fig = px.histogram(data['AMT_INCOME_TOTAL'][data['AMT_INCOME_TOTAL']<800000])
            fig.add_vline(x=revenu, line_width=5, line_color='red', annotation_text='Le client') 
            st.plotly_chart(fig, use_container_width=True)
            st.write("Description des salaires de nos clients")
            df_salaire = pd.DataFrame({'Salaire': data['AMT_INCOME_TOTAL'].describe()})
            st.table(df_salaire)       

        with tab3:
            st.write("L'age du client : ",age)
            df_age = -data['DAYS_BIRTH_x'].apply(calculate_age)
            fig = px.histogram(df_age)
            fig.add_vline(x=age, line_width=5, line_color='red', annotation_text='Le client') 
            st.plotly_chart(fig, use_container_width=True)
            st.write("Description de l'age de nos clients")
            df_age = pd.DataFrame({'Age': df_age.describe()})
            st.table(df_age) 
           
        with tab4:
            st.write("Les 10 Features les plus importantes ainsi que leurs poids dans la décision")
            Dict_feat = {x:y for x,y in Dict[1].items() if y is not None}
            Dict_feat = pd.DataFrame.from_dict([list(Dict_feat),Dict_feat.values()]).transpose()
            Dict_feat = Dict_feat.rename(columns={0: "Variable", 1: "Poids"})
            fig = px.bar(Dict_feat, x='Variable', y="Poids")
            st.plotly_chart(fig, use_container_width=True)
            st.write("Tableau")
            st.table(Dict_feat)
        



if __name__ == '__main__':
    main()
