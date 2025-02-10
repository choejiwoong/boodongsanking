### 학군 크롤러: 완성됨
import requests
from bs4 import BeautifulSoup
import pandas as pd



# 학군 계산 클래스
class SchoolAchievement:
    def __init__(self, selected_sido, selected_sigungu, gwangyeok_dict: dict = None, sigungu_dict: dict = None):
        self.selected_sido = selected_sido
        self.selected_sigungu = selected_sigungu
        self.gwangyeok_dict = gwangyeok_dict
        self.sigungu_dict = sigungu_dict

    # def fetch_school_achievement(self):
    #     """
    #     시군구 코드를 이용해 학교 학업성취도와 특목고 진학률 데이터를 크롤링합니다.
    #     """
    #     if not self.selected_sigungu:
    #         return None
    #     base_url = "https://asil.kr/asil/sub/school_list.jsp"
    #
    #     school_data = []
    #
    #     for key, value in self.gwangyeok_dict.items():
    #         # 광역시
    #         params = {'area': value}
    #         try:
    #             response = requests.get(base_url, params=params, verify=False)
    #             response.raise_for_status()  # HTTP 오류 확인
    #         except requests.exceptions.RequestException as e:
    #             print(f"요청 실패: {e}")
    #             return None
    #
    #         soup = BeautifulSoup(response.text, 'html.parser')
    #
    #         # <td> 태그 안의 <a> 태그와 관련된 데이터를 크롤링
    #         rows = soup.select("table tbody tr")  # 테이블의 모든 행 가져오기
    #
    #         for i, row in enumerate(rows):
    #             if i >= 15:  # 15개까지만 추가
    #                 break
    #             # 각 행에서 학교 이름이 포함된 <a> 태그 추출
    #             school_link = row.select_one("td a")
    #             if school_link:
    #                 school_name = school_link.text.strip()
    #
    #                 # 학업성취도 평균 값 (5번째 <td>)
    #                 try:
    #                     achievement = row.select("td")[4].text.strip()  # N번째 <td> (0부터 시작)
    #                 except IndexError:
    #                     achievement = "데이터 없음"
    #
    #                 # 특목고 진학률 (9번째 <td>)
    #                 try:
    #                     admission_rate = row.select("td")[8].text.strip()  # N번째 <td> (0부터 시작)
    #                 except IndexError:
    #                     admission_rate = "데이터 없음"
    #
    #                 school_data.append({
    #                     "구분": key,
    #                     "학교명": school_name,
    #                     "학업성취도 평균": achievement,
    #                     "특목고 진학률": admission_rate
    #                 })
    #
    #     # 모든 시군구
    #     sigungus = self.sigungu_dict[self.selected_sido]
    #     if self.selected_sigungu != '전체':
    #         for key, value in sigungus.items():
    #             if key != '전체': # '전체' 항목 제외
    #                 params = {'area': value['전체'][:5]} # 시군구 코드를 가져옴
    #                 try:
    #                     response = requests.get(base_url, params=params, verify=False)
    #                     response.raise_for_status()  # HTTP 오류 확인
    #                 except requests.exceptions.RequestException as e:
    #                     print(f"요청 실패: {e}")
    #                     return None
    #
    #                 soup = BeautifulSoup(response.text, 'html.parser')
    #
    #                 # <td> 태그 안의 <a> 태그와 관련된 데이터를 크롤링
    #                 rows = soup.select("table tbody tr")  # 테이블의 모든 행 가져오기
    #
    #                 for row in rows:
    #                     # 각 행에서 학교 이름이 포함된 <a> 태그 추출
    #                     school_link = row.select_one("td a")
    #                     if school_link:
    #                         school_name = school_link.text.strip()
    #
    #                         # 학업성취도 평균 값 (5번째 <td>)
    #                         try:
    #                             achievement = row.select("td")[4].text.strip()  # N번째 <td> (0부터 시작)
    #                         except IndexError:
    #                             achievement = "데이터 없음"
    #
    #                         # 특목고 진학률 (9번째 <td>)
    #                         try:
    #                             admission_rate = row.select("td")[8].text.strip()  # N번째 <td> (0부터 시작)
    #                         except IndexError:
    #                             admission_rate = "데이터 없음"
    #
    #                         school_data.append({
    #                             "구분": key,
    #                             "학교명": school_name,
    #                             "학업성취도 평균": achievement,
    #                             "특목고 진학률": admission_rate
    #                         })
    #
    #     return school_data

    def fetch_school_achievement(self):
        """
        시군구 코드를 이용해 학교 학업성취도와 특목고 진학률 데이터를 크롤링합니다.
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
                    data.append({
                        "구분": key,
                        "학교명": school_name,
                        "학업성취도 평균": achievement,
                        "특목고 진학률": admission_rate
                    })
            return data

        # 광역시 데이터 크롤링
        for key, value in self.gwangyeok_dict.items():
            params = {'area': value}
            school_data.extend(fetch_data(params, key))

        # 시군구 데이터 크롤링
        sigungus = self.sigungu_dict.get(self.selected_sido, {})
        if self.selected_sigungu != '전체':
            for key, value in sigungus.items():
                if key != '전체':  # '전체' 항목 제외
                    params = {'area': value['전체'][:5]}  # 시군구 코드를 가져옴
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
