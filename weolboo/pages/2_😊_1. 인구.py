import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_icon="😊",
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

if 'get_age_population_data_gwangyeok' not in st.session_state:
    st.session_state.get_age_population_data_gwangyeok = None
if 'get_age_population_plotly_gwangyeok' not in st.session_state:
    st.session_state.get_age_population_plotly_gwangyeok = None
if 'get_age_population_data_sigungu' not in st.session_state:
    st.session_state.get_age_population_data_sigungu = None
if 'get_age_population_plotly_sigungu' not in st.session_state:
    st.session_state.get_age_population_plotly_sigungu = None

if st.session_state.get_age_population_data_sigungu == None:
    st.warning("⚠ 인구 데이터가 없습니다.")
if st.session_state.get_age_population_data_sigungu:
    st.header("😊 1. 인구")
    selected_sido = st.session_state.selected_sido
    selected_sigungu = st.session_state.selected_sigungu
    # ==============================================================================
    # 광역시별 / 시도 시군구 읍면동별 연령별 비중
    # ==============================================================================
    if st.session_state.get_age_population_data_gwangyeok is not None:
        # df 그리기
        st.subheader("광역시별 연령대별 인구수 데이터")
        st.dataframe(st.session_state.get_age_population_data_gwangyeok, use_container_width=True)
        # 그래프 그리기
        st.plotly_chart(st.session_state.get_age_population_plotly_gwangyeok)

    if st.session_state.get_age_population_data_sigungu is not None:
        # df 그리기
        st.subheader(f"{selected_sido} {selected_sigungu} 연령대별 인구수 데이터")
        st.dataframe(st.session_state.get_age_population_data_sigungu, use_container_width=True)
        # 그래프 그리기
        st.plotly_chart(st.session_state.get_age_population_plotly_sigungu)
    # ==============================================================================
    # 광역시별 / 시군구별 / 시도 시군구 읍면동별 총인구수, 세대수, 세대당 인구
    # ==============================================================================




