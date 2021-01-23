#!/usr/bin/python
# -*- coding: utf-8 -*-

## PARAMETERS ##
import requests
import numpy as np
import pandas as pd
import io
import yaml
import socket
from textblob import TextBlob
import scipy
import geoip2.database
import folium
from streamlit_folium import folium_static
from plotnine import *


## CONTENT ##

st.markdown(Path("markdown/balance.md").read_text(), unsafe_allow_html=True)

st.markdown("## Balance")

st.write("Balance is affirmative action for knowledge search - an attempt towards fairer knowledge access.")

query = st.text_input("Type something you wish to know and hit return!").strip()
polarity = st.slider('Adjust balance metric', -1.0, 1.0, (-1.0, 1.0))

st.markdown("\n\n\n\n")

st.markdown("_STILL COOKING!_ Watch our [github](https://github.com/saurabh-khanna/sonder) repository for updates.")
