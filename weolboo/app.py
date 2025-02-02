import streamlit as st
import pandas as pd
import numpy as np
import population_page

# 페이지 기본 설정
st.set_page_config(
    page_icon="🏠",
    page_title="최밥통의 부동산 임장보고서",
    layout="wide",
)

population_page.show_population_page()
