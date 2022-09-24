## PARAMETERS ##
# from glob import escape
# from altair.vegalite.v4.schema.channels import Tooltip
# import socket
from flask import copy_current_request_context
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from client import RestClient
import os
import altair as alt
from sentence_transformers import SentenceTransformer, util
from plotnine import *


@st.cache(show_spinner=False, suppress_st_warning=True)
def fetch_data(query, model):
    # st.info("fetch_data running...")
    post_data = dict()
    post_data[len(post_data)] = dict(
        language_code="en", location_code=2840, keyword=query
    )
    response = client.post("/v3/serp/google/organic/live/regular", post_data)
    df = pd.DataFrame(response["tasks"][0]["result"][0]["items"])
    df.rename(columns={"content": "description"}, inplace=True)
    df.dropna(subset=["title", "description"], inplace=True)
    df.drop_duplicates(inplace=True)

    # clean domain
    df["domain"] = df.apply(lambda row: remove_prefix(str(row["domain"])), axis=1)
    # merge in pageranks
    df = df.merge(
        pd.read_csv(Path("data/opr_top10milliondomains.csv"))[
            ["domain", "open_page_rank"]
        ],
        on=["domain"],
        how="left",
    )
    df["open_page_rank"] = df["open_page_rank"].fillna(0)

    # all text for embeddings
    df["all_text"] = df["title"] + ". " + df["description"]

    query_embedding = model.encode(query)
    df["result_embedding"] = df.apply(lambda row: model.encode(row["all_text"]), axis=1)
    corpus_embedding = np.average(df["result_embedding"], weights=df["open_page_rank"])

    df["relevance"] = df.apply(
        lambda row: util.cos_sim(row["result_embedding"], query_embedding).item(),
        axis=1,
    )
    df["representation"] = df.apply(
        lambda row: util.cos_sim(row["result_embedding"], corpus_embedding).item(),
        axis=1,
    )
    metric = round(util.cos_sim(corpus_embedding, query_embedding).item(), 2)

    df = df[["url", "title", "description", "relevance", "representation"]]

    return (df, metric)


# Remove domain prefix
def remove_prefix(text, prefix="www."):
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


@st.cache(allow_output_mutation=True, show_spinner=False, suppress_st_warning=True)
def load_model():
    # st.info("load_model running...")
    return SentenceTransformer("all-MiniLM-L6-v2")


