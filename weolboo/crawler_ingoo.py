from PublicDataReader import Kosis
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_db import *



class Ingoo:
    def __init__(self, service_key: str = "YWZhOWE3ZjgxYzY0YThkYWRmMDgyYzQzZDZjMjM2NTk=", gwangyeok_dict: dict = None, sigungu_dict: dict = None, hdong_dict: dict = None):
        # 시군구 이름과 KOSIS 서비스 키를 받아서 초기화
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
    # 연령대 매핑 함수 (10세 단위로 그룹화)
    def get_age_group(self, value):
        if value == 0:
            return '전체'
        elif value >= 60:
            return '60세+'
        else:
            lower_bound = (value - 5) // 10 * 10
            upper_bound = lower_bound + 9
            return f'{lower_bound}-{upper_bound}세'

    def get_age_population_data(self, sigunguhdong_name, sigunguhdong_dict, df_save, sigunguhdong_type):
        """
        시군구 또는 행정동별 인구 데이터를 가져와서 df_age에 저장하는 함수
        :param sigunguhdong_name: 시도 또는 시군구 또는 행정동 이름
        :param sigunguhdong_dict: 해당 시군구/행정동의 코드 딕셔너리
        :param df_save: 데이터 저장할 DataFrame
        :param sigunguhdong_type: 'sido' 또는 'gungu' 또는 'hdong' (구분값)
        """

        sigunguhdong_code = (
            sigunguhdong_dict['전체'][:2] if sigunguhdong_type == 'sido' else
            sigunguhdong_dict['전체'][:5] if sigunguhdong_type == 'gungu' else
            sigunguhdong_dict[sigunguhdong_name]
        )
        max_year = self.get_latest_year("101", "DT_1B04005N")
        df = api.get_data(
            "통계자료",
            orgId="101",
            tblId="DT_1B04005N",
            objL1=sigunguhdong_code,  # 분류값ID1
            objL2='ALL',  # 모든 연령대 포함
            itmId="T2",  # 항목ID: 총인구수 항목
            prdSe="Y",  # 수록주기
            startPrdDe=max_year,
            endPrdDe=max_year,
        )

        for objL2_value in range(0, 110, 5):
            age_group = self.get_age_group(objL2_value)
            df_save.loc[sigunguhdong_name, age_group] = df[df['분류값ID2'].astype(int) == objL2_value]['수치값'].sum()

        return df_save

    # def get_age_population_data(self):
    #     data = []  # 광역시명, 연령대, 수치값을 저장할 리스트
    #     orgId = "101"  # 기관ID
    #     tblId = "DT_1B04005N"  # 통계표ID
    #     itmId = "T2"  # 항목ID: 총인구수 항목
    #     prdSe = "Y"  # 수록주기
    #     max_year = self.get_latest_year(orgId, tblId)
    #
    #     # 연령대 매핑 함수 (10세 단위로 그룹화)
    #     def get_age_group(value):
    #         if value == 0:
    #             return '전체'
    #         elif value >= 60:
    #             return '60세+'
    #         else:
    #             lower_bound = (value - 5) // 10 * 10
    #             upper_bound = lower_bound + 9
    #             return f'{lower_bound}-{upper_bound}세'
    #     for objL2_value in range(0, 110, 5):  # 0부터 105까지 5세 간격
    #         if self.gwangyeok_dict:
    #             for gwangyeok_name, gwangyeok_code in self.gwangyeok_dict.items():
    #                 df = self.api.get_data(
    #                     "통계자료",
    #                     orgId=orgId,
    #                     tblId=tblId,
    #                     objL1=gwangyeok_code, # 분류값ID1
    #                     objL2=str(objL2_value), # 분류값ID2
    #                     itmId=itmId,
    #                     prdSe=prdSe,
    #                     startPrdDe=max_year,
    #                     endPrdDe=max_year,
    #                 )
    #                 if df is not None and not df.empty:
    #                     value = df['수치값'].sum()
    #                     data.append({
    #                         '구분': gwangyeok_name,
    #                         '연령대': get_age_group(objL2_value),
    #                         '연령대숫자': objL2_value,
    #                         '수치값': value
    #                     })
    #         if self.sigungu_dict:
    #             for sigungu_name, sigungu_code in self.sigungu_dict.items():
    #                 df = self.api.get_data(
    #                     "통계자료",
    #                     orgId=orgId,
    #                     tblId=tblId,
    #                     objL1=sigungu_code[:5], # 분류값ID1
    #                     objL2=str(objL2_value), # 분류값ID2
    #                     itmId=itmId,
    #                     prdSe=prdSe,
    #                     startPrdDe=max_year,
    #                     endPrdDe=max_year,
    #                 )
    #                 if df is not None and not df.empty:
    #                     value = df['수치값'].sum()
    #                     data.append({
    #                         '구분': sigungu_name,
    #                         '연령대': get_age_group(objL2_value),
    #                         '연령대숫자': objL2_value,
    #                         '수치값': value
    #                     })
    #         if self.hdong_dict:
    #             for hdong_name, hdong_code in self.hdong_dict.items():
    #                 df = self.api.get_data(
    #                     "통계자료",
    #                     orgId=orgId,
    #                     tblId=tblId,
    #                     objL1=hdong_code,
    #                     objL2=str(objL2_value),
    #                     itmId=itmId,
    #                     prdSe=prdSe,
    #                     startPrdDe=max_year,
    #                     endPrdDe=max_year,
    #                 )
    #                 if df is not None and not df.empty:
    #                     value = df['수치값'].sum()
    #                     data.append({
    #                         '구분': hdong_name,
    #                         '연령대': get_age_group(objL2_value),
    #                         '연령대숫자': objL2_value,
    #                         '수치값': value
    #                     })
    #     # 데이터가 없는 경우 대비
    #     if not data:
    #         print("⚠️ 결과 데이터가 없습니다. API 응답을 확인하세요.")
    #         return pd.DataFrame()
    #     # 데이터프레임 생성 후 10세 단위로 그룹화 및 피벗
    #     result_df = pd.DataFrame(data)
    #     result_df['수치값'] = pd.to_numeric(result_df['수치값'], errors='coerce')
    #     # 10세 단위로 그룹화하여 합산
    #     grouped_df = result_df.groupby(['구분', '연령대']).agg({'수치값': 'sum'}).reset_index()
    #     # 연령대 기준으로 피벗 테이블 생성
    #     pivot_df = grouped_df.pivot_table(index='구분', columns='연령대', values='수치값', aggfunc='sum').reset_index()
    #     pivot_df.set_index('구분', inplace=True)
    #     pivot_df = pivot_df.apply(pd.to_numeric, errors='coerce')
    #     print(pivot_df)
    #     return pivot_df

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
            return None


    # ============================================================================================================================================================
    # 광역시별 / 시군구별 / 시도 시군구 읍면동별 총인구수, 세대수, 세대당 인구: 행정구역(시군구)별 주민등록세대수
    # ============================================================================================================================================================
    # 특정 도시 시군구별 세대수
    def get_population_data(self):
        data = []  # 광역시명, 연령대, 수치값을 저장할 리스트
        orgId = "101"  # 기관ID
        tblId = "DT_1B040B3"  # 통계표ID
        # objL1 = "26470" # 시군구 코드
        itmId = "ALL"  # 총인구수 항목
        prdSe = "Y"  # 수록주기
        max_year = self.get_latest_year(orgId, tblId)

        if self.gwangyeok_dict:
            for gwangyeok_name, gwangyeok_code in self.gwangyeok_dict.items():
                df = self.api.get_data(
                    service_name="통계자료",  # 서비스명: '통계자료'로 수정
                    orgId=orgId,  # 기관 ID: '101'은 해당 통계를 제공하는 기관 ID
                    tblId=tblId,  # 통계표 ID: 통계표 ID는 실제 통계 표에 해당하는 고유 ID (예: 'DT_1B040B3')
                    objL1=gwangyeok_code,  # 분류ID: 'A'는 행정구역별 통계 자료를 요청하는 항목
                    itmId=itmId,  # 분류값ID: 'T1'은 세대수와 관련된 항목
                    prdSe=prdSe,  # 수록주기: 'Y'는 연간 기준 데이터 요청
                    startPrdDe=max_year,  # 시작 기간: '202211'은 2022년 11월
                    endPrdDe=max_year,  # 종료 기간: 동일한 2022년 11월
                )
                if df is not None and not df.empty:
                    value = df['수치값'].sum()
                    data.append({
                        '구분': gwangyeok_name,
                        '수치값': value
                    })
        if self.sigungu_dict:
            for sigungu_name, sigungu_code in self.sigungu_dict.items():
                df = self.api.get_data(
                    service_name="통계자료",  # 서비스명: '통계자료'로 수정
                    orgId=orgId,  # 기관 ID: '101'은 해당 통계를 제공하는 기관 ID
                    tblId=tblId,  # 통계표 ID: 통계표 ID는 실제 통계 표에 해당하는 고유 ID (예: 'DT_1B040B3')
                    objL1=sigungu_code[:5],  # 분류ID: 'A'는 행정구역별 통계 자료를 요청하는 항목
                    itmId=itmId,  # 분류값ID: 'T1'은 세대수와 관련된 항목
                    prdSe=prdSe,  # 수록주기: 'Y'는 연간 기준 데이터 요청
                    startPrdDe=max_year,  # 시작 기간: '202211'은 2022년 11월
                    endPrdDe=max_year,  # 종료 기간: 동일한 2022년 11월
                )
                if df is not None and not df.empty:
                    value = df['수치값'].sum()
                    data.append({
                        '구분': sigungu_name,
                        '수치값': value
                    })
        ### 이부분은 원래 자료에 안들어가는듯...? 다른 자료를 불러와야 함
        # 여기 참고: https://kosis.kr/statHtml/statHtml.do?sso=ok&returnurl=https%3A%2F%2Fwww.kosis.kr%3A443%2FstatHtml%2FstatHtml.do%3Flist_id%3D202A_542_54201_B%26obj_var_id%3D%26seqNo%3D%26tblId%3DDT_54201_B001023%26vw_cd%3DMT_OTITLE%26orgId%3D542%26path%3D%252FstatisticsList%252FstatisticsListIndex.do%26conn_path%3DMT_OTITLE%26itm_id%3D%26lang_mode%3Dko%26scrId%3D%26
        # if self.hdong_dict:
        #     for hdong_name, hdong_code in self.hdong_dict.items():
        #         df = self.api.get_data(
        #             service_name="통계자료",  # 서비스명: '통계자료'로 수정
        #             orgId=orgId,  # 기관 ID: '101'은 해당 통계를 제공하는 기관 ID
        #             tblId=tblId,  # 통계표 ID: 통계표 ID는 실제 통계 표에 해당하는 고유 ID (예: 'DT_1B040B3')
        #             objL1="ALL",  # 분류ID: 'A'는 행정구역별 통계 자료를 요청하는 항목 hdong_code
        #             itmId=itmId,  # 분류값ID: 'T1'은 세대수와 관련된 항목
        #             prdSe=prdSe,  # 수록주기: 'Y'는 연간 기준 데이터 요청
        #             startPrdDe=max_year,  # 시작 기간: '202211'은 2022년 11월
        #             endPrdDe=max_year,  # 종료 기간: 동일한 2022년 11월
        #         )
        #         if df is not None and not df.empty:
        #             value = df['수치값'].sum()
        #             data.append({
        #                 '구분': hdong_name,
        #                 '수치값': value
        #             })
        # 데이터가 없는 경우 대비
        if not data:
            print("⚠️ 결과 데이터가 없습니다. API 응답을 확인하세요.")
            return pd.DataFrame()
        result_df = pd.DataFrame(data)
        result_df['수치값'] = pd.to_numeric(result_df['수치값'], errors='coerce')
        result_df.set_index('구분', inplace=True)

        return result_df

    # ==============================================================================
    # 광역시별 / 시군구별 / 시도 시군구 읍면동별 총인구수, 세대수, 세대당 인구 그래프 그리기
    # ==============================================================================
    def get_population_plotly(self, df):
        if df is None:
            st.write("데이터를 가져올 수 없습니다.")
            return None
        # 연령대별 색상 매핑
        color_map = px.colors.qualitative.Pastel1  # 색상 맵
        # NaN 값을 0으로 대체 (또는 다른 값으로 처리)
        df.fillna(0, inplace=True)
        # 시군구별 누적 막대 그래프 그리기
        if not df.empty:
            # 두 개의 y축을 사용하여 각각 다른 데이터 시각화
            fig = make_subplots(
                rows=1, cols=1,
                shared_xaxes=True,  # x축 공유
                vertical_spacing=0.1,
                specs=[[{"secondary_y": True}]]  # 두 번째 y축 추가
            )

            # 막대 그래프: 총인구수와 세대수
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df['총인구수'],
                    name='총인구수',
                    marker=dict(color=color_map[6]),
                ),
                secondary_y=False  # 첫 번째 y축 사용
            )

            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df['세대수'],
                    name='세대수',
                    marker=dict(color=color_map[5]),
                ),
                secondary_y=False  # 첫 번째 y축 사용
            )

            # 꺾은선 그래프: 세대당 인구수
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['세대당 인구수'],
                    mode='lines+markers',
                    name='세대당 인구수',
                    line=dict(color=color_map[4]),
                    text=df['세대당 인구수'].round(2),
                    textposition='top center'
                ),
                secondary_y=True  # 두 번째 y축 사용
            )

            # 그래프 레이아웃 업데이트
            fig.update_layout(
                yaxis_title="인구수, 세대수",  # 첫 번째 y축 제목
                yaxis2_title="세대당 인구수",  # 두 번째 y축 제목
                template='plotly_white',  # 배경을 흰색으로 설정
                showlegend=True
            )
            return fig

        else:
            return None

