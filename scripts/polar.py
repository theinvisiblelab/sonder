#!/usr/bin/python
# -*- coding: utf-8 -*-

## PARAMETERS ##
import os
import requests
import pandas as pd
import yaml
from textblob import TextBlob

url = 'https://rapidapi.p.rapidapi.com/api/search/NewsSearchAPI'


@st.cache(allow_output_mutation=True)
def load_data(query):
    querystring = {
        'pageSize': '50',
        'q': query,
        'autoCorrect': 'true',
        'pageNumber': '1',
        'safeSearch': 'true',
        'toPublishedDate': 'null',
        'fromPublishedDate': 'null',
    }
    headers = \
        {'x-rapidapi-host': os.environ['API_HOST'],
         'x-rapidapi-key': os.environ['API_KEY']}
    response = requests.request('GET', url, headers=headers,
                                params=querystring)
    text = yaml.safe_load(response.text)
    return pd.DataFrame(text['value'])


@st.cache
def sentiment_calc(text):
    try:
        return TextBlob(text).sentiment
    except:
        return None


## CONTENT ##

st.header('Polar')


st.write("Polar opens up access to the diametric ends of knowledge.")

query = st.text_input('Type something you wish to know and hit return!').strip()

(col1, col2) = st.beta_columns(2)

if query != '':
    df = load_data(query)
    df['polarity'] = df.apply(
        lambda row: sentiment_calc(row['title'])[0], axis=1)
    col1.subheader('Results with low polarity')
    col1.markdown("---")
    col2.subheader('Results with high polarity')
    col2.markdown("---") 
    df_low = df[(df['polarity'] <= 0)].head(10)
    df_high = df[(df['polarity'] > 0)].head(10)
    for index, row in df_low.iterrows():
        with col1.beta_expander(row['title']):
            st.write('.'.join(row['body'].split('.')[:2]).strip() + ".")
            st.write("Read it all here: ", row['url'])
    for index, row in df_high.iterrows():
        with col2.beta_expander(row['title']):
            st.write('.'.join(row['body'].split('.')[:2]).strip() + ".")
            st.write("Read it all here: ", row['url'])
