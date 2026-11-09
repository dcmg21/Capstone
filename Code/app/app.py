"""
Brand Radar. Run from the Code/app folder:   streamlit run app.py
"""

import streamlit as st

from common import APP_NAME, CSS

st.set_page_config(page_title=APP_NAME, page_icon="🥃", layout="wide", initial_sidebar_state="expanded")
st.markdown(CSS, unsafe_allow_html=True)

pages = [
    st.Page("views/home.py", title="Home", icon=":material/home:", default=True),
    st.Page("views/list.py", title="The List", icon=":material/format_list_numbered:"),
    st.Page("views/brand.py", title="One Brand", icon=":material/query_stats:"),
    st.Page("views/rules.py", title="How Labels Work", icon=":material/menu_book:"),
    st.Page("views/model.py", title="The Model", icon=":material/verified:"),
]
st.navigation(pages, position="sidebar").run()
