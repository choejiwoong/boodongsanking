### 학군 크롤러: 완성됨
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime

# 학군 계산 클래스
class SchoolAchievement:
    def __init__(self, selected_sido, selected_sigungu, gwangyeok_dict: dict = None, sigungu_dict: dict = None):
        self.selected_sido = selected_sido
        self.selected_sigungu = selected_sigungu
        self.gwangyeok_dict = gwangyeok_dict
        self.sigungu_dict = sigungu_dict

    def fetch_school_achievement(self, type):
        """
        시군구 코드를 이용해 학교 학업성취도와 특목고 진학률 데이터를 크롤링합니다.
        type = 중학교: "3", 고등학교: "4"
        """
        if not self.selected_sigungu:
            return None

        base_url = "https://asil.kr/asil/sub/school_list.jsp"
        school_data = []

        def fetch_data(params, key):
            try:
                response = requests.get(base_url, params=params, verify=False)
                response.raise_for_status()  # HTTP 오류 확인
            except requests.exceptions.RequestException as e:
                print(f"요청 실패: {e}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.select("table tbody tr")  # 테이블의 모든 행 가져오기

            if type == "3":
                # 광역시는 15개까지만 크롤링
                if key in self.gwangyeok_dict and len(rows) > 15:
                    rows = rows[:15]

            data = []
            for row in rows:
                school_link = row.select_one("td a")
                if school_link:
                    school_name = school_link.text.strip()
                    achievement = row.select("td")[4].text.strip()
                    admission_rate = row.select("td")[8].text.strip()
                    if type == "3":
                        data.append({
                            "구분": key,
                            "학교명": school_name,
                            "학업성취도 평균": achievement,
                            "특목고 진학률": admission_rate
                        })
                    elif type == "4":
                        location = row.select("td")[1].text.strip()
                        data.append({
                            "구분": key,
                            "위치": location,
                            "학교명": school_name,
                            "학업성취도 평균": achievement,
                            "대학교 진학률": admission_rate
                        })
            return data

        # 광역시 데이터 크롤링
        for key, value in self.gwangyeok_dict.items():
            params = {'area': value, "type1": type}
            school_data.extend(fetch_data(params, key))

        # 시군구 데이터 크롤링
        sigungus = self.sigungu_dict.get(self.selected_sido, {})
        if self.selected_sigungu != '전체':
            for key, value in sigungus.items():
                if key != '전체':  # '전체' 항목 제외
                    params = {'area': value['전체'][:5], "type1": type}  # 시군구 코드를 가져옴
                    school_data.extend(fetch_data(params, key))

        return school_data

    def calculate_ranking(self, school_data):
        """학군 랭크 계산"""
        school_df = pd.DataFrame(school_data)
        # 학업성취도를 숫자로 변환
        school_df["학업성취도 평균"] = school_df["학업성취도 평균"].str.rstrip('%').astype(float)

        # 조건에 따라 갯수 세기
        count_95 = (school_df["학업성취도 평균"] >= 95).sum()
        count_90 = (school_df["학업성취도 평균"] >= 90).sum()
        count_85 = (school_df["학업성취도 평균"] >= 85).sum()
        count_80 = (school_df["학업성취도 평균"] >= 80).sum()
        rank = None

        if count_95 >= 3:
            rank = "S"
        elif count_90 >= 5:
            rank = "A"
        elif count_85 >= 5:
            rank = "B"
        else:
            rank = "C"

        return {'등급': rank, '95% 이상': count_95, '90% 이상': count_90, '85% 이상': count_85, '80% 이상': count_80}

# 학교 알리미 초등학교 코딩
class SchoolInfoAPI:
    def __init__(self, region_code=None):
        """
        SchoolInfoAPI 클래스 초기화
        :param api_key: 학교알리미 API 키 (기본값: "85250d27c3df45868670a5b63064ab32")
        :param region_code: 지역 코드
        :param year: 공시년도 (기본값: 전년도)
        :param school_kind: 학교 종류 코드 (기본값: 초등학교 "02")
        """
        self.api_key = "85250d27c3df45868670a5b63064ab32"
        self.region_code = region_code
        self.year = datetime.now().year - 1
        self.school_kind = "02"
        self.url = "http://www.schoolinfo.go.kr/openApi.do"

    def fetch_elem_school_data(self):
        """학교 데이터를 가져오는 함수"""
        params = {
            "apiKey": self.api_key,
            "apiType": "09",  # 학년별·학급별 학생수
            "pbanYr": self.year,
            "schulKndCode": self.school_kind,  # 초등학교: "02", 중학교: "0"
        }

        response = requests.get(self.url, params=params, verify=False)
        return self._process_response(response)

    def _process_response(self, response):
        """API 응답 처리 및 필터링"""
        alimi_list = []
        try:
            data = response.json()
            if data.get("resultCode") == "success":
                for item in data.get("list", []):
                    if item.get("ADRCD_CD") and self.region_code in item.get("ADRCD_CD"):
                        alimi_list.append(item)
            else:
                print("API 호출 실패:", data.get("resultMsg", "Unknown error"))
        except requests.exceptions.JSONDecodeError:
            print("JSON 응답 오류:", response.text)
        return alimi_list

    def process_school_info_data(self, school_data):
        """학교 데이터를 DataFrame으로 변환하고 처리하는 함수"""
        df = pd.DataFrame(school_data)

        # 컬럼명 변경
        df.rename(columns={
            "SCHUL_NM": "학교명", "COL_S_SUM": "전체 학생수", "COL_S1": "1학년", "COL_S2": "2학년",
            "COL_S3": "3학년", "COL_S4": "4학년", "COL_S5": "5학년", "COL_S6": "6학년", "COL_SUM": "학급당 학생수"
        }, inplace=True)

        # 추세선 기울기 추가
        df["추세선 기울기"] = df.apply(self.calculate_slope, axis=1)

        # 추세선 기울기 포맷팅 (소수점 첫째 자리까지)
        df["추세선 기울기"] = df["추세선 기울기"].apply(lambda x: f"{x:.1f}")

        # 필요한 컬럼만 필터링하고, 전체 학생수 기준으로 내림차순 정렬
        df_filtered = df[["학교명", "전체 학생수", "1학년", "2학년", "3학년", "4학년", "5학년", "6학년", "학급당 학생수", "추세선 기울기"]]

        # 학교명을 인덱스로 설정
        df_filtered.set_index("학교명", inplace=True)
        df_sorted = df_filtered.sort_values(by="전체 학생수", ascending=False)

        return df_sorted

    def calculate_slope(self, row):
        """학생 수에 대한 추세선 기울기를 계산하는 함수"""
        x = np.array([1, 2, 3, 4, 5, 6])  # 학년
        y = row[["1학년", "2학년", "3학년", "4학년", "5학년", "6학년"]].astype(float).fillna(0).values
        slope, _ = np.polyfit(x, y, 1)  # 1차 다항식으로 기울기만 반환
        return slope