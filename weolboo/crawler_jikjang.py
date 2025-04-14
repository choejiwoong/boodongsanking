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

    def get_latest_year(self, orgId, tblId):
        """
        최신 년도 정보를 반환하는 함수
        """
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
        orgId = "118"
        tblId = "DT_118N_SAUPN75"
        max_year = self.get_latest_year(orgId, tblId)
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
        orgId = "118"
        tblId = "DT_118N_SAUPN75"
        max_year = self.get_latest_year(orgId, tblId)
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
        orgId = "118"
        tblId = "DT_118N_SAUPN75"
        max_year = self.get_latest_year(orgId, tblId)
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
            copy_df['총인구수'] = st.session_state.df_sido['총인구수']
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
            copy_df['총인구수'] = st.session_state.df_gungu['총인구수']
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

    def get_income(self):
        # ==============================================================================
        # # 주소지 소득
        # # ==============================================================================
        df = pd.DataFrame()
        orgId = "133"
        tblId = "DT_133001N_4215"
        max_year = self.get_latest_year(orgId, tblId)

        # 첫 번째 데이터 (인원) 처리
        item1 = self.api.get_data(
            "통계자료",
            orgId=orgId,
            tblId=tblId,
            itmId="T001",  # 인원
            objL1="ALL",  # 시군구
            objL2="B01",  # 급여총계
            prdSe="Y",
            startPrdDe=max_year,
            endPrdDe=max_year,
        )

        # 두 번째 데이터 (금액) 처리
        item2 = self.api.get_data(
            "통계자료",
            orgId=orgId,
            tblId=tblId,
            itmId="T002",  # 금액
            objL1="ALL",  # 시군구
            objL2="B01",  # 급여총계
            prdSe="Y",
            startPrdDe=max_year,
            endPrdDe=max_year,
        )

        item1.loc[:, '수치값'] = pd.to_numeric(item1['수치값'], errors='coerce')  # errors='coerce'는 변환할 수 없는 값을 NaN으로 처리
        item2.loc[:, '수치값'] = pd.to_numeric(item2['수치값'], errors='coerce')  # errors='coerce'는 변환할 수 없는 값을 NaN으로 처리

        df['구분'] = item1['분류값명1']
        df['구분ID'] = item1['분류값ID1']
        df['주소지 소득'] = (item2['수치값'] * 100) / item1['수치값']

        # ==============================================================================
        # # 원천징수지 소득
        # # ==============================================================================
        orgId = "133"
        tblId = "DT_133001N_4214"
        max_year = self.get_latest_year(orgId, tblId)
        # 첫 번째 데이터 (인원) 처리
        item1 = self.api.get_data(
            "통계자료",
            orgId=orgId,
            tblId=tblId,
            itmId="T001",  # 인원
            objL1="ALL",  # 시군구 ex) 남구: "A1404"
            objL2="B01",  # 급여총계
            prdSe="Y",
            startPrdDe=max_year,
            endPrdDe=max_year,
        )

        # 두 번째 데이터 (금액) 처리
        item2 = self.api.get_data(
            "통계자료",
            orgId=orgId,
            tblId=tblId,
            itmId="T002",  # 금액
            objL1="ALL",  # 시군구
            objL2="B01",  # 급여총계
            prdSe="Y",
            startPrdDe=max_year,
            endPrdDe=max_year,
        )

        item1.loc[:, '수치값'] = pd.to_numeric(item1['수치값'], errors='coerce')  # errors='coerce'는 변환할 수 없는 값을 NaN으로 처리
        item2.loc[:, '수치값'] = pd.to_numeric(item2['수치값'], errors='coerce')  # errors='coerce'는 변환할 수 없는 값을 NaN으로 처리

        df['구분'] = item1['분류값명1']
        df['구분ID'] = item1['분류값ID1']
        df['원천징수지 소득'] = (item2['수치값'] * 100) / item1['수치값']

        if self.gwangyeok_dict is not None:
            stripped_keys = [key.strip("광역시") for key in self.gwangyeok_dict.keys()]
            df_set_gwangyeok = df.loc[df['구분'].isin(stripped_keys), '구분ID']
            df_filtered_gwangyeok = df[df['구분ID'].isin(df_set_gwangyeok)]  # 광역시 코드
            return df_filtered_gwangyeok
        elif self.sigungu_dict is not None:
            df_set_sigungu = df.loc[df['구분'] == st.session_state.selected_sido.strip("광역시"), '구분ID']
            df_filtered_sigungu = df[df['구분ID'].str.contains(df_set_sigungu.values[0], na=False)]  # 시군구 코드
            return df_filtered_sigungu

    def get_bjoong(self):
        df = pd.DataFrame()
        # ==============================================================================
        # # 부산광역시 시군구 소득비중
        # # ==============================================================================
        # 해마다 달라짐
        item = self.api.get_data(
            "통계자료",
            orgId="202",
            tblId="DT_202005Y2024N063",
            itmId="ALL",
            objL1="ALL",  # 부산
            objL2="ALL",
            prdSe="Y",
            startPrdDe="2024",
            endPrdDe="2024",
        )

        copy_item = item.copy()
        df['구분'] = copy_item['분류값명1']
        copy_item['수치값'] = pd.to_numeric(copy_item['수치값'], errors='coerce')
        copy_item['수치값'] = copy_item['수치값'].fillna(0)
        df['50만원 미만'] = copy_item.loc[(copy_item['분류값ID2'] == '1053'), '수치값']
        df['50~100만원'] = copy_item.loc[(copy_item['분류값ID2'] == '2054'), '수치값']
        df['100~200만원'] = copy_item.loc[(copy_item['분류값ID2'] == '3055'), '수치값']
        df['200~300만원'] = copy_item.loc[(copy_item['분류값ID2'] == '4056'), '수치값']
        df['300~400만원'] = copy_item.loc[(copy_item['분류값ID2'] == '5057'), '수치값']
        df['400~500만원'] = copy_item.loc[(copy_item['분류값ID2'] == '6058'), '수치값']
        df['500~600만원'] = copy_item.loc[(copy_item['분류값ID2'] == '7059'), '수치값']
        df['600~700만원'] = copy_item.loc[(copy_item['분류값ID2'] == '8060'), '수치값']
        df['700~800만원'] = copy_item.loc[(copy_item['분류값ID2'] == '9061'), '수치값']
        df['800만원 이상'] = copy_item.loc[(copy_item['분류값ID2'] == '10062'), '수치값']

        # 시군구만 포함된 행 필터링
        filtered_df = df[df['구분'].str.contains('구$', na=False)]
        # 그룹별로 NaN 값을 채워넣고 중복 행 제거
        df_cleaned = filtered_df.groupby("구분").max()
        # 결과 출력
        df_cleaned['저소득층 비중'] = df_cleaned['50만원 미만'] + df_cleaned['50~100만원'] + df_cleaned['100~200만원']
        df_cleaned['중산층 비중'] = df_cleaned['400~500만원']
        df_cleaned['고소득층 비중'] = df_cleaned['700~800만원'] + df_cleaned['800만원 이상']
        return df_cleaned

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
api = Kosis("YWZhOWE3ZjgxYzY0YThkYWRmMDgyYzQzZDZjMjM2NTk=")

