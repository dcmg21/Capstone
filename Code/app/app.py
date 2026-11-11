"""
Brand Radar. Run from the Code/app folder:   streamlit run app.py
"""

import streamlit as st

from common import APP_NAME, CSS

st.set_page_config(page_title=APP_NAME, page_icon="🥃", layout="wide", initial_sidebar_state="expanded")
st.markdown(CSS, unsafe_allow_html=True)

# grouped so the sidebar reads as three short lists, not one long one
pages = {
    "": [st.Page("views/home.py", title="Home", icon=":material/home:", default=True)],
    "Brands": [st.Page("views/list.py", title="Brand List", icon=":material/format_list_numbered:"),
               st.Page("views/brand.py", title="One Brand", icon=":material/query_stats:")],
    "Suppliers": [st.Page("views/suppliers.py", title="Supplier List", icon=":material/domain:"),
                  st.Page("views/supplier.py", title="One Supplier", icon=":material/inventory_2:")],
    "How it works": [st.Page("views/rules.py", title="How Labels Work", icon=":material/menu_book:"),
                     st.Page("views/model.py", title="How the Model Works", icon=":material/verified:")],
}
st.navigation(pages, position="sidebar").run()
