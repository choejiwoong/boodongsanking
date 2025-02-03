import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_icon="👨‍👩‍👧‍👦",
    page_title="인구",
    layout="wide",
)
# session_state 기본값 설정
# sigungu_dict
if 'sigungu_dict' not in st.session_state:
    st.session_state.sigungu_dict = None  # 초기값 설정 (None, 빈 문자열, 또는 적당한 값)
# selected_sido
if 'selected_sido' not in st.session_state:
    st.session_state.selected_sido = None  # 초기값 설정 (None, 빈 문자열, 또는 적당한 값)
# selected_sigungu
if 'selected_sigungu' not in st.session_state:
    st.session_state.selected_sigungu = None  # 초기값 설정 (None, 빈 문자열, 또는 적당한 값)

st.header("인구분석")
if st.session_state.sigungu_dict:
    selected_sido = st.session_state.selected_sido
    selected_sigungu = st.session_state.selected_sigungu
    st.write(selected_sido)
    st.write(selected_sigungu)
    # sigungu_dict = st.session_state.sigungu_dict
    # st.write(sigungu_dict)
    # st.write(sigungu_dict.get(selected_sido, '선택된 시도 정보가 없습니다.'))