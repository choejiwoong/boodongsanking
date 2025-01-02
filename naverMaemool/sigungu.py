import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
import time

class RegionInfo:
    def __init__(self):
        self.cookies = {
            'NNB': 'QBJH3FYZZ44WM', 'NaverSuggestUse': 'use%26unuse', 'ASID': 'd372c8ac0000018f6ca118b20000004b',
            'NFS': '2', '_ga': 'GA1.1.1708709179.1715900740', 'nstore_session': 'e2xvvnF4PNOoR4AVoeHCceZl',
            'NV_WETR_LOCATION_RGN_M': '"V0ROWkwwMDAxNQ=="', 'authorization': 'Bearer YOUR_AUTH_TOKEN'
        }
        self.headers = {
            'Accept': '*/*', 'Accept-Language': 'ko-KR', 'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://new.land.naver.com/search'
        }

    # # HTTPS 경고 숨기기
    # warnings.simplefilter("ignore", InsecureRequestWarning)

    def _get_json(self, url):
        response = requests.get(url, cookies=self.cookies, headers=self.headers, verify=False)
        return response.json() if response.status_code == 200 else {}

    # 도시 정보 dict
    def get_si_dict(self):
        url = 'https://m.land.naver.com/map/getRegionList?cortarNo=0000000000'
        return {region['CortarNm']: region['CortarNo'] for region in self._get_json(url).get('result', {}).get('list', [])}

    # 군구 정보 dict
    def get_gungu_dict(self, si_name):
        si_codes = self.get_si_dict()
        base_code = si_codes.get(si_name)
        if not base_code:
            return {}
        url = f'https://m.land.naver.com/map/getRegionList?cortarNo={base_code}'
        return {region['CortarNm']: region['CortarNo'] for region in self._get_json(url).get('result', {}).get('list', [])}

    # 동 정보 dict
    def get_dong_list(self, si_name, gungu_name):
        gungu_codes = self.get_gungu_dict(si_name)
        base_code = gungu_codes.get(gungu_name)
        if not base_code:
            return []
        url = f'https://m.land.naver.com/map/getRegionList?cortarNo={base_code}'
        return [{
            'CortarNm': region['CortarNm'],
            'CortarNo': region['CortarNo'],
        } for region in self._get_json(url).get('result', {}).get('list', [])]

    # 동 내 아파트 단지 정보 dict
    def get_apt_list_dict(self, si_name, gungu_name):
        dong_codes = self.get_dong_list(si_name, gungu_name)
        apt_list_dict = {}
        for dong_code in dong_codes:
            url = f"https://m.land.naver.com/complex/ajax/complexListByCortarNo?cortarNo={dong_code['CortarNo']}"
            # JSON 데이터 가져오기
            data = self._get_json(url).get('result', [])
            # hscpTypeCd가 "A01"인 항목 필터링 후 딕셔너리로 변환
            filtered_dict = {apt['hscpNo']: apt['hscpNm'] for apt in data if apt.get('hscpTypeCd') == 'A01'}
            apt_list_dict.update(filtered_dict)
        return apt_list_dict

    # 아파트 매물 정보 dict
    def get_apt_maemool_dict(self, si_name, gungu_name, apt_name):
        apt_list_dict = self.get_apt_list_dict(si_name, gungu_name)
        print(apt_list_dict)
        all_results = []  # 모든 페이지에서 가져온 결과를 저장할 리스트
        for key, value in apt_list_dict.items():
            # if apt_name in value:  # apt_name이 value의 일부와 일치하면
                page = 0
                while True:
                    # 페이지별 URL
                    url = f"https://fin.land.naver.com/front-api/v1/complex/article/list?complexNumber={key}&tradeTypes=A1&userChannelType=PC&page={page}"
                    # JSON 데이터 가져오기
                    response = self._get_json(url)
                    # 결과 데이터 추출
                    results = response.get('result', {}).get('list', [])
                    # 결과가 없으면 반복 종료
                    if not results:
                        break
                    # 결과가 있으면 all_results에 추가
                    all_results.extend(results)
                    # 다음 페이지로 이동
                    page += 1
        return all_results if all_results else []

    def parse_articles(self, response):
        # List to hold articles in dictionary format
        all_articles = []
        for article in response:
            # 동일매물 묶기
            representative_info = article.get('representativeArticleInfo', {})
            # 필요한 정보만 추출하여 dict 형태로 변환
            article_data = {
                "매물번호": representative_info.get("articleNumber"),
                "아파트명": representative_info.get("complexName"),
                "호가": representative_info.get("priceInfo", {}).get("dealPrice"),
                "동": representative_info.get("dongName", {}),
                "층": representative_info.get("articleDetail", {}).get("floorInfo"),
                "면적": representative_info.get("spaceInfo", {}).get("supplySpace", "N/A"),  # "면적"이 없으면 "N/A"로 대체
                "타입": representative_info.get("spaceInfo", {}).get("exclusiveSpaceName", "N/A"),
                "방향": representative_info.get("articleDetail", {}).get("direction", "N/A"),
                "설명": representative_info.get("articleDetail", {}).get("articleFeatureDescription", "N/A"),
                "등록일자": representative_info.get("verificationInfo", {}).get("exposureStartDate", "N/A"),
                "공인중개사": representative_info.get("brokerInfo", {}).get("brokerageName", "N/A"),
            }
            all_articles.append(article_data)
        return all_articles if all_articles else []


#if __name__ == '__main__':
#    regioninfo = RegionInfo()
#    get_apt_maemool_dict = regioninfo.get_apt_maemool_dict('부산시', '연제구', '거제1차') # 예시: 8747: 거제1차현대홈타운
#    print(regioninfo.parse_articles(response=get_apt_maemool_dict))