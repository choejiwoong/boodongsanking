import pandas as pd
import requests
import re

# 모든 행과 열을 출력하도록 설정
pd.set_option('display.max_rows', None)  # 출력 가능한 최대 행 개수
pd.set_option('display.max_columns', None)  # 출력 가능한 최대 열 개수

# API 기본 정보
BASE_URL = "https://api.odcloud.kr/api"
API_KEY = "9bg1tTFeumrhYeac4TTMmKVoiH5BV2qRxRlwEm/gFZB2vrjW+PpwQgFI0s7p5w9ipE7/qtijjWOmrxwEODkyMA=="  # API 키 필요 시 입력

# 요청 헤더
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"  # 인증 방식에 따라 변경 가능
}

# API 메타데이터 가져오기
metadata_url = "https://infuser.odcloud.kr/oas/docs?namespace=3057229/v1"
response = requests.get(metadata_url, headers=headers, verify=False)

# 응답 확인
if response.status_code == 200:
    api_metadata = response.json()
else:
    print(f"Error: {response.status_code}, {response.text}")
    exit()

# 최신 데이터 엔드포인트 찾기
def find_latest_api(data):
    latest_year = 0
    latest_endpoint = None

    for endpoint, details in data["paths"].items():
        description = details["get"].get("summary", "")  # API 설명 가져오기
        match = re.search(r"(\d{4})", description)  # 연도 추출

        if match:
            year = int(match.group(1))
            if year > latest_year:
                latest_year = year
                latest_endpoint = endpoint

    return latest_year, latest_endpoint

latest_year, latest_endpoint = find_latest_api(api_metadata)

if latest_endpoint:
    print(f"최신 연도: {latest_year}")
    print(f"최신 엔드포인트: {latest_endpoint}")

    # 최신 데이터 가져오기
    latest_url = f"{BASE_URL}{latest_endpoint}"
    for i in range(50):
        params = {
            "page": i,
            "perPage": 1000,  # 최대 데이터 요청
            "returnType": "JSON",
            "serviceKey": API_KEY  # 인증 방식이 쿼리 파라미터일 경우 추가
        }

        latest_response = requests.get(latest_url, headers=headers, params=params, verify=False)

        if latest_response.status_code == 200:
            latest_data = latest_response.json()
            print("최신 데이터 가져오기 성공!")
            if latest_data['data'] == []:
                break

            df = pd.DataFrame(latest_data['data'])
            # print(df)

            # 출근시간
            work_hours = ['06시-07시', '07시-08시', '08시-09시', '09시-10시']
            # 퇴근시간
            out_hours = ['16시-17시', '17시-18시', '18시-19시', '19시-20시']

            # 출근시간과 퇴근시간의 합계 컬럼 추가
            df['출근시간_합계'] = df[work_hours].sum(axis=1)
            df['퇴근시간_합계'] = df[out_hours].sum(axis=1)
            df['출퇴근시간_합계'] = df['출근시간_합계'] + df['퇴근시간_합계']

            # 역번호, 역명, 구분(승차/하차)별 출퇴근 시간 합계
            result_by_type = df.groupby(['역번호', '역명', '구분'])[['출근시간_합계', '퇴근시간_합계', '출퇴근시간_합계']].sum().reset_index()

            # 역번호, 역명별 (승하차 합친) 출퇴근 시간 총합 추가
            result_total = df.groupby(['역번호', '역명'])[['출근시간_합계', '퇴근시간_합계', '출퇴근시간_합계']].sum().reset_index()
            result_total['구분'] = '총합'  # 구분 컬럼에 '총합' 표시]

            print(result_total)

            # # 승차/하차별 데이터와 총합 데이터 합치기
            # final_result = pd.concat([result_by_type, result_total], ignore_index=True)
            #
            # # 구분이 '총합'인 데이터를 기준으로 출퇴근_총합 내림차순 정렬
            # final_result = final_result.sort_values(by=['구분', '출퇴근시간_합계'], ascending=[True, False]).reset_index(drop=True)
            #
            # # 천 단위 구분기호 추가
            # for col in ['출근시간_합계', '퇴근시간_합계', '출퇴근_총합']:
            #     final_result[col] = final_result[col].apply(lambda x: f'{x:,}')
            #
            # # 결과 출력
            # print(final_result.head(20))

        else:
            print(f"Error: {latest_response.status_code}, {latest_response.text}")

else:
    print("최신 데이터를 찾을 수 없습니다.")





