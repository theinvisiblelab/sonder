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
from statistics import median
from statistics import mean
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
            x=alt.X("sentiment_median", title="Sentiment"),
            y=alt.Y("country", title="Country", sort="-x"),
            tooltip=["sentiment_median"],
            color=alt.condition(
                alt.datum.sentiment_median > 0,
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
            x=alt.X("eco_fr", title="Eco-friendliness"),
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
            x=alt.X("eco_fr:Q", title="Eco-friendliness"),
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


# this is actually another bar chart for now
def draw_eco_corr(df):
    plot_corr = (
        alt.Chart(df)
        .mark_bar(size=20, opacity=0.8)
        .encode(
            x=alt.X("trend_rank:Q", title="Search Trend Rank"),
            y=alt.Y("eco_fr:Q", title="Mean Eco-friendliness"),
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


#############
## CONTENT ##
#############

st.markdown("## 🕸️ Web Trends")
st.write("Explore fairness trends for internet search across the globe.")
st.markdown("&nbsp;")
navigate_web = st.radio("Explore", ["Sentiment", "Eco-friendliness"], 0)
st.markdown("---")
st.markdown("&nbsp;")

# read data
df = pd.read_csv(
    Path("today/web_trends.csv"),
    converters={
    "sentiment_dist": lambda x: x.strip("[]").replace("'", "").split(", "),
    "is_green": lambda x: x.strip("[]").replace("'", "").split(", ")
    },
)

country_list_raw = sorted(list(set(df["country"].tolist())))

country_list = [i.replace("_", " ").title() for i in country_list_raw]
country_list.insert(0, "")

df["date"] = pd.to_datetime(df["date"])
st.write("_Updated: " + df["date"].iloc[0].strftime("%B %d, %Y") + "_")

col1, col2 = st.beta_columns([1, 1])


if navigate_web == "Sentiment":

    df["trend_rank"] = 21 - np.power((df["weight"]), 1 / 3)
    df["sentiment_dictionary"] = df.apply(
        lambda row: list_to_dict(row["sentiment_dist"]), axis=1
    )
    df["sentiment_median"] = df.apply(
        lambda row: median(row["sentiment_dictionary"].values()), axis=1
    )

    with col1:
        st.write("## Global Trends Today")
        st.write("&nbsp;")
        st.write("#### Sentiment ranking")
        st.write("\n\n")

        # country rank plot
        df_country = pd.DataFrame(
            df.groupby(["country"])[["sentiment_median"]].median(),
            columns=["sentiment_median"],
        )
        df_country = df_country.reset_index()
        df_country["country"] = df_country.apply(
            lambda row: row["country"].replace("_", " ").title(), axis=1
        )
        draw_bar(df_country)

        # sentiment distribution
        st.write("#### Global: Sentiment distribution today*")
        st.write("\n\n")
        df_dist = pd.DataFrame(sentiment_flatlist(df), columns=["sentiment"])
        draw_dist(df_dist)

        #
        st.write("#### Global: Sentiment variation with Trend Rank")
        st.write("\n\n")
        df_median = pd.DataFrame(
            df.groupby(["trend_rank"])[["sentiment_median"]].median(),
            columns=["sentiment_median"],
        )
        df_median = df_median.reset_index()
        draw_corr(df_median)

    with col2:
        st.write("## Regional Trends Today")
        # draw_dist(sentiment_flatlist(df))
        st.write("&nbsp;")
        country = st.selectbox("Choose a country", country_list)
        if country != "":
            st.write("&nbsp;")

            st.write("#### " + str(country) + ": Search queries today")
            country_lower = country.lower().replace(" ", "_")
            st.image(
                Image.open(Path("wordclouds/" + str(country_lower) + ".png")),
                use_column_width="auto",
            )

            st.write("#### " + str(country) + ": Sentiment distribution today")
            st.write("\n\n")
            draw_dist(
                pd.DataFrame(
                    sentiment_flatlist(df[df["country"] == country_lower]),
                    columns=["sentiment"],
                )
            )
            st.write("#### " + str(country) + ": Sentiment variation with Trend Rank")
            st.write("\n\n")
            draw_corr(df[df["country"] == country_lower])


if navigate_web == "Eco-friendliness":
    df["trend_rank"] = 21 - np.power((df["weight"]), 1 / 3)
    df["is_green"] = df.apply(
        lambda row: list(map(int, row["is_green"])), axis=1
    )
    df["eco_fr"] = df.apply(
        lambda row: mean(row["is_green"]), axis=1
    )
    eco_fr_mean = df["eco_fr"].mean()

    with col1:
        st.write("## Global Trends Today")
        st.write("&nbsp;")
        st.write("#### Eco-friendliness ranking")
        st.write("\n\n")

        # country rank plot
        df_country = pd.DataFrame(
            df.groupby(["country"])[["eco_fr"]].mean(),
            columns=["eco_fr"],
        )
        df_country = df_country.reset_index()
        df_country["country"] = df_country.apply(
            lambda row: row["country"].replace("_", " ").title(), axis=1
        )
        draw_eco_bar(df_country)

        # sentiment distribution
        st.write("#### Global: Eco-friendliness distribution today*")
        st.write("\n\n")
        draw_eco_dist(df[["eco_fr"]])

        st.write("#### Global: Eco-friendliness variation with Trend Rank")
        st.write("\n\n")
        df_mean = pd.DataFrame(
            df.groupby(["trend_rank"])[["eco_fr"]].mean(),
            columns=["eco_fr"],
        )
        df_mean = df_mean.reset_index()
        draw_eco_corr(df_mean)

    with col2:
        st.write("## Regional Trends Today")
        # draw_dist(sentiment_flatlist(df))
        st.write("&nbsp;")
        country = st.selectbox("Choose a country", country_list)
        if country != "":
            st.write("&nbsp;")

            st.write("#### " + str(country) + ": Search queries today")
            country_lower = country.lower().replace(" ", "_")
            st.image(
                Image.open(Path("wordclouds/" + str(country_lower) + ".png")),
                use_column_width="auto",
            )

            st.write("#### " + str(country) + ": Eco-friendliness distribution today")
            st.write("\n\n")
            draw_eco_dist(df[df["country"] == country_lower][["eco_fr"]])

            st.write(
                "#### " + str(country) + ": Eco-friendliness variation with Trend Rank"
            )
            st.write("\n\n")
            draw_eco_corr(df[df["country"] == country_lower])
