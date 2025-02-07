import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_icon="🎓",
    page_title="학군분석",
    layout="wide",
)

st.header("학군분석")

if 'school_achievement_ranking' not in st.session_state:
    st.session_state.school_achievement_ranking = None

if st.session_state.school_achievement_ranking:
    st.write(st.session_state.school_achievement_ranking)