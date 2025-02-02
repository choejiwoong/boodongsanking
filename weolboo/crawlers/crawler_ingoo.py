# import PublicDataReader as pdr
# from PublicDataReader import Kosis
# import pandas as pd
# from sigunguCode import *
#
# # 시군구코드 불러오기
# sido_name = "부산광역시"
# code = SigunguCode(sido_name)
# code.load_sigungu()
# sigungu_dict = code.get_sigungu_dict()
# # ==============================================================================
# # 시군구 연령별 인구수
# # 모든 시군구의 연령별 인구수를 불러옴
# # ==============================================================================
# # KOSIS 공유서비스 Open API 사용자 인증키
# service_key = "YWZhOWE3ZjgxYzY0YThkYWRmMDgyYzQzZDZjMjM2NTk="
#
# # 인스턴스 생성하기
# api = Kosis(service_key)
#
# # 전체 결과 담을 딕셔너리 초기화
# age_population_dict = {}
#
# # 가장 최신 수록 년도 추출
# df_update = api.get_data(
#     "통계표설명",
#     "자료갱신일",
#     orgId="101",
#     tblId="DT_1B04005N"
# )
# df_update_grouped = df_update.groupby(by=['수록주기']).agg({"수록시점": ["min", "max"]})
# max_year = df_update_grouped.loc['년', ('수록시점', 'max')]
#
# for sigungu, code in sigungu_dict.items():
#     # age_population_dict 업데이트
#     if sigungu not in age_population_dict:
#         age_population_dict[sigungu] = {}
#     for objL2_value in range(0, 106, 5):
#         # 연령대 범위 정의
#         if objL2_value == 0:
#             age_group = "전체"
#         else:
#             # 연령대 정의 (예: 5 -> "0 - 4세")
#             age_group = f"{objL2_value - 5} - {objL2_value - 1}세"
#         df = api.get_data(
#             "통계자료",
#             orgId="101", # 기관ID
#             tblId="DT_1B04005N", # 통계표ID
#             objL1=code, # 분류값ID1: 시군구코드 ex) 부산시: "26", 연제구: "26470", "거제1동": "2647010100"
#             objL2=str(objL2_value), # 분류값ID2: 연령대별 분류 ex) "0": 전체, "5": 5 - 9세
#             itmId="T2", # 항목ID: 총인구수
#             prdSe="Y", # 수록주기:
#             startPrdDe="2022", #max_year
#             endPrdDe="2022", #max_year
#         )
#         if df is None:
#             break
#         else:
#             pv = df.pivot(index=["분류값ID1","분류값명1","수록시점"], columns=["항목명"], values="수치값")
#             pv.columns.name = None
#             pv["총인구수"] = pd.to_numeric(pv["총인구수"])
#
#             # 나이대별 인구수 업데이트
#             age_population_dict[sigungu][age_group] = float(pv["총인구수"].iloc[0])
#             print(pv["총인구수"])
#
# print(pd.DataFrame(data=age_population_dict))

import PublicDataReader as pdr
from PublicDataReader import Kosis
import pandas as pd
from sigunguCode import *


class AgePopulationAnalysis:
    def __init__(self, sido_name: str, service_key: str = "YWZhOWE3ZjgxYzY0YThkYWRmMDgyYzQzZDZjMjM2NTk="):
        # 시군구 이름과 KOSIS 서비스 키를 받아서 초기화
        self.sido_name = sido_name
        self.service_key = service_key
        self.age_population_dict = {}

        # 시군구 코드 불러오기
        self.code = SigunguCode(sido_name)
        self.code.load_sigungu()
        self.sigungu_dict = self.code.get_sigungu_dict()

        # KOSIS 인스턴스 생성
        self.api = Kosis(service_key)

    def get_latest_year(self):
        # 가장 최신 수록 년도 추출
        df_update = self.api.get_data(
            "통계표설명",
            "자료갱신일",
            orgId="101",
            tblId="DT_1B04005N"
        )
        df_update_grouped = df_update.groupby(by=['수록주기']).agg({"수록시점": ["min", "max"]})
        max_year = df_update_grouped.loc['년', ('수록시점', 'max')]
        return max_year

    def fetch_age_population_data(self, sigungu_code, objL2_value, max_year):
        # 연령대별 인구수 가져오기
        df = self.api.get_data(
            "통계자료",
            orgId="101",  # 기관ID
            tblId="DT_1B04005N",  # 통계표ID
            objL1=sigungu_code,  # 시군구 코드
            objL2=str(objL2_value),  # 연령대별 분류
            itmId="T2",  # 총인구수 항목
            prdSe="Y",  # 수록주기
            startPrdDe="2022",  # 최신 연도
            endPrdDe="2022",  # 최신 연도
        )
        return df

    def process_population_data(self):
        # 시군구별 연령대별 인구수 업데이트
        max_year = self.get_latest_year()

        for sigungu, code in self.sigungu_dict.items():
            if sigungu not in self.age_population_dict:
                self.age_population_dict[sigungu] = {}

            for objL2_value in range(0, 106, 5):
                if objL2_value == 0:
                    age_group = "전체"
                else:
                    age_group = f"{objL2_value - 5} - {objL2_value - 1}세"

                df = self.fetch_age_population_data(code, objL2_value, max_year)

                if df is None:
                    continue
                else:
                    pv = df.pivot(index=["분류값ID1", "분류값명1", "수록시점"], columns=["항목명"], values="수치값")
                    pv.columns.name = None
                    pv["총인구수"] = pd.to_numeric(pv["총인구수"])

                    # 나이대별 인구수 업데이트
                    self.age_population_dict[sigungu][age_group] = float(pv["총인구수"].iloc[0])
                    print(pv["총인구수"])

    def get_population_data(self):
        # 데이터를 DataFrame 형태로 반환
        return pd.DataFrame(data=self.age_population_dict)