df = pd.DataFrame()
# item = api.get_data(
#     "KOSIS통합검색",
#     searchNm="월평균 가구소득",
# )

# item = api.get_data(
#     "통계자료",
#     orgId="322",
#     tblId="DT_32202_B018_1",
#     itmId="ALL",
#     objL1="A003",  # 부산
#     objL2="ALL",
#     prdSe="Y",
#     startPrdDe="2021",
#     endPrdDe="2021",
# )

# 해마다 달라짐
item = api.get_data(
    "통계자료",
    orgId="202",
    tblId="DT_202005Y2024N063",
    itmId="ALL",
    objL1="ALL",  # 부산
    objL2="ALL",
    prdSe="Y",
    startPrdDe="2024",
    endPrdDe="2024",
)

# print(item.loc[(item['분류값ID2'] == '1053'), '수치값'] ) # &
copy_item = item.copy()
df['구분'] = copy_item['분류값명1']
copy_item['수치값'] = pd.to_numeric(copy_item['수치값'], errors='coerce')
copy_item['수치값'] = copy_item['수치값'].fillna(0)
df['50만원 미만'] = copy_item.loc[(copy_item['분류값ID2'] == '1053'), '수치값']
df['50~100만원'] = copy_item.loc[(copy_item['분류값ID2'] == '2054'), '수치값']
df['100~200만원'] = copy_item.loc[(copy_item['분류값ID2'] == '3055'), '수치값']
df['200~300만원'] = copy_item.loc[(copy_item['분류값ID2'] == '4056'), '수치값']
df['300~400만원'] = copy_item.loc[(copy_item['분류값ID2'] == '5057'), '수치값']
df['400~500만원'] = copy_item.loc[(copy_item['분류값ID2'] == '6058'), '수치값']
df['500~600만원'] = copy_item.loc[(copy_item['분류값ID2'] == '7059'), '수치값']
df['600~700만원'] = copy_item.loc[(copy_item['분류값ID2'] == '8060'), '수치값']
df['700~800만원'] = copy_item.loc[(copy_item['분류값ID2'] == '9061'), '수치값']
df['800만원 이상'] = copy_item.loc[(copy_item['분류값ID2'] == '10062'), '수치값']

# 시군구만 포함된 행 필터링
filtered_df = df[df['구분'].str.contains('구$', na=False)]
# 그룹별로 NaN 값을 채워넣고 중복 행 제거
df_cleaned = filtered_df.groupby("구분").max()
# 결과 출력
df_cleaned['저소득층 비중'] = df_cleaned['50만원 미만'] + df_cleaned['50~100만원'] + df_cleaned['100~200만원']
df_cleaned['중산층 비중'] = df_cleaned['400~500만원']
df_cleaned['고소득층 비중'] = df_cleaned['700~800만원'] + df_cleaned['800만원 이상']
# print(df_cleaned)


