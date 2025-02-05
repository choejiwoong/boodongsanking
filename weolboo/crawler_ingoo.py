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

    def get_latest_year(self, orgId, tblId):
        # 가장 최신 수록 년도 추출
        df_update = self.api.get_data(
            "통계표설명",
            "자료갱신일",
            orgId=orgId,
            tblId=tblId,
        )
        df_update_grouped = df_update.groupby(by=['수록주기']).agg({"수록시점": ["min", "max"]})
        max_year = df_update_grouped.loc['년', ('수록시점', 'max')]
        return max_year

    # 행정구역(읍면동)별/5세별 주민등록인구(2011년~)
    def get_age_population_data(self):
        data = []  # 광역시명, 연령대, 수치값을 저장할 리스트
        orgId = "101"  # 기관ID
        tblId = "DT_1B04005N"  # 통계표ID
        itmId = "T2"  # 총인구수 항목
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
                        objL1=gwangyeok_code,
                        objL2=str(objL2_value),
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
                         title="시군구별 연령별 인구 분포",
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

    # 특정 도시 시군구별 연령대별 인구수
    def process_population_data(self):
        max_year = self.get_latest_year("101", "DT_1B04005N")
        for sigungu, code in self.sigungu_dict.items():
            if sigungu not in self.population_dict:
                self.population_dict[sigungu] = {}
            for objL2_value in range(0, 106, 5):
                if objL2_value == 0:
                    age_group = "전체"
                else:
                    age_group = f"{objL2_value - 5} - {objL2_value - 1}세"
                df = self.get_age_population_data(code, objL2_value, max_year)
                if df is None:
                    continue
                else:
                    pv = df.pivot(index=["분류값ID1", "분류값명1", "수록시점"], columns=["항목명"], values="수치값")
                    pv.columns.name = None
                    pv["총인구수"] = pd.to_numeric(pv["총인구수"])
                    # 나이대별 인구수 업데이트
                    self.population_dict[sigungu][age_group] = float(pv["총인구수"].iloc[0])
                    print(pv["총인구수"])

    def get_population_data(self):
        print(self.population_dict)
        # 데이터를 DataFrame 형태로 반환
        return pd.DataFrame(data=self.population_dict)


# 용례
# sido_name = "부산광역시"
# sigungu_name = "연제구"

# code = AgePopulationAnalysis()
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
