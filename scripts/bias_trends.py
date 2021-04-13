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
import altair as alt

## CONTENT ##

# st.markdown(Path("markdown/balance.md").read_text(), unsafe_allow_html=True)

st.markdown("## 📣 Bias trends")
st.markdown("&nbsp;")
# st.write(
#     "Balance enables fairer knowledge search by valuing relevance and diversity. Affirmative action for knowledge search per se."
# )

# query = st.text_input("Seek the unknown...").strip()
# st.slider("Adjust balance metric", -1.0, 1.0, (-1.0, 1.0))

with st.beta_expander("🕸️ Web"):

    col1, col2 = st.beta_columns([1, 2])

    country = col1.selectbox('Choose a country', ("Wherever I am", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua & Deps", "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina", "Burundi", "Cambodia", "Cameroon", "Canada", "Cape Verde", "Central African Rep", "Chad", "Chile", "China", "Colombia", "Comoros", "Congo", "Congo {Democratic Rep}", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "East Timor", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland {Republic}", "Israel", "Italy", "Ivory Coast", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea North", "Korea South", "Kosovo", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Macedonia", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russian Federation", "Rwanda", "St Kitts & Nevis", "St Lucia", "Saint Vincent & the Grenadines", "Samoa", "San Marino", "Sao Tome & Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Swaziland", "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Togo", "Tonga", "Trinidad & Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"))

    duration = col2.slider('Choose a window (days)', 15, 100, 30)

    st.write("\n\n")
    st.write('#### Bias trends in ' + str(country) + ' for the last ' + str(duration) + ' days *')

    # df1 = pd.DataFrame(
    # np.random.randint(low = 15, high = 31, size=(duration, 1)),
    # columns=['Sentiment Bias'])
    #
    # df1['Environmental Hazard'] = np.random.randint(low = 40, high = 71, size=(duration, 1))
    #
    # st.line_chart(df1)
    source = pd.DataFrame({
        'Window (Days)': np.arange(duration),
        'Sentiment bias': np.random.randint(low = 0, high = 75, size = duration),
        'Spatial bias': np.random.randint(low = 20, high = 100, size = duration),
        'Environmental bias': np.random.randint(low = 40, high = 100, size = duration)
    })

    base = alt.Chart(source).mark_circle(opacity=0.5).transform_fold(
        fold=['Sentiment bias', 'Spatial bias', 'Environmental bias'],
        as_=['Bias category', 'Bias magnitude']
    ).encode(
        alt.X('Window (Days):Q'),
        alt.Y('Bias magnitude:Q'),
        alt.Color('Bias category:N')
    ).properties(
        title=alt.TitleParams(
            ['* Chart populated with proxy data'],
            baseline='bottom',
            orient='bottom',
            anchor='end',
            fontWeight='normal',
            fontSize=11
        )
    )

    st.altair_chart(base + base.transform_loess('Window (Days)', 'Bias magnitude', groupby=['Bias category']).mark_line(size=4), use_container_width = True)

    st.markdown("&nbsp;")
    st.markdown("_STILL COOKING!_ :spaghetti:")
    st.markdown(
        "Watch our [GitHub](https://github.com/sonder-labs/sonder) repository for updates."
    )
    st.markdown("&nbsp;")

with st.beta_expander("🗞️ News"):
    st.markdown("&nbsp;")
    st.markdown("_STILL COOKING!_ :spaghetti:")
    st.markdown(
        "Watch our [GitHub](https://github.com/sonder-labs/sonder) repository for updates."
    )
    st.markdown("&nbsp;")

with st.beta_expander("🐦 Twitter"):
    st.markdown("&nbsp;")
    st.markdown("_STILL COOKING!_ :spaghetti:")
    st.markdown(
        "Watch our [GitHub](https://github.com/sonder-labs/sonder) repository for updates."
    )
    st.markdown("&nbsp;")

with st.beta_expander("💡 Wikipedia"):
    st.markdown("&nbsp;")
    st.markdown("_STILL COOKING!_ :spaghetti:")
    st.markdown(
        "Watch our [GitHub](https://github.com/sonder-labs/sonder) repository for updates."
    )
    st.markdown("&nbsp;")
