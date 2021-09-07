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
from statistics import median, mean
import datetime

# can use for search rank
def list_to_dict(lst):
    res_dict = {i + 1: float(lst[i]) for i in range(len(lst))}
    return res_dict


def sentiment_flatlist(df):
    sentlist1 = df["sentiment_dist"].tolist()
    sentlist2 = [x for x in sentlist1 if x is not None]  # remove none
    sentlist3 = [item for sublist in sentlist2 for item in sublist]
    sentiment_list = [float(x) for x in sentlist3 if x != "nan"]
    return sentiment_list


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


def draw_eco_bar(df_summary):
    plot_summary = (
        alt.Chart(df_summary)
        .mark_bar(opacity=0.80)
        .encode(
            x=alt.X("eco_fr", title="Carbon Cost"),
            y=alt.Y("country", title="Country", sort="-x"),
            tooltip=["eco_fr"],
            color=alt.condition(
                alt.datum.eco_fr > df_summary["eco_fr"].mean(),
                alt.value("#0ec956"),  # The positive color
                alt.value("#ff1717"),  # The negative color
            ),
        )
    )
    rule = (
        alt.Chart(df_summary[df_summary["eco_fr"].notna()])
        .mark_rule(color="red", strokeDash=[10, 10], size=2)
        .encode(x="mean(eco_fr):Q")
    )
    st.altair_chart(
        alt.layer(plot_summary, rule)
        .configure_title(fontSize=18)
        .configure_axis(labelFontSize=15, titleFontSize=15),
        use_container_width=True,
    )


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
                ["* Dashed red line indicates the distribution mean"],
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
        .encode(x="mean(sentiment):Q")
    )

    st.altair_chart(web_dist_sent1 + web_dist_sent2, use_container_width=True)
    st.markdown("\n")


def draw_eco_dist(df_temp):
    web_dist_sent1 = (
        alt.Chart(df_temp[df_temp["eco_fr"].notna()])
        .transform_density(
            "eco_fr",
            as_=["eco_fr", "density"],
        )
        .mark_area(opacity=0.75)
        .encode(
            x="eco_fr:Q",
            y="density:Q",
            tooltip=["eco_fr"],
        )
        .encode(
            x=alt.X("eco_fr:Q", title="Carbon Cost"),
            y=alt.Y("density:Q", title=""),
        )
        .properties(
            title=alt.TitleParams(
                ["* Dashed red line indicates the distribution mean"],
                baseline="bottom",
                orient="bottom",
                anchor="end",
                fontWeight="normal",
                fontSize=11,
            )
        )
    )
    web_dist_sent2 = (
        alt.Chart(df_temp[df_temp["eco_fr"].notna()])
        .mark_rule(color="red", strokeDash=[10, 10], size=2)
        .encode(x="mean(eco_fr):Q")
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
            y=alt.Y("sentiment_mean:Q", title="Mean Sentiment"),
            tooltip=["trend_rank", "sentiment_mean"],
            color=alt.condition(
                alt.datum.sentiment_mean >= 0,
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


# this is actually another bar chart for now
def draw_eco_corr(df):
    plot_corr = (
        alt.Chart(df)
        .mark_bar(size=20, opacity=0.8)
        .encode(
            x=alt.X("trend_rank:Q", title="Search Trend Rank"),
            y=alt.Y("eco_fr:Q", title="Mean Carbon Cost"),
            tooltip=["trend_rank", "eco_fr"],
            color=alt.condition(
                alt.datum.eco_fr > df["eco_fr"].mean(),
                alt.value("#0ec956"),  # The positive color
                alt.value("#ff1717"),  # The negative color
            ),
        )
    ).properties(
        title=alt.TitleParams(
            ["* Dashed red line indicates the distribution mean"],
            baseline="bottom",
            orient="bottom",
            anchor="end",
            fontWeight="normal",
            fontSize=11,
        )
    )
    rule_corr = (
        alt.Chart(pd.DataFrame({"y": [df["eco_fr"].mean()]}))
        .mark_rule(strokeDash=[10, 10], size=1.5, color="red")
        .encode(y="y")
    )
    st.altair_chart(plot_corr + rule_corr, use_container_width=True)


def print_headlines(df):
    for index, row in df.iterrows():
        with st.container():
            # st.write("Sentiment: ", row["sentiment"])
            # st.write("Host Country: `", row["country_name"], "`")
            st.markdown(
                "> "
                + "<a href='"
                + row["url"]
                + "' target='_blank'>"
                + row["title"]
                + "</a>",
                unsafe_allow_html=True,
            )
            # st.markdown("---")
    st.markdown("&nbsp;")


#############
## CONTENT ##
#############

with st.expander("🎈 Why Sonder?"):
    st.info(
        """
    *son$\cdot$der (n.)*

    the realization that each random passerby is living a life as vivid and complex as your own
    """
    )
    st.markdown(
        """
    Internet search shows you what you consume. Sonder shows you what you miss out on. We assess the opportunity cost of internet search.

    Our access to knowledge is biased by ~~public~~ private algorithms, trained on ~~diverse~~ mainstream data, intended to maximize ~~representation~~ consumption. This robs us of the choice to understand those who think and learn differently. Sonder is an attempt to make our lack of choice explicit. To at least be mindful of our filter bubbles, if not break them.

    We are working along two dimensions (view 👈 sidebar):

    + ⚖️ *Balance*: Tackle bias as you search the web. Balance relevance with diversity.
    + 📣 *Trends*: Highlight fairness in web, news, wiki, and social media trends.

    &nbsp;
    """
    )

st.markdown("## 🗞️ News Trends")
st.write("Explore fairness trends for news across the globe.")
st.markdown("&nbsp;")
navigate_web = st.radio("Explore", ["Sentiment", "Carbon Cost"], 0)
st.markdown("---")
st.markdown("&nbsp;")

# read data
df = pd.read_csv(Path("today/news_trends.csv"))
df.rename(columns={"country": "cctld"}, inplace=True)
df = pd.merge(
    df,
    pd.read_csv(Path("cctld/capitals.csv")),
    on="cctld",
    how="left",
)
df.rename(columns={"country_cctld": "country"}, inplace=True)

# excluding rows with just 1 headline for a country
df = df.groupby("country").filter(lambda x: len(x) > 1)

df["sentiment"] = pd.to_numeric(df["sentiment"], errors="coerce")
df["is_green"] = pd.to_numeric(df["is_green"], errors="coerce")

# st.write(df)
country_list = sorted(list(set(df["country"].tolist())))
country_list.insert(0, "")


df["date"] = pd.to_datetime(df["date"])
st.write("_Update: " + df["date"].iloc[0].strftime("%B %d, %Y") + "_")
st.write(
    "_Today's Sample: "
    + f"{len(df.index):,}"
    + " trending news results across "
    + str(len(country_list) - 1)
    + " countries._"
)

col1, col2 = st.columns([1, 1])

if navigate_web == "Sentiment":

    with col1:
        st.write("## Global Trends Today")
        st.write("&nbsp;")
        st.write("#### Sentiment ranking")
        st.write("\n\n")

        # country rank plot
        df_country = pd.DataFrame(
            df.groupby(["country"])[["sentiment"]].mean(),  # mean or median?
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

            st.write("#### " + str(country) + ": News Headlines")
            st.markdown("---")
            print_headlines(df[df["country"] == country])
