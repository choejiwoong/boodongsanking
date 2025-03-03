####  산업별, 동별 사업체수 및 종사자수
#### 아직 안 끝남....
from PublicDataReader import Kosis
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import re
# https://github.com/WooilJeong/PublicDataReader/blob/main/assets/docs/kosis/Kosis.md
# 최대 출력할 행 수와 열 수 설정
pd.set_option('display.max_rows', None)  # 모든 행 출력
pd.set_option('display.max_columns', None)  # 모든 열 출력
pd.set_option('display.width', None)  # 출력 너비 제한 없애기
pd.set_option('display.max_colwidth', None)  # 열의 최대 너비를 제한하지 않음

class KosisDataFetcher:
    def __init__(self, service_key: str = "YWZhOWE3ZjgxYzY0YThkYWRmMDgyYzQzZDZjMjM2NTk=", gwangyeok_dict: dict = None, sigungu_dict: dict = None, selected_sido: str = None):
        self.service_key = service_key
        self.gwangyeok_dict = gwangyeok_dict
        self.sigungu_dict = sigungu_dict
        self.selected_sido = selected_sido
        self.api = Kosis(service_key)  # Kosis API 인스턴스 생성

    def get_latest_year(self):
        """
        최신 년도 정보를 반환하는 함수
        """
        orgId = "118"
        tblId = "DT_118N_SAUPN75"
        df_update = self.api.get_data(
            "통계표설명",
            "자료갱신일",
            orgId=orgId,
            tblId=tblId,
        )
        df_update_grouped = df_update.groupby(by=['수록주기']).agg({"수록시점": ["min", "max"]})
        max_year = df_update_grouped.loc['년', ('수록시점', 'max')]
        return max_year

    def get_classification_id_by_city(self):
        """
        각 도시 이름에 해당하는 '분류값ID1' 값을 반환하는 함수
        """
        max_year = self.get_latest_year()
        orgId = "118"
        tblId = "DT_118N_SAUPN75"
        result = {}
        if self.gwangyeok_dict:
            for gwangyeok_name in self.gwangyeok_dict.keys():
                df = self.api.get_data(
                    service_name="통계자료",  # 서비스명
                    orgId=orgId,  # 기관 ID
                    tblId=tblId,  # 통계표 ID
                    objL1="ALL",  # 지역 코드
                    objL2="190326INDUSTRY_10S0",  # 산업분류별 코드
                    objL3="15118SIZES_0709",  # 규모별 코드 (500인 이상)
                    itmId="16118ED_1",  # 항목 (사업체수)
                    prdSe="Y",  # 수록주기
                    startPrdDe=max_year,  # 시작년도
                    endPrdDe=max_year,  # 종료년도
                )

                filtered_df = df[df['분류값명1'] == gwangyeok_name]

                if not filtered_df.empty:
                    result[gwangyeok_name] = filtered_df['분류값ID1'].iloc[0]
                else:
                    result[gwangyeok_name] = None

        if self.selected_sido:
            df = self.api.get_data(
                service_name="통계자료",  # 서비스명
                orgId=orgId,  # 기관 ID
                tblId=tblId,  # 통계표 ID
                objL1="ALL",  # 지역 코드
                objL2="190326INDUSTRY_10S0",  # 산업분류별 코드
                objL3="15118SIZES_0709",  # 규모별 코드 (500인 이상)
                itmId="16118ED_1",  # 항목 (사업체수)
                prdSe="Y",  # 수록주기
                startPrdDe=max_year,  # 시작년도
                endPrdDe=max_year,  # 종료년도
            )
            # print(self.selected_sido)
            filtered_df = df[df['분류값명1'] == self.selected_sido]

            if not filtered_df.empty:
                result[self.selected_sido] = filtered_df['분류값ID1'].iloc[0]
                # print(result[self.selected_sido])
            else:
                result[self.selected_sido] = None
        return result

    def fetch_and_process_data(self):
        """
        각 시군구 및 objL3별 데이터 가져오기
        """
        max_year = self.get_latest_year()
        orgId = "118"
        tblId = "DT_118N_SAUPN75"
        objL3_list = ["15118SIZES_0709", "15118SIZES_0710", "15118SIZES_0700"]  # 500~999인, 1000인 이상 항목, 전규모
        itmId_list = ["16118ED_1", '16118ED_9A'] # 사업체수, 종사자수
        data = []

        # 🔹 광역시 데이터 처리
        if self.gwangyeok_dict:
            gwangyeok_list = [gwangyeok for gwangyeok in self.gwangyeok_dict.keys() if gwangyeok != '전체']
            classification_id = self.get_classification_id_by_city()

            for gwangyeok in gwangyeok_list:
                for itmId in itmId_list:
                    for objL3 in objL3_list:
                        df = self.api.get_data(
                            service_name="통계자료",
                            orgId=orgId,
                            tblId=tblId,
                            objL1=classification_id[gwangyeok],  # 지역 코드
                            objL2="190326INDUSTRY_10S0",  # 산업분류별 코드
                            objL3=objL3,  # 규모별 코드
                            itmId=itmId,  # 항목 (사업체수)
                            prdSe="Y",  # 수록주기
                            startPrdDe=max_year,  # 시작년도
                            endPrdDe=max_year,  # 종료년도
                        )

                        if df is None or df.empty:
                            print(f"데이터 없음: {gwangyeok}")
                            continue

                        data.append({
                            "구분": df['분류값명1'].iloc[0],
                            "항목명": df['항목명'].iloc[0],
                            "규모명": df['분류값명3'].iloc[0],
                            "수치값": df['수치값'].sum(),
                        })

        # 🔹 시군구 데이터 처리 (광역시와 분리되지 않도록 return 제거)
        if self.sigungu_dict:
            sigungu_list = [sigungu for sigungu in self.sigungu_dict.keys() if sigungu != '전체']
            classification_id = self.get_classification_id_by_city()
            modified_dict = self.generate_modified_dict(classification_id)

            for i, sigungu in enumerate(sigungu_list):
                for itmId in itmId_list:
                    for objL3 in objL3_list:
                        df = self.api.get_data(
                            service_name="통계자료",
                            orgId=orgId,
                            tblId=tblId,
                            objL1=f"{modified_dict[self.selected_sido]}{str(i + 1).zfill(2)}",
                            objL2="190326INDUSTRY_10S0",
                            objL3=objL3,
                            itmId=itmId,
                            prdSe="Y",
                            startPrdDe=max_year,
                            endPrdDe=max_year,
                        )

                        if df is None or df.empty:
                            print(f"데이터 없음: {sigungu}")
                            continue

                        data.append({
                            "구분": df['분류값명1'].iloc[0],
                            "항목명": df['항목명'].iloc[0],
                            "규모명": df['분류값명3'].iloc[0],
                            "수치값": df['수치값'].sum(),
                        })

        # 📌 **광역시 + 시군구 데이터를 모두 포함한 최종 DataFrame 변환**
        result_df = self.process_data(data)
        return result_df

    def fetch_and_process_industry_data(self):
        """
        각 시군구 및 objL3별 데이터 가져오기
        """
        max_year = self.get_latest_year()

        orgId = "118"
        tblId = "DT_118N_SAUPN75"
        data = []
        # 산업분류 코드 리스트 생성
        industry_codes = [f"190326INDUSTRY_10S{chr(i)}" for i in range(ord('A'), ord('S') + 1)]
        # 🔹 광역시 데이터 처리
        if self.gwangyeok_dict is not None:
            gwangyeok_list = [gwangyeok for gwangyeok in self.gwangyeok_dict.keys() if gwangyeok != '전체']
            classification_id = self.get_classification_id_by_city()
            for gwangyeok in gwangyeok_list:
                for industry_code in industry_codes:
                    df = self.api.get_data(
                        service_name="통계자료",  # 서비스명
                        orgId=orgId,  # 기관 ID
                        tblId=tblId,  # 통계표 ID
                        objL1=classification_id[gwangyeok],  # 지역 코드
                        objL2=industry_code,  # 산업분류별 코드 ex) 전체: 190326INDUSTRY_10S0
                        objL3="15118SIZES_0700",  # 규모별 코드 ex) 전체
                        itmId="16118ED_1",  # 사업체수 항목
                        prdSe="Y",  # 수록주기
                        startPrdDe=max_year,  # 시작년도
                        endPrdDe=max_year,  # 종료년도
                    )

                    # df가 None이거나 DataFrame이 아니거나 비어 있으면 break
                    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
                        print(f"⚠️ objL2={industry_code}: 데이터 없음, 루프 종료")
                        break

                    data.append({
                        "구분": df['분류값명1'].iloc[0],
                        "산업명": df['분류값명2'].iloc[0],
                        "수치값": df['수치값'].sum(),
                    })
        else:
            # 🔹 시군구 데이터 처리
            sigungu_list = [sigungu for sigungu in self.sigungu_dict.keys() if sigungu != '전체']
            classification_id = self.get_classification_id_by_city()
            modified_dict = self.generate_modified_dict(classification_id)
            for i, sigungu in enumerate(sigungu_list):
                for industry_code in industry_codes:
                    df = self.api.get_data(
                        service_name="통계자료",  # 서비스명
                        orgId=orgId,  # 기관 ID
                        tblId=tblId,  # 통계표 ID
                        objL1=f"{modified_dict[self.selected_sido]}{str(i + 1).zfill(2)}",  # 지역 코드 15118ZONE2012_212113
                        objL2=industry_code,  # 산업분류별 코드 ex) 전체: 190326INDUSTRY_10S0
                        objL3="15118SIZES_0700",  # 규모별 코드 ex) 전체
                        itmId="16118ED_1",  # 사업체수 항목
                        prdSe="Y",  # 수록주기
                        startPrdDe=max_year,  # 시작년도
                        endPrdDe=max_year,  # 종료년도
                    )

                    # df가 None이거나 DataFrame이 아니거나 비어 있으면 break
                    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
                        print(f"⚠️ objL2={industry_code}: 데이터 없음, 루프 종료")
                        break

                    data.append({
                        "구분": df['분류값명1'].iloc[0],
                        "산업명": df['분류값명2'].iloc[0],
                        "수치값": df['수치값'].sum(),
                    })
        new_df = pd.DataFrame(data)
        pivot_df = new_df.pivot(index="구분", columns="산업명", values="수치값")
        pivot_df['J.정보통신업(58~63)'] = pd.to_numeric(pivot_df['J.정보통신업(58~63)'], errors='coerce')
        pivot_df['K.금융 및 보험업(64~66)'] = pd.to_numeric(pivot_df['K.금융 및 보험업(64~66)'], errors='coerce')
        pivot_df['M.전문 과학 및 기술 서비스업(70~73)'] = pd.to_numeric(pivot_df['M.전문 과학 및 기술 서비스업(70~73)'], errors='coerce')
        pivot_df['고소득산업'] = pivot_df['J.정보통신업(58~63)'] + pivot_df['K.금융 및 보험업(64~66)'] + pivot_df['M.전문 과학 및 기술 서비스업(70~73)']
        pivot_df = pivot_df.apply(pd.to_numeric, errors='coerce')
        return pivot_df

    def generate_modified_dict(self, classification_id):
        """
        시군구 코드 끝 두 자리를 추가하는 함수
        """
        modified_dict = {}
        for sigungu, code in classification_id.items():
            city_code = code[-2:]  # 끝 두 자리를 추출
            new_code = code + city_code  # 끝에 해당 숫자 두 자리를 한 번만 추가
            modified_dict[sigungu] = new_code
        return modified_dict

    def process_data(self, data):
        """
        데이터를 처리하여 최종 DataFrame으로 변환하는 함수
        """
        if 'get_population_data_gwangyeok' not in st.session_state:
            st.session_state.get_population_data_gwangyeok = None  # 초기값 설정 (None, 빈 문자열, 또는 적당한 값)
        if 'get_population_data_sigungu' not in st.session_state:
            st.session_state.get_population_data_sigungu = None  # 초기값 설정 (None, 빈 문자열, 또는 적당한 값)

        result_df = pd.DataFrame(data)

        df_pivot = result_df.pivot(index="구분", columns=["항목명", "규모명"], values="수치값").reset_index()

        # '사업체수_500~999인'과 '사업체수_1000인이상'을 숫자로 변환
        df_pivot[('사업체수', '500~999인')] = pd.to_numeric(df_pivot[('사업체수', '500~999인')], errors='coerce')
        df_pivot[('사업체수', '1000인이상')] = pd.to_numeric(df_pivot[('사업체수', '1000인이상')], errors='coerce')

        # 합산 컬럼 추가
        df_pivot['500인 이상 사업체수'] = df_pivot[('사업체수', '500~999인')] + df_pivot[('사업체수', '1000인이상')]
        df_pivot = df_pivot.rename(columns={('총종사자수_계'): '종사자수'})

        # print(df_pivot)
        df_pivot_reset = df_pivot.reset_index()
        df_pivot_reset.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in df_pivot_reset.columns]
        # print(df_pivot_reset.columns)

        # 필요한 열 선택
        new_df = df_pivot_reset[['구분_', '사업체수_전규모', '종사자수_전규모', '500인 이상 사업체수_']]

        # 열 이름 변경
        new_df.columns = ['구분', '사업체수', '종사자수', '500인 이상 사업체수']

        new_df.set_index("구분", inplace=True)
        copy_df = new_df.copy()

        if self.gwangyeok_dict is not None:
            copy_df['총인구수'] = st.session_state.get_population_data_gwangyeok['수치값']
            copy_df['총인구수'] = pd.to_numeric(copy_df['총인구수'], errors='coerce')
            copy_df['사업체수'] = pd.to_numeric(copy_df['사업체수'], errors='coerce')
            copy_df['종사자수'] = pd.to_numeric(copy_df['종사자수'], errors='coerce')
            copy_df['등급'] = copy_df['종사자수'].apply(
                lambda x: 'S' if x >= 300000 else ('A' if x >= 200000 else ('B' if x >= 100000 else 'C'))
            )

            copy_df['총인구수 대비 종사자비율'] = copy_df.apply(lambda row: round((row['종사자수'] / row['총인구수'] * 100), 1), axis=1)
            copy_df['사업체수'] = copy_df['사업체수'].apply(lambda x: f'{x:,}' if isinstance(x, (int, float)) else x)
            copy_df['종사자수'] = copy_df['종사자수'].apply(lambda x: f'{x:,}' if isinstance(x, (int, float)) else x)
            copy_df['500인 이상 사업체수'] = copy_df['500인 이상 사업체수'].apply(lambda x: f'{x:,}' if isinstance(x, (int, float)) else x)

        else:
            copy_df['총인구수'] = st.session_state.get_population_data_sigungu['수치값']
            copy_df['총인구수'] = pd.to_numeric(copy_df['총인구수'], errors='coerce')
            copy_df['사업체수'] = pd.to_numeric(copy_df['사업체수'], errors='coerce')
            copy_df['종사자수'] = pd.to_numeric(copy_df['종사자수'], errors='coerce')
            copy_df['등급'] = copy_df['종사자수'].apply(
                lambda x: 'S' if x >= 300000 else ('A' if x >= 200000 else ('B' if x >= 100000 else 'C'))
            )

            copy_df['총인구수 대비 종사자비율'] = copy_df.apply(lambda row: round((row['종사자수'] / row['총인구수'] * 100), 1), axis=1)
            copy_df['사업체수'] = copy_df['사업체수'].apply(lambda x: f'{x:,}' if isinstance(x, (int, float)) else x)
            copy_df['종사자수'] = copy_df['종사자수'].apply(lambda x: f'{x:,}' if isinstance(x, (int, float)) else x)
            copy_df['500인 이상 사업체수'] = copy_df['500인 이상 사업체수'].apply(lambda x: f'{x:,}' if isinstance(x, (int, float)) else x)

        return copy_df

    # ==============================================================================
    # 산업별 비중 그래프 그리기
    # ==============================================================================
    def get_plotly(self, df):
        # print(df.dtypes)
        # print(df.columns)  # 컬럼명 확인
        # print(df.index)

        # 연령대별 색상 매핑
        color_map = px.colors.qualitative.Pastel1  # 또는 Pastel2
        # Streamlit에서 DataFrame 출력
        if not df.empty:

            # 색상 맵 정의
            color_map = px.colors.qualitative.Pastel1

            # bar 그래프 생성
            fig = px.bar(df,
                         x=df.index,  # 지역명
                         y=df.columns,  # 산업별 수치
                         color_discrete_map=color_map,  # 색상 맵 적용
                        barmode = 'stack'
                         )

            # # 고소득사업 값을 Scatter로 추가
            # scatter_trace = go.Scatter(
            #     x=df.index,
            #     y=df_active,  # 경제활동인구 값
            #     mode='lines+markers',
            #     name='경제활동인구',
            #     line=dict(color='black', dash='dot'),
            #     text=df_active.round(1),
            #     textposition='top center'
            # )
            # # 그래프에 Scatter trace 추가
            # fig.add_trace(scatter_trace)
            # 그래프 표시
            fig.show()
            return fig
        else:
            return None

