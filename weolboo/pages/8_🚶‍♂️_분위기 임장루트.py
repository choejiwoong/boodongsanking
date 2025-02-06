from streamlit.components.v1 import iframe
import pandas as pd
from folium import *
import streamlit as st
import folium
import json

# 페이지 기본 설정
st.set_page_config(
    page_icon="🚶‍♂️",
    page_title="분위기 임장루트",
    layout="wide",
)

st.header("분위기 임장루트")

# 지도 생성 (부산시 연제구 중심)
map_center = [35.17318611, 129.082075]
m = folium.Map(location=map_center, zoom_start=13.5)

# 대형마트, 백화점
# 마커에 Tooltip 추가 (마우스 올렸을 때 표시)
# {'pink', 'gray', 'darkgreen', 'lightgray', 'green', 'black', 'orange', 'lightblue', 'lightgree', 'purple', 'darkblue', 'cadetblue', 'darkred', 'beige', 'darkpurple', 'red', 'blue', 'white', 'lightred'}.
# 마커 좌표 및 정보 리스트
markers = [
    {"location": [35.173883, 129.081865], "tooltip": "연산골드포레"},
    {"location": [35.180000, 129.075000], "tooltip": "해운대아이파크"},
    {"location": [35.160000, 129.090000], "tooltip": "수영SK뷰"},
    {"location": [35.150000, 129.100000], "tooltip": "광안KCC스위첸"},
    {"location": [35.140000, 129.110000], "tooltip": "센텀리버뷰"},
]

# 여러 개의 마커 추가
for marker in markers:
    folium.Marker(
        location=marker["location"],
        tooltip=Tooltip(marker["tooltip"], sticky=True),
        icon=Icon(icon='landmark', prefix='fa')
    ).add_to(m)


# 지도 클릭 시 좌표 팝업 표시
m.add_child(folium.LatLngPopup())

# 상권 polygon
folium.Polygon(
    locations=[
        [35.1735, 129.0815],
        [35.1740, 129.0818],
        [35.1745, 129.0820],
        [35.1740, 129.0825],
        [35.1735, 129.0822],
    ],
    color="darkgreen",  # 테두리 색상
    fill=True,
    fill_color="darkgreen",  # 채우기 색상
    fill_opacity=0.3,  # 투명도 조절
).add_to(m)

# folium 지도를 HTML로 변환하여 Streamlit에 표시
m.save('map_atmo_imjang.html')

# 지도 HTML 불러오기
with open('map_atmo_imjang.html', 'r', encoding='utf-8') as f:
    map_html = f.read()

# Streamlit에서 지도 표시
st.components.v1.html(map_html, width=700, height=500)

