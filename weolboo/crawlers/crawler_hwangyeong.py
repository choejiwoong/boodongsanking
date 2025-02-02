###### 반쯤 완료??
import requests

# Kakao API 키
api_key = "d7514f12a0f0d5e317dc677c7bcd97af"  # 발급받은 API 키를 입력하세요

# 시군구명으로 위도, 경도 구하는 함수
def get_coordinates_from_sgg(sgg_name):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {
        "Authorization": f"KakaoAK {api_key}",
    }
    params = {
        "query": sgg_name,  # 시군구명
    }
    response = requests.get(url, params=params, headers=headers, verify=False)

    if response.status_code == 200:
        data = response.json()
        if data['documents']:
            # 첫 번째 문서에서 좌표 정보 가져오기
            latitude = data['documents'][0]['y']
            longitude = data['documents'][0]['x']
            return latitude, longitude
        else:
            print("해당 시군구에 대한 좌표 정보를 찾을 수 없습니다.")
            return None, None
    else:
        print(f"Error: {response.status_code}, Response: {response.text}")
        return None, None


# 카테고리별 장소 검색 함수
def search_category(category_code, category_name, query=None, latitude=None, longitude=None, sigungu_name=None):
    category_url = "https://dapi.kakao.com/v2/local/search/category.json" if query is None else "https://dapi.kakao.com/v2/local/search/query.json"
    category_headers = {
        "Authorization": f"KakaoAK {api_key}",
    }
    params = {
        "category_group_code": category_code,  # 카테고리 코드
        "radius": 2000,  # 검색 반경 (단위: 미터)
        "x": longitude,  # 경도
        "y": latitude,  # 위도
    }
    if query:
        params["query"] = query  # 쿼리 파라미터로 키워드 설정

    page = 1
    total_count = 0  # 카운팅할 개수
    seen_places = set()  # 이미 출력된 장소를 기록할 집합
    while True:
        params["page"] = page
        response = requests.get(category_url, params=params, headers=category_headers, verify=False)
        if response.status_code == 200:
            data = response.json()
            places = data['documents']
            if not places:
                break
            for place in places:
                place_id = place['id']  # 고유 ID를 사용하여 중복을 방지
                if place_id not in seen_places and sigungu_name in place['road_address_name']:  # 해당 시군구명에 속한 장소만 필터링
                    seen_places.add(place_id)
                    total_count += 1
                    print(f"{category_name} 이름: {place['place_name']}")
                    print(f"주소: {place['address_name']}")
                    print(f"위도: {place['y']}, 경도: {place['x']}")
                    print('-' * 50)
            # 페이지가 더 있는지 확인
            if page * 15 >= data['meta']['total_count']:  # 한 페이지에 최대 15개 장소가 나옴
                break
            page += 1
        else:
            print(f"{category_name} 검색 오류: {response.status_code}, Response: {response.text}")
            break
    return total_count


# 스타벅스 검색 함수
def search_starbucks(latitude, longitude, sigungu_name):
    search_query = '스타벅스'
    url = f'https://dapi.kakao.com/v2/local/search/keyword.json?query={search_query}'
    headers = {
        "Authorization": f"KakaoAK {api_key}",
    }
    params = {
        "x": longitude,  # 경도
        "y": latitude,  # 위도
        "radius": 2000,  # 검색 반경 (단위: 미터)
    }

    response = requests.get(url, headers=headers, params=params, verify=False)
    total_count = 0  # 스타벅스 개수를 셀 변수
    if response.status_code == 200:
        data = response.json()
        places = data['documents']
        seen_places = set()  # 이미 출력된 장소 고유 ID 기록
        for place in places:
            place_id = place['id']
            # 스타벅스만 필터링
            if '스타벅스' in place['place_name'] and place_id not in seen_places and sigungu_name in place['road_address_name']:
                seen_places.add(place_id)
                total_count += 1
                print(f"스타벅스 이름: {place['place_name']}")
                print(f"주소: {place['address_name']}")
                print(f"위도: {place['y']}, 경도: {place['x']}")
                print('-' * 50)
    else:
        print(f"스타벅스 검색 오류: {response.status_code}, Response: {response.text}")
    return total_count  # 스타벅스 개수 반환


