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
if 'get_age_population_data_hdong' not in st.session_state:
    st.session_state.get_age_population_data_hdong = None
if 'get_age_population_plotly_hdong' not in st.session_state:
    st.session_state.get_age_population_plotly_hdong = None
if 'pop_div_saedae_gwangyeok' not in st.session_state:
    st.session_state.pop_div_saedae_gwangyeok = None
if 'get_population_plotly_gwangyeok' not in st.session_state:
    st.session_state.get_population_plotly_gwangyeok = None
if 'pop_div_saedae_sigungu' not in st.session_state:
    st.session_state.pop_div_saedae_sigungu = None
if 'get_population_plotly_sigungu' not in st.session_state:
    st.session_state.get_population_plotly_sigungu = None
if 'pop_div_saedae_hdong' not in st.session_state:
    st.session_state.pop_div_saedae_hdong = None
if 'get_population_plotly_hdong' not in st.session_state:
    st.session_state.get_population_plotly_hdong = None

if st.session_state.get_age_population_data_hdong is None:
    st.warning("⚠ 인구 데이터가 없습니다.")
else:
    st.header("😊 1. 인구")
    selected_sido = st.session_state.selected_sido
    selected_sigungu = st.session_state.selected_sigungu
    # ==============================================================================
    # 광역시별 데이터
    # ==============================================================================
    if st.session_state.get_age_population_data_gwangyeok is not None:
        # df 그리기
        st.subheader("광역시별 비교")
        if st.session_state.pop_div_saedae_gwangyeok is not None:
            result_df = st.session_state.pop_div_saedae_gwangyeok
            st.markdown("#### 인구, 세대, 세대 당 인구수")
            st.dataframe(result_df, use_container_width=True)
            st.plotly_chart(st.session_state.get_population_plotly_gwangyeok)
        st.markdown("#### 연령대별 인구수")
        st.dataframe(st.session_state.get_age_population_data_gwangyeok, use_container_width=True)
        # 그래프 그리기
        st.plotly_chart(st.session_state.get_age_population_plotly_gwangyeok)
    # ==============================================================================
    # 시군구별 데이터
    # ==============================================================================
    if st.session_state.get_age_population_data_sigungu is not None:
        # df 그리기
        st.subheader("시군구별 비교")
        if st.session_state.pop_div_saedae_sigungu is not None:
            result_df = st.session_state.pop_div_saedae_sigungu
            st.markdown("#### 인구, 세대, 세대 당 인구수")
            st.dataframe(result_df, use_container_width=True)
            st.plotly_chart(st.session_state.get_population_plotly_sigungu)
        st.markdown("#### 연령대별 인구수")
        st.dataframe(st.session_state.get_age_population_data_sigungu, use_container_width=True)
        # 그래프 그리기
        st.plotly_chart(st.session_state.get_age_population_plotly_sigungu)
    # ==============================================================================
    # 행정동별 데이터
    # ==============================================================================
    if st.session_state.get_age_population_data_hdong is not None:
        # df 그리기
        st.subheader(f"{selected_sido} {selected_sigungu} 연령대별 인구수")
        st.dataframe(st.session_state.get_age_population_data_hdong, use_container_width=True)
        # 그래프 그리기
        st.plotly_chart(st.session_state.get_age_population_plotly_hdong)

        # if st.session_state.pop_div_saedae_hdong is not None:
        #     result_df = st.session_state.pop_div_saedae_hdong
        #     # result_df['세대당 인구수'] = result_df['세대당 인구수'].apply(lambda x: f"{x:.2f}") # '세대당 인구수' 열을 소수점 두 자리로 포맷팅
        #     # result_df['총인구수'] = result_df['총인구수'].apply(lambda x: f"{x:,}") # '총인구수'와 '세대수' 열을 천 단위 구분 기호로 표시
        #     # result_df['세대수'] = result_df['세대수'].apply(lambda x: f"{x:,}") # '총인구수'와 '세대수' 열을 천 단위 구분 기호로 표시
        #     st.dataframe(result_df, use_container_width=True, height=height)
        #     st.plotly_chart(st.session_state.get_population_plotly_hdong, height=height)

    # ==============================================================================
    # 광역시별 / 시군구별 / 시도 시군구 읍면동별 총인구수, 세대수, 세대당 인구
    # ==============================================================================




