import PublicDataReader as pdr
from streamlit_db import *
import numpy as np

# ==============================================================================
# sigunguhdong을 pdr로 추출해서 mongodb 에 넣는 함수: 유사시에만 쓸 것!
# ==============================================================================
def sigunguhdong_to_mongodb():
    hdong_dict = {}
    hdong_code = pdr.code_hdong()
    # 말소일자가 없는 행만 추출
    hdong_code['말소일자'] = hdong_code['말소일자'].replace('', np.nan)
    hdong_code_updated = hdong_code[hdong_code['말소일자'].isna()]
    # df => dict
    for _, row in hdong_code_updated.iterrows():
        si_name = row['시도명']
        si_code = row['시도코드']
        gungu_name = row['시군구명']
        gungu_code = row['시군구코드']
        dong_name = row['읍면동명']
        dong_code = row['행정동코드']
        # 빈 문자열인 항목 제외
        if si_name == '' or gungu_name == '' or dong_name == '':
            continue
        # '시도명'이 없는 경우 새로운 항목 추가
        if si_name not in hdong_dict:
            hdong_dict[si_name] = {'전체': si_code.ljust(10, '0')}
        # '시군구명'이 없는 경우 새로운 항목 추가
        if gungu_name not in hdong_dict[si_name]:
            hdong_dict[si_name][gungu_name] = {'전체': gungu_code.ljust(10, '0')}
        # '읍면동명'에 해당하는 행정동코드 추가
        hdong_dict[si_name][gungu_name][dong_name] = dong_code

    collection = connect_to_mongodb(db_name='db', collection_name='sigungu')
    # delete_collection(collection) # 컬렉션 삭제
    insert_document(collection, hdong_dict) # 시군구동 데이터 삽입
    return hdong_dict