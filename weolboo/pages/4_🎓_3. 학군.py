import streamlit as st
from streamlit.components.v1 import iframe

# 페이지 기본 설정
st.set_page_config(
    page_icon="🎓",
    page_title="학군분석",
    layout="wide",
)

st.header("학군분석")

if 'selected_sido' not in st.session_state:
    st.session_state.selected_sido = None
if 'selected_sigungu' not in st.session_state:
    st.session_state.selected_sigungu = None

if 'fetch_school_achievement' not in st.session_state:
    st.session_state.fetch_school_achievement = None
if 'school_achievement_ranking' not in st.session_state:
    st.session_state.school_achievement_ranking = None

# 통계지리정보서비스 생활업종 통계지도
st.markdown("""
<style>
.stylish-button {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 14px 28px;
    font-size: 18px;
    font-weight: bold;
    color: white !important;
    background: linear-gradient(135deg, #6e8efb, #a777e3);
    border-radius: 10px;
    text-decoration: none;
    transition: 0.3s;
    margin-bottom: 30px; /* 버튼 아래 여백 추가 */
}
.stylish-button:hover {
    background: linear-gradient(135deg, #5a7be0, #9168d8);
}
</style>
<a class="stylish-button" href="https://sgis.kostat.go.kr/view/bizStats/bizStatsMap" target="_blank">
    🚀 통계지리정보서비스 생활업종 통계지도로 이동
</a>
""", unsafe_allow_html=True)

# 학군등급
if st.session_state.selected_sido and st.session_state.selected_sigungu:
    st.subheader(f"{st.session_state.selected_sido} {st.session_state.selected_sigungu} 학군 데이터")

# Google My Maps 공유 링크 (여기에 본인 지도 URL 입력)
google_maps_url = "https://www.google.com/maps/d/embed?mid=1GqeLe9S_dDf0zRAuGrbK5TNhuyIKBIs&usp=sharing"  # 내 지도 URL로 변경!

# Streamlit에서 지도 표시 (iframe 사용)
st.components.v1.iframe(google_maps_url, width=800, height=600)

if st.session_state.fetch_school_achievement:
    st.dataframe(st.session_state.fetch_school_achievement, use_container_width=True)
    st.subheader(f"학군 SUMMARY: {st.session_state.school_achievement_ranking['등급']}")
    st.text_area("지역 내에서 학군지로 선호하는 동네는?")
    st.text_area("학군을 이유로 외부지역에서 넘어오는가?")
    st.text_area("SUMMARY")