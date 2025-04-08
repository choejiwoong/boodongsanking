import streamlit as st
import pandas as pd
import numpy as np
from click import style
from streamlit_db import *

from crawler_ingoo import *
from crawler_sigungu import *
from streamlit_db import *
from bson import ObjectId
from crawler_hakgun import *
from crawler_hwangyeong import *
from crawler_gyotong import *
from crawler_jikjang import *
import pymongo

# ==============================================================================
# 페이지 기본 설정
# ==============================================================================
st.set_page_config(
    page_icon="💡",
    page_title="부동산 임장보고서",
    layout="wide",
)
st.header("💡 부동산 임장보고서")

# ==============================================================================
# 시군구명 selectbox data mongodb에서 불러오기
# ==============================================================================
# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    return pymongo.MongoClient(st.secrets["mongo"]["uri"])

client = init_connection()
st.session_state.client = client

# 데이터가 있으면 시군구 구분 선택할 수 있는 콤보박스 현시
collection = connect_to_mongodb(db_name='db', collection_name='sigungu')
if get_all_documents(collection):
    sigunguhdong_dict = collection.find_one({}, {"_id": 0})
    # sigungu_dict session_state에 저장
    st.session_state.sigunguhdong_dict = sigunguhdong_dict
    # 도시 선택 selectedbox
    selected_sido = st.selectbox('도시를 선택하세요.', list(sigunguhdong_dict.keys()), index=1)
    # 선택된 시도 session_state에 저장
    st.session_state.selected_sido = selected_sido
    # 시군구 선택 selectedbox
    selected_gungu = st.selectbox('시군구를 선택하세요.', sigunguhdong_dict[selected_sido].keys())
    # 선택된 시군구 session_state에 저장
    st.session_state.selected_gungu = selected_gungu

