### 학군 크롤러: 완성됨
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 학군 계산 클래스
class SchoolAchievement:
    def __init__(self, si_name, gungu_name):
        self.city_name = si_name
        self.sigungu_name = gungu_name
        self.sigungucode = "26470"

    def fetch_school_achievement(self):
        """
        시군구 코드를 이용해 학교 학업성취도와 특목고 진학률 데이터를 크롤링합니다.
        """
        if not self.sigungucode:
            return None

        base_url = "https://asil.kr/asil/sub/school_list.jsp"
        params = {"area": self.sigungucode}

        try:
            response = requests.get(base_url, params=params, verify=False)
            response.raise_for_status()  # HTTP 오류 확인
        except requests.exceptions.RequestException as e:
            print(f"요청 실패: {e}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # <td> 태그 안의 <a> 태그와 관련된 데이터를 크롤링
        rows = soup.select("table tbody tr")  # 테이블의 모든 행 가져오기
        school_data = []

        for row in rows:
            # 각 행에서 학교 이름이 포함된 <a> 태그 추출
            school_link = row.select_one("td a")
            if school_link:
                school_name = school_link.text.strip()

                # 학업성취도 평균 값 (5번째 <td>)
                try:
                    achievement = row.select("td")[4].text.strip()  # N번째 <td> (0부터 시작)
                except IndexError:
                    achievement = "데이터 없음"

                # 특목고 진학률 (9번째 <td>)
                try:
                    admission_rate = row.select("td")[8].text.strip()  # N번째 <td> (0부터 시작)
                except IndexError:
                    admission_rate = "데이터 없음"

                school_data.append({
                    "학교명": school_name,
                    "학업성취도 평균": achievement,
                    "특목고 진학률": admission_rate
                })

        return pd.DataFrame(school_data)

    def calculate_ranking(self):
        """학군 랭크 계산"""
        school_achievement_list = self.fetch_school_achievement()
        if not school_achievement_list:
            print("데이터를 가져오지 못했습니다.")
            return None

        print("=" * 10)
        print("학교별 학업성취도 평균 및 특목고 진학률:")

        # 학업성취도 기준 카운터 초기화
        achievement_above_95 = 0
        achievement_above_90 = 0
        achievement_above_85 = 0

        for school in school_achievement_list:
            print(f"{school['학교명']}: "
                  f"학업성취도 {school['학업성취도 평균']}, "
                  f"특목고 진학률 {school['특목고 진학률']}")

            # 학업성취도 값 처리
            try:
                achievement = float(school['학업성취도 평균'].replace('%', ''))
                rounded_achievement = round(achievement, 1)  # 소수점 첫째 자리에서 반올림

                # 학업성취도 조건별 카운트
                if rounded_achievement >= 95:
                    achievement_above_95 += 1
                if rounded_achievement >= 90:
                    achievement_above_90 += 1
                if rounded_achievement >= 85:
                    achievement_above_85 += 1
            except ValueError:
                print(f"잘못된 학업성취도 데이터 형식: {school['학업성취도 평균']}")

        print("=" * 10)
        # 결과 출력
        print("학업성취도 기준 학교 수:")
        print(f"95% 이상: {achievement_above_95}개")
        print(f"90% 이상: {achievement_above_90}개")
        print(f"85% 이상: {achievement_above_85}개")

        # 학군 랭크 매기기
        if achievement_above_95 >= 3:
            rank = "S"
        elif achievement_above_90 >= 3:
            rank = "A"
        elif achievement_above_85 >= 3:
            rank = "B"
        else:
            rank = "C"

        print("=" * 10)
        print(f"학군 랭크: {rank}")
        return rank