# gwangyeok_dict = {'부산광역시': '260000', '대구광역시': '315555'}
# # sigungu_dict = {'연제구': '260000000', '해운대구': '250000000', '해운대ㅇㅇㅇ구': '250000000', '해ㄴㄹㄴㅇㅁㄹ대구': '250000000', '해운대ㄹㅁㄴㄹ': '250000000', '해ㅇ': '250000000', 'ㅇㅇ': '250000000'}  # 예시 데이터
#
# fetcher = KosisDataFetcher(gwangyeok_dict=gwangyeok_dict)
# print(fetcher.fetch_and_process_industry_data())

# gwangyeok_dict = {'부산광역시': '260000', '대구광역시': '315555'}  # 예시 데이터
# sigungu_dict = {'연제구': '260000000', '해운대구': '250000000', '해운대ㅇㅇㅇ구': '250000000', '해ㄴㄹㄴㅇㅁㄹ대구': '250000000', '해운대ㄹㅁㄴㄹ': '250000000', '해ㅇ': '250000000', 'ㅇㅇ': '250000000'}  # 예시 데이터
#
# fetcher = KosisDataFetcher(gwangyeok_dict=gwangyeok_dict)
# # fetcher = KosisDataFetcher(sigungu_dict=sigungu_dict, selected_sido="부산광역시")
# result_df = fetcher.fetch_and_process_data()
# print(result_df)

