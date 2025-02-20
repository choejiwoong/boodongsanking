import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_icon="🏙",
    page_title="직장분석",
    layout="wide",
)

st.warning("⚠ 직장 데이터가 없습니다.")

# if st.session_state.get_age_population_data_hdong is None:
#     st.warning("⚠ 직장 데이터가 없습니다.")
# else:
#     st.header("😊 1. 인구")