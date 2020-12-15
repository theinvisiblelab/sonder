#!/usr/bin/python
# -*- coding: utf-8 -*-

## PARAMETERS ##
import requests
import pandas as pd
import io
from textblob import TextBlob

# The url below can be replaced with 'http://localhost/8888/search' if searx is locally setup.
# See https://searx.github.io/searx/admin/installation.html for more details.
url = 'http://searx.sonder.care/search'

@st.cache(allow_output_mutation=True)
def load_data(query):
    df = []
    for page in range(1, 4):
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


@st.cache
def sentiment_calc(text):
    try:
        return TextBlob(text).sentiment
    except:
        return None


## CONTENT ##

st.header('Spectrum')

st.write("Spectrum opens up access to the spectrum of knowledge.")

query = st.text_input('Type something you wish to know and hit return!').strip()

(col1, col2) = st.beta_columns([1, 1.6180339887])

choose_metric = col1.selectbox('Choose a metric', ["Polarity", "Subjectivity"])
if choose_metric == "Polarity":
    polarity = col2.slider('Adjust polarity', -1.0, 1.0, (-1.0, 1.0))
elif choose_metric == "Subjectivity":
    subjectivity = col2.slider('Adjust subjectivity', 0.0, 1.0, (0.0, 1.0))

(col3, col4) = st.beta_columns(2)

if query != '':
    df = load_data(query)
    if choose_metric == "Polarity":
        df['polarity'] = df.apply(lambda row: sentiment_calc(row['title'])[0], axis=1)
        df['polarity'] = df['polarity'].apply(lambda x: round(x, 2))
        df_filtered = df[(df['polarity'] >= polarity[0]) & (df['polarity'] <= polarity[1])]
        df_low = df_filtered[(df_filtered['polarity'] < 0)]
        df_low = df_low.sort_values(by=['polarity'], ascending=True).head(30)
        df_high = df_filtered[(df_filtered['polarity'] >= 0)]
        df_high = df_high.sort_values(by=['polarity'], ascending=False).head(30)
        col3.subheader('Results with low polarity')
        col3.markdown("---")
        col4.subheader('Results with high polarity')
        col4.markdown("---")
        for index, row in df_low.iterrows():
            with col3.beta_expander(row['title']):
                st.write("Polarity: ", row['polarity'])
                if row['content'] == row['content']:
                    st.write(row['content'])
                st.write("Read it all here: ", row['url'])
        for index, row in df_high.iterrows():
            with col4.beta_expander(row['title']):
                st.write("Polarity: ", row['polarity'])
                if row['content'] == row['content']:
                    st.write(row['content'])
                st.write("Read it all here: ", row['url'])
    elif choose_metric == "Subjectivity":
        df['subjectivity'] = df.apply(lambda row: sentiment_calc(row['title'])[1], axis=1)
        df['subjectivity'] = df['subjectivity'].apply(lambda x: round(x, 2))
        st.subheader('Results in chosen subjectivity spectrum')
        st.markdown("---")
        df_filtered = df[(df['subjectivity'] >= subjectivity[0]) & (df['subjectivity'] <= subjectivity[1])].head(10)
        for index, row in df_filtered.iterrows():
            with st.beta_expander(row['title']): 
                st.write("Subjectivity: ", row['subjectivity'])
                if row['content'] == row['content']:
                    st.write(row['content'])
                st.write("Read it all here: ", row['url'])

