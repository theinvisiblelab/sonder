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
from statistics import median
import datetime


def draw_bar(df_summary):
    plot_summary = (
        alt.Chart(df_summary)
        .mark_bar(opacity=0.80)
        .encode(
            x=alt.X("sentiment", title="Sentiment"),
            y=alt.Y("country", title="Country", sort="-x"),
            tooltip=["sentiment"],
            color=alt.condition(
                alt.datum.sentiment > 0,
                alt.value("#0ec956"),  # The positive color
                alt.value("#ff1717"),  # The negative color
            ),
        )
        .configure_title(fontSize=18)
        .configure_axis(labelFontSize=15, titleFontSize=15)
    )
    st.altair_chart(plot_summary, use_container_width=True)


def draw_dist(df_temp):
    web_dist_sent1 = (
        alt.Chart(df_temp[df_temp["sentiment"].notna()])
        .transform_density(
            "sentiment",
            as_=["sentiment", "density"],
        )
        .mark_area(opacity=0.75)
        .encode(
            x="sentiment:Q",
            y="density:Q",
            tooltip=["sentiment"],
        )
        .encode(
            x=alt.X("sentiment:Q", title="Sentiment"),
            y=alt.Y("density:Q", title=""),
        )
        .properties(
            title=alt.TitleParams(
                ["* Dashed red line indicates the distribution median"],
                baseline="bottom",
                orient="bottom",
                anchor="end",
                fontWeight="normal",
                fontSize=11,
            )
        )
    )
    web_dist_sent2 = (
        alt.Chart(df_temp[df_temp["sentiment"].notna()])
        .mark_rule(color="red", strokeDash=[10, 10], size=2)
        .encode(x="median(sentiment):Q")
    )

    st.altair_chart(web_dist_sent1 + web_dist_sent2, use_container_width=True)
    st.markdown("\n")


# this is actually another bar chart for now
def draw_corr(df):
    plot_corr = (
        alt.Chart(df)
        .mark_bar(size=20, opacity=0.8)
        .encode(
            x=alt.X("trend_rank:Q", title="Search Trend Rank"),
            y=alt.Y("sentiment_median:Q", title="Median Sentiment"),
            tooltip=["trend_rank", "sentiment_median"],
            color=alt.condition(
                alt.datum.sentiment_median >= 0,
                alt.value("#0ec956"),  # The positive color
                alt.value("#ff1717"),  # The negative color
            ),
        )
    )
    rule_corr = (
        alt.Chart(pd.DataFrame({"y": [0]}))
        .mark_rule(strokeDash=[10, 10], size=1.5)
        .encode(y="y")
    )
    st.altair_chart(plot_corr + rule_corr, use_container_width=True)


def print_trends(df):
    for index, row in df.iterrows():
        with st.beta_container():
            # st.write("Sentiment: ", row["sentiment"])
            # st.write("Host Country: `", row["country_name"], "`")
            st.markdown(
                "> " + row["article"],
                unsafe_allow_html=True,
            )
            # st.markdown("---")
    st.markdown("&nbsp;")


#############
## CONTENT ##
#############

st.markdown("## 🕯️ Wiki Trends")
st.write("Explore sentiment trends for Wikipedia search across the globe.")
st.markdown("&nbsp;")
navigate_wiki = st.radio("Explore", ["All", "Desktop", "Mobile"], 0)
st.markdown("---")
st.markdown("&nbsp;")

# read data
df = pd.read_csv(Path("today/wiki_trends.csv"))
df.dropna(subset=["sentiment"], inplace=True)

df.rename(columns={"country": "cctld"}, inplace=True)
df = pd.merge(
    df,
    pd.read_csv(Path("cctld/capitals.csv")),
    on="cctld",
    how="left",
)
df.rename(columns={"country_cctld": "country"}, inplace=True)

# excluding rows with just 1 trend for a country
df = df.groupby("country").filter(lambda x: len(x) > 1)

df["sentiment"] = pd.to_numeric(df["sentiment"], errors="coerce")
df["article"] = df["article"].str.replace("_", " ")

# st.write(df)
country_list = sorted(list(set(df["country"].tolist())))
country_list.insert(0, "")

df["date"] = pd.to_datetime(df["date"])
st.write("_Updated: " + df["date"].iloc[0].strftime("%B %d, %Y") + "_")

col1, col2 = st.beta_columns([1, 1])

if navigate_wiki == "All":

    with col1:
        st.write("## Global Trends Today")
        st.write("&nbsp;")
        st.write("#### Sentiment ranking")
        st.write("\n\n")

        # country rank plot
        df_country = pd.DataFrame(
            df.groupby(["country"])[["sentiment"]].median(),
            columns=["sentiment"],
        )
        df_country = df_country.reset_index()
        df_country["country"] = df_country.apply(
            lambda row: row["country"].replace("_", " ").title(), axis=1
        )
        df_country.dropna(subset=["sentiment"], inplace=True)
        draw_bar(df_country)

        # sentiment distribution
        st.write("#### Global: Sentiment distribution today*")
        st.write("\n\n")
        df_dist = pd.DataFrame(df, columns=["sentiment"])
        draw_dist(df_dist)

    with col2:
        st.write("## Regional Trends Today")
        # draw_dist(sentiment_flatlist(df))
        st.write("&nbsp;")
        country = st.selectbox("Choose a country", country_list)
        if country != "":
            st.write("&nbsp;")

            st.write("#### " + str(country) + ": Sentiment distribution today")
            st.write("\n\n")
            df_dist = pd.DataFrame(df[df["country"] == country], columns=["sentiment"])
            draw_dist(df_dist)

            st.write("#### " + str(country) + ": Wiki Trends")
            st.markdown("---")
            print_trends(df[df["country"] == country])
