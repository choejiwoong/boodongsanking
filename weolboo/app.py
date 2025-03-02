import streamlit as st
import pandas as pd
import numpy as np
from click import style

from crawler_ingoo import *
from crawler_sigungu import *
from streamlit_db import *
from bson import ObjectId
from crawler_hakgun import *
from crawler_hwangyeong import *
from crawler_gyotong import *
from crawler_jikjang import *

# ==============================================================================
# 페이지 기본 설정
# ==============================================================================
st.set_page_config(
    page_icon="💡",
    page_title="부동산 임장보고서",
    layout="wide",
)
st.header("💡 부동산 임장보고서")
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
    selected_sigungu = st.selectbox('시군구를 선택하세요.', sigungu_dict[0][selected_sido].keys())
    # 선택된 시군구 session_state에 저장
    if 'selected_sigungu' not in st.session_state or st.session_state.selected_sigungu != selected_sigungu:
        st.session_state.selected_sigungu = selected_sigungu
    # print(st.session_state.sigungu_dict[selected_sido].keys())

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
# '광역시'가 포함된 시군구명만 dict로 만들기
gwangyeok_dict = {
    sido: sigungu_dict["전체"][:2]  # '전체' 키의 값을 가져옴
    for sido, sigungu_dict in st.session_state.sigungu_dict.items()
    if "광역시" in sido and "전체" in sigungu_dict  # '광역시' 포함 + '전체' 키가 있는 경우만
}


