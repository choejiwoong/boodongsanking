import geopandas as gpd
from pyproj import CRS

# Projection 정의 (UTM-K -> WGS84)
proj_UTMK = CRS("EPSG:5178")  # UTM-K 좌표계
proj_WGS84 = CRS("EPSG:4326")  # WGS84 좌표계

# GeoJSON 파일을 KML 파일로 변환하는 함수
def transform_geojson_to_kml(input_geojson, output_kml):
    # GeoPandas로 GeoJSON 파일 읽기
    gdf = gpd.read_file(input_geojson)

    # 좌표계가 UTM-K가 아니라면 좌표계 설정
    if gdf.crs != proj_UTMK:
        gdf.set_crs(proj_UTMK, allow_override=True, inplace=True)

    # 좌표 변환 (UTM-K -> WGS84)
    gdf = gdf.to_crs(proj_WGS84)

    # 변환된 GeoDataFrame을 KML 파일로 저장
    gdf.to_file(output_kml, driver='KML')

# 사용 예시
input_geojson = 'C:/Users/cbbtng/Downloads/sig.json'  # 원본 GeoJSON 파일 경로
output_kml = 'C:/Users/cbbtng/Downloads/sig_wgs.kml'  # 저장할 KML 파일 경로
transform_geojson_to_kml(input_geojson, output_kml)