# ==============================================================================
# 데이터 수집 버튼
# ==============================================================================
if st.button("😊 인구 데이터 수집", use_container_width=True):
    with st.spinner('잠시만 기다려주세요. 데이터를 불러오는 중입니다...⏳'):
        if st.session_state.selected_gungu != '전체':
            # 선택된 시군구
            selected_sido = st.session_state.selected_sido
            selected_gungu = st.session_state.selected_gungu
            # 연령별 비중 empty dataframe
            df_age_sido = pd.DataFrame()
            df_age_gungu = pd.DataFrame()
            df_age_hdong = pd.DataFrame()
            # 세대당 인구 수 empty dataframe
            df_sido = pd.DataFrame()
            df_gungu = pd.DataFrame()
            df_hdong = pd.DataFrame()
            # 저장된 시군구 정보
            sigunguhdong_dict = st.session_state.sigunguhdong_dict
            # 인스턴스화
            ingoo = Ingoo()
            # 시도 데이터 가져오기
            for sido_name, sido_dict in sigunguhdong_dict.items():
                # 연령별 비중 데이터
                ingoo.get_age_population_data(sido_name, sido_dict, df_age_sido, 'sido')
                # 세대당 인구 수 데이터
                ingoo.get_population_data(sido_name, sido_dict, df_sido, 'sido')
            # 시군구 데이터 가져오기
            for gungu_name, gungu_dict in sigunguhdong_dict[selected_sido].items():
                if gungu_name == "전체":
                    continue
                # 연령별 비중 데이터
                ingoo.get_age_population_data(gungu_name, gungu_dict, df_age_gungu, 'gungu')
                # 세대당 인구 수 데이터
                ingoo.get_population_data(gungu_name, gungu_dict, df_gungu, 'gungu')
            # 행정동 데이터 가져오기
            for hdong_name, hdong_code in sigunguhdong_dict[selected_sido][selected_gungu].items():
                if hdong_name == "전체":
                    continue
                # 연령별 비중 데이터
                ingoo.get_age_population_data(hdong_name, hdong_code, df_age_hdong,'hdong')
                # # 세대당 인구 수 데이터
                # ingoo.get_population_data(hdong_name, hdong_code, df_hdong, 'hdong')

            # ==============================================================================
            # 시도 시군구 읍면동별 연령별 비중: 행정구역(읍면동)별/5세별 주민등록인구(2011년~)
            # ==============================================================================
            # format 바꾸기
            df_age_sido = df_age_sido.apply(pd.to_numeric, errors='coerce').astype('Int64')
            df_age_gungu = df_age_gungu.apply(pd.to_numeric, errors='coerce').astype('Int64')
            df_age_hdong = df_age_hdong.apply(pd.to_numeric, errors='coerce').astype('Int64')
            # 경제활동인구 열 추가
            df_age_sido['경제활동인구'] = df_age_sido['0-9세'] + df_age_sido['10-19세'] + df_age_sido['30-39세'] + df_age_sido['40-49세'] + df_age_sido['50-59세']
            df_age_gungu['경제활동인구'] = df_age_gungu['0-9세'] + df_age_gungu['10-19세'] + df_age_gungu['30-39세'] + df_age_gungu['40-49세'] + df_age_gungu['50-59세']
            df_age_hdong['경제활동인구'] = df_age_hdong['0-9세'] + df_age_hdong['10-19세'] + df_age_hdong['30-39세'] + df_age_hdong['40-49세'] + df_age_hdong['50-59세']
            # 경제활동인구비율 열 추가
            df_age_sido['경제활동인구비율'] = (df_age_sido['경제활동인구']/df_age_sido['전체']*100).round(1)
            df_age_gungu['경제활동인구비율'] = (df_age_gungu['경제활동인구']/df_age_gungu['전체']*100).round(1)
            df_age_hdong['경제활동인구비율'] = (df_age_hdong['경제활동인구']/df_age_hdong['전체']*100).round(1)
            # session_state 에 저장하기
            st.session_state.df_age_sido = df_age_sido
            st.session_state.df_age_gungu = df_age_gungu
            st.session_state.df_age_hdong = df_age_hdong
            ### 그래프 그리기
            st.session_state.get_age_population_plotly_sido = ingoo.get_age_population_plotly(df_age_sido)
            st.session_state.get_age_population_plotly_gungu = ingoo.get_age_population_plotly(df_age_gungu)
            st.session_state.get_age_population_plotly_hdong = ingoo.get_age_population_plotly(df_age_hdong)
            # ==============================================================================
            # 시도 시군구 읍면동별 총인구수, 세대수, 세대당 인구: 행정구역(시군구)별 주민등록세대수
            # ==============================================================================
            # 총 인구수 열 추가
            df_sido["총인구수"] = df_age_sido['전체']
            df_gungu["총인구수"] = df_age_gungu['전체']
            # df_hdong["총인구수"] = df_age_hdong['전체']
            # format 바꾸기
            df_sido["총인구수"] = pd.to_numeric(df_sido["총인구수"], errors='coerce').astype('Int64')
            df_sido["세대수"] = pd.to_numeric(df_sido["세대수"], errors='coerce').astype('Int64')
            df_sido['세대당 인구수'] = (df_sido["총인구수"] / df_sido['세대수']).round(2)
            df_gungu["총인구수"] = pd.to_numeric(df_gungu["총인구수"], errors='coerce').astype('Int64')
            df_gungu["세대수"] = pd.to_numeric(df_gungu["세대수"], errors='coerce').astype('Int64')
            df_gungu['세대당 인구수'] = (df_gungu["총인구수"] / df_gungu['세대수']).round(2)
            # df_hdong["총인구수"] = pd.to_numeric(df_hdong["총인구수"], errors='coerce').astype('Int64')
            # df_hdong["세대수"] = pd.to_numeric(df_hdong["세대수"], errors='coerce').astype('Int64')
            # df_hdong['세대당 인구수'] = (df_age_hdong['전체'] / df_hdong['세대수']).round(2)
            # session_state 에 저장하기
            st.session_state.df_sido = df_sido
            st.session_state.df_gungu = df_gungu
            # st.session_state.df_hdong = df_hdong
            ### 그래프 그리기
            st.session_state.get_population_plotly_sido = ingoo.get_population_plotly(df_sido)
            st.session_state.get_population_plotly_gungu = ingoo.get_population_plotly(df_gungu)
            # st.session_state.get_population_plotly_hdong = ingoo.get_population_plotly(df_hdong)
            # 성공 메시지
            st.success('😊_1. 인구 데이터 불러오기 완료')
        else:
            # 에러 메시지
            st.error('☢ 시군구명을 선택해주세요!')

