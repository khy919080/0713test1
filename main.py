import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="서울-양평 도시 열섬현상 분석", layout="wide")

st.title("🏙️ 서울 vs 🌲 양평 기온 비교를 통한 도시 열섬현상 분석")
st.markdown("""
본 웹앱은 서울(도심)과 양평(교외)의 2025년 시간별 기온 데이터를 비교하여 **도시 열섬현상(Urban Heat Island Effect)**을 시각적으로 분석합니다.
- **도시 열섬현상**: 인공 열, 콘크리트 구조물 등으로 인해 도심의 기온이 주변 교외 지역보다 높게 나타나는 현상
""")

# 데이터 로드 함수
@st.cache_data
def load_data():
    try:
        # 3. 한글 파일 처리를 위한 encoding="cp949" 설정
        seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
        yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
        
        # 일시 컬럼을 datetime 형식으로 변환하여 시간/월 추출 가능하게 만듦
        seoul['일시'] = pd.to_datetime(seoul['일시'])
        yangpyeong['일시'] = pd.to_datetime(yangpyeong['일시'])
        
        # 월, 시각 컬럼 추출
        seoul['월'] = seoul['일시'].dt.month
        seoul['시각'] = seoul['일시'].dt.hour
        yangpyeong['월'] = yangpyeong['일시'].dt.month
        yangpyeong['시각'] = yangpyeong['일시'].dt.hour
        
        return seoul, yangpyeong
    except Exception as e:
        st.error(f"데이터를 읽어오는 중 오류가 발생했습니다. 파일명과 인코딩(cp949)을 확인해주세요. \n오류 내용: {e}")
        return None, None

# 데이터 로드
seoul_df, yang_df = load_data()

if seoul_df is not None and yang_df is not None:
    # 2. '일시' 컬럼을 기준으로 두 지역 데이터 병합
    merged = pd.merge(
        seoul_df[['일시', '월', '시각', '기온(°C)']], 
        yang_df[['일시', '기온(°C)']], 
        on='일시', 
        suffixes=('_서울', '_양평')
    )
    # 기온차 계산 (서울 - 양평)
    merged['기온차(서울-양평)'] = merged['기온(°C)_서울'] - merged['기온(°C)_양평']

    # ----------------------------------------
    # ① 1년간 두 지역의 기온 변화 (선그래프)
    # ----------------------------------------
    st.subheader("① 1년간 두 지역의 기온 변화 (선그래프)")
    
    # 데이터량이 많으므로 사용자가 원하는 월만 필터링해서 볼 수 있는 인터랙션 기능 추가
    month_filter = st.multiselect("원하는 월을 선택하여 필터링할 수 있습니다 (비워두면 전체 표시)", options=list(range(1, 13)), default=[])
    
    chart_data = merged.copy()
    if month_filter:
        chart_data = chart_data[chart_data['월'].isin(month_filter)]
    
    # st.line_chart 처리를 위한 데이터 정렬
    line_df = chart_data.set_index('일시')[['기온(°C)_서울', '기온(°C)_양평']]
    line_df.columns = ['서울 기온', '양평 기온']
    st.line_chart(line_df)

    # 화면을 좌우로 나누기 위한 컬럼 배치
    col1, col2 = st.columns(2)

    with col1:
        # ----------------------------------------
        # ② 시각(0~23시)별 평균 기온차 (막대그래프)
        # ----------------------------------------
        st.subheader("② 시각(0~23시)별 평균 기온차 (서울-양평)")
        hour_diff = merged.groupby('시각')['기온차(서울-양평)'].mean().reset_index()
        hour_diff = hour_diff.set_index('시각')
        st.bar_chart(hour_diff)
        st.caption("주로 해가 진 뒤 대기가 냉각되는 밤~새벽 시간대에 서울의 기온이 양평보다 확연히 높은 열섬현상이 잘 드러납니다.")

    with col2:
        # ----------------------------------------
        # ③ 월(1~12월)별 평균 기온차 (막대그래프)
        # ----------------------------------------
        st.subheader("③ 월(1~12월)별 평균 기온차 (서울-양평)")
        month_diff = merged.groupby('월')['기온차(서울-양평)'].mean().reset_index()
        month_diff = month_diff.set_index('월')
        st.bar_chart(month_diff)
        st.caption("계절별로 도심과 교외 간의 평균 기온 편차가 어떻게 달라지는지 볼 수 있습니다.")

    # 📊 추가하면 좋은 대시보드 스탯 지표
    st.markdown("---")
    st.subheader("📊 2025년 전체 요약 통계")
    avg_seoul = merged['기온(°C)_서울'].mean()
    avg_yang = merged['기온(°C)_양평'].mean()
    avg_diff = merged['기온차(서울-양평)'].mean()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("서울 연평균 기온", f"{avg_seoul:.2f} °C")
    c2.metric("양평 연평균 기온", f"{avg_yang:.2f} °C")
    c3.metric("평균 기온 편차 (서울-양평)", f"{avg_diff:.2f} °C", delta=f"{avg_diff:.2f} °C (서울이 높음)")

else:
    st.warning("데이터 파일을 불러오지 못했습니다. '서울_기온.csv'와 '양평_기온.csv' 파일이 스크립트와 같은 폴더에 있는지 확인해주세요.")
