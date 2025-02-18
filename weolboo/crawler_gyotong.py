import requests
import pandas as pd
import re
import urllib3
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


# if __name__ == "__main__":
#     # DataCollector 객체 생성
#     collector = Gyotong()
#
#     # 메타데이터 가져오기
#     api_metadata = collector.get_metadata()
#
#     if api_metadata:
#         latest_year, latest_endpoint = collector.find_latest_api(api_metadata)
#         if latest_endpoint:
#             # 최신 데이터 가져오기
#             collector.fetch_data(latest_endpoint)
#             # 데이터 처리 및 집계
#             final_result = collector.process_data()
#
#             if final_result is not None:
#                 print(final_result.head(20))  # 상위 20개 데이터 출력
#             else:
#                 print("처리된 데이터가 없습니다.")
#         else:
#             print("최신 엔드포인트를 찾을 수 없습니다.")
#     else:
#         print("메타데이터를 가져올 수 없습니다.")


# 요청 보내기
url = "https://stcis.go.kr/pivotIndi/excelSearchCntAdd.do"

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}

payload = {
    "indiCd": "Z01701",
    "searchAreaGubun": "2",
    "siteGb": "P",
    "zoneSd": "26",
    "zoneSgg": "26440,26410,26710,26290,26170,26260,26230,26320,26530,26380,26140,26500,26470,26200,26110,26350",
    "zoneDstrct": "",
    "selectZoneSd": "26",
    "selectZoneSgg": ""
}

response = requests.post(url, headers=headers, data=payload, verify=False)

if response.status_code == 200:
    print(response)
#     with open("data.xlsx", "wb") as f:
#         f.write(response.content)
#     # 엑셀 파일을 pandas DataFrame으로 읽기
#     df = pd.read_excel("data.xlsx")
#     print(df.head())  # 첫 5개 행 출력
# else:
#     print(f"요청 실패: {response.status_code}")