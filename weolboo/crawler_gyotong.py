import requests
import pandas as pd
import re
import urllib3
from bs4 import BeautifulSoup
import plotly.express as px
import streamlit as st

# 지하철 데이터는 여기 참고: https://www.data.go.kr/data/3057229/fileData.do#/
# 지하철, 버스 이용률 데이터는 여기 참고: https://stcis.go.kr/pivotIndi/wpsPivotIndicator.do?siteGb=P&indiClss=IC01

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # InsecureRequestWarning 방지
# # 모든 행과 열을 출력하도록 설정
# pd.set_option('display.max_rows', None)  # 출력 가능한 최대 행 개수
# pd.set_option('display.max_columns', None)  # 출력 가능한 최대 열 개수

class Gyotong:
    def __init__(self):
        self.base_url = "https://api.odcloud.kr/api"
        self.api_key = "9bg1tTFeumrhYeac4TTMmKVoiH5BV2qRxRlwEm/gFZB2vrjW+PpwQgFI0s7p5w9ipE7/qtijjWOmrxwEODkyMA=="
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.df_list = []  # 데이터를 저장할 리스트
        self.seen_data = set()  # 중복 체크용 Set
        self.work_hours = ['06시-07시', '07시-08시', '08시-09시', '09시-10시']  # 출근시간
        self.out_hours = ['16시-17시', '17시-18시', '18시-19시', '19시-20시']  # 퇴근시간

    def get_metadata(self):
        """API 메타데이터 가져오기"""
        metadata_url = "https://infuser.odcloud.kr/oas/docs?namespace=3057229/v1"
        response = requests.get(metadata_url, headers=self.headers, verify=False)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None

    def find_latest_api(self, data):
        """최신 연도와 엔드포인트 찾기"""
        latest_year = 0
        latest_endpoint = None

        for endpoint, details in data["paths"].items():
            description = details["get"].get("summary", "")  # API 설명 가져오기
            match = re.search(r"(\d{4})[\s\-/]*(12)", description)

            if match:
                year = int(match.group(1))
                month = int(match.group(2))

                # 가장 최신 연도의 12월 데이터를 선택
                if year > latest_year:
                    latest_year = year
                    latest_endpoint = endpoint

        return latest_year, latest_endpoint

    def fetch_data(self, endpoint):
        """최신 데이터 가져오기"""
        page = 1
        while True:
            params = {
                "page": page,
                "perPage": 5000,  # 최대 데이터 요청
                "returnType": "JSON",
                "serviceKey": self.api_key  # 인증 방식이 쿼리 파라미터일 경우 추가
            }
            latest_url = f"{self.base_url}{endpoint}"
            latest_response = requests.get(latest_url, headers=self.headers, params=params, verify=False)

            if latest_response.status_code == 200:
                latest_data = latest_response.json()
                if not latest_data['data']:  # 데이터가 없으면 종료
                    print("더 이상 가져올 데이터가 없습니다.")
                    break
                df = pd.DataFrame(latest_data['data'])

                # 중복 제거 로직 개선
                df_tuples = set(df.itertuples(index=False, name=None))
                new_data = [row for row in df_tuples if row not in self.seen_data]
                if new_data:
                    self.seen_data.update(new_data)
                    new_df = pd.DataFrame(new_data, columns=df.columns)

                    # NaN 값 처리 후 출근/퇴근시간 합산
                    new_df['출근시간'] = new_df[self.work_hours].fillna(0).sum(axis=1)
                    new_df['퇴근시간'] = new_df[self.out_hours].fillna(0).sum(axis=1)
                    new_df['출퇴근시간'] = new_df['출근시간'] + new_df['퇴근시간']

                    self.df_list.append(new_df)
                page += 1  # 다음 페이지로 이동

            else:
                print(f"Error: {latest_response.status_code}, {latest_response.text}")
                break

    def process_data(self):
        """데이터 처리 및 집계"""
        if self.df_list:
            final_df = pd.concat(self.df_list, ignore_index=True)
            # 날짜와 승하차 구분까지 포함하여 집계
            result_total = final_df.groupby(['역번호', '역명'])[['출근시간', '퇴근시간', '출퇴근시간']].sum().reset_index()

            # 출퇴근_총합 내림차순 정렬
            final_result = result_total.sort_values(by='출퇴근시간', ascending=False).reset_index(drop=True)
            # 역번호 index로 하기
            final_result.set_index("역번호", inplace=True)

            # 천 단위 구분기호 추가
            for col in ['출근시간', '퇴근시간', '출퇴근시간']:
                final_result[col] = final_result[col].apply(lambda x: f'{x:,}')

            return final_result
        else:
            return None

    def fetch_transport_data(self):
        """응용 지표(대중교통 수단간 분담률) 데이터 가져오기"""
        # 요청 URL
        url = "https://stcis.go.kr/pivotIndi/indicatorAjax.do"

        # 요청 페이로드 (데이터)
        params = {
            "indiCd": "Z01715",
            "siteGb": "P",
            "indiNm": "응용 지표(대중교통 수단간 분담률)",
            "searchDateGubun": "1",
            "searchFromYear": "2024",
            "searchToYear": "2024",
            "searchFromMonth": "2025-01",
            "searchToMonth": "2025-01",
            "searchFromDay": "2025-01-31",
            "searchFromDayDD": "20250131",
            "searchToDay": "2025-01-31",
            "searchAreaGubun": "1",
            "zoneSd": "11,26,27,28,29,30,31,36,41,43,44,45,46,47,48,50,51,52",
            "zoneSgg": "",
            "zoneEmd": "",
            "zoneDstrct": "",
            "selectZoneSd": "",
            "selectZoneSgg": "",
            "tcboId": "",
            "excclcAreaCd": "",
            "routeId": "",
            "routeSdCd": "",
            "routeSggCd": "",
            "tcboIdSttn": "",
            "excclcAreaCdSttn": "",
            "sttnId": "",
            "sttnIdGrp": "",
            "sttnSdCd": "",
            "sttnSggCd": "",
            "searchODAreaGubun": "",
            "searchODAreaGubun_2": "",
            "rdStgptSel": "Y",
            "searchStgptZoneSd": "",
            "searchStgptZoneSgg": "",
            "searchStgptZoneEmd": "",
            "rdAlocSel": "Y",
            "searchAlocZoneSd": "",
            "searchAlocZoneSgg": "",
            "searchAlocZoneEmd": "",
            "pgngYn": "Y",
            "daybyTblNm": "DM_WAYTRCV_001",
            "mnbyTblNm": "DM_MMBY_WAYTRCV_001",
            "yrbyTblNm": "DM_YRBY_WAYTRCV_001",
            "dstrctTblNm": "DM_DCTBY_WAYTRCV_T",
            "mnbyDstrctTblNm": "DM_MMBY_DCTBY_WAYTRCV_T",
            "yrbyDstrctTblNm": "DM_YRBY_DCTBY_WAYTRCV_T"
        }

        # 요청 헤더
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        # POST 요청 보내기
        response = requests.get(url, params=params, headers=headers, verify=False)

        # 응답 데이터 확인
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # 테이블 찾기
            table = soup.find("table", {"class": "main_tb"})

            # # 테이블 헤더 추출
            # headers = [th.text.strip() for th in table.find_all("td", class_="header_style")]

            # 새로운 헤더 목록 정의
            filtered_headers = ['시도', '시내', '시외', '좌석', '마을', '광역', '농어촌', '공항', '도시철도', '기타']

            # 데이터 추출
            data = []
            rows = table.find_all("tr")[2:]  # 첫 두 개는 헤더 관련, 실제 데이터는 3번째 행부터

            for row in rows:
                cols = [td.text.strip() for td in row.find_all("td")]
                if cols:
                    data.append(cols)

            cleaned_data = []
            for i, row in enumerate(data):
                if i == 0:  # 첫 번째 행만 수정
                    cleaned_data.append(row[1:])  # 첫 번째 열 제외하고 나머지 열만 추가
                else:  # 나머지는 그대로 추가
                    cleaned_data.append(row)  # 첫 번째 열 제외하고 나머지 열만 추가

            # 데이터프레임 생성
            df_filtered = pd.DataFrame(cleaned_data, columns=filtered_headers)

            # '도시철도'와 '기타' 열을 숫자형으로 변환
            df_filtered['도시철도'] = pd.to_numeric(df_filtered['도시철도'], errors='coerce')
            df_filtered['기타'] = pd.to_numeric(df_filtered['기타'], errors='coerce')
            # '버스' 열 계산 (100 - (도시철도 + 기타))
            df_filtered['버스'] = 100 - (df_filtered['도시철도'] + df_filtered['기타'])
            # '시도', '버스', '도시철도', '기타' 열만 선택하여 출력
            df_filtered = df_filtered[['시도', '버스', '도시철도', '기타']]
            # '시도', '버스', '도시철도', '기타' 열만 선택하고 '도시철도' 내림차순 정렬
            df_filtered = df_filtered[['시도', '버스', '도시철도', '기타']].sort_values(by='도시철도', ascending=False)

            # 결과 출력
            return df_filtered
        else:
            print(f"요청 실패: {response.status_code}")
            return None

    def get_transport_div_plotly(self, df):
        if df is None:
            st.write("데이터를 가져올 수 없습니다.")
            return None
        # 색상 매핑
        color_map = px.colors.qualitative.Pastel1  # 또는 Pastel2
        # Streamlit에서 DataFrame 출력
        if not df.empty:
            # 시군구별 누적 막대 그래프 그리기
            fig = px.bar(df,
                         x='시도',
                         y=['버스', '도시철도', '기타'],
                         labels={"value": "교통수단 비율(%)", "variable": "교통수단"},
                         color_discrete_sequence=color_map,
                         # text=flattened_text,  # Use flattened text values
                         barmode='stack')
            return fig


