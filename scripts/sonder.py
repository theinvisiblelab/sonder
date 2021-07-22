#!/usr/bin/python
# -*- coding: utf-8 -*-
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Sonder", page_icon=":balloon:", layout="wide")

# hiding the hamburger menu and footer
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>

"""

# Main page

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("S🎈nder")
st.write("_The Opportunity Cost of Internet Search_")
st.markdown("&nbsp;")


# Sidebar
st.sidebar.title("S🎈nder")
st.sidebar.write("_The Opportunity Cost of Internet Search_")
st.sidebar.markdown("---")

navigate_sidebar = st.sidebar.radio(
    "Go to",
    [
        "⚖️ Balance",
        "🕸️ Web Trends",
        "🗞️ News Trends",
        "🕯️ Wiki Trends",
        "🐦 Twitter Trends",
        "About",
    ],
    0,
)
st.sidebar.markdown("---")

st.sidebar.markdown("**🐧 Contribute**")
st.sidebar.info(
    "Contributions welcome through comments, issues, and pull requests to the open-source [code base](https://github.com/sonder-labs/sonder)."
)

st.sidebar.markdown("**🏅 Awards**")
st.sidebar.info(
    "🏆 Design Challenge Research Award, Stanford University (June 2021) \n\n 🏆 Digital Learning Design Challenge Grant, Stanford University (March 2021)"
)

st.sidebar.markdown("**:octopus: Maitainers**")
st.sidebar.info(
    "[Saurabh Khanna](mailto:saurabhkhanna@stanford.edu)  \n[Shruti Jain](mailto:shruti_jain@berkeley.edu)  \n\nWrite to us to join forces!"
)

# Main page

# Balance
if navigate_sidebar == "⚖️ Balance":
    exec(open("scripts/balance.py").read())

# Bias trends
if navigate_sidebar == "🕸️ Web Trends":
    exec(open("scripts/web_trends.py").read())

if navigate_sidebar == "🗞️ News Trends":
    exec(open("scripts/news_trends.py").read())

if navigate_sidebar == "🕯️ Wiki Trends":
    # exec(open("scripts/wiki_trends.py").read())
    st.markdown("&nbsp;")
    st.markdown("_STILL COOKING!_ :spaghetti:")
    st.markdown(
        "Watch our [GitHub](https://github.com/sonder-labs/sonder) repository for updates on this feature."
    )
    st.markdown("&nbsp;")


if navigate_sidebar == "🐦 Twitter Trends":
    st.markdown("&nbsp;")
    st.markdown("_STILL COOKING!_ :spaghetti:")
    st.markdown(
        "Watch our [GitHub](https://github.com/sonder-labs/sonder) repository for updates on this feature."
    )
    st.markdown("&nbsp;")

# Philosophy
if navigate_sidebar == "About":
    exec(open("scripts/about_us.py").read())

# Unsung
# if navigate_sidebar == "📻 Unsung":
#     st.markdown("## 📻 Unsung")
#     st.markdown("\n\n")
#     st.info(
#         ":heart: Do [write to us](mailto:saurabhkhanna@stanford.edu) to contribute an untold story that needs to be heard. Our story archive is hosted [here](https://github.com/sonder-labs/sonder/tree/main/unsung)."
#     )
#     st.markdown(Path("unsung/unsung-sotw.md").read_text(), unsafe_allow_html=True)
