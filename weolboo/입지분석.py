import streamlit as st
from crawlers.crawler_ingoo import *

st.write("세부 항목을 선택하세요:")

# 각 섹션에 대한 컨텐츠
st.markdown("""
    # 인구
    ## 부산 구별 인구 수(양/질) 
    """)

sido_name = "부산광역시"

# AgePopulationAnalysis 인스턴스 생성 (service_key는 기본값 사용)
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

st.markdown("""
    # 환경 분석
    환경 분석에 관한 내용이 여기에 들어갑니다.
    """)

st.markdown("""
    # 교통 분석
    """)
