import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_icon="🚇",
    page_title="교통",
    layout="wide",
)

# ==============================================================================
# session_state 초기화
# ==============================================================================

if 'gyotong_subway' not in st.session_state:
    st.session_state.gyotong_subway = None

if st.session_state.gyotong_subway == None:
    st.warning("⚠ 교통 데이터가 없습니다.")
if st.session_state.gyotong_subway:
    st.header("🚇 6. 교통")
    st.dataframe(st.session_state.gyotong_subway, use_container_width=True)