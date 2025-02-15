import requests
import urllib3
import pandas as pd

# category_code는 여기 참고: https://developers.kakao.com/docs/latest/ko/local/dev-guide

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # InsecureRequestWarning 방지
# # 모든 행과 열을 출력하도록 설정
# pd.set_option('display.max_rows', None)  # 출력 가능한 최대 행 개수
# pd.set_option('display.max_columns', None)  # 출력 가능한 최대 열 개수

class PlaceSearcher:
    def __init__(self, api_key="d7514f12a0f0d5e317dc677c7bcd97af"):
        self.api_key = api_key
        self.categories = {
            "백화점": {"query": "백화점", "allowed_names": ["신세계백화점", "롯데백화점", "현대백화점"]},
            "대형마트": {"query": None, "category_code": "MT1", "allowed_names": ["롯데마트", "메가마트", "이케아", "가정,생활 > 대형마트 > 이마트", "가정,생활 > 대형마트 > 홈플러스", "코스트코", "트레이더스 홀세일 클럽"]},
            "종합병원": {"query": "종합병원", "allowed_names": None},
            "스타벅스": {"query": "스타벅스", "allowed_names": None},
            "문화시설": {"query": None, "category_code": "CT1", "allowed_names": None},
            "소아청소년과": {"query": "소아청소년과", "allowed_names": None},
            "유기농마트": {"query": "유기농마트", "allowed_names": None},
            "도서관": {"query": "도서관", "allowed_names": None},
            "공원": {"query": "공원", "allowed_names": None},
            "체육시설": {"query": "체육관", "allowed_names": None}
        }
        self.results = {category: [] for category in self.categories}
        self.all_places = {category: [] for category in self.categories}

    def get_coordinates_from_sgg(self, sido_name, sigungu_name):
        url = "https://dapi.kakao.com/v2/local/search/address.json"
        headers = {"Authorization": f"KakaoAK {self.api_key}"}
        params = {"query": f"{sido_name} {sigungu_name}"}
        response = requests.get(url, params=params, headers=headers, verify=False)

        if response.status_code == 200:
            data = response.json()
            if data['documents']:
                return data['documents'][0]['y'], data['documents'][0]['x']
        return None, None

    def search_places(self, latitude, longitude, sigungu_name, category):
        params = {"x": longitude, "y": latitude, "radius": 20000}
        category_info = self.categories[category]
        url = "https://dapi.kakao.com/v2/local/search/keyword.json" if category_info["query"] else "https://dapi.kakao.com/v2/local/search/category.json"
        headers = {"Authorization": f"KakaoAK {self.api_key}"}
        if category_info["query"]:
            params["query"] = category_info["query"]
        elif category_info["category_code"]:
            params["category_group_code"] = category_info["category_code"]

        try:
            response = requests.get(url, headers=headers, params=params, verify=False)
            response.raise_for_status()
            places = response.json().get('documents', [])
            results = []
            seen_places = set()
            seen_addresses = set()

            for place in places:
                place_id = place['id']
                place_name = place['place_name']
                category_name = place.get('category_name', '')
                address = place.get('address_name', '정보 없음')

                # allowed_names가 category_name에 포함되면 해당 장소를 추가
                if category_info["allowed_names"] and not any(name in category_name for name in category_info["allowed_names"]):
                    continue

                if place_id not in seen_places and address not in seen_addresses and sigungu_name in place.get('road_address_name', ''):
                    seen_places.add(place_id)
                    seen_addresses.add(address)
                    results.append({
                        "장소 이름": place_name,
                        "카테고리": category_name,
                        "주소": address,
                        "위도": place['y'],
                        "경도": place['x']
                    })

            return pd.DataFrame(results)
        except requests.exceptions.RequestException as e:
            print(f"요청 오류: {e}")
            return pd.DataFrame()

    def search_all_categories(self, latitude, longitude, sigungu_name):
        category_results = {}
        for category in self.categories:
            category_results[category] = self.search_places(latitude, longitude, sigungu_name, category)
        return category_results

    def get_results_for_sgg(self, sido_name, sigungu_names):
        for sigungu_name in sigungu_names:
            latitude, longitude = self.get_coordinates_from_sgg(sido_name, sigungu_name)
            if latitude and longitude:
                category_results = self.search_all_categories(latitude, longitude, sigungu_name)

                # 카테고리별로 개수를 results 딕셔너리에 저장
                for category, df in category_results.items():
                    self.results[category].append(len(df))

                # 카테고리별로 장소 정보를 all_places에 추가
                for category, df in category_results.items():
                    for place in df.to_dict(orient="records"):
                        place["시군구"] = sigungu_name
                        self.all_places[category].append(place)

        # 각 카테고리별로 장소 정보를 데이터프레임으로 변환하고 출력
        all_places_df = pd.DataFrame(columns=["카테고리", "시군구", "장소 이름", "주소", "위도", "경도"])
        for category in self.categories:
            category_df = pd.DataFrame(self.all_places[category])
            category_df["카테고리"] = category
            all_places_df = pd.concat([all_places_df, category_df], ignore_index=True)

        # 랭킹 점수 총합 열 추가
        final_df = pd.DataFrame(self.results, index=sigungu_names)
        final_df['랭킹 점수 합계'] = final_df.sum(axis=1)

        return final_df, all_places_df

    def calculate_ranking(self, final_df, sigungu_name):
        # sigungu_name에 해당하는 행을 선택
        sigungu_data = final_df.loc[sigungu_name]

        # 백화점과 대형마트가 1 이상인 경우 계산
        department_store_count = sigungu_data["백화점"] >= 1
        supermarket_count = sigungu_data["대형마트"] >= 1

        # 등급 판별
        if department_store_count >= 2:
            rank = "S"
        elif department_store_count >= 1:
            rank = "A"
        elif supermarket_count >= 1:
            rank = "B"
        else:
            rank = "C"

        # 결과 반환
        return {'등급': rank, '백화점 수': department_store_count, '대형마트 수': supermarket_count}

