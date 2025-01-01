import time
import requests
import pandas as pd

class RealEstateFetcher:
    def __init__(self, region_data):
        self.cookies = {
            'NNB': 'QBJH3FYZZ44WM',
            'NaverSuggestUse': 'use%26unuse',
            'ASID': 'd372c8ac0000018f6ca118b20000004b',
            'NFS': '2',
            '_ga_EFBDNNF91G': 'GS1.1.1716793361.3.0.1716793361.0.0.0',
            '_ga': 'GA1.1.1708709179.1715900740',
            '_fwb': '127T1NS2yUR0tQBRMA5sX8j.1718159969845',
            'landHomeFlashUseYn': 'Y',
            'tooltipDisplayed': 'true',
            '_ga_8P4PY65YZ2': 'GS1.1.1722424213.1.1.1722424362.34.0.0',
            '_ga_451MFZ9CFM': 'GS1.1.1726817041.2.1.1726817429.0.0.0',
            '_gcl_au': '1.1.394087561.1729586842',
            'naverfinancial_CID': '2646fb100b404624824589879711ac85',
            '_ga_Q7G1QTKPGB': 'GS1.1.1729586841.1.1.1729586980.0.0.0',
            'nstore_session': 'e2xvvnF4PNOoR4AVoeHCceZl',
            'nstore_pagesession': 'izEkQlqQTkFUolsnfpR-092277',
            'NV_WETR_LAST_ACCESS_RGN_M': '"V0ROWkwwMDAxNQ=="',
            'NV_WETR_LOCATION_RGN_M': '"V0ROWkwwMDAxNQ=="',
            'SHOW_FIN_BADGE': 'Y',
            'NAC': 'rzPyBcwLs7EF',
            'NACT': '1',
            'JSESSIONID': 'A1B0E014930CD060BBD743A835F22F87',
            'REALESTATE': '1735708142146',
            'BUC': '2WfOYj1Jw0VTJ3IphOTz_YlY-QzKkDD6NAzt7GqoiRc=',
            'wcs_bt': '44058a670db444:1735708181',
        }

        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Referer': 'https://m.land.naver.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        self.params = {
            'rletTpCd': 'APT:ABYG:JGC', # APT: 아파트, ABYG: 아파트분양권, JGC: 재건축
            'tradTpCd': 'A1:B1', # A1: 매매, B1: 전세
            'z': '13', # 축척
            'lat': region_data['centerLat'], # 위도
            'lon': region_data['centerLon'], # 경도
            'btm': region_data['centerLat'] - 0.25, # 밑쪽 끝 위도
            'lft': region_data['centerLon'] - 0.25, # 왼쪽 끝 경도
            'top': region_data['centerLat'] + 0.25, # 위쪽 끝 위도
            'rgt': region_data['centerLon'] + 0.25, # 오른쪽 끝 경도
            'showR0': '',
            'cortarNo': region_data['cortarNo'],
            'page': 1,
        }

    def fetch_real_estate_data(self, page):
        # 페이지 값을 동적으로 설정
        self.params['page'] = page
        url = 'https://m.land.naver.com/cluster/ajax/articleList'
        response = requests.get(url, cookies=self.cookies, headers=self.headers, params=self.params, verify=False)
        if response.status_code == 200:
            return response.json().get("body", [])
        elif response.status_code == 307:
            print(f"총 {page} 페이지의 크롤링이 완료되었습니다.")
            return []
        else:
            print(f"Failed to fetch data for page {page}. Status code: {response.status_code}")
            return []

    def get_all_articles(self):
        all_articles = []
        page = 1
        while True:
            articles = self.fetch_real_estate_data(page)
            if not articles:
                break
            all_articles.extend(articles)
            page += 1
            # time.sleep(2)
        return all_articles

    def get_dataframe(self):
        # get_all_articles 메서드를 비동기적으로 호출
        all_articles = self.get_all_articles()

        if all_articles:
            data = [{
                "매물번호": article.get("atclNo"),
                "아파트명": article.get("atclNm"),
                "매매/전세": article.get("tradTpNm"),
                "호가": article.get("prc"),
                "동": article.get("bildNm"),
                "층": article.get("flrInfo"),
                "등록일자": article.get("atclCfmYmd"),
                "면적": article.get("spc2"),
                "방향": article.get("direction"),
                "태그": article.get("tagList"),
                "설명": article.get("atclFetrDesc"),
            } for article in all_articles]
            # DataFrame 생성
            df = pd.DataFrame(data)
            # # 중복값 제거 (매물번호 기준)
            # df = df.drop_duplicates(subset=["매물번호"], keep="first")
            return df
        else:
            return pd.DataFrame()