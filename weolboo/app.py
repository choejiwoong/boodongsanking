import streamlit as st
import pandas as pd
import numpy as np
import population_page
from crawler_ingoo import AgePopulationAnalysis
from crawler_sigungu import *
from streamlit_db import *
from bson import ObjectId

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

    # 도시 선택 selectedbox
    selected_sido = st.selectbox('도시를 선택하세요.', list(sigungu_dict[0].keys()), index=1)
    # 선택된 시도 session_state에 저장
    if 'selected_sido' not in st.session_state or st.session_state.selected_sido != selected_sido:
        st.session_state.selected_sido = selected_sido

    # 시군구 선택 selectedbox
    selected_sigungu = st.selectbox('시군구를 선택하세요.', sigungu_dict[0][selected_sido], index=1)
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


# ==============================================================================
# 데이터 수집 버튼
# ==============================================================================
st.subheader("데이터 수집")
if st.button("데이터 수집"):
    with st.spinner('잠시만 기다려주세요. 데이터를 불러오는 중입니다...⏳'):
        # time.sleep(10)
        # st.success('데이터 수집완료')
        # '광역시'가 포함된 시군구명만 dict로 만들기
        gwangyeok_dict = {sido: list(st.session_state.sigungu_dict[sido].values())[0][:2]
                          for sido in filter(lambda x: '광역시' in x, st.session_state.sigungu_dict)}
        code = AgePopulationAnalysis(gwangyeok_dict=gwangyeok_dict)
        st.write(code.get_age_population_data())

# ==============================================================================
# 입지평가 기준
# ==============================================================================
st.subheader("입지 평가 기준")
# 수도권 기준
data_sudo = {
    ('직장', '종사자 수'): ['30만명 이상', '20만명 이상', '10만명 이상', '10만명 미만'],
    ('교통', '강남 및 업무지구 접근성'): ['강남 30분 이하', '강남 1시간, 부도심 30분 이하', '부도심 1시간 이하', '그 외'],
    ('학군', '학업 성취도'): ['95% 3개 이상', '90% 5개 이상', '85% 5개 이상', '85% 5개 미만'],
    ('환경', '편의시설'): ['1km 이내 백화점 2개 이상', '1km 이내 백화점 1개 이상', '1km 이내 대형마트', '편의시설 없음'],
    ('공급', '3년간 공급물량'): ['인구수 × 0.25% 이하', '인구수 × 0.5% 이하', '인구수 × 1% 이하', '인구수 × 1% 초과'],
}
df_sudo = pd.DataFrame(data_sudo, index= ['S등급', 'A등급', 'B등급', 'C등급'])
st.write("수도권('구' 단위)"),
st.dataframe(df_sudo, use_container_width=True)
# 지방_시 기준
data_jibangsi = {
    ('인구', '인구 수'): ['300만명 이상', '200만명 이상', '100만명 이상', '50만명 이상'],
    ('직장', '종사자 수'): ['30만명 이상', '20만명 이상', '10만명 이상', '10만명 미만'],
    ('학군', '학업 성취도'): ['95% 3개 이상', '90% 5개 이상', '85% 5개 이상', '85% 5개 미만'],
    ('환경', '편의시설'): ['백화점 5개 이상', '백화점 3개 이상', '백화점 2개 이상', '백화점 2개 미만'],
    ('공급', '3년간 공급물량'): ['인구수 × 0.25% 이하', '인구수 × 0.5% 이하', '인구수 × 1% 이하', '인구수 × 1% 초과'],
    ('기타', '교통 등'): ['', '교통', '호재', ''],
}
df_jibansi = pd.DataFrame(data_sudo, index= ['S등급', 'A등급', 'B등급', 'C등급'])
st.write("지방('시' 단위)"),
st.dataframe(df_jibansi, use_container_width=True)
# 지방_시군구 기준
data_jibangsigungu = {
    ('인구', '인구 수'): ['30만명 이상', '20만명 이상', '10만명 이상', '10만명 미만'],
    ('직장', '종사자 수'): ['30만명 이상', '20만명 이상', '10만명 이상', '10만명 미만'],
    ('학군', '학업 성취도'): ['95% 3개 이상', '90% 5개 이상', '85% 5개 이상', '85% 5개 미만'],
    ('환경', '편의시설'): ['1km 이내 백화점 2개 이상', '1km 이내 백화점 1개 이상', '1km 이내 대형마트', '편의시설 없음'],
    ('공급', '3년간 공급물량'): ['인구수 × 0.25% 이하', '인구수 × 0.5% 이하', '인구수 × 1% 이하', '인구수 × 1% 초과'],
    ('교통', '업무지구 접근성'): ['자차 15분 이내', '자차 30분 이내', '자차 40분 이내', '자차 40분 이상'],
}
df_jibangsigungu = pd.DataFrame(data_jibangsigungu, index= ['S등급', 'A등급', 'B등급', 'C등급'])
st.write("지방('구' 단위)"),
st.dataframe(df_jibangsigungu, use_container_width=True)