# for i in range(10):
#     item = api.get_data(
#         "통계자료",
#         orgId = "322",
#         tblId = "DT_32202_B018_1",
#         itmId = "ALL",
#         objL1 = "A003", # 부산
#         objL2 = f"B0{str(i).zfill(2)}",
#         prdSe = "Y",
#         startPrdDe="2021",
#         endPrdDe="2021",
#     )
#
#     print(item)


# # ==============================================================================
# # # 시군구내 최고연봉 기업
# # # ==============================================================================
# # 국민연금 사업자 가입현황: https://www.data.go.kr/data/15083277/fileData.do#/API%20%EB%AA%A9%EB%A1%9D/getuddi%3A45ba8ffb-ab8c-44da-abd6-b10ec30821cd
# import requests
# import json
#
# # 올바른 API URL을 확인하세요.
# base_url = "https://api.odcloud.kr/api"
# end_point = "/15083277/v1/uddi:c6bf89c2-8c0b-4c8e-8698-b2cd9dc31d1f_201908061635"
#
# # API 인증 키
# api_key = "9bg1tTFeumrhYeac4TTMmKVoiH5BV2qRxRlwEm/gFZB2vrjW+PpwQgFI0s7p5w9ipE7/qtijjWOmrxwEODkyMA=="
#
# # 요청 URL 생성
# url = f"{base_url}{end_point}"
#
# # 한 번에 가져올 데이터 수 (최대값으로 설정)
# per_page = 1000
# page = 1  # 시작 페이지
# all_data = []  # 필요한 데이터만 저장할 리스트
#
# # 필터링 기준
# target_code = "26260" # 연제구: 26470, 부산진구: 26230, 동래구: 26260
#
# while True:
#     # API 요청 파라미터 설정
#     params = {
#         "serviceKey": api_key,
#         "page": page,
#         "perPage": per_page,
#     }
#
#     # API 요청
#     res = requests.get(url, params=params, verify=False)
#
#     # 응답 상태 코드 확인
#     if res.status_code != 200:
#         print(f"오류 발생: {res.status_code}, 응답 내용: {res.text}")
#         break
#
#     # JSON 데이터 변환
#     try:
#         response_data = res.json()
#     except json.JSONDecodeError:
#         print("JSON 변환 실패:", res.text)
#         break
#
#     # 현재 페이지 데이터 필터링
#     data_list = response_data.get("data", [])
#     filtered_data = [
#         data for data in data_list
#         if target_code in str(data.get("고객법정동주소코드 CUST_LDONG_ADDR_CD\tVARCHAR(10)", ""))
#     ]
#
#     # 필터링된 데이터만 저장
#     all_data.extend(filtered_data)
#
#     # 현재 가져온 개수와 전체 개수를 확인
#     current_count = len(data_list)  # 가져온 원본 데이터 개수
#     filtered_count = len(filtered_data)  # 필터링된 데이터 개수
#     total_count = response_data.get("totalCount", 0)
#
#     print(f"페이지 {page}의 데이터 {current_count}개 중 {filtered_count}개 필터링됨 (누적 {len(all_data)}개)")
#
#     # 더 이상 데이터가 없으면 중단
#     if not data_list:
#         print("모든 데이터를 불러왔습니다.")
#         break
#
#     # 다음 페이지로 이동
#     page += 1
#
#     # 전체 개수를 다 가져왔으면 중단
#     if total_count and len(all_data) >= total_count:
#         break
#
# # 최종 필터링된 데이터 출력
# print(f"\n'고객법정동주소코드'가 {target_code}인 데이터 {len(all_data)}개 발견!")
#
# df = pd.DataFrame(data=all_data)
# # 필요한 컬럼 이름 (실제 컬럼명을 확인하고 수정 필요)
# subscriber_col = "가입자수 JNNGP_CNT INTEGER"
# bill_col = "당월고지금액 CRRMM_NTC_AMT\tINTEGER"
#
# # 가입자수가 500명 이상인 데이터 필터링
# filtered_df = df[df[subscriber_col] >= 500].copy()
#
# # 근로자 평균 월급 계산
# filtered_df["총 월급"] = filtered_df[bill_col] / 0.09
# filtered_df["평균 월급"] = filtered_df["총 월급"] / filtered_df[subscriber_col]
#
# # 평균 월급이 가장 큰 사업장 찾기
# if not filtered_df.empty:
#     top_business = filtered_df.loc[filtered_df["평균 월급"].idxmax()]
#     print("가입자수 500명 이상 중 근로자 평균 월급이 가장 큰 사업장:")
#     print(top_business)
#     print(f"\n해당 사업장의 근로자 평균 월급: {top_business['평균 월급']:.2f} 원")
# else:
#     print("가입자수 500명 이상인 사업장이 없습니다.")