if st.button("😊 인구 데이터 수집", use_container_width=True):
    with st.spinner('잠시만 기다려주세요. 데이터를 불러오는 중입니다...⏳'):
        if selected_sigungu != '전체':
            # ==============================================================================
            # 광역시별 인구 데이터
            # ==============================================================================
            code_gwangyeok = AgePopulationAnalysis(gwangyeok_dict=gwangyeok_dict)
            get_age_population_data_gwangyeok = code_gwangyeok.get_age_population_data()
            st.session_state.get_age_population_data_gwangyeok = get_age_population_data_gwangyeok
            # 세대수
            get_population_data_gwangyeok = code_gwangyeok.get_population_data()
            st.session_state.get_population_data_gwangyeok = get_population_data_gwangyeok
            result_df = get_age_population_data_gwangyeok[['전체']].copy()  # '전체' 열만 가져오고 복사
            result_df = result_df.rename(columns={'전체': '총인구수'})  # '전체' 열을 '총인구수'로 변경
            result_df['세대수'] = get_population_data_gwangyeok['수치값']  # '세대수' 열 추가
            result_df['세대당 인구수'] = result_df['총인구수'] / result_df['세대수']  # '총인구수'를 '세대수'으로 나눈 새로운 열 추가
            st.session_state.pop_div_saedae_hdong = result_df
            st.session_state.get_population_plotly_gwangyeok = code_gwangyeok.get_population_plotly(result_df)
            st.session_state.get_age_population_plotly_gwangyeok = code_gwangyeok.get_age_population_plotly(get_age_population_data_gwangyeok)
            st.success('😊_1. 인구/광역시별 인구 데이터 불러오기 완료')
            # ==============================================================================
            # 시군구별 인구 데이터
            # ==============================================================================
            sigungu_dict = st.session_state.sigungu_dict[selected_sido]
            sigungu_dict_filtered = {key: value['전체'] for key, value in sigungu_dict.items() if isinstance(value, dict)}
            code_sigungu = AgePopulationAnalysis(sigungu_dict=sigungu_dict_filtered)
            get_age_population_data_sigungu = code_sigungu.get_age_population_data()
            st.session_state.get_age_population_data_sigungu = get_age_population_data_sigungu
            # 세대수
            get_population_data_sigungu = code_sigungu.get_population_data()
            st.session_state.get_population_data_sigungu = get_population_data_sigungu

            result_df = get_age_population_data_sigungu[['전체']].copy()  # '전체' 열만 가져오고 복사
            result_df = result_df.rename(columns={'전체': '총인구수'})  # '전체' 열을 '총인구수'로 변경
            result_df['세대수'] = get_population_data_sigungu['수치값']  # '세대수' 열 추가
            result_df['세대당 인구수'] = result_df['총인구수'] / result_df['세대수']  # '총인구수'를 '세대수'으로 나눈 새로운 열 추가
            st.session_state.pop_div_saedae_sigungu = result_df
            st.session_state.get_population_plotly_sigungu = code_sigungu.get_population_plotly(result_df)
            st.session_state.get_age_population_plotly_sigungu = code_sigungu.get_age_population_plotly(get_age_population_data_sigungu)
            st.success('😊_1. 인구/시군구별 인구 데이터 불러오기 완료')
            # ==============================================================================
            # 행정동별 인구 데이터
            # ==============================================================================
            selected_sido = st.session_state.selected_sido
            selected_sigungu = st.session_state.selected_sigungu
            hdong_dict = st.session_state.sigungu_dict[selected_sido][selected_sigungu]
            code_hdong = AgePopulationAnalysis(hdong_dict=hdong_dict)
            get_age_population_data_hdong = code_hdong.get_age_population_data()
            st.session_state.get_age_population_data_hdong = get_age_population_data_hdong
            st.session_state.get_age_population_plotly_hdong = code_hdong.get_age_population_plotly(get_age_population_data_hdong)
            # # 세대수
            # get_population_data_hdong = code_hdong.get_population_data()
            # result_df = get_age_population_data_hdong[['전체']].copy()  # '전체' 열만 가져오고 복사
            # result_df = result_df.rename(columns={'전체': '총인구수'})  # '전체' 열을 '총인구수'로 변경
            # result_df['세대수'] = get_population_data_hdong['수치값']  # '세대수' 열 추가
            # result_df['세대당 인구수'] = result_df['총인구수'] / result_df['세대수']  # '총인구수'를 '세대수'으로 나눈 새로운 열 추가
            # st.session_state.pop_div_saedae_hdong = result_df
            # st.session_state.get_population_plotly_hdong = code_hdong.get_population_plotly(result_df)
            st.success('😊_1. 인구/행정동별 인구 데이터 불러오기 완료')


            ############ test
            # # 직장 관련 인스턴스 생성
            # # 광역시
            # fetcher = KosisDataFetcher(gwangyeok_dict=gwangyeok_dict)
            # st.session_state.jikjang_gwangyeok_df = fetcher.fetch_and_process_data()
            # # 시군구
            # sigungu_dict = st.session_state.sigungu_dict[selected_sido]
            # sigungu_dict_filtered = {key: value['전체'] for key, value in sigungu_dict.items() if isinstance(value, dict)}
            # fetcher = KosisDataFetcher(sigungu_dict=sigungu_dict_filtered, selected_sido=st.session_state.selected_sido)
            # st.session_state.jikjang_sigungu_df = fetcher.fetch_and_process_data()
            # st.success('🏙_2. 직장 데이터 불러오기 완료')
        else:
            st.error('☢ 시군구명을 선택해주세요!')
# ==============================================================================
# 직장 데이터 수집 버튼
# ==============================================================================
if st.button("🏙 직장 데이터 수집", use_container_width=True):
    with st.spinner('잠시만 기다려주세요. 데이터를 불러오는 중입니다...⏳'):
        if selected_sigungu != '전체':
            # 직장 관련 인스턴스 생성
            # 광역시
            fetcher = KosisDataFetcher(gwangyeok_dict=gwangyeok_dict)
            st.session_state.jikjang_gwangyeok_df = fetcher.fetch_and_process_data()
            # 시군구
            sigungu_dict = st.session_state.sigungu_dict[selected_sido]
            sigungu_dict_filtered = {key: value['전체'] for key, value in sigungu_dict.items() if isinstance(value, dict)}
            fetcher = KosisDataFetcher(sigungu_dict=sigungu_dict_filtered, selected_sido=st.session_state.selected_sido)
            st.session_state.jikjang_sigungu_df = fetcher.fetch_and_process_data()
            st.success('🏙_2. 직장 데이터 불러오기 완료')
        else:
            st.error('☢ 시군구명을 선택해주세요!')
