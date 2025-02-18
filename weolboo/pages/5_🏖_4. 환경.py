import streamlit as st
from streamlit.components.v1 import iframe
import pandas as pd

# 페이지 기본 설정
st.set_page_config(
    page_icon="🏖",
    page_title="환경분석",
    layout="wide",
)

# ==============================================================================
# session_state 초기화
# ==============================================================================

if 'hwangyeong_tuple' not in st.session_state:
    st.session_state.hwangyeong_tuple = None
if 'hwangyeong_ranking' not in st.session_state:
    st.session_state.hwangyeong_ranking = None

if st.session_state.hwangyeong_tuple == None:
    st.warning("⚠ 환경 데이터가 없습니다.")
if st.session_state.hwangyeong_tuple:
    st.header("🏖 4. 환경")
    selected_sido = st.session_state.selected_sido
    selected_sigungu = st.session_state.selected_sigungu
    # ==============================================================================
    # 상권/편의시설
    # ==============================================================================
    st.subheader(f"{selected_sido} 상권/편의시설")
    # 두 개의 열을 생성
    col1, col2 = st.columns(2)
    # 높이 설정
    height = 600
    with col1:
        st.dataframe(st.session_state.hwangyeong_tuple[0], use_container_width=True, height=height)
    with col2:
        st.dataframe(st.session_state.hwangyeong_tuple[1], use_container_width=True, height=height)
    st.text_area("📝 생활편의시설 평가")
    # ==============================================================================
    # 주거지 균질성(아파트 택지)
    # ==============================================================================
    st.subheader(f"{selected_sigungu} 주거지 균질성(아파트 택지)")
    # Google My Maps 공유 링크 (여기에 본인 지도 URL 입력)
    google_maps_url = "https://www.google.com/maps/d/embed?mid=1GqeLe9S_dDf0zRAuGrbK5TNhuyIKBIs&usp=sharing"  # 내 지도 URL로 변경!
    # Streamlit에서 지도 표시 (iframe 사용)
    st.components.v1.iframe(google_maps_url, width=800, height=600)
    st.text_area("📝 주거지 균질성(아파트 택지) 평가")
    # ==============================================================================
    # 주거지 균질성(경사도)
    # ==============================================================================
    st.subheader(f"{selected_sigungu} 주거지 균질성(경사도)")
    # 경사도
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
    <a class="stylish-button" href="https://hogangnono.com/" target="_blank">
        🚀 호갱노노로 이동
    </a>
    """, unsafe_allow_html=True)
    st.text_area("📝 주거지 균질성(경사도) 평가")
    # ==============================================================================
    # 상권의 질
    # ==============================================================================
    st.subheader(f"{selected_sigungu} 상권의 질")
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
    st.text_area("📝 상권의 질 평가: 유흥상권(여관(모텔포함) 및 여인숙 업종, 호프 및 간이주점 업종), 주거상권(카페 업종, 교습학원 업종)")
    # ==============================================================================
    # 분위기 임장
    # ==============================================================================
    st.subheader(f"{selected_sigungu} 분위기 임장")
    # 초기 데이터프레임 생성
    data = {
        "카테고리": ["직장", "", "교통", "학군", "", "환경", "", "", "", "", ""],
        "세부 항목": [
            "직장의 규모", "직장인의 모습",
            "출퇴근 혼잡도",
            "학원가의 종류", "면학 분위기",
            "택지", "거주지 상권", "유해 시설", "지형", "거주민 분위기 (연령대)"
        ],
        "상": [False, False, False, False, False, False, False, False, False, False],
        "중": [False, False, False, False, False, False, False, False, False, False],
        "하": [False, False, False, False, False, False, False, False, False, False]
    }
    st.markdown("##### 📌 분위기임장 체크리스트")
    # ✅ 각 열의 길이를 맞춤 (10행으로 통일)
    data = {
        "카테고리": ["직장", "직장", "교통", "학군", "학군", "환경", "환경", "환경", "환경", "환경"],
        "세부 항목": [
            "직장의 규모", "직장인의 모습",
            "출퇴근 혼잡도",
            "학원가의 종류", "면학 분위기",
            "택지", "거주지 상권", "유해 시설", "지형", "거주민 분위기 (연령대)"
        ],
        "상": [False] * 10,
        "중": [False] * 10,
        "하": [False] * 10,
        "비고": [  # 추가 설명
            "정장, 작업복",
            "",
            "",
            "영재학원, 입시컨설팅(플랜카드)",
            "입시플랜카드, 대형학원",
            "",
            "유기농마트, 초록마을, 한살림, 명품의류편집샵, 필라테스샵, 네일샵, 영어유치원, 영어학원, 정신과, 심리치료",
            "유흥시설, 공장, 교도소, 비행장 등",
            "",
            "옷차림, 표정, 말투"
        ],
    }
    # DataFrame 생성
    df = pd.DataFrame(data)
    # ✅ 체크박스 포함된 데이터프레임 (수정 가능)
    edited_df = st.data_editor(df, key="checklist", num_rows="dynamic", use_container_width=True)
    # ✅ 선택된 체크박스 개수 개별 합산
    total_high = edited_df["상"].sum()
    total_mid = edited_df["중"].sum()
    total_low = edited_df["하"].sum()
    # ✅ 체크 개수 출력
    check_text = f"상: {int(total_high)} 개 / 중: {int(total_mid)} 개 / 하: {int(total_low)} 개"
    # ✅ 추가 의견 입력
    additional_comments = st.text_area("📝 추가 의견 입력", value=check_text)
# ==============================================================================
# 환경 SUMMARY
# ==============================================================================
if st.session_state.hwangyeong_ranking:
    st.subheader(f"환경 SUMMARY: {st.session_state.hwangyeong_ranking['등급']}")
    st.text_area("지역 내에서 환경이 제일 좋은 곳은 어디인가?")
    st.text_area("SUMMARY")