#!/usr/bin/python
# -*- coding: utf-8 -*-

## PARAMETERS ##
import requests
import pandas as pd
import io

# The url below can be replaced with 'http://localhost/8888/search' if searx is locally setup.
# See https://searx.github.io/searx/admin/installation.html for more details.
url = 'http://searx.sonder.care/search'

@st.cache(allow_output_mutation=True)
def load_data(query):
    df = []
    for page in range(1, 6):
        querystring = {
            'q': query,
            'categories': 'news',
            'pageno': page,
            'format': 'csv',
            'language': "en-US" 
        }
        response = requests.request('GET', url, params=querystring).content
        df_mini = pd.read_csv(io.StringIO(response.decode('utf-8')))
        df.append(df_mini)
    df = pd.concat(df)
    return df



## CONTENT ##

st.header('Spacetime')

st.write("Spacetime highlights spatial and temporal bias in search results.")

query = st.text_input('Type something you wish to know and hit return!').strip()

if query != '':
    df = load_data(query)
    st.write(df.head(10))
