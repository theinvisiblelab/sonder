## PARAMETERS ##
import requests
import numpy as np
import pandas as pd
import io
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
    res_dict = {str(i + 1): float(lst[i]) for i in range(len(lst))}
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
            x=alt.X("is_green", title="Carbon Cost"),
            y=alt.Y("country", title="Country", sort="-x"),
            tooltip=["is_green"],
            color=alt.condition(
                alt.datum.is_green > df_summary["is_green"].mean(),
                alt.value("#0ec956"),  # The positive color
                alt.value("#ff1717"),  # The negative color
            ),
        )
    ).properties(
        title=alt.TitleParams(
            ["* Dashed red line indicates the cross-country mean"],
            baseline="bottom",
            orient="bottom",
            anchor="start",
            fontWeight="normal",
            fontSize=11,
        )
    )

    rule = (
        alt.Chart(df_summary[df_summary["is_green"].notna()])
        .mark_rule(color="red", strokeDash=[10, 10], size=2)
        .encode(x="mean(is_green):Q")
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
        alt.Chart(df_temp[df_temp["is_green"].notna()])
        .transform_density(
            "is_green",
            as_=["is_green", "density"],
        )
        .mark_area(opacity=0.75)
        .encode(
            x="is_green:Q",
            y="density:Q",
            tooltip=["is_green"],
        )
        .encode(
            x=alt.X("is_green:Q", title="Carbon Cost"),
            y=alt.Y("density:Q", title=""),
        )
        .properties(
            title=alt.TitleParams(
                ["* Dashed red line indicates the distribution mean"],
                baseline="bottom",
                orient="bottom",
                anchor="start",
                fontWeight="normal",
                fontSize=11,
            )
        )
    )
    web_dist_sent2 = (
        alt.Chart(df_temp[df_temp["is_green"].notna()])
        .mark_rule(color="red", strokeDash=[10, 10], size=2)
        .encode(x="mean(is_green):Q")
    )

    st.altair_chart(web_dist_sent1 + web_dist_sent2, use_container_width=True)
    st.markdown("\n")


