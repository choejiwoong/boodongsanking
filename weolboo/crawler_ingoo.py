import PublicDataReader as pdr
import streamlit
from PublicDataReader import Kosis
import pandas as pd
from sigunguCode import *
from datetime import datetime


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
        orgId = "101" # 기관ID
        tblId = "DT_1B04005N" # 통계표ID
        itmId = "T2" # 총인구수 항목
        prdSe = "Y" # 수록주기
        max_year = self.get_latest_year(orgId, tblId)

        # 연령대 매핑 함수
        def get_age_group(value):
            if value == 0:
                return '전체'
            elif value == 105:
                return '100세 이상'
            else:
                return f'{value - 5}-{value - 1}세'

        for objL2_value in range(0, 110, 5):  # 0부터 105까지 5씩 증가
            if self.gwangyeok_dict:
                for gwangyeok_name, gwangyeok_code in self.gwangyeok_dict.items():
                    df = self.api.get_data(
                        "통계자료",
                        orgId=orgId,  # 기관ID
                        tblId=tblId,  # 통계표ID
                        objL1=gwangyeok_code,  # 시군구 코드
                        objL2=str(objL2_value),  # 연령대별 분류
                        itmId=itmId,  # 총인구수 항목
                        prdSe=prdSe,  # 수록주기
                        startPrdDe=max_year,  # 최신 연도
                        endPrdDe=max_year,  # 최신 연도
                    )
                    if df is not None and not df.empty:  # DataFrame이 유효한 경우에만 추가
                        value = df['수치값'].sum()  # 여러 값이 있으면 합산
                        data.append({
                            '구분': gwangyeok_name,
                            '연령대': get_age_group(objL2_value),
                            '수치값': value
                        })
                        print({
                            '구분': gwangyeok_name,
                            '연령대': get_age_group(objL2_value),
                            '수치값': value
                        })
            if self.hdong_dict:
                for hdong_name, hdong_code in self.hdong_dict.items():
                    df = self.api.get_data(
                        "통계자료",
                        orgId=orgId,  # 기관ID
                        tblId=tblId,  # 통계표ID
                        objL1=hdong_code,  # 읍면동 코드
                        objL2=str(objL2_value),  # 연령대별 분류
                        itmId=itmId,  # 총인구수 항목
                        prdSe=prdSe,  # 수록주기
                        startPrdDe=max_year,  # 최신 연도
                        endPrdDe=max_year,  # 최신 연도
                    )
                    if df is not None and not df.empty:  # DataFrame이 유효한 경우에만 추가
                        value = df['수치값'].sum()  # 여러 값이 있으면 합산
                        data.append({
                            '구분': gwangyeok_name,
                            '연령대': get_age_group(objL2_value),
                            '수치값': value
                        })
        # 데이터프레임 생성 후 피벗
        result_df = pd.DataFrame(data)
        # 정렬
        result_df = result_df.sort_values(by=['구분', '연령대'])
        # 수치값을 숫자로 변환 (혹시 남아있는 문자열이 있다면)
        result_df['수치값'] = pd.to_numeric(result_df['수치값'], errors='coerce')
        pivot_df = result_df.pivot_table(index='구분', columns='연령대', values='수치값', aggfunc='sum').reset_index()
        return pivot_df


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
