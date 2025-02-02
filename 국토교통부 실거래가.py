### 대충 완료함

from PublicDataReader import TransactionPrice

service_key = "uIpKsI5ZLpNqZwMOkFMo1ey%2BiPufiaF57op3k4kt5gQ5u0UozQGi5c5ZmNs3j1HMJtIWXJn75mVEey4B%2BriCHA%3D%3D"
api = TransactionPrice(service_key)

# 기간 내 조회
df = api.get_data(
    property_type="아파트",
    trade_type="매매",
    sigungu_code="26470", # 부산 연제구
    start_year_month="202201",
    end_year_month="202412",
)

# 각 행에서 필요한 정보를 뽑아서 보기 좋은 이름으로 딕셔너리로 변환
for index, row in df.iterrows():
    apartment_info = {
        "아파트명": row['aptNm'],
        "거래연도": row['dealYear'],
        "거래월": row['dealMonth'],
        "거래일": row['dealDay'],
        "거래금액": row['dealAmount'],
        "층수": row['floor'],
        "거래구분": row['dealingGbn'],
        "전용면적": row['excluUseAr'],
        "아파트Seq": row['aptSeq']
    }

    print(apartment_info)