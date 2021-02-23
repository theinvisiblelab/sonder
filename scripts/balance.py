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

st.markdown("## ⚖️ Balance")

st.write(
    "`Balance` is an attempt to enable fairer knowledge access. Affirmative action for knowledge search per se."
)

query = st.text_input("Seek the unknown...").strip()
st.slider("Adjust balance metric", -1.0, 1.0, (-1.0, 1.0))

st.markdown("&nbsp;")
st.markdown("&nbsp;")

st.markdown("_STILL COOKING!_ :spaghetti:")
st.markdown(
    "Watch our [github](https://github.com/saurabh-khanna/sonder) repository for updates."
)