# 백화점 검색 함수
def search_department_store(latitude, longitude, sigungu_name):
    search_query = '백화점'
    url = f'https://dapi.kakao.com/v2/local/search/keyword.json?query={search_query}'
    headers = {
        "Authorization": f"KakaoAK {api_key}",
    }
    params = {
        "x": longitude,  # 경도
        "y": latitude,  # 위도
        "radius": 2000,  # 검색 반경 (단위: 미터)
    }

    response = requests.get(url, headers=headers, params=params, verify=False)
    total_count = 0  # 백화점 개수를 셀 변수
    if response.status_code == 200:
        data = response.json()
        places = data['documents']
        seen_places = set()  # 이미 출력된 장소 고유 ID 기록
        for place in places:
            place_id = place['id']
            # 백화점만 필터링
            if '백화점' in place['place_name'] and '백화점' in place['category_name'] and place_id not in seen_places and sigungu_name in place['road_address_name']:
                seen_places.add(place_id)
                total_count += 1
                print(f"백화점 이름: {place['place_name']}")
                print(f"주소: {place['address_name']}")
                print(f"위도: {place['y']}, 경도: {place['x']}")
                print('-' * 50)
    else:
        print(f"백화점 검색 오류: {response.status_code}, Response: {response.text}")
    return total_count  # 백화점 개수 반환


# 장소 검색을 위한 함수
def search_places(latitude, longitude, sigungu_name):
    # 대형마트 검색
    mart_count = search_category("MT1", "대형마트", latitude=latitude, longitude=longitude, sigungu_name=sigungu_name)

    # 종합병원 검색 (병원 중 종합병원만 필터링)
    hospital_count = 0
    page = 1
    seen_hospitals = set()  # 이미 출력된 병원 고유 ID 기록
    while True:
        hospital_url = "https://dapi.kakao.com/v2/local/search/category.json"
        hospital_params = {
            "category_group_code": "HP8",  # 병원 카테고리 코드
            "radius": 2000,  # 검색 반경 (단위: 미터)
            "x": longitude,  # 경도
            "y": latitude,  # 위도
            "page": page,  # 페이지 번호
        }
        response = requests.get(hospital_url, params=hospital_params, headers={"Authorization": f"KakaoAK {api_key}"}, verify=False)
        if response.status_code == 200:
            data = response.json()
            places = data['documents']
            if not places:
                break
            for place in places:
                place_id = place['id']
                # 병원 카테고리가 '종합병원'인 경우만 필터링
                if (('종합병원' in place['category_name']) or ('대학병원' in place['category_name'])) and place_id not in seen_hospitals and sigungu_name in place['road_address_name']:
                    seen_hospitals.add(place_id)
                    hospital_count += 1
                    print(f"종합병원 이름: {place['place_name']}")
                    print(f"주소: {place['address_name']}")
                    print(f"위도: {place['y']}, 경도: {place['x']}")
                    print('-' * 50)
            # 페이지가 더 있는지 확인
            if page * 15 >= data['meta']['total_count']:
                break
            page += 1
        else:
            print(f"종합병원 검색 오류: {response.status_code}, Response: {response.text}")
            break

    # 백화점 검색
    department_store_count = search_department_store(latitude, longitude, sigungu_name)

    # 스타벅스 검색
    starbucks_count = search_starbucks(latitude, longitude, sigungu_name)

    # 각 카테고리의 개수를 출력
    print(f"총 백화점 개수: {department_store_count}")
    print(f"총 대형마트 개수: {mart_count}")
    print(f"총 종합병원 개수: {hospital_count}")
    print(f"총 스타벅스 개수: {starbucks_count}")


# 예시: 부산 연제구의 대형마트, 병원, 백화점, 스타벅스 검색
sgg_name = ("부산 부산진구")
latitude, longitude = get_coordinates_from_sgg(sgg_name)

if latitude and longitude:
    search_places(latitude, longitude, sgg_name)