#### 2025/04/08 여기서 부터 하기~~~~~~~
# ==============================================================================
# 직장 데이터 수집 버튼
# ==============================================================================
# if st.button("🏙 직장 데이터 수집", use_container_width=True):
#     with st.spinner('잠시만 기다려주세요. 데이터를 불러오는 중입니다...⏳'):
#         if selected_gungu != '전체':
#             # 직장 관련 인스턴스 생성
#             # 광역시
#             fetcher = KosisDataFetcher(gwangyeok_dict=gwangyeok_dict)
#             st.session_state.jikjang_gwangyeok_df = fetcher.fetch_and_process_data()
#             st.session_state.jikjang_gwangyeok_industry_df = fetcher.fetch_and_process_industry_data()
#             # print(st.session_state.jikjang_gwangyeok_industry_df)
#             # st.session_state.jikjang_gwangyeok_industry_plotly = fetcher.get_plotly(st.session_state.jikjang_gwangyeok_industry_df)
#             st.session_state.jikjang_income_gwangyeok = fetcher.get_income()
#             # 시군구
#             sigungu_dict = st.session_state.sigungu_dict[selected_sido]
#             sigungu_dict_filtered = {key: value['전체'] for key, value in sigungu_dict.items() if isinstance(value, dict)}
#             fetcher = KosisDataFetcher(sigungu_dict=sigungu_dict_filtered, selected_sido=st.session_state.selected_sido)
#             st.session_state.jikjang_sigungu_df = fetcher.fetch_and_process_data()
#             st.session_state.jikjang_sigungu_industry_df = fetcher.fetch_and_process_industry_data()
#             # st.session_state.jikjang_sigungu_industry_plotly = fetcher.get_plotly(st.session_state.jikjang_sigungu_industry_df)
#             st.session_state.jikjang_income_sigungu = fetcher.get_income()
#             st.session_state.jikjang_bjoong_sigungu = fetcher.get_bjoong()
#
#             st.success('🏙_2. 직장 데이터 불러오기 완료')
#         else:
#             st.error('☢ 시군구명을 선택해주세요!')
# ==============================================================================
# 학군 데이터 수집 버튼
# ==============================================================================
# if st.button("🎓 학군 데이터 수집", use_container_width=True):
#     with st.spinner('잠시만 기다려주세요. 데이터를 불러오는 중입니다...⏳'):
#         if selected_gungu != '전체':
#             # 학업성취도 관련 인스턴스 생성
#             school_achievement = SchoolAchievement(selected_sido, selected_gungu, gwangyeok_dict, st.session_state.sigungu_dict)
#             # 중학교 학업성취도 관련 크롤링
#             st.session_state.fetch_mid_school_achievement = school_achievement.fetch_school_achievement("3")
#             filtered_data = [item for item in st.session_state.fetch_mid_school_achievement if item['구분'] == selected_gungu]
#             st.session_state.mid_school_achievement_ranking = school_achievement.calculate_ranking(filtered_data)
#             # 고등학교 학업성취도 관련 크롤링
#             st.session_state.fetch_high_school_achievement = school_achievement.fetch_school_achievement("4")
#
#             # 초등학교 관련 인스턴스 생성
#             region_code = st.session_state.sigungu_dict[selected_sido][selected_gungu]["전체"][:5]
#             school_info_api = SchoolInfoAPI(region_code)
#             # 데이터 크롤링
#             elem_school_data = school_info_api.fetch_elem_school_data()
#             # 데이터 처리
#             st.session_state.process_school_info_data = school_info_api.process_school_info_data(elem_school_data)
#             st.success('🎓_3. 학군 데이터 불러오기 완료')
#         else:
#             st.error('☢ 시군구명을 선택해주세요!')
# ==============================================================================
# 환경 데이터 수집 버튼
# ==============================================================================
if st.button("🏖 환경 데이터 수집", use_container_width=True):
    with st.spinner('잠시만 기다려주세요. 데이터를 불러오는 중입니다...⏳'):
        if selected_gungu != '전체':
            # 환경 관련 인스턴스 생성
            place_seacher = PlaceSearcher()
            # 환경 관련 크롤링
            sigungu_names = list(st.session_state.sigungu_dict[selected_sido].keys())  # sigungu_names 리스트 생성
            sigungu_names = [name for name in sigungu_names if name != '전체']  # "전체" 제외
            final_df, all_places_df = place_seacher.get_results_for_sgg(selected_sido, sigungu_names)
            st.session_state.hwangyeong_tuple = final_df, all_places_df
            st.session_state.hwangyeong_ranking = place_seacher.calculate_ranking(final_df, selected_gungu)
            st.success('🏖_4. 환경 데이터 불러오기 완료')
        else:
            st.error('☢ 시군구명을 선택해주세요!')
# ==============================================================================
# 교통 데이터 수집 버튼
# ==============================================================================
if st.button("🚇 교통 데이터 수집", use_container_width=True):
    with st.spinner('잠시만 기다려주세요. 데이터를 불러오는 중입니다...⏳'):
        if selected_gungu != '전체':
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

