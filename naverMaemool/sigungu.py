import requests

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

    def _get_json(self, url):
        response = requests.get(url, cookies=self.cookies, headers=self.headers, verify=False)
        return response.json() if response.status_code == 200 else {}

    def get_si_dict(self):
        url = 'https://m.land.naver.com/map/getRegionList?cortarNo=0000000000'
        return {region['CortarNm']: region['CortarNo'] for region in self._get_json(url).get('result', {}).get('list', [])}

    def get_gungu_dict(self, si_name):
        si_codes = self.get_si_dict()
        base_code = si_codes.get(si_name)
        if not base_code:
            return {}
        url = f'https://m.land.naver.com/map/getRegionList?cortarNo={base_code}'
        return {region['CortarNm']: region['CortarNo'] for region in self._get_json(url).get('result', {}).get('list', [])}

    def get_dong_list(self, si_name, gungu_name):
        gungu_codes = self.get_gungu_dict(si_name)
        base_code = gungu_codes.get(gungu_name)
        if not base_code:
            return []
        url = f'https://m.land.naver.com/map/getRegionList?cortarNo={base_code}'
        return [{
            'CortarNm': region['CortarNm'],
            'CortarNo': region['CortarNo'],
            'MapXCrdn': region['MapXCrdn'],
            'MapYCrdn': region['MapYCrdn']
        } for region in self._get_json(url).get('result', {}).get('list', [])]
