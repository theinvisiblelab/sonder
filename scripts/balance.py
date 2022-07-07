## PARAMETERS ##
# from glob import escape
# from altair.vegalite.v4.schema.channels import Tooltip
# import socket
import numpy as np
import pandas as pd
from statistics import mean
from dotenv import load_dotenv
from client import RestClient
import os

import altair as alt


@st.cache(allow_output_mutation=True, show_spinner=False)
def fetch_data(query):
    post_data = dict()
    post_data[len(post_data)] = dict(
        language_code="en", location_code=2840, keyword=query
    )
    response = client.post("/v3/serp/google/organic/live/regular", post_data)
    df = pd.DataFrame(response["tasks"][0]["result"][0]["items"])
    df.rename(columns={"content": "description"}, inplace=True)
    df.dropna(subset=["title", "description"], inplace=True)
    return df


# Remove domain prefix
def remove_prefix(text, prefix="www."):
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


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
    Internet search shows you what you consume. Sonder shows you what you miss out on. We assess the opportunity cost of internet search.

    Our access to knowledge is biased by ~~public~~ private algorithms, trained on ~~diverse~~ mainstream data, intended to maximize ~~representation~~ consumption. This robs us of the choice to understand those who think and learn differently. Sonder is an attempt to make our lack of choice explicit. To at least be mindful of our filter bubbles, if not break them.

    We are working along two dimensions (view 👈 sidebar):

    + ⚖️ *Balance*: Assess invisible knowledge as you search the web. Balance relevance with diversity.
    + 📣 *Trends*: Highlight fairness in web, news, wiki, and social media trends.

    &nbsp;
    """
    )


st.markdown("&nbsp;")

col_a, col_b = st.columns([1, 1.618])

col_a.write("&nbsp;")
col_a.write("1. Pick search query")
col_a.write("&nbsp;")
col_a.write("2. Balance relevance and representation")

query = col_b.text_input("").lower().strip()

if query != "":
    with st.spinner("Assessing visibility for your knowledge search..."):
        load_dotenv()
        client = RestClient(os.environ.get("D4S_LOGIN"), os.environ.get("D4S_PWD"))
        # demo
        if query in ["climate change"]:
            df = pd.read_csv(Path("demo/" + query + ".csv"))
        # default
        else:
            df = fetch_data(query)
            df["search_rank"] = df.reset_index().index + 1
        df_size = len(df.index)


lamda = col_b.slider("", min_value = 0.0, max_value = 1.0, value = 0.5)

st.markdown("&nbsp;")

if query != "":

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Search results")
        st.markdown("---")
        for index, row in df.iterrows():
            with st.container():
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

    col2.markdown("### Visibility")
    col2.markdown("---")

    