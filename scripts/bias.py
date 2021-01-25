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

# The url below can be replaced with 'http://localhost/8888/search' if searx is locally setup.
# See https://searx.github.io/searx/admin/installation.html for more details.
url = "http://searx.sonder.care/search"


@st.cache(allow_output_mutation=True, show_spinner=False)
def load_data(query):
    df = []
    for page in range(1, 11):
        querystring = {
            "q": query,
            "categories": "general",
            "engines": ["google", "bing", "duckduckgo"],
            "pageno": page,
            "format": "json",
        }
        response = requests.request("GET", url, params=querystring)
        text = yaml.safe_load(response.text)
        df_mini = pd.DataFrame(text["results"])
        df.append(df_mini)
    df = pd.concat(df)
    df = df.sort_values(by=["score"], ascending=False)
    df["title"] = df["title"].str.encode("utf-8", "ignore").str.decode("utf-8")
    df["content"] = df["content"].str.encode("utf-8", "ignore").str.decode("utf-8")
    return df


@st.cache(allow_output_mutation=True, show_spinner=False)
def sentiment_calc(text):
    try:
        return TextBlob(text).sentiment
    except:
        return None


def get_ip(hostname):
    try:
        return socket.gethostbyname(hostname)
    except:
        return None


# You can get your own free maxmind geoip key and GeoLite2-City database if deploying your own sonder servers
# Check https://dev.maxmind.com/geoip/geoip2/geolite2/ for more details.
def map_result(ip_address):
    try:
        with geoip2.database.Reader(Path("geoip/GeoLite2-City.mmdb")) as reader:
            response = reader.city(ip_address)
            return (
                response.country.iso_code,
                response.location.latitude,
                response.location.longitude,
                response.city.name,
                response.country.name,
            )
    except:
        return None


## CONTENT ##

st.markdown(Path("markdown/bias.md").read_text(), unsafe_allow_html=True)

st.markdown("## Bias")

st.write("`Bias` is an attempt to understand how fair our search for web knowledge is.")

query = st.text_input("Seek the unknown...").strip()

st.markdown("&nbsp;")


if query != "":
    with st.spinner("Finding what you seek..."):
        df = load_data(query)

    expander1 = st.beta_expander("Sentiment Bias", expanded=True)
    expander2 = st.beta_expander("Spatial Bias", expanded=False)
    expander3 = st.beta_expander("Lingual Bias", expanded=False)
    expander4 = st.beta_expander("View Search Results", expanded=False)

    with expander1:
        with st.spinner("Assessing sentiment in your search results..."):
            df["polarity"] = df.apply(
                lambda row: sentiment_calc(row["title"] + " " + str(row["content"]))[0],
                axis=1,
            )
            df["polarity"] = df["polarity"].apply(lambda x: round(x, 4))
            df["rank"] = df.reset_index().index + 1
            sentiment_mean = round(df["polarity"].mean(), 4)
            sentiment_median = round(df["polarity"].median(), 4)
            sentiment_min = df["polarity"].min()
            sentiment_max = df["polarity"].max()
            df_size = len(df.index)
            # df['new_score'] = df['score'] + abs(df['polarity'])
            # st.write(df.head(20))
            if sentiment_mean <= -0.1:
                sentiment_text = "negative"
            if sentiment_mean > -0.1 and sentiment_mean < 0.1:
                sentiment_text = "neutral"
            if sentiment_mean >= 0.1:
                sentiment_text = "positive"
            st.write(
                "The average sentiment in your top "
                + str(df_size)
                + " search results is "
                + sentiment_text
                + ", with a mean of "
                + str(sentiment_mean)
                + ". The distribution of sentiment in these results is shown below, with the red line highlighting the distribution median."
            )
            plot_dist = (
                ggplot(df, aes("polarity"))
                + geom_density(fill="blue", alpha=0.25, na_rm=True)
                + geom_vline(
                    xintercept=sentiment_median, linetype="dashed", color="red"
                )
                + theme_bw()
                + xlim(sentiment_min, sentiment_max)
                + labs(x="Sentiment", y="Density")
            )
            st.pyplot(ggplot.draw(plot_dist))
            correlation = round(df["rank"].corr(df["polarity"]), 4)
            st.write(
                "The correlation between search result rank and its sentiment is "
                + str(correlation)
                + ". The scatterplot is shown below."
            )
            plot_corr = (
                ggplot(df, aes("rank", "polarity"))
                + geom_jitter(fill="blue", alpha=0.5, size=2.5)
                + theme_bw()
                + labs(x="Search Result Rank", y="Sentiment")
            )
            st.pyplot(ggplot.draw(plot_corr))
            st.markdown("&nbsp;")