# # ==============================================================================
# # 광역시 소득비중
# # ==============================================================================
# api = Kosis("YWZhOWE3ZjgxYzY0YThkYWRmMDgyYzQzZDZjMjM2NTk=")
# item = api.get_data(
#     "통계자료",
#     orgId = "322",
#     tblId = "DT_32202_B018_1",
#     itmId = "ALL",
#     objL1 = "ALL",
#     objL2 = "ALL",
#     prdSe = "Y",
#     startPrdDe="2021",
#     endPrdDe="2021",
# )
# print(item)

# ==============================================================================
# # 주소지 소득
# # ==============================================================================
api = Kosis("YWZhOWE3ZjgxYzY0YThkYWRmMDgyYzQzZDZjMjM2NTk=")
df = pd.DataFrame()

# 첫 번째 데이터 (인원) 처리
item1 = api.get_data(
    "통계자료",
    orgId="133",
    tblId="DT_133001N_4215",
    itmId="T001",  # 인원
    objL1="ALL",  # 시군구 ex) 남구: "A1404"
    objL2="B01",  # 급여총계
    prdSe="Y",
    startPrdDe="2021",
    endPrdDe="2021",
)

# 두 번째 데이터 (금액) 처리
item2 = api.get_data(
    "통계자료",
    orgId="133",
    tblId="DT_133001N_4215",
    itmId="T002",  # 금액
    objL1="ALL",  # 시군구
    objL2="B01",  # 급여총계
    prdSe="Y",
    startPrdDe="2021",
    endPrdDe="2021",
)

