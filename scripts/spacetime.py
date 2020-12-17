#!/usr/bin/python
# -*- coding: utf-8 -*-

## PARAMETERS ##
import requests
import pandas as pd
import io
import os
import yaml
import socket
import geoip2.webservice

# The url below can be replaced with 'http://localhost/8888/search' if searx is locally setup.
# See https://searx.github.io/searx/admin/installation.html for more details.
url = 'http://searx.sonder.care/search'

@st.cache(allow_output_mutation=True, show_spinner=False)
def load_data(query):
    df = []
    for page in range(1, 2):
        querystring = {
            'q': query,
            'categories': 'news',
            'pageno': page,
            'format': 'json',
            'language': "en-US" 
        }
        response = requests.request('GET', url, params=querystring)
        text = yaml.safe_load(response.text)
        df_mini = pd.DataFrame(text['results'])
        df.append(df_mini)
    df = pd.concat(df)
    return df


def get_ip(hostname):
    try:
        return socket.gethostbyname(hostname)
    except:
        return None

# you can get your own free maxmind geoip key if deploying your own sonder servers
def map_result(ip_address):
	try:
		with geoip2.webservice.Client(os.environ['MAXMIND_ACCOUNT'], os.environ['MAXMIND_FREE_API_KEY'], host = 'geolite.info') as client:
			response = client.city(ip_address)
			return(response.country.name, response.location.latitude, response.location.longitude)
	except:
		return None


## CONTENT ##

st.header('Spacetime')

st.write("Spacetime highlights spatial and temporal bias in search results.")

query = st.text_input('Type something you wish to know and hit return!').strip()

'''
# Spatial bias
'''

if query != '':
	with st.spinner('Geolocating your search...'):
		df = load_data(query)
		df['domain'] = df.apply(lambda row: row['parsed_url'][1], axis=1)
		df['ip_address'] = df.apply(lambda row: get_ip(row['domain']), axis=1)
		df['map_result_tuple'] = df.apply(lambda row: map_result(row['ip_address']), axis=1)
	st.write(df)
	df['country'] = df.apply(lambda row: row['map_result_tuple'][0], axis=1)
	df['latitude'] = df.apply(lambda row: row['map_result_tuple'][1], axis=1)
	df['longitude'] = df.apply(lambda row: row['map_result_tuple'][2], axis=1)
	df['cctld'] = df.apply(lambda row: row['domain'].split('.')[-1], axis=1)
	#st.write(df)
	st.balloons()
