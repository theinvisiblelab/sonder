## PARAMETERS ##
from glob import escape
from altair.vegalite.v4.schema.channels import Tooltip
import socket
import numpy as np
import pandas as pd
from statistics import mean, median, NormalDist
from nltk import tokenize
from dotenv import load_dotenv
from client import RestClient
import os

import rpy2.robjects as ro
from rpy2.robjects.packages import importr

overlapping = importr("overlapping")

from textblob import TextBlob
import altair as alt

from transformers import pipeline

@st.cache(allow_output_mutation=True, show_spinner=False)
def load_searx_data(query):
    post_data = dict()
    post_data[len(post_data)] = dict(
        language_code="en", location_code=2840, keyword=query
    )
    response = client.post("/v3/serp/google/organic/live/regular", post_data)
    df = pd.DataFrame(response["tasks"][0]["result"][0]["items"])
    df.rename(columns={"content": "description"}, inplace=True)
    df.dropna(subset=["title", "description"], inplace=True)
    return df


def subjectivity_calc(text):
    try:
        return TextBlob(text).sentiment.subjectivity
    except:
        return None


def sentiment_calc(text):
    try:
        if subjectivity_calc(text) == 0:
            return 0
        else:
            result = classifier(text)[0]
            if result["label"] == "POSITIVE":
                return round(result["score"], 4)
            elif result["label"] == "NEGATIVE":
                return -result["score"]
            else:
                return 0
    except:
        return None


@st.cache(allow_output_mutation=True, show_spinner=False)
def sentiment_all(text):
    try:
        sent_list = []
        for sent in tokenize.sent_tokenize(text):
            sent_list.append(sentiment_calc(sent))
        return mean(sent_list)
    except:
        return None


# Calculate distribution overlap
def overlap_calc(df, n_top=10):
    if n_top <= 1:
        return 0
    else:
        df = df[df["sentiment"].notna()]
        v1 = ro.vectors.FloatVector(df["sentiment"])
        v2 = ro.vectors.FloatVector(df.head(n_top)["sentiment"])
        ovl = overlapping.overlap([v1, v2])
        return np.array(ovl.rx("OV"))[0][0]
    # return 1-ks_2samp(df["sentiment"], df.head(n_top)["sentiment"])[0]


# Remove domain prefix
def remove_prefix(text, prefix="www."):
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


## CONTENT ##

