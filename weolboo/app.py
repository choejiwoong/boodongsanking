import streamlit as st
import pandas as pd
import numpy as np
from crawler_ingoo import AgePopulationAnalysis
from crawler_sigungu import *
from streamlit_db import *
from bson import ObjectId
from crawler_hakgun import *

# ==============================================================================
# 페이지 기본 설정
# ==============================================================================
st.set_page_config(
    page_icon="📑",
    page_title="최밥통의 부동산 임장보고서",
    layout="wide",
)
st.header("📑 최밥통의 부동산 임장보고서")
# mongodb 'sigungu' collection 연결
uri = 'mongodb+srv://wldndchl0926:oklove0610!@boodongsancluster.fo8xa.mongodb.net/?retryWrites=true&w=majority&appName=boodongsanCluster'
db_name = "db"
collection_name = 'sigungu'
collection_sigungu = connect_to_mongodb(uri, db_name, collection_name)


# ==============================================================================
# 시군구명 selectbox data mongodb에서 불러오기
# ==============================================================================
# 데이터가 있으면 시군구 구분 선택할 수 있는 콤보박스 현시
query = {'_id': ObjectId('67a09c8bc9f63336ba4040c1')}
projection = {'_id': 0}  # _id 제외
if find_documents(collection_sigungu, query):
    sigungu_dict = find_documents(collection_sigungu, query, projection)
    # sigungu_dict session_state에 저장
    if 'sigungu_dict' not in st.session_state or st.session_state.sigungu_dict != sigungu_dict[0]:
        st.session_state.sigungu_dict = sigungu_dict[0]
        print(sigungu_dict[0])

    # 도시 선택 selectedbox
    selected_sido = st.selectbox('도시를 선택하세요.', list(sigungu_dict[0].keys()), index=1)
    # 선택된 시도 session_state에 저장
    if 'selected_sido' not in st.session_state or st.session_state.selected_sido != selected_sido:
        st.session_state.selected_sido = selected_sido
    # 시군구 선택 selectedbox
    selected_sigungu = st.selectbox('시군구를 선택하세요.', sigungu_dict[0][selected_sido].keys())
    # 선택된 시군구 session_state에 저장
    if 'selected_sigungu' not in st.session_state or st.session_state.selected_sigungu != selected_sigungu:
        st.session_state.selected_sigungu = selected_sigungu

# ==============================================================================
# 정보수집 버튼들
# ==============================================================================
# ==============================================================================
# 시군구명 selectbox data 크롤링 버튼(유사시)
# ==============================================================================
# if st.button("시군구명 다시 불러오기"):
#     # 시군구명 불러오기
#     code = SigunguCode()
#     code.load_sigungu_name()
#     sigungu_name = code.get_sigungu_name_dict()
#     # 시군구명 mongodb 덮어쓰기
#     overwrite_document(collection_sigungu, query, sigungu_name)
#     st.success('시군구명 업데이트 완료!')
#
# # 행정동명 불러오기
# if st.session_state.selected_sigungu:
#     code = SigunguCode(sigungu_name=st.session_state.selected_sigungu)
#     code.load_hdong()
#     hdong_name = code.get_hdong_dict()
#     # 시군구명 mongodb 덮어쓰기
#     overwrite_document(collection_sigungu, query, hdong_name)
#     st.success('행정동명 업데이트 완료!')

# ==============================================================================
# 데이터 수집 버튼
# ==============================================================================
st.subheader("데이터 수집")
if st.button("데이터 수집"):
    with st.spinner('잠시만 기다려주세요. 데이터를 불러오는 중입니다...⏳'):
        # '광역시'가 포함된 시군구명만 dict로 만들기
        gwangyeok_dict = {
            sido: list(list(hdong_dict.values())[0][:2]  # 첫 번째 행정동 코드에서 앞 두 자리만 추출
                       for sigungu, hdong_dict in sigungu_dict.items())[0]
            for sido, sigungu_dict in st.session_state.sigungu_dict.items()
            if '광역시' in sido  # 광역시에 해당하는 시도만 필터링
        }
        code_gwangyeok = AgePopulationAnalysis(gwangyeok_dict=gwangyeok_dict)
        get_age_population_data_gwangyeok = code_gwangyeok.get_age_population_data()
        st.session_state.get_age_population_data_gwangyeok = get_age_population_data_gwangyeok
        get_age_population_plotly_gwangyeok = code_gwangyeok.get_age_population_plotly(get_age_population_data_gwangyeok)
        st.session_state.get_age_population_plotly_gwangyeok = get_age_population_plotly_gwangyeok
        # 특정 시군구의 행정동
        selected_sido = st.session_state.selected_sido
        selected_sigungu = st.session_state.selected_sigungu
        hdong_dict = st.session_state.sigungu_dict[selected_sido][selected_sigungu]
        code_hdong = AgePopulationAnalysis(hdong_dict=hdong_dict)
        get_age_population_data_sigungu = code_hdong.get_age_population_data()
        st.session_state.get_age_population_data_sigungu = get_age_population_data_sigungu
        get_age_population_plotly_sigungu = code_hdong.get_age_population_plotly(get_age_population_data_sigungu)
        st.session_state.get_age_population_plotly_sigungu = get_age_population_plotly_sigungu
        st.success('😊_1. 인구/연령대별 인구수 데이터 불러오기 완료')

        school_achievement = SchoolAchievement(st.session_state.selected_sido, st.session_state.selected_sigungu)
        st.session_state.school_achievement_ranking = school_achievement.calculate_ranking()
        st.success('🎓_3. 학군 데이터 불러오기 완료')
