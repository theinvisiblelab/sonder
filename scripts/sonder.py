#!/usr/bin/python
# -*- coding: utf-8 -*-
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Metrics", page_icon=":balloon:", layout="wide")

# hiding the hamburger menu and footer
hide_streamlit_style = """
<style>
MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>

"""

# Main page

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("S🎈nder")
st.markdown("&nbsp;")


# Sidebar
st.sidebar.title("S🎈nder")
st.sidebar.write("_Enabling fairer information access_")
st.sidebar.markdown("---")

navigate_sidebar = st.sidebar.radio(
    "Go to",
    [
        "🎈 Home",
        "🚲 Demo",
        "🔧 Learn more",
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
    "🏆 Design Challenge Research Award, Stanford University \n\n 🏆 Karr Fellowship, Stanford University \n\n 🏆 Digital Learning Design Challenge Grant, Stanford University"
)

st.sidebar.markdown("**👾 Maitainer**")
st.sidebar.info("[Saurabh Khanna](mailto:saurabhkhanna@stanford.edu)")

# Main page

# Balance
if navigate_sidebar == "🎈 Home":
    exec(open("scripts/old/balance.py").read())

# Metrics
if navigate_sidebar == "🚲 Demo":
    exec(open("scripts/demo.py").read())

# About Us
if navigate_sidebar == "🔧 Learn more":
    st.write("Learn more [here](https://github.com/sonder-labs/sonder).")

# Unsung
# if navigate_sidebar == "📻 Unsung":
#     st.markdown("## 📻 Unsung")
#     st.markdown("\n\n")
#     st.info(
#         ":heart: Do [write to us](mailto:saurabhkhanna@stanford.edu) to contribute an untold story that needs to be heard. Our story archive is hosted [here](https://github.com/sonder-labs/sonder/tree/main/unsung)."
#     )
#     st.markdown(Path("unsung/unsung-sotw.md").read_text(), unsafe_allow_html=True)