item1.loc[:, '수치값'] = pd.to_numeric(item1['수치값'], errors='coerce')  # errors='coerce'는 변환할 수 없는 값을 NaN으로 처리
item2.loc[:, '수치값'] = pd.to_numeric(item2['수치값'], errors='coerce')  # errors='coerce'는 변환할 수 없는 값을 NaN으로 처리

df['구분'] = item1['분류값명1']
df['구분ID'] = item1['분류값ID1']
df['주소지 소득'] = (item2['수치값'] * 100) / item1['수치값']
# print(df)


# ==============================================================================
# # 원천징수지 소득
# # ==============================================================================
api = Kosis("YWZhOWE3ZjgxYzY0YThkYWRmMDgyYzQzZDZjMjM2NTk=")

# 첫 번째 데이터 (인원) 처리
item1 = api.get_data(
    "통계자료",
    orgId="133",
    tblId="DT_133001N_4214",
    itmId="T001",  # 인원
    objL1="ALL",  # 시군구 ex) 남구: "A1404"
    objL2="B01",  # 급여총계
    prdSe="Y",
    startPrdDe="2021",
    endPrdDe="2021",
)

# 두 번째 데이터 (금액) 처리
item2 = api.get_data(
    "통계자료",
    orgId="133",
    tblId="DT_133001N_4214",
    itmId="T002",  # 금액
    objL1="ALL",  # 시군구
    objL2="B01",  # 급여총계
    prdSe="Y",
    startPrdDe="2021",
    endPrdDe="2021",
)

item1.loc[:, '수치값'] = pd.to_numeric(item1['수치값'], errors='coerce')  # errors='coerce'는 변환할 수 없는 값을 NaN으로 처리
item2.loc[:, '수치값'] = pd.to_numeric(item2['수치값'], errors='coerce')  # errors='coerce'는 변환할 수 없는 값을 NaN으로 처리

df['구분'] = item1['분류값명1']
df['구분ID'] = item1['분류값ID1']
df['원천징수지 소득'] = (item2['수치값'] * 100) / item1['수치값']
# print(df)

df1 = api.get_data(
    "KOSIS통합검색",
    searchNm="기업별 국민연금 납부금액",
    )

print(df1)

# ==============================================================================
# # 시군구내 최고연봉 기업
# # ==============================================================================
# 국민연금 사업자 가입현황: https://www.data.go.kr/data/15083277/fileData.do#/API%20%EB%AA%A9%EB%A1%9D/getuddi%3A45ba8ffb-ab8c-44da-abd6-b10ec30821cd