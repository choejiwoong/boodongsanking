# boodongsanking
## 부동산 지표 및 부동산 매물 수집
### 참고사이트
+ '크롬 검사 - Network(Fetch/XHR) - Copy as cURL(bash)'을 붙여넣으면 request 하기 쉽게 바꿔주는 사이트: https://curlconverter.com/
### cmd streamlit 사용법
+ cd naverMaemool
+ streamlit run main.py
### 체크리스트
#### 2025/01/01
+[x] main 필터에 면적에 따른 필터 추가
+[x] 총 매물 필터하고 나면 몇개가 남았는지 알려주는 멘트 추가
+[x] 전국 데이터 다 조회 가능하게 바뀜
#### 2025/01/03
- 여기(https://m.land.naver.com/complex/ajax/complexListByCortarNo?cortarNo=2647010200)에서 동을 입력하고 아파트 전체리스트를 받아서
- 여기(https://fin.land.naver.com/front-api/v1/complex/article/list?complexNumber=124249&userChannelType=PC&page=0)에서 아파트 매물 정보를 받는 대대적인 개편을 해야할듯
- 자꾸 거제동 아파트만 뜨지 왜...
- cortarNo이 다르다는 걸 알게 됨... -> 동까지 크롤링하는 코드를 추가해서 그걸 기반으로 크롤링해야 할듯
#### 2025/01/05
+ [ ] 테스트 한번 해봐야함
#### what to do next?