#!/usr/bin/python
# -*- coding: utf-8 -*-
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Sonder", page_icon="favicon/favicon.png")

"""
# Sonder
_An Open-source Knowledge Platform_

---
"""

# Main
st.sidebar.title("Sonder")
st.sidebar.markdown("_An Open-source Knowledge Platform_")

st.sidebar.markdown("---")

# Sidebar
navigate_sidebar = st.sidebar.radio("Go to", ["Bias", "Balance", "Philosophy"], 0)

st.sidebar.markdown("---")

st.sidebar.markdown("**Contribute**")
st.sidebar.info(
    "Sonder is an open-source project enabling access to diverse knowledge. Please contribute any comments, questions, code changes, and resources as [issues](https://github.com/saurabh-khanna/sonder/issues) of or [pull requests](https://github.com/saurabh-khanna/sonder/pulls) to the [source code](https://github.com/saurabh-khanna/sonder)."
)

st.sidebar.markdown("**About me**")
st.sidebar.info(
    """I am a PhD candidate at Stanford studying how knowledge flows through networks. You can learn more about me [here](https://saurabh-khanna.github.io)."""
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
