import requests

class RegionInfo:
    def __init__(self):
        self.cookies = {
            'NNB': 'QBJH3FYZZ44WM',
            'NaverSuggestUse': 'use%26unuse',
            '_fwb': '120tha1PVbTbfzqyAZXtOZ5.1715509356751',
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
            'wcs_bt': '4f99b5681ce60:1732693422',
            'NV_WETR_LAST_ACCESS_RGN_M': '"V0ROWkwwMDAxNQ=="',
            'NV_WETR_LOCATION_RGN_M': '"V0ROWkwwMDAxNQ=="',
            'SHOW_FIN_BADGE': 'Y',
            'NAC': 'rzPyBcwLs7EF',
            'NACT': '1',
            'nhn.realestate.article.rlet_type_cd': 'A01',
            'nhn.realestate.article.trade_type_cd': '""',
            'REALESTATE': 'Wed%20Jan%2001%202025%2011%3A32%3A30%20GMT%2B0900%20(Korean%20Standard%20Time)',
            'BUC': '-4kZc3eS9THt39xeiYn2u1fk4hd91e2Wr3j5oAHXwsU=',
        }
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            # 'Cookie': 'NNB=QBJH3FYZZ44WM; NaverSuggestUse=use%26unuse; _fwb=120tha1PVbTbfzqyAZXtOZ5.1715509356751; ASID=d372c8ac0000018f6ca118b20000004b; NFS=2; _ga_EFBDNNF91G=GS1.1.1716793361.3.0.1716793361.0.0.0; _ga=GA1.1.1708709179.1715900740; _fwb=127T1NS2yUR0tQBRMA5sX8j.1718159969845; landHomeFlashUseYn=Y; tooltipDisplayed=true; _ga_8P4PY65YZ2=GS1.1.1722424213.1.1.1722424362.34.0.0; _ga_451MFZ9CFM=GS1.1.1726817041.2.1.1726817429.0.0.0; _gcl_au=1.1.394087561.1729586842; naverfinancial_CID=2646fb100b404624824589879711ac85; _ga_Q7G1QTKPGB=GS1.1.1729586841.1.1.1729586980.0.0.0; nstore_session=e2xvvnF4PNOoR4AVoeHCceZl; nstore_pagesession=izEkQlqQTkFUolsnfpR-092277; wcs_bt=4f99b5681ce60:1732693422; NV_WETR_LAST_ACCESS_RGN_M="V0ROWkwwMDAxNQ=="; NV_WETR_LOCATION_RGN_M="V0ROWkwwMDAxNQ=="; SHOW_FIN_BADGE=Y; NAC=rzPyBcwLs7EF; NACT=1; nhn.realestate.article.rlet_type_cd=A01; nhn.realestate.article.trade_type_cd=""; REALESTATE=Wed%20Jan%2001%202025%2011%3A32%3A30%20GMT%2B0900%20(Korean%20Standard%20Time); BUC=-4kZc3eS9THt39xeiYn2u1fk4hd91e2Wr3j5oAHXwsU=',
            'Referer': 'https://new.land.naver.com/search?ms=35.1788973,129.081145,16&a=APT:ABYG:JGC:PRE&e=RETAIL&ad=true',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IlJFQUxFU1RBVEUiLCJpYXQiOjE3MzU2OTg3NTAsImV4cCI6MTczNTcwOTU1MH0.c6nBfkAPzPxPr0G14zYSPzBIIodtySVsuhEopOeU5uQ',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

    def get_region_data(self, region_name):
        response = requests.get('https://new.land.naver.com/api/regions/list?cortarNo=2600000000', cookies=self.cookies, headers=self.headers, verify=False) # 부산

        if response.status_code == 200:
            region_list = response.json().get('regionList', [])
            for region in region_list:
                if region['cortarName'] == region_name:
                    return {
                        'cortarNo': region['cortarNo'], # 지역코드
                        'centerLat': region['centerLat'], # 지역위도
                        'centerLon': region['centerLon'] # 지역경도
                    }
        return None