########################
# 모든 행, 모든 열 출력 설정
pd.set_option('display.max_rows', None)  # 모든 행 출력
pd.set_option('display.max_columns', None)  # 모든 열 출력
pd.set_option('display.width', None)  # 가로 길이 자동 조정
pd.set_option('display.expand_frame_repr', False)  # 줄바꿈 방지


api = Kosis("YWZhOWE3ZjgxYzY0YThkYWRmMDgyYzQzZDZjMjM2NTk=")



#############################################
# # 연령대 매핑 함수 (10세 단위로 그룹화)
# def get_age_group(value):
#     if value == 0:
#         return '전체'
#     elif value >= 60:
#         return '60세+'
#     else:
#         lower_bound = (value - 5) // 10 * 10
#         upper_bound = lower_bound + 9
#         return f'{lower_bound}-{upper_bound}세'
#
# def get_age_population_data(sigunguhdong_name, sigunguhdong_dict, df_save, sigunguhdong_type):
#     """
#     시군구 또는 행정동별 인구 데이터를 가져와서 df_age에 저장하는 함수
#     :param sigunguhdong_name: 시도 또는 시군구 또는 행정동 이름
#     :param sigunguhdong_dict: 해당 시군구/행정동의 코드 딕셔너리
#     :param df_save: 데이터 저장할 DataFrame
#     :param sigunguhdong_type: 'sido' 또는 'gungu' 또는 'hdong' (구분값)
#     """
#     sigunguhdong_code = (
#         sigunguhdong_dict['전체'][:2] if sigunguhdong_type == 'sido' else
#         sigunguhdong_dict['전체'][:5] if sigunguhdong_type == 'gungu' else
#         sigunguhdong_dict[sigunguhdong_name]
#     )
#     max_year = self.get_latest_year(orgId, tblId)
#     df = api.get_data(
#         "통계자료",
#         orgId="101",
#         tblId="DT_1B04005N",
#         objL1=sigunguhdong_code,  # 분류값ID1
#         objL2='ALL',  # 모든 연령대 포함
#         itmId="T2", # 항목ID: 총인구수 항목
#         prdSe="Y", # 수록주기
#         startPrdDe=max_year,
#         endPrdDe=max_year,
#     )
#
#     for objL2_value in range(0, 110, 5):
#         age_group = get_age_group(objL2_value)
#         df_save.loc[sigunguhdong_name, age_group] = df[df['분류값ID2'].astype(int) == objL2_value]['수치값'].sum()


