#!/usr/bin/python
# -*- coding: utf-8 -*-
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Sonder", page_icon="data/favicon/favicon.png")

'''
# Sonder
_An Open Knowledge Platform_

---
'''

# Main
st.sidebar.title('Sonder')
st.sidebar.markdown('_An Open Knowledge Platform_')

st.sidebar.markdown('---')

# Sidebar
navigate_sidebar = st.sidebar.empty()
value = navigate_sidebar.radio('Go to', ['Home', 'Spectrum', 'Spacetime', 'Balance'], 0)

st.sidebar.markdown('---')

st.sidebar.markdown('**Contribute**')
st.sidebar.info('Sonder is an open-source project enabling access to diverse knowledge. Please contribute any comments, questions, code changes, and resources as [issues](https://github.com/saurabh-khanna/sonder/issues) of or [pull requests](https://github.com/saurabh-khanna/sonder/pulls) to the [source code](https://github.com/saurabh-khanna/sonder).')

st.sidebar.markdown('**About me**')
st.sidebar.info("""I am a PhD candidate at Stanford studying how knowledge flows through networks. You can learn more about me [here](https://saurabh-khanna.github.io).""")


# Main page
col_a, col_b, col_c, col_d = st.beta_columns([1,1,1,1])

if col_a.button('Home'):
    value = 'Home'

if col_b.button('Spectrum'):
    value = navigate_sidebar.radio('Go to', ['Home', 'Spectrum', 'Spacetime', 'Balance'], 1)

if col_c.button('Spacetime'):
    value = navigate_sidebar.radio('Go to', ['Home', 'Spectrum', 'Spacetime', 'Balance'], 2)

if col_d.button('Balance'):
    value = navigate_sidebar.radio('Go to', ['Home', 'Spectrum', 'Spacetime', 'Balance'], 3)


# Home
if value == 'Home':
    st.markdown(Path("markdown/home_top.md").read_text(), unsafe_allow_html=True)
    st.markdown(Path("markdown/home_bottom.md").read_text(), unsafe_allow_html=True)

# Spectrum
if value == 'Spectrum':
    exec(open('scripts/spectrum.py').read())

# Spacetime
if value == 'Spacetime':
    exec(open('scripts/spacetime.py').read())

# Balance
if value == 'Balance':
    st.write('Still cooking!!')


# hiding the footer
hide_footer_style = \
    """
    <style>
    .reportview-container .main footer {visibility: hidden;}    
    """
st.markdown(hide_footer_style, unsafe_allow_html=True)
