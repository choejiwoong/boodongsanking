import streamlit as st
import pandas as pd

# 페이지 기본 설정
st.set_page_config(
    page_icon="🏙",
    page_title="직장분석",
    layout="wide",
)

if 'jikjang_gwangyeok_df' not in st.session_state:
    st.session_state.jikjang_gwangyeok_df = None  # 초기값 설정 (None, 빈 문자열, 또는 적당한 값)
if 'jikjang_sigungu_df' not in st.session_state:
    st.session_state.jikjang_sigungu_df = None  # 초기값 설정 (None, 빈 문자열, 또는 적당한 값)
if 'jikjang_gwangyeok_industry_df' not in st.session_state:
    st.session_state.jikjang_gwangyeok_industry_df = None  # 초기값 설정 (None, 빈 문자열, 또는 적당한 값)
if 'jikjang_sigungu_industry_df' not in st.session_state:
    st.session_state.jikjang_sigungu_industry_df = None  # 초기값 설정 (None, 빈 문자열, 또는 적당한 값)
if 'jikjang_gwangyeok_industry_plotly' not in st.session_state:
    st.session_state.jikjang_gwangyeok_industry_plotly = None  # 초기값 설정 (None, 빈 문자열, 또는 적당한 값)
if 'jikjang_sigungu_industry_plotly' not in st.session_state:
    st.session_state.jikjang_sigungu_industry_plotly = None  # 초기값 설정 (None, 빈 문자열, 또는 적당한 값)
if 'get_population_data_gwangyeok' not in st.session_state:
    st.session_state.get_population_data_gwangyeok = None  # 초기값 설정 (None, 빈 문자열, 또는 적당한 값)
if 'get_population_data_sigungu' not in st.session_state:
    st.session_state.get_population_data_sigungu = None  # 초기값 설정 (None, 빈 문자열, 또는 적당한 값)
if 'jikjang_income_gwangyeok' not in st.session_state:
    st.session_state.jikjang_income_gwangyeok = None  # 초기값 설정 (None, 빈 문자열, 또는 적당한 값)
if 'jikjang_income_sigungu' not in st.session_state:
    st.session_state.jikjang_income_sigungu = None  # 초기값 설정 (None, 빈 문자열, 또는 적당한 값)


if st.session_state.jikjang_gwangyeok_df is None:
    st.warning("⚠ 직장 데이터가 없습니다.")
else:
    st.header("🏙 2. 직장")
    # 두 개의 열을 생성
    col1, col2, col3 = st.columns(3)
    # 높이 설정
    height = 600
    with col1:
        jikjang_gwangyeok_df = st.session_state.jikjang_gwangyeok_df
        st.dataframe(jikjang_gwangyeok_df, use_container_width=True)
    with col2:
        jikjang_gwangyeok_industry_df = st.session_state.jikjang_gwangyeok_industry_df
        st.dataframe(jikjang_gwangyeok_industry_df, use_container_width=True)

        # st.plotly_chart(st.session_state.jikjang_gwangyeok_industry_plotly)
    with col3:
        st.dataframe(st.session_state.jikjang_income_gwangyeok)

    # 두 개의 열을 생성
    col1, col2, col3 = st.columns(3)
    with col1:
        jikjang_sigungu_df = st.session_state.jikjang_sigungu_df
        st.dataframe(jikjang_sigungu_df, use_container_width=True)
    with col2:
        jikjang_sigungu_industry_df = st.session_state.jikjang_sigungu_industry_df
        st.dataframe(jikjang_sigungu_industry_df, use_container_width=True)

        # st.plotly_chart(st.session_state.jikjang_sigungu_industry_plotly)
    with col3:
        st.dataframe(st.session_state.jikjang_income_sigungu)