# this is actually another bar chart for now
def draw_corr(df):
    plot_corr = (
        alt.Chart(df)
        # .mark_point(size=20, opacity=0.8)
        .mark_circle(size=150, opacity=0.8).encode(
            x=alt.X("rank_group:Q", title="Search Rank"),
            y=alt.Y("sentiment:Q", title="Mean Sentiment"),
            tooltip=["rank_group", "sentiment"],
            color=alt.condition(
                alt.datum.sentiment >= 0,
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
        .mark_circle(size=150, opacity=0.8)
        .encode(
            x=alt.X("rank_group:Q", title="Search Rank"),
            y=alt.Y("is_green:Q", title="Mean Carbon Cost"),
            tooltip=["rank_group", "is_green"],
            color=alt.condition(
                alt.datum.is_green > df["is_green"].mean(),
                alt.value("#0ec956"),  # The positive color
                alt.value("#ff1717"),  # The negative color
            ),
        )
    ).properties(
        title=alt.TitleParams(
            ["* Dashed red line indicates the distribution mean"],
            baseline="bottom",
            orient="bottom",
            anchor="start",
            fontWeight="normal",
            fontSize=11,
        )
    )
    rule_corr = (
        alt.Chart(pd.DataFrame({"y": [df["is_green"].mean()]}))
        .mark_rule(strokeDash=[10, 10], size=1.5, color="red")
        .encode(y="y")
    )
    st.altair_chart(plot_corr + rule_corr, use_container_width=True)


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

st.markdown("## 🕸️ Web Trends")
st.write("Explore fairness trends for internet search across the globe.")
st.markdown("&nbsp;")
navigate_web = st.radio("Explore", ["Sentiment", "Carbon Cost"], 0)
st.markdown("---")
st.markdown("&nbsp;")

# read data
df = pd.read_parquet(Path("today/trends.parquet"))
df = df.loc[df["type"] == "organic"]
# df = df.loc[df['type'] == "news_search"]

country_list_raw = sorted(list(set(df["country"].tolist())))

country_list = [i.replace("_", " ").title() for i in country_list_raw]
country_list.insert(0, "")

df["date"] = pd.to_datetime(df["date"])
st.write("_Update: " + df["date"].iloc[0].strftime("%B %d, %Y") + "_")
# st.write("_Update: September 20, 2021_")
st.write(
    "_Today's Sample: "
    + f"{len(df.index):,}"
    + " web search results for top trends across 48 countries._"
)

col1, col2 = st.columns([1, 1])


if navigate_web == "Sentiment":

    with col1:
        st.write("## Global Trends Today")
        st.write("&nbsp;")
        st.write("#### Sentiment ranking")
        st.write("\n\n")

        # country rank plot
        df_country = df.groupby(["country"])["sentiment"].mean().reset_index()
        df_country["country"] = df_country.apply(
            lambda row: row["country"].replace("_", " ").title(), axis=1
        )
        draw_bar(df_country)

        # sentiment distribution
        # st.write("#### Global: Sentiment distribution today*")
        # st.write("\n\n")
        # draw_dist(df[["sentiment"]])

        # correlation with search rank
        st.write("#### Global: Sentiment variation with Search Rank")
        st.write("\n\n")
        draw_corr(df.groupby(["rank_group"])["sentiment"].mean().reset_index())

    with col2:
        st.write("## Regional Trends Today")
        st.write("&nbsp;")
        country = st.selectbox("Choose a country", country_list)
        if country != "":
            st.write("&nbsp;")

            country_lower = country.lower().replace(" ", "_")
            st.write(
                "#### "
                + str(country)
                + ": Search queries today ("
                + str(len(df[df["country"] == country_lower].index))
                + " results)"
            )
            st.image(
                Image.open(Path("wordclouds/" + str(country_lower) + ".png")),
                use_column_width="auto",
            )

            # st.write("#### " + str(country) + ": Sentiment distribution today")
            # st.write("\n\n")
            # draw_dist(df[df["country"] == country_lower][["sentiment"]])

            st.write("#### " + str(country) + ": Sentiment variation with Search Rank")
            st.write("\n\n")
            draw_corr(
                df[df["country"] == country_lower]
                .groupby(["rank_group"])["sentiment"]
                .mean()
                .reset_index()
            )

###################
### CARBON COST ###
###################

if navigate_web == "Carbon Cost":
    # df["trend_rank"] = 21 - np.power((df["weight"]), 1 / 3)
    # df["is_green"] = df.apply(lambda row: list(map(int, row["is_green"])), axis=1)
    # df["eco_fr"] = df.apply(lambda row: mean(row["is_green"]), axis=1)
    # eco_fr_mean = df["is_green"].mean()

    with col1:
        st.write("## Global Trends Today")
        st.write("&nbsp;")
        st.write("#### Carbon Cost ranking")
        st.write("\n\n")

        # country rank plot
        df_country = df.groupby(["country"])["is_green"].mean().reset_index()
        df_country["country"] = df_country.apply(
            lambda row: row["country"].replace("_", " ").title(), axis=1
        )
        draw_eco_bar(df_country)

        # sentiment distribution
        st.write("#### Global: Carbon Cost distribution today*")
        st.write("\n\n")
        # aggregating to query level
        draw_eco_dist(df.groupby(["query"])["is_green"].mean().reset_index())

        st.write("#### Global: Carbon Cost variation with Search Rank")
        st.write("\n\n")
        draw_eco_corr(df.groupby(["rank_group"])["is_green"].mean().reset_index())

    with col2:
        st.write("## Regional Trends Today")
        # draw_dist(sentiment_flatlist(df))
        st.write("&nbsp;")
        country = st.selectbox("Choose a country", country_list)
        if country != "":
            st.write("&nbsp;")

            country_lower = country.lower().replace(" ", "_")
            st.write(
                "#### "
                + str(country)
                + ": Search queries today ("
                + str(len(df[df["country"] == country_lower].index))
                + " results)"
            )
            st.image(
                Image.open(Path("wordclouds/" + str(country_lower) + ".png")),
                use_column_width="auto",
            )

            st.write("#### " + str(country) + ": Carbon Cost distribution today")
            st.write("\n\n")
            draw_eco_dist(
                df[df["country"] == country_lower]
                .groupby(["query"])["is_green"]
                .mean()
                .reset_index()
            )

            st.write("#### " + str(country) + ": Carbon Cost variation with Trend Rank")
            st.write("\n\n")
            draw_eco_corr(
                df[df["country"] == country_lower]
                .groupby(["rank_group"])["is_green"]
                .mean()
                .reset_index()
            )
