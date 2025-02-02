import streamlit as st
import home_page, population_page

def main():
    st.sidebar.title("부동산 임장보고서 App")
    page = st.sidebar.selectbox("페이지를 선택하세요", ["홈", "연령대별 인구 분석", "분석 결과"])

    if page == "홈":
        home_page.show_home_page()
    elif page == "연령대별 인구 분석":
        population_page.show_population_page()

if __name__ == "__main__":
    main()