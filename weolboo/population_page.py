import streamlit as st
import plotly.express as px
from crawler_ingoo import AgePopulationAnalysis

def show_population_page():
    st.title("부산광역시 연령대별 인구 분석")
    if st.button("데이터 불러오기"):
        with st.spinner("불러오는 중입니다. 잠시만 기다려주세용 ⌛"):
            get_population_data()

            # # Altair로 막대 차트 만들기
            # chart = alt.Chart(data).mark_bar().encode(
            #     x='Category',
            #     y='Value',
            #     color='Group',  # 색상 계열을 그룹별로 다르게
            #     column='Group'  # 계열(필터) 추가
            # ).properties(width=200, height=200)
        st.success("데이터 불러오기 완료")

def get_population_data():
    sido_name = "부산광역시"
    population_analysis = AgePopulationAnalysis(sido_name)

    # 연령별 인구수 데이터 처리
    population_analysis.process_population_data()

    # 결과 DataFrame 가져오기
    age_population_df = population_analysis.get_population_data().T

    # 0-9세 합치기
    age_population_df['영유아'] = age_population_df['0 - 4세'] + age_population_df['5 - 9세']
    age_population_df.drop(columns=['0 - 4세', '5 - 9세'], inplace=True)
    # 10-19세 합치기
    age_population_df['10대'] = age_population_df['10 - 14세'] + age_population_df['15 - 19세']
    age_population_df.drop(columns=['10 - 14세', '15 - 19세'], inplace=True)
    # 20-29세 합치기
    age_population_df['20대'] = age_population_df['20 - 24세'] + age_population_df['25 - 29세']
    age_population_df.drop(columns=['20 - 24세', '25 - 29세'], inplace=True)
    # 30-39세 합치기
    age_population_df['30대'] = age_population_df['30 - 34세'] + age_population_df['35 - 39세']
    age_population_df.drop(columns=['30 - 34세', '35 - 39세'], inplace=True)
    # 40-49세 합치기
    age_population_df['40대'] = age_population_df['40 - 44세'] + age_population_df['45 - 49세']
    age_population_df.drop(columns=['40 - 44세', '45 - 49세'], inplace=True)
    # 50-59세 합치기
    age_population_df['50대'] = age_population_df['50 - 54세'] + age_population_df['55 - 59세']
    age_population_df.drop(columns=['50 - 54세', '55 - 59세'], inplace=True)
    # 60-104세 합치기
    age_population_df['60대 이상'] = age_population_df['60 - 64세'] + age_population_df['65 - 69세'] + age_population_df['70 - 74세'] + age_population_df['75 - 79세'] + age_population_df['80 - 84세'] + age_population_df[
        '85 - 89세'] + age_population_df['90 - 94세'] + age_population_df['95 - 99세'] + age_population_df['100 - 104세']
    age_population_df.drop(columns=['60 - 64세', '65 - 69세', '70 - 74세', '75 - 79세',
                                    '80 - 84세', '85 - 89세', '90 - 94세', '95 - 99세',
                                    '100 - 104세'], inplace=True)

    # Streamlit에서 DataFrame 출력
    if not age_population_df.empty:
        st.write("연령대별 인구수 데이터:")
        st.dataframe(age_population_df)
        # 시군구별 누적 막대 그래프 그리기
        fig = px.bar(age_population_df,
                     x=age_population_df.index,
                     y=['영유아', '10대', '20대', '30대', '40대', '50대', '60대 이상'],
                     title="시군구별 연령별 인구 분포",
                     labels={"value": "인구수", "variable": "연령대"},
                     color="variable",
                     barmode='stack')

        # 그래프 표시
        st.plotly_chart(fig)
    else:
        st.write("데이터를 가져올 수 없습니다.")