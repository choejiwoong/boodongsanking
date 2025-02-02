import streamlit as st
from weolboo.crawlers.crawler_ingoo import AgePopulationAnalysis

def show_population_page():
    st.title("부산광역시 연령대별 인구 분석")

    sido_name = "부산광역시"
    population_analysis = AgePopulationAnalysis(sido_name)

    # 연령별 인구수 데이터 처리
    population_analysis.process_population_data()

    # 결과 DataFrame 가져오기
    age_population_df = population_analysis.get_population_data()

    # Streamlit에서 DataFrame 출력
    if not age_population_df.empty:
        st.write("연령대별 인구수 데이터:")
        st.dataframe(age_population_df)
    else:
        st.write("데이터를 가져올 수 없습니다.")