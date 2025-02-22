import streamlit as st
import pandas as pd

# 페이지 기본 설정
st.set_page_config(
    page_icon="🏙",
    page_title="직장분석",
    layout="wide",
)

st.warning("⚠ 직장 데이터가 없습니다.")

if 'jikjang_gwangyeok_df' not in st.session_state:
    st.session_state.jikjang_gwangyeok_df = None  # 초기값 설정 (None, 빈 문자열, 또는 적당한 값)
if 'jikjang_sigungu_df' not in st.session_state:
    st.session_state.jikjang_sigungu_df = None  # 초기값 설정 (None, 빈 문자열, 또는 적당한 값)
if 'get_population_data_sigungu' not in st.session_state:
    st.session_state.get_population_data_sigungu = None  # 초기값 설정 (None, 빈 문자열, 또는 적당한 값)


if (st.session_state.jikjang_gwangyeok_df is None) and (st.session_state.jikjang_sigungu_df is None) and (st.session_state.get_population_data_sigungu is None):
    st.warning("⚠ 직장 데이터가 없습니다.")
else:
    st.header("🏙 2. 직장")
    # 두 개의 열을 생성
    col1, col2 = st.columns(2)
    # 높이 설정
    height = 600

    with col1:
        st.dataframe(st.session_state.jikjang_gwangyeok_df, use_container_width=True)
    with col2:
        df = st.session_state.jikjang_sigungu_df
        df['총인구수'] = st.session_state.get_population_data_sigungu['수치값']
        df['총인구수'] = pd.to_numeric(df['총인구수'], errors='coerce')
        df['사업체수'] = pd.to_numeric(df['사업체수'], errors='coerce')
        df['종사자수'] = pd.to_numeric(df['종사자수'], errors='coerce')
        df['등급'] = df['종사자수'].apply(
            lambda x: 'S' if x >= 300000 else ('A' if x >= 200000 else ('B' if x >= 100000 else 'C'))
        )

        df['총인구수 대비 종사자비율'] = df.apply(lambda row: round((row['종사자수'] / row['총인구수'] * 100), 1), axis=1)
        df['사업체수'] = df['사업체수'].apply(lambda x: f'{x:,}' if isinstance(x, (int, float)) else x)
        df['종사자수'] = df['종사자수'].apply(lambda x: f'{x:,}' if isinstance(x, (int, float)) else x)
        df['500인 이상 사업체수'] = df['500인 이상 사업체수'].apply(lambda x: f'{x:,}' if isinstance(x, (int, float)) else x)

        st.dataframe(df, use_container_width=True)