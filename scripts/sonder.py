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
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

"""
# S🎈nder
_Empowering humans with fairer knowledge access_

---
"""

# Sidebar
st.sidebar.title("S🎈nder")
st.sidebar.markdown("---")

navigate_sidebar = st.sidebar.radio(
    "Go to", ["Home", "⚖️ Balance", "📣 Trends"], 0
)
st.sidebar.markdown("---")

st.sidebar.markdown("**🏆 Awards**")
st.sidebar.info(
    "Digital Learning Design Challenge Winter Grant [Stanford Transforming Learning Accelerator]"
)

st.sidebar.markdown("**:octopus: Maitainers**")
st.sidebar.info(
    "[Saurabh Khanna](mailto:saurabhkhanna@stanford.edu)  \n[Shruti Jain](mailto:shruti_jain@berkeley.edu)  \n\nWrite to us to join forces!"
)

st.sidebar.markdown("**🐧 Contribute**")
st.sidebar.info(
    "We welcome contributions through comments, issues, and pull requests to our [open-source code](https://github.com/sonder-labs)."
)

# Main page

# Philosophy
if navigate_sidebar == "Home":
    exec(open("scripts/about_us.py").read())

# Balance
if navigate_sidebar == "⚖️ Balance":
    exec(open("scripts/balance.py").read())

# Bias trends
if navigate_sidebar == "📣 Trends":
    exec(open("scripts/bias_trends.py").read())

# Unsung
if navigate_sidebar == "📻 Unsung":
    st.markdown("## 📻 Unsung")
    st.markdown("\n\n")
    st.info(
        ":heart: Do [write to us](mailto:saurabhkhanna@stanford.edu) to contribute an untold story that needs to be heard. Our story archive is hosted [here](https://github.com/sonder-labs/sonder/tree/main/unsung)."
    )
    st.markdown(Path("unsung/unsung-sotw.md").read_text(), unsafe_allow_html=True)
