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
    def fetch_age_population_data(self, sigungu_code, objL2_value, max_year):
        df = self.api.get_data(
            "통계자료",
            orgId="101",  # 기관ID
            tblId="DT_1B04005N",  # 통계표ID
            objL1=sigungu_code,  # 시군구 코드
            objL2=str(objL2_value),  # 연령대별 분류
            itmId="T2",  # 총인구수 항목
            prdSe="Y",  # 수록주기
            startPrdDe=max_year,  # 최신 연도
            endPrdDe=max_year,  # 최신 연도
        )
        return df

    # 특정 도시 시군구별 연령대별 인구수
    def process_population_data(self):
        max_year = self.get_latest_year("101", "DT_1B04005N")
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
        print(self.age_population_dict)
        # 데이터를 DataFrame 형태로 반환
        return pd.DataFrame(data=self.age_population_dict)