# st.markdown(Path("markdown/bias.md").read_text(), unsafe_allow_html=True)
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

    + ⚖️ *Balance*: Assess invisible knowledge as you search the web. Balance relevance with diversity.
    + 📣 *Trends*: Highlight fairness in web, news, wiki, and social media trends.

    &nbsp;
    """
    )


st.markdown("&nbsp;")

st.write("Evaluate invisible information as you search the web in 3 steps:")


col_a, col_b = st.columns([1, 1.618])

col_a.write("&nbsp;")
col_a.write("1. Pick search query")
col_a.write("&nbsp;")
col_a.write("2. Pick a dimension")
col_a.write("&nbsp;")
col_a.write("3. Pick number of results you see")

query = col_b.text_input("").lower().strip()
df_size = 100

if query != "":
    with st.spinner("Assessing visibility for your knowledge search..."):
        load_dotenv()
        client = RestClient(os.environ.get("D4S_LOGIN"), os.environ.get("D4S_PWD"))
        # demo
        if query in ["climate change"]:
            df = pd.read_csv(Path("demo/" + query + ".csv"))
        # default
        else:
            df = load_searx_data(query)
            df["search_rank"] = df.reset_index().index + 1
        df_size = len(df.index)


dimension = col_b.selectbox('', ('Sentiment', 'Readability'))
n_results = col_b.slider('', 0, df_size, 0)

st.markdown("&nbsp;")

if query != "":

    col2, col1 = st.columns(2)

    with col1:
        st.markdown("### Search results")
        st.markdown("---")
        for index, row in df.iterrows():
            with st.container():
                # st.write("Sentiment: ", row["sentiment"])
                # st.write("Host Country: `", row["country_name"], "`")
                if row["description"] == row["description"]:
                    st.markdown(
                        "> "
                        + row["url"]
                        + "<br/><br/><i>"
                        + row["title"]
                        + ".</i> "
                        + row["description"],
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        "> " + row["url"] + "<br/><br/>" + row["title"],
                        unsafe_allow_html=True,
                    )
                st.markdown("---")

    col2.markdown("### " + dimension + " visibility")
    col2.markdown("---")

    expander1 = col2.expander("🗣️ Sentiment")

    with expander1:
        with st.spinner("Assessing sentiment in your search results..."):
            # sentiment analyzer loading
            if "sentiment" not in df.columns:
                classifier = pipeline("sentiment-analysis")
                df["sentiment"] = df.apply(
                    lambda row: sentiment_all(
                        str(row["title"]) + ". " + str(row["description"])
                    ),
                    axis=1,
                )
                df.to_csv(Path("demo/" + query + ".csv"), encoding="utf-8", index=False)

            sentiment_mean = round(df["sentiment"].mean(), 4)
            sentiment_median = round(df["sentiment"].median(), 4)
            sentiment_min = df["sentiment"].min()
            sentiment_max = df["sentiment"].max()

            n_top = 10  # number of top results

            # st.error("Invisibility: __" + str(sentiment_bias) + "%__")
            # st.write("\n")
            df["search_rank"] = df["search_rank"] / df_size
            st.write(
                "Here's how sentiment varies with rank for your search results. You miss out on the gray region."
            )

            # DEMO
            if query in ["climate change"]:
                n_top_demo = st.slider("Results viewed", 0, df_size, (0, 0))

            plot_corr = (
                alt.Chart(df[df["sentiment"].notna()])
                .mark_circle(size=150, opacity=0.8)
                .encode(
                    x=alt.X(
                        "search_rank:Q",
                        title="Search results viewed",
                        axis=alt.Axis(format="%"),
                    ),
                    y=alt.Y("sentiment:Q", title="Sentiment"),
                    tooltip=["title"],
                    color=alt.condition(
                        alt.datum.sentiment >= 0,
                        alt.value("#0ec956"),  # The positive color
                        alt.value("#ff1717"),  # The negative color
                    ),
                )
            )
            rule_corr = (
                alt.Chart(pd.DataFrame({"y": [0]}))
                .mark_rule(strokeDash=[10 / df_size, 10 / df_size], size=1.5)
                .encode(y="y")
            )

            # DEMO
            if query in ["climate change"]:

                cutoff = pd.DataFrame(
                    {
                        "start": [n_top_demo[1] / df_size, n_top_demo[1] / df_size],
                        "stop": [1, 1],
                    }
                )
                areas = (
                    alt.Chart(cutoff.reset_index())
                    .mark_rect(opacity=0.30)
                    .encode(x="start", x2="stop")
                )

                cutoff0 = pd.DataFrame(
                    {
                        "start": [0, 0],
                        "stop": [n_top_demo[0] / df_size, n_top_demo[0] / df_size],
                    }
                )
                areas0 = (
                    alt.Chart(cutoff0.reset_index())
                    .mark_rect(opacity=0.30)
                    .encode(x="start", x2="stop")
                )

                st.altair_chart(
                    rule_corr + plot_corr + areas + areas0, use_container_width=True
                )

                df_inv = pd.DataFrame(
                    [
                        (i, overlap_calc(df, i))
                        for i in range(n_top_demo[0], n_top_demo[1] + 1)
                    ],
                    columns=["rank", "visibility"],
                )
                df_inv["rank"] = df_inv["rank"] / df_size

                vis_present = round(df_inv["visibility"].iloc[-1] * 100, 2)
                if n_top_demo[1] == df_size:
                    effic_present = round(df_inv["visibility"].mean() * 100, 2)
                else:
                    effic_present = "--"

                plot_vis_continuous = (
                    alt.Chart(df_inv)
                    .mark_area(color="#ffd875", line=True, opacity=0.75)
                    .encode(
                        x=alt.X(
                            "rank:Q",
                            title="Search results viewed",
                            axis=alt.Axis(format="%"),
                            scale=alt.Scale(domain=(0, 1)),
                        ),
                        y=alt.Y(
                            "visibility:Q",
                            title="Visibility",
                            axis=alt.Axis(format="%"),
                            scale=alt.Scale(domain=(0, 1)),
                        ),
                        tooltip=["visibility"],
                    )
                )
                st.altair_chart(plot_vis_continuous, use_container_width=True)

                st.metric(label="Visibility", value=str(vis_present) + "%")
                st.metric(label="Efficiency", value=str(effic_present) + "%")

            # default path
            else:
                cutoff = pd.DataFrame(
                    {"start": [10 / df_size, 10 / df_size], "stop": [1, 1]}
                )
                areas = (
                    alt.Chart(cutoff.reset_index())
                    .mark_rect(opacity=0.30)
                    .encode(x="start", x2="stop")
                )

                st.altair_chart(rule_corr + plot_corr + areas, use_container_width=True)

                df_inv = pd.DataFrame(
                    [(i, overlap_calc(df, i)) for i in range(1, df_size + 1)],
                    columns=["rank", "visibility"],
                )
                df_inv["rank"] = df_inv["rank"] / df_size
                st.write("\n")
                st.write(
                    "Here's how visibility (in sentiment) varies with rank for your search results. Your visibility reaches "
                    + str(round(df_inv["visibility"].iloc[9] * 100))
                    + "% by staying on the first page."
                )

                plot_vis_continuous = (
                    alt.Chart(df_inv)
                    .mark_area(color="#ffd875", line=True, opacity=0.75)
                    .encode(
                        x=alt.X(
                            "rank:Q",
                            title="Search results viewed",
                            axis=alt.Axis(format="%"),
                        ),
                        y=alt.Y(
                            "visibility:Q",
                            title="Visibility",
                            axis=alt.Axis(format="%"),
                        ),
                        tooltip=["visibility"],
                    )
                )
                st.altair_chart(plot_vis_continuous, use_container_width=True)

            st.markdown("&nbsp;")