st.markdown("&nbsp;")
st.markdown("&nbsp;")

if query != "":
    with expander2:
        st.write("Highlighting spatial bias in your search results.")
        with st.spinner("Geolocating your search results..."):
            df["domain"] = df.apply(lambda row: row["parsed_url"][1], axis=1)
            df["ip_address"] = df.apply(lambda row: get_ip(row["domain"]), axis=1)
            df = df[df["ip_address"].notnull()]
            df["map_result_tuple"] = df.apply(
                lambda row: map_result(row["ip_address"]), axis=1
            )
            df = df[df["map_result_tuple"].notnull()]
            df["country"] = df.apply(lambda row: row["map_result_tuple"][0], axis=1)
            df["latitude"] = df.apply(lambda row: row["map_result_tuple"][1], axis=1)
            df["longitude"] = df.apply(lambda row: row["map_result_tuple"][2], axis=1)
            df["city"] = df.apply(lambda row: row["map_result_tuple"][3], axis=1)
            df["country_name"] = df.apply(
                lambda row: row["map_result_tuple"][4], axis=1
            )
            df["cctld"] = df.apply(lambda row: row["domain"].split(".")[-1], axis=1)

            # correcting locations based on cctld
            df = pd.merge(
                df,
                pd.read_csv(Path("cctld/capitals.csv")),
                on="cctld",
                how="left",
            )
            df.loc[
                (df["cap_lat"].notnull())
                & (df["cap_long"].notnull())
                & (df["country"].str.lower() != df["cctld"]),
                "latitude",
            ] = df.loc[
                (df["cap_lat"].notnull())
                & (df["cap_long"].notnull())
                & (df["country"].str.lower() != df["cctld"]),
                "cap_lat",
            ]
            df.loc[
                (df["cap_lat"].notnull())
                & (df["cap_long"].notnull())
                & (df["country"].str.lower() != df["cctld"]),
                "longitude",
            ] = df.loc[
                (df["cap_lat"].notnull())
                & (df["cap_long"].notnull())
                & (df["country"].str.lower() != df["cctld"]),
                "cap_long",
            ]
            df.loc[
                (df["cap_lat"].notnull())
                & (df["cap_long"].notnull())
                & (df["country"].str.lower() != df["cctld"]),
                "city",
            ] = df.loc[
                (df["cap_lat"].notnull())
                & (df["cap_long"].notnull())
                & (df["country"].str.lower() != df["cctld"]),
                "capital",
            ]
            df.loc[
                (df["cap_lat"].notnull())
                & (df["cap_long"].notnull())
                & (df["country"].str.lower() != df["cctld"]),
                "country_name",
            ] = df.loc[
                (df["cap_lat"].notnull())
                & (df["cap_long"].notnull())
                & (df["country"].str.lower() != df["cctld"]),
                "country_cctld",
            ]

            map = folium.Map(location=[0, 0], zoom_start=1.49, tiles="cartodb positron")
            for i in range(0, len(df)):
                folium.Marker(
                    location=[df.iloc[i]["latitude"], df.iloc[i]["longitude"]],
                    popup=df.iloc[i]["city"],
                ).add_to(map)
            folium_static(map)

            st.write(
                "Your top "
                + str(df_size)
                + " search results come from websites hosted in "
                + str(df["country_name"].nunique())
                + " countries."
            )

            plot_country = (
                ggplot(df, aes("country_name"))
                + geom_bar(fill="blue", color="black", alpha=0.25, na_rm=True)
                + theme_bw()
                + coord_flip()
                + labs(x="Country", y="Results")
            )
            st.pyplot(ggplot.draw(plot_country))
            st.markdown("&nbsp;")

            # IDEA: Add average rank per country plot.

st.markdown("&nbsp;")
st.markdown("&nbsp;")

if query != "":
    with expander3:
        st.write("Highlighting lingual bias in your search results.")
        st.markdown("&nbsp;")
        st.markdown(
            "_STILL COOKING!_ Watch our [github](https://github.com/saurabh-khanna/sonder) repository for updates."
        )
        st.markdown("&nbsp;")

st.markdown("&nbsp;")
st.markdown("&nbsp;")

if query != "":
    with expander4:
        st.markdown("\n\n")
        # st.write(df)
        for index, row in df.iterrows():
            with st.beta_container():
                st.write("Sentiment: ", row["polarity"])
                st.write("Host Country: ", row["country_name"])
                # st.write('Search Rank: ', row['rank'])
                if row["content"] == row["content"]:
                    st.write(row["content"])
                st.write("Read it all [here](" + row["url"] + ")")
                st.markdown("---")
