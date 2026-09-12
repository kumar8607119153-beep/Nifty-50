import streamlit as st
from pathlib import Path
import streamlit.components.v1 as components

st.set_page_config(page_title='NIFTY • BANK NIFTY • SENSEX', page_icon='📈', layout='centered')
st.markdown('''<style>html,body,[data-testid="stAppViewContainer"]{background:#fff}.block-container{max-width:100%;padding:.2rem .1rem 1rem}.stApp{overflow-x:hidden}header{visibility:hidden;height:0}iframe{width:100%!important;border:0!important}</style>''', unsafe_allow_html=True)
html = Path(__file__).with_name('dashboard.html').read_text(encoding='utf-8')
components.html(html, height=2400, scrolling=True)
