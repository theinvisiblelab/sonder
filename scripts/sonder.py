#!/usr/bin/python
# -*- coding: utf-8 -*-
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Sonder", page_icon=":balloon:", layout="wide")

"""
# S🎈nder
_Enabling fairer knowledge search_

---
"""

# Main
st.sidebar.title("S🎈nder")
st.sidebar.markdown("_Enabling fairer knowledge search_")

st.sidebar.markdown("---")

# Sidebar
navigate_sidebar = st.sidebar.radio("Go to", ["Bias", "Balance", "Philosophy"], 0)

st.sidebar.markdown("---")

st.sidebar.markdown("**📖 About**")
st.sidebar.info(
    "Sonder is an open-source search platform enabling fairer access to human knowledge. We welcome contributions through comments, questions, issues, and pull requests to our [source code](https://github.com/sonder-labs/sonder)."
)

st.sidebar.markdown("**🏆 Awards**")
st.sidebar.info(
    "Digital Learning Design Challenge Winter Grant, March 2021 [Stanford University and StartX]"
)

st.sidebar.markdown("**🎋 Contributors**")
st.sidebar.info(
    "[Saurabh Khanna](mailto:saurabhkhanna@stanford.edu)  \n[Shruti Jain](mailto:shruti_jain@berkeley.edu)  \n\nWrite to us to join forces!"
)

# Main page

# Bias
if navigate_sidebar == "Bias":
    exec(open("scripts/bias.py").read())

# Balance
if navigate_sidebar == "Balance":
    exec(open("scripts/balance.py").read())

# Philosophy
if navigate_sidebar == "Philosophy":
    st.markdown(Path("markdown/philosophy.md").read_text(), unsafe_allow_html=True)


# hiding the footer
hide_footer_style = """
    <style>
    .reportview-container .main footer {visibility: hidden;}
    """
st.markdown(hide_footer_style, unsafe_allow_html=True)
