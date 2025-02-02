import PublicDataReader as pdr

class SigunguCode:
    def __init__(self, sido_name: str, sigungu_name: str = None):
        self.sido_name = sido_name
        self.sigungu_name = sigungu_name
        self.sigungu_dict = {}

    def load_sigungu(self):
        # 행정동 코드 데이터 불러오기
        bdong_code = pdr.code_bdong()
        # 부산광역시에 해당하는 데이터 필터링
        filtered_code = bdong_code.loc[bdong_code['시도명'] == self.sido_name]
        # 시군구명을 입력했으면, 특정 시군구를 필터링
        if self.sigungu_name:
            filtered_code = filtered_code.loc[filtered_code['시군구명'] == self.sigungu_name]
        # # 중복된 행을 제거하여 고유한 '행정동코드'만 처리
        # filtered_code = filtered_code.drop_duplicates(subset=['행정동코드'])
        # 시군구별로 데이터를 추가
        for _, row in filtered_code.iterrows():
            sigungu_name = row['시군구명']
            hdong_name = row['읍면동명']
            sigungu_code = row['시군구코드']
            if sigungu_name:  # 시군구명이 빈 문자열이 아닐 경우만 추가
                self.sigungu_dict[sigungu_name] = sigungu_code

    def get_sigungu_dict(self):
        return dict(self.sigungu_dict)

sido_name = "부산광역시"
code = SigunguCode(sido_name)
code.load_sigungu()
print(code.get_sigungu_dict())