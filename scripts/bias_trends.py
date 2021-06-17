## PARAMETERS ##
import requests
import numpy as np
import pandas as pd
import io
import yaml
import socket
# from textblob import TextBlob
import scipy
import altair as alt
from wordcloud import WordCloud
from PIL import Image

## CONTENT ##

st.markdown("## 📣 Trends")
st.write("Explore fairness trends for internet access across the globe.")

st.markdown("&nbsp;")

expander_1 = st.beta_expander("🕸️ Web")
expander_2 = st.beta_expander("🗞️ News")
expander_3 = st.beta_expander("🐦 Twitter")
expander_4 = st.beta_expander("💡 Wikipedia")

with expander_1:

    col1, col2 = st.beta_columns([1, 2])
    country_list = [
        "United States",
        "Argentina",
        "Australia",
        "Austria",
        "Belgium",
        "Brazil",
        "Canada",
        "Chile",
        "Colombia",
        "Czech Republic",
        "Denmark",
        "Egypt",
        "Finland",
        "France",
        "Germany",
        "Greece",
        "Hong Kong",
        "Hungary",
        "India",
        "Indonesia",
        "Ireland",
        "Israel",
        "Italy",
        "Japan",
        "Kenya",
        "Malaysia",
        "Mexico",
        "Netherlands",
        "New Zealand",
        "Nigeria",
        "Norway",
        "Philippines",
        "Poland",
        "Portugal",
        "Romania",
        "Russia",
        "Saudi Arabia",
        "Singapore",
        "South Africa",
        "South Korea",
        "Sweden",
        "Switzerland",
        "Taiwan",
        "Thailand",
        "Turkey",
        "Ukraine",
        "United Kingdom",
        "Vietnam",
    ]
    country = col1.selectbox("Choose a country", country_list)

    duration = col2.slider("Choose a window (days)", 15, 100, 50)

    col2.write("\n\n")
    col2.write(
        "#### "
        + str(country)
        + ": Bias trends for the last "
        + str(duration)
        + " days*"
    )
    col2.markdown("&nbsp;")

    source = pd.DataFrame(
        {
            "Window (Days)": np.arange(duration),
            "Sentiment representation": np.random.randint(low=0, high=75, size=duration),
            "Spatial representation": np.random.randint(low=20, high=100, size=duration),
            "Eco-friendliness": np.random.randint(low=10, high=60, size=duration),
        }
    )

    base = (
        alt.Chart(source)
        .mark_circle(opacity=0.5)
        .transform_fold(
            fold=["Sentiment representation", "Spatial representation", "Eco-friendliness"],
            as_=["Bias category", "Bias magnitude"],
        )
        .encode(
            alt.X("Window (Days):Q"),
            alt.Y("Bias magnitude:Q"),
            alt.Color("Bias category:N"),
        )
        .properties(
            title=alt.TitleParams(
                ["* Chart populated with proxy data"],
                baseline="bottom",
                orient="bottom",
                anchor="end",
                fontWeight="normal",
                fontSize=11,
            )
        )
    )

    col2.altair_chart(
        base
        + base.transform_loess(
            "Window (Days)", "Bias magnitude", groupby=["Bias category"]
        ).mark_line(size=4),
        use_container_width=True,
    )

    col1.write("\n\n")
    col1.write("#### " + str(country) + ": Search trends for the last 24 hours")
    country_lower = country.lower().replace(" ", "_")
    col1.image(
        Image.open(Path("wordclouds/" + str(country_lower) + ".png")),
        use_column_width="auto",
    )

with expander_2:
    st.markdown("&nbsp;")
    st.markdown("_STILL COOKING!_ :spaghetti:")
    st.markdown(
        "Watch our [GitHub](https://github.com/sonder-labs/sonder) repository for updates on this feature."
    )
    st.markdown("&nbsp;")

with expander_3:
    st.markdown("&nbsp;")
    st.markdown("_STILL COOKING!_ :spaghetti:")
    st.markdown(
        "Watch our [GitHub](https://github.com/sonder-labs/sonder) repository for updates on this feature."
    )
    st.markdown("&nbsp;")

with expander_4:
    st.markdown("&nbsp;")
    st.markdown("_STILL COOKING!_ :spaghetti:")
    st.markdown(
        "Watch our [GitHub](https://github.com/sonder-labs/sonder) repository for updates on this feature."
    )
    st.markdown("&nbsp;")