#############
## CONTENT ##
#############

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
    Internet search shows you what you consume. Sonder shows you what you miss out on by balancing relevance and visibility.

    Our access to knowledge is biased by ~~public~~ private algorithms, trained on ~~diverse~~ mainstream data, intended to maximize ~~visibility~~ consumption. This robs us of the choice to understand those who think and learn differently. Sonder is an attempt to make our lack of choice explicit. To at least be mindful of our filter bubbles, if not break them.

    &nbsp;
    """
    )


st.markdown("&nbsp;")

# col_a, col_b = st.columns([1, 1.618])

# st.write("&nbsp;")
# st.write("1. Pick search query")
# st.write("&nbsp;")
# st.write("2. Balance relevance and visibility")

query = st.text_input("Pick search query").lower().strip()

choice = st.radio(
    "",
    [
        "🔦 Default result order",
        "⚖️ Balance relevance and visibility",
    ],
    0,
)

if query != "" and choice == "🔦 Default result order":

    st.markdown("&nbsp;")

    with st.spinner("Fetching your search results..."):

        model = load_model()

        load_dotenv()
        client = RestClient(os.environ.get("D4S_LOGIN"), os.environ.get("D4S_PWD"))

        # demo
        if query in ["climate changez"]:
            df = pd.read_csv(Path("demo/" + query + ".csv"))
            metric = 0.5
        # default
        else:
            response = fetch_data(query, model)
            df = response[0]
            metric = response[1]

    col2, col1 = st.columns([1, 1])
    df_print = df.copy()

    # df_print["final_score"] = (1 - lamda) * df_print["relevance"] + lamda * df_print["representation"]
    # df_print = df_print.sort_values("final_score", ascending=False)
    df_print["final_rank"] = df_print.reset_index().index + 1
    metric_corr_relevance = round(df_print["final_rank"].corr(df_print["relevance"]), 2)
    metric_corr_rep = round(df_print["final_rank"].corr(df_print["representation"]), 2)

    with col1:
        st.markdown("### Search results")
        st.markdown("---")
        for index, row in df_print.iterrows():
            with st.container():
                if row["description"] == row["description"]:
                    st.markdown(
                        "> "
                        + row["url"]
                        + "<br/><br/><i>"
                        + row["title"]
                        + ".</i> "
                        + row["description"]
                        + "<br/><br/>"
                        + "Visibility: `"
                        + str(round(row["representation"], 2))
                        + "`",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        "> " + row["url"] + "<br/><br/>" + row["title"],
                        unsafe_allow_html=True,
                    )
                st.markdown("---")

    col2.markdown("### Metrics")
    col2.markdown("---")

    with col2:
        # st.metric("Relevance Correlation", metric_corr_relevance)

        p1 = (
            ggplot(df_print, aes("final_rank", "relevance"))
            + geom_point()
            + geom_smooth()
            + theme_xkcd()
            + labs(x="Search Result Rank", y="Relevance")
        )
        st.pyplot(ggplot.draw(p1))

        # st.metric("Visibility Correlation", metric_corr_rep)

        p2 = (
            ggplot(df_print, aes("final_rank", "representation"))
            + geom_point()
            + geom_smooth()
            + theme_xkcd()
            + labs(x="Search Result Rank", y="Visibility")
        )
        st.pyplot(ggplot.draw(p2))

if query != "" and choice == "⚖️ Balance relevance and visibility":

    lamda = st.slider(
        "2. Balance relevance and visibility", min_value=0.0, max_value=1.0, value=0.5
    )

    with st.spinner("Fetching your search results..."):

        model = load_model()

        load_dotenv()
        client = RestClient(os.environ.get("D4S_LOGIN"), os.environ.get("D4S_PWD"))

        # demo
        if query in ["climate changez"]:
            df = pd.read_csv(Path("demo/" + query + ".csv"))
            metric = 0.5
        # default
        else:
            response = fetch_data(query, model)
            df = response[0]
            metric = response[1]

    col2, col1 = st.columns([1, 1])
    df_print = df.copy()

    df_print["final_score"] = (1 - lamda) * df_print["relevance"] + lamda * df_print[
        "representation"
    ]
    df_print = df_print.sort_values("final_score", ascending=False)
    df_print["final_rank"] = df_print.reset_index().index + 1
    metric_corr_relevance = round(df_print["final_rank"].corr(df_print["relevance"]), 2)
    metric_corr_rep = round(df_print["final_rank"].corr(df_print["representation"]), 2)

    with col1:
        st.markdown("### Search results")
        st.markdown("---")
        for index, row in df_print.iterrows():
            with st.container():
                if row["description"] == row["description"]:
                    st.markdown(
                        "> "
                        + row["url"]
                        + "<br/><br/><i>"
                        + row["title"]
                        + ".</i> "
                        + row["description"]
                        + "<br/><br/>"
                        + "Visibility: `"
                        + str(round(row["representation"], 2))
                        + "`",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        "> " + row["url"] + "<br/><br/>" + row["title"],
                        unsafe_allow_html=True,
                    )
                st.markdown("---")

    col2.markdown("### Metrics")
    col2.markdown("---")

    with col2:
        # st.metric("Distance", metric)
        # st.metric("Relevance Correlation", metric_corr_relevance)

        p1 = (
            ggplot(df_print, aes("final_rank", "relevance"))
            + geom_point()
            + geom_smooth()
            + theme_xkcd()
            + labs(x="Search Result Rank", y="Relevance")
        )
        st.pyplot(ggplot.draw(p1))

        # st.metric("Visibility Correlation", metric_corr_rep)

        p2 = (
            ggplot(df_print, aes("final_rank", "representation"))
            + geom_point()
            + geom_smooth()
            + theme_xkcd()
            + labs(x="Search Result Rank", y="Visibility")
        )
        st.pyplot(ggplot.draw(p2))
