import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_icon="🚇",
    page_title="교통",
    layout="wide",
)

# ==============================================================================
# session_state 초기화
# ==============================================================================

if 'gyotong_subway' not in st.session_state:
    st.session_state.gyotong_subway = None
if 'fetch_transport_data' not in st.session_state:
    st.session_state.fetch_transport_data = None

if st.session_state.gyotong_subway is None:
    st.warning("⚠ 교통 데이터가 없습니다.")
else:
    st.header("🚇 6. 교통")
    # ==============================================================================
    # 역세권의 가치는 어느 정도일까?
    # ==============================================================================
    st.subheader("역세권의 가치는 어느 정도일까?")
    # 두 개의 열을 생성
    col1, col2 = st.columns(2)
    # 높이 설정
    height = 600
    with col1:
        # ==============================================================================
        # 지하철 버스 수송분담률 그래프
        # ==============================================================================
        if st.session_state.fetch_transport_data is not None:
            # st.dataframe(st.session_state.fetch_transport_data, use_container_width=True)
            st.plotly_chart(st.session_state.get_transport_div_plotly)
    with col2:
        # ==============================================================================
        # 부산지하철 역별 출퇴근시간 승하차인원 df
        # ==============================================================================
        st.dataframe(st.session_state.gyotong_subway, use_container_width=True)
    st.text_area("📝 역세권 가치 평가")
    # ==============================================================================
    # 교통호재
    # ==============================================================================
    st.subheader("교통호재")
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
    <a class="stylish-button" href="https://m.richgo.ai/" target="_blank">
        🚀 교통호재 보기
    </a>
    """, unsafe_allow_html=True)
    st.text_area("📝 교통호재 평가")

    # ranking으로 걸려면 kakaomap api 해봐야함
    # if st.session_state.mid_school_achievement_ranking:
    # st.subheader(f"교통 SUMMARY: {st.session_state.mid_school_achievement_ranking['등급']}")
    st.subheader(f"교통 SUMMARY")
    # 두 개의 열을 생성
    col1, col2 = st.columns(2)
    # 높이 설정
    height = 600
    with col1:
        st.text_area("교통의 가치가 있는 도시인가?")
    with col2:
        st.text_area("교통호재? 실현가능성? 입지가 좋아지는가?")
    # # HTML 및 CSS를 사용하여 text_area 스타일 변경
    # st.markdown(
    #     """
    #     <style>
    #     /* 마지막 text_area만 스타일 적용 */
    #     .stTextArea:nth-of-type(4) textarea {
    #         background-color: #FFD700;  /* 노란 배경색 */
    #     }
    #     </style>
    #     """,
    #     unsafe_allow_html=True
    # )
    st.text_area("SUMMARY")


