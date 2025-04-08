import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_icon="😊",
    page_title="인구",
    layout="wide",
)

if st.session_state.selected_gungu == "전체":
    st.warning("⚠ 인구 데이터가 없습니다.")
else:
    st.header("😊 1. 인구")
    selected_sido = st.session_state.selected_sido
    selected_gungu = st.session_state.selected_gungu
    # 변수 정의
    # 연령별 비중
    df_age_sido = st.session_state.df_age_sido
    df_age_gungu = st.session_state.df_age_gungu
    df_age_hdong = st.session_state.df_age_hdong
    age_population_plotly_sido = st.session_state.get_age_population_plotly_sido
    age_population_plotly_gungu = st.session_state.get_age_population_plotly_gungu
    age_population_plotly_hdong = st.session_state.get_age_population_plotly_hdong
    # 세대당 인구 수
    df_sido = st.session_state.df_sido
    df_gungu = st.session_state.df_gungu
    # df_hdong = st.session_state.df_hdong
    population_plotly_sido = st.session_state.get_population_plotly_sido
    population_plotly_gungu = st.session_state.get_population_plotly_gungu
    # population_plotly_hdong = st.session_state.get_population_plotly_hdong
    # ==============================================================================
    # 시도별 데이터
    # ==============================================================================
    st.subheader("시도별 비교")
    st.markdown("#### 인구, 세대, 세대 당 인구수")
    # df 그리기
    st.dataframe(df_sido, use_container_width=True)
    # plotly 그리기
    st.plotly_chart(population_plotly_sido)
    st.markdown("#### 연령대별 인구수")
    # df 그리기
    st.dataframe(df_age_sido, use_container_width=True)
    # 그래프 그리기
    st.plotly_chart(age_population_plotly_sido)
    # ==============================================================================
    # 시군구별 데이터
    # ==============================================================================
    st.subheader("시군구별 비교")
    st.markdown("#### 인구, 세대, 세대 당 인구수")
    # df 그리기
    st.dataframe(df_gungu, use_container_width=True)
    # plotly 그리기
    st.plotly_chart(population_plotly_gungu)
    st.markdown("#### 연령대별 인구수")
    # df 그리기
    st.dataframe(df_age_gungu, use_container_width=True)
    # 그래프 그리기
    st.plotly_chart(age_population_plotly_gungu)
    # ==============================================================================
    # 행정동별 데이터
    # ==============================================================================
    st.subheader(f"{selected_sido} {selected_gungu} 연령대별 인구수")
    st.dataframe(df_age_hdong, use_container_width=True)
    # 그래프 그리기
    st.plotly_chart(age_population_plotly_hdong)




