import PublicDataReader as pdr

class SigunguCode:
    def __init__(self, sido_name: str = None, sigungu_name: str = None):
        # 모든 시도 시군구
        self.sigungu_name_dict = {}
        # 광역시
        self.gwangyeok_list = ['부산광역시', '대구광역시', '인천광역시', '광주광역시', '대전광역시', '울산광역시']
        self.gwangyeok_dict = {}
        # 시도: app.py의 콤보박스로 입력받기
        self.sido_name = sido_name
        # 시군구: app.py의 콤보박스로 입력받기
        self.sigungu_name = sigungu_name
        self.sigungu_dict = {}
        # 시도 시군구 읍면동 행정동코드 dict
        self.hdong_dict = {}

    def load_sigungu_name(self):
        # 법정동 코드 데이터 불러오기
        bdong_code = pdr.code_bdong()
        # 시도명 매핑 규칙: mapping 항목이 있으면 제외
        mapping = ['직할시', '제주도', '전라북도', '강원도']
        # 직할시 -> 광역시 / 제주도 -> 제주특별자치도 / 전라북도 -> 전북특별자치도 / 강원도 -> 강원특별자치도
        # 시도별로 데이터를 추가
        for _, row in bdong_code.iterrows():
            sido_name = row['시도명']
            sigungu_name = row['시군구명']
            sigungu_code = row['시군구코드']
            # 시도명 매핑 적용
            if any(item in sido_name for item in mapping):
                continue
            # 시도명이 빈 문자열이 아닐 경우만 추가
            if sido_name:
                # 시도명이 이미 딕셔너리에 존재하면
                if sido_name in self.sigungu_name_dict:
                    # 시군구명이 빈 문자열이 아닐 경우만 추가하고 중복 방지
                    if sigungu_name not in self.sigungu_name_dict[sido_name]:
                        self.sigungu_name_dict[sido_name][sigungu_name] = sigungu_code
                else:
                    # 새 시도명 추가
                    if sigungu_name:
                        self.sigungu_name_dict[sido_name] = {sigungu_name: sigungu_code}

    def load_gwangyeok(self):
        # 법정동 코드 데이터 불러오기
        bdong_code = pdr.code_bdong()
        # 광역시에 해당하는 데이터 필터링
        filtered_code = bdong_code.loc[bdong_code['시도명'].isin(self.gwangyeok_list)]
        # 광역시별로 데이터를 추가
        for _, row in filtered_code.iterrows():
            sido_name = row['시도명']
            sido_code = row['시도코드']
            # 광역시명이 빈 문자열이 아닐 경우만 추가
            if sido_name:
                self.gwangyeok_dict[sido_name] = sido_code

    def load_sigungu(self):
        # 법정동 코드 데이터 불러오기
        bdong_code = pdr.code_bdong()
        # 시도에 해당하는 데이터 필터링
        filtered_code = bdong_code.loc[bdong_code['시도명'] == self.sido_name]
        # 시군구별로 데이터를 추가
        for _, row in filtered_code.iterrows():
            sigungu_name = row['시군구명']
            sigungu_code = row['시군구코드']
            # 시군구명이 빈 문자열이 아닐 경우만 추가
            if sigungu_name:
                self.sigungu_dict[sigungu_name] = sigungu_code

    def load_hdong(self):
        # 행정동 코드 데이터 불러오기
        hdong_code = pdr.code_hdong()
        # 읍면동에 해당하는 데이터 필터링
        filtered_code = hdong_code.loc[hdong_code['시도명'] == self.sido_name]
        if self.sigungu_name:
            filtered_code = filtered_code.loc[filtered_code['시군구명'] == self.sigungu_name]
        # 읍면동별로 데이터를 추가
        for _, row in filtered_code.iterrows():
            hdong_name = row['읍면동명']
            hdong_code = row['행정동코드']
            # 읍면동명이 빈 문자열이 아닐 경우만 추가
            if hdong_name:
                self.hdong_dict[hdong_name] = hdong_code

    def get_sigungu_name_dict(self):
        return dict(self.sigungu_name_dict)

    def get_gwangyeok_dict(self):
        return dict(self.gwangyeok_dict)

    def get_sigungu_dict(self):
        return dict(self.sigungu_dict)

    def get_hdong_dict(self):
        return dict(self.hdong_dict)

# # 용례
# sido_name = "부산광역시"
# sigungu_name = "연제구"
# code = SigunguCode(sido_name, sigungu_name)
# code.load_sigungu_name()
# code.load_gwangyeok()
# code.load_sigungu()
# code.load_hdong()
# print(code.get_sigungu_name_dict())
# print(code.get_gwangyeok_dict())
# print(code.get_sigungu_dict())
# print(code.get_hdong_dict())