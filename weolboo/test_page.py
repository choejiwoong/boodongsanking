import streamlit as st
import requests
from bs4 import BeautifulSoup

# 페이지 제목
st.title("크롤링 앱 예제")

# session_state 초기화
if 'crawled' not in st.session_state:
    st.session_state.crawled = False
if 'data' not in st.session_state:
    st.session_state.data_sudo = None

# 기본적으로 보여줄 내용
if not st.session_state.crawled:
    st.write("환영합니다! 아래 버튼을 눌러 데이터를 가져오세요.")

# 버튼 클릭 시 크롤링 함수 실행
if st.button("데이터 크롤링"):
    # 예시 크롤링 (네이버 뉴스 헤드라인 가져오기)
    url = "https://news.naver.com"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 데이터 추출 (헤드라인 예시)
    headlines = [headline.text.strip() for headline in soup.select('.hdline_article_tit a')]

    # 크롤링 결과 저장
    st.session_state.data_sudo = headlines
    st.session_state.crawled = True

# 크롤링 결과 표시
if st.session_state.crawled:
    st.write("크롤링 결과:")
    for idx, headline in enumerate(st.session_state.data_sudo, 1):
        st.write(f"{idx}. {headline}")

# 페이지 하단 고정 내용
st.write("---")
st.write("이 앱은 Streamlit을 사용하여 작성되었습니다.")