# if __name__ == "__main__":
#     # DataCollector 객체 생성
#     collector = Gyotong()
#
#     # 메타데이터 가져오기
#     fetch_transport_data = collector.fetch_transport_data()
#     print(fetch_transport_data)


############## 이 코드는 회사에서 안돌아감... 집에서 해야겠당
import requests

# 카카오맵 API 키
KAKAO_API_KEY = "d7514f12a0f0d5e317dc677c7bcd97af"

# 카카오맵 장소 검색 API URL
SEARCH_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"
DIRECTIONS_URL = "https://apis-navi.kakaomobility.com/v1/directions"


# 장소 이름을 좌표로 변환하는 함수
def get_coordinates(place_name):
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": place_name}

    response = requests.get(SEARCH_URL, headers=headers, params=params, timeout=10, verify=False)

    if response.status_code == 200:
        data = response.json()
        if data['documents']:
            place = data['documents'][0]
            return float(place['x']), float(place['y'])  # (경도, 위도)
        else:
            print(f"장소 '{place_name}'를 찾을 수 없습니다.")
            return None
    else:
        print(f"장소 검색 API 요청 실패: {response.status_code}")
        return None


# # 출발지와 도착지 입력
# origin_name = "부산 종합운동장역"
# destination_name = "서면역"
#
# # 좌표 검색
# origin_coords = get_coordinates(origin_name)
# destination_coords = get_coordinates(destination_name)
#
# if origin_coords and destination_coords:
#     # 길찾기 API 요청
#     headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
#     params = {
#         "origin": f"{origin_coords[0]},{origin_coords[1]}",
#         "destination": f"{destination_coords[0]},{destination_coords[1]}",
#         "priority": "RECOMMEND",
#         "car_fuel": "GASOLINE",
#         "car_hipass": False,
#     }
#
#     response = requests.get(DIRECTIONS_URL, headers=headers, params=params, timeout=10, verify=False)
#
#     if response.status_code == 200:
#         data = response.json()
#         if data['routes'][0]['result_code'] == 0:
#             distance = data['routes'][0]['summary']['distance']
#             duration = data['routes'][0]['summary']['duration']
#
#             hours = duration // 3600  # 시간
#             minutes = (duration % 3600) // 60  # 분
#             seconds = duration % 60  # 초
#
#             # 출력
#             print(f"출발지: {origin_name} ({origin_coords})")
#             print(f"도착지: {destination_name} ({destination_coords})")
#             print(f"경로 거리: {distance / 1000:.2f}km")
#             print(f"예상 소요 시간: {duration}초 ({hours}시간 {minutes}분 {seconds}초)")
#         else:
#             print("길찾기 API에서 결과를 찾을 수 없습니다.")
#     else:
#         print(f"길찾기 API 요청 실패: {response.status_code}")



