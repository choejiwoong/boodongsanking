import PublicDataReader as pdr
import streamlit
from PublicDataReader import Kosis
import pandas as pd
from crawler_sigungu import *
from datetime import datetime
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

class AgePopulationAnalysis:
    def __init__(self, service_key: str = "YWZhOWE3ZjgxYzY0YThkYWRmMDgyYzQzZDZjMjM2NTk=", gwangyeok_dict: dict = None, sigungu_dict: dict = None, hdong_dict: dict = None):
        # 시군구 이름과 KOSIS 서비스 키를 받아서 초기화
        self.service_key = service_key
        self.gwangyeok_dict = gwangyeok_dict
        self.sigungu_dict = sigungu_dict
        self.hdong_dict = hdong_dict
        # KOSIS 인스턴스 생성
        self.api = Kosis(service_key)
        # 인구관련 정보 담는 dict
        self.population_dict = {}

    # ==============================================================================
    # 가장 최신 수록연도 추출
    # ==============================================================================
    def get_latest_year(self, orgId, tblId):
        df_update = self.api.get_data(
            "통계표설명",
            "자료갱신일",
            orgId=orgId,
            tblId=tblId,
        )
        df_update_grouped = df_update.groupby(by=['수록주기']).agg({"수록시점": ["min", "max"]})
        max_year = df_update_grouped.loc['년', ('수록시점', 'max')]
        return max_year

    # ==============================================================================
    # 광역시별 / 시도 시군구 읍면동별 연령별 비중: 행정구역(읍면동)별/5세별 주민등록인구(2011년~)
    # ==============================================================================
    def get_age_population_data(self):
        data = []  # 광역시명, 연령대, 수치값을 저장할 리스트
        orgId = "101"  # 기관ID
        tblId = "DT_1B04005N"  # 통계표ID
        itmId = "T2"  # 항목ID: 총인구수 항목
        prdSe = "Y"  # 수록주기
        max_year = self.get_latest_year(orgId, tblId)
        # 연령대 매핑 함수 (10세 단위로 그룹화)
        def get_age_group(value):
            if value == 0:
                return '전체'
            elif value >= 60:
                return '60세+'
            else:
                lower_bound = (value - 5) // 10 * 10
                upper_bound = lower_bound + 9
                return f'{lower_bound}-{upper_bound}세'
        for objL2_value in range(0, 110, 5):  # 0부터 105까지 5세 간격
            if self.gwangyeok_dict:
                for gwangyeok_name, gwangyeok_code in self.gwangyeok_dict.items():
                    df = self.api.get_data(
                        "통계자료",
                        orgId=orgId,
                        tblId=tblId,
                        objL1=gwangyeok_code, # 분류값ID1
                        objL2=str(objL2_value), # 분류값ID2
                        itmId=itmId,
                        prdSe=prdSe,
                        startPrdDe=max_year,
                        endPrdDe=max_year,
                    )
                    if df is not None and not df.empty:
                        value = df['수치값'].sum()
                        data.append({
                            '구분': gwangyeok_name,
                            '연령대': get_age_group(objL2_value),
                            '연령대숫자': objL2_value,
                            '수치값': value
                        })
            if self.hdong_dict:
                for hdong_name, hdong_code in self.hdong_dict.items():
                    df = self.api.get_data(
                        "통계자료",
                        orgId=orgId,
                        tblId=tblId,
                        objL1=hdong_code,
                        objL2=str(objL2_value),
                        itmId=itmId,
                        prdSe=prdSe,
                        startPrdDe=max_year,
                        endPrdDe=max_year,
                    )
                    if df is not None and not df.empty:
                        value = df['수치값'].sum()
                        data.append({
                            '구분': hdong_name,
                            '연령대': get_age_group(objL2_value),
                            '연령대숫자': objL2_value,
                            '수치값': value
                        })
        # 데이터가 없는 경우 대비
        if not data:
            print("⚠️ 결과 데이터가 없습니다. API 응답을 확인하세요.")
            return pd.DataFrame()
        # 데이터프레임 생성 후 10세 단위로 그룹화 및 피벗
        result_df = pd.DataFrame(data)
        result_df['수치값'] = pd.to_numeric(result_df['수치값'], errors='coerce')
        # 10세 단위로 그룹화하여 합산
        grouped_df = result_df.groupby(['구분', '연령대']).agg({'수치값': 'sum'}).reset_index()
        # 연령대 기준으로 피벗 테이블 생성
        pivot_df = grouped_df.pivot_table(index='구분', columns='연령대', values='수치값', aggfunc='sum').reset_index()
        pivot_df.set_index('구분', inplace=True)
        pivot_df = pivot_df.apply(pd.to_numeric, errors='coerce')
        # 결과 출력
        print(pivot_df)
        return pivot_df

    # ==============================================================================
    # 광역시별 / 시도 시군구 읍면동별 연령별 비중 그래프 그리기
    # ==============================================================================
    def get_age_population_plotly(self, df):
        # 각 연령대별 인구수를 전체 인구수로 나누어 비율(%)로 변환
        # df.set_index('구분', inplace=True)
        # df = df.apply(pd.to_numeric, errors='coerce')
        df_ratio = df.div(df['전체'], axis=0) * 100
        # 경제활동인구
        df_active = df_ratio['0-9세'] + df_ratio['10-19세'] + df_ratio['30-39세'] + df_ratio['40-49세'] + df_ratio['50-59세']
        df_ratio.drop(columns=['전체'], inplace=True)
        # 연령대별 색상 매핑
        color_map = px.colors.qualitative.Pastel1  # 또는 Pastel2
        # Streamlit에서 DataFrame 출력
        if not df_ratio.empty:
            # 시군구별 누적 막대 그래프 그리기
            fig = px.bar(df_ratio,
                         x=df_ratio.index,
                         y=df_ratio.columns,
                         labels={"value": "인구 비율(%)", "variable": "연령대"},
                         color_discrete_map={col: color_map[i] for i, col in enumerate(df_ratio.columns)},
                         # text=flattened_text,  # Use flattened text values
                         barmode='stack')
            # # 텍스트 위치 조정
            # fig.update_traces(textposition='inside')
            # 경제활동인구 값을 Scatter로 추가
            scatter_trace = go.Scatter(
                x=df_ratio.index,
                y=df_active,  # 경제활동인구 값
                mode='lines+markers',
                name='경제활동인구',
                line=dict(color='black', dash='dot'),
                text=df_active.round(1),
                textposition='top center'
            )
            # 그래프에 Scatter trace 추가
            fig.add_trace(scatter_trace)
            # 그래프 표시
            return fig
        else:
            st.write("데이터를 가져올 수 없습니다.")
            return None


    # ============================================================================================================================================================
    # 광역시별 / 시군구별 / 시도 시군구 읍면동별 총인구수, 세대수, 세대당 인구: 행정구역(시군구)별 주민등록세대수
    # ============================================================================================================================================================
    # 특정 도시 시군구별 세대수
    def get_population_data(self):
        data = []  # 광역시명, 연령대, 수치값을 저장할 리스트
        orgId = "101"  # 기관ID
        tblId = "DT_1B040B3"  # 통계표ID
        itmId = "T2"  # 총인구수 항목
        prdSe = "Y"  # 수록주기
        max_year = self.get_latest_year(orgId, tblId)
        # df = self.api.get_data(
        #     "KOSIS통합검색",
        #     searchNm="주민등록 세대수"
        # )
        # print(df.head(1))

        item = self.api.get_data(
            "통계표설명",
            "분류항목",
            orgId=orgId,
            tblId=tblId,
        )
        print(item)

        # # 예시: 통계자료 요청 수정 / 참고: https://www.kosis.kr/openapi/devGuide/devGuide_0201List.do
        # df = self.api.get_data(
        #     service_name="통계자료",  # 서비스명: '통계자료'로 수정
        #     orgId="101",  # 기관 ID: '101'은 해당 통계를 제공하는 기관 ID
        #     tblId="DT_1B040B3",  # 통계표 ID: 통계표 ID는 실제 통계 표에 해당하는 고유 ID (예: 'DT_1B040B3')
        #     objL1="11110",  # 분류값 ID 1: 'A'는 행정구역별 통계 자료를 요청하는 항목
        #     itmId="ITEM",  # 항목 ID: 'T1'은 세대수와 관련된 항목
        #     prdSe="Y",  # 수록주기: 'Y'는 연간 기준 데이터 요청
        #     startPrdDe="2022",  # 시작 기간: '202211'은 2022년 11월
        #     endPrdDe="2022",  # 종료 기간: 동일한 2022년 11월
        # )
        # print(df)

    # def get_population_data(self):
    #     print(self.population_dict)
    #     # 데이터를 DataFrame 형태로 반환
    #     return pd.DataFrame(data=self.population_dict)


# 용례
# 최대 출력할 행 수와 열 수 설정
pd.set_option('display.max_rows', None)  # 모든 행 출력
pd.set_option('display.max_columns', None)  # 모든 열 출력
pd.set_option('display.width', None)  # 출력 너비 제한 없애기
pd.set_option('display.max_colwidth', None)  # 열의 최대 너비를 제한하지 않음
# sido_name = "부산광역시"
# sigungu_name = "연제구"

code = AgePopulationAnalysis()
#
# print(code.get_age_population_data(0,))
# code = SigunguCode(sido_name, sigungu_name)
# code.load_sigungu_name()
# code.load_gwangyeok()
# code.load_sigungu()
# code.load_hdong()
# print(code.get_sigungu_name_dict())
# print(code.get_gwangyeok_dict())
# print(code.get_sigungu_dict())
# print(code.get_hdong_dict())

code.get_population_data()