# ==============================================================================
# 학군 데이터 수집 버튼
# ==============================================================================
if st.button("🎓 학군 데이터 수집", use_container_width=True):
    with st.spinner('잠시만 기다려주세요. 데이터를 불러오는 중입니다...⏳'):
        if selected_sigungu != '전체':
            # 학업성취도 관련 인스턴스 생성
            school_achievement = SchoolAchievement(selected_sido, selected_sigungu, gwangyeok_dict, st.session_state.sigungu_dict)
            # 중학교 학업성취도 관련 크롤링
            st.session_state.fetch_mid_school_achievement = school_achievement.fetch_school_achievement("3")
            filtered_data = [item for item in st.session_state.fetch_mid_school_achievement if item['구분'] == selected_sigungu]
            st.session_state.mid_school_achievement_ranking = school_achievement.calculate_ranking(filtered_data)
            # 고등학교 학업성취도 관련 크롤링
            st.session_state.fetch_high_school_achievement = school_achievement.fetch_school_achievement("4")

            # 초등학교 관련 인스턴스 생성
            region_code = st.session_state.sigungu_dict[selected_sido][selected_sigungu]["전체"][:5]
            school_info_api = SchoolInfoAPI(region_code)
            # 데이터 크롤링
            elem_school_data = school_info_api.fetch_elem_school_data()
            # 데이터 처리
            st.session_state.process_school_info_data = school_info_api.process_school_info_data(elem_school_data)
            st.success('🎓_3. 학군 데이터 불러오기 완료')
        else:
            st.error('☢ 시군구명을 선택해주세요!')
# ==============================================================================
# 환경 데이터 수집 버튼
# ==============================================================================
if st.button("🏖 환경 데이터 수집", use_container_width=True):
    with st.spinner('잠시만 기다려주세요. 데이터를 불러오는 중입니다...⏳'):
        if selected_sigungu != '전체':
            # 환경 관련 인스턴스 생성
            place_seacher = PlaceSearcher()
            # 환경 관련 크롤링
            sigungu_names = list(st.session_state.sigungu_dict[selected_sido].keys())  # sigungu_names 리스트 생성
            sigungu_names = [name for name in sigungu_names if name != '전체']  # "전체" 제외
            final_df, all_places_df = place_seacher.get_results_for_sgg(selected_sido, sigungu_names)
            st.session_state.hwangyeong_tuple = final_df, all_places_df
            st.session_state.hwangyeong_ranking = place_seacher.calculate_ranking(final_df, selected_sigungu)
            st.success('🏖_4. 환경 데이터 불러오기 완료')
        else:
            st.error('☢ 시군구명을 선택해주세요!')
# ==============================================================================
# 교통 데이터 수집 버튼
# ==============================================================================
if st.button("🚇 교통 데이터 수집", use_container_width=True):
    with st.spinner('잠시만 기다려주세요. 데이터를 불러오는 중입니다...⏳'):
        if selected_sigungu != '전체':
            # 교통 관련 인스턴스 생성
            gyotong = Gyotong()
            # 지하철 버스 수송분담률 관련 크롤링
            st.session_state.fetch_transport_data = gyotong.fetch_transport_data()
            st.session_state.get_transport_div_plotly = gyotong.get_transport_div_plotly(st.session_state.fetch_transport_data)

            # 지하철 교통 관련 크롤링
            api_metadata = gyotong.get_metadata()
            if api_metadata:
                latest_year, latest_endpoint = gyotong.find_latest_api(api_metadata)
                if latest_endpoint:
                    # 최신 데이터 가져오기
                    gyotong.fetch_data(latest_endpoint)
                    # 데이터 처리 및 집계
                    final_result = gyotong.process_data()

                    if final_result is not None:
                        st.session_state.gyotong_subway = final_result.head(20) # 상위 20개 데이터 출력
                    else:
                        st.error("처리된 데이터가 없습니다.")
                else:
                    st.error("최신 엔드포인트를 찾을 수 없습니다.")
            else:
                st.error("메타데이터를 가져올 수 없습니다.")
            st.success('🚇_6. 교통 데이터 불러오기 완료')
        else:
            st.error('☢ 시군구명을 선택해주세요!')

