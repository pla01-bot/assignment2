import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# ---------------------------------------------------------
# 1. 페이지 기본 설정 및 제목
# ---------------------------------------------------------
st.set_page_config(page_title="예술의전당 운영 전략 대시보드", layout="wide")
st.title("🏛️ 예술의전당 운영 전략 대시보드")
st.markdown("데이터 기반의 의사결정을 위한 시각화 대시보드입니다. 각 차트 하단의 화살표를 누르면 쿼리와 인사이트를 볼 수 있어요!")

# ---------------------------------------------------------
# 2. 데이터베이스 연결 및 오류 처리
# ---------------------------------------------------------
db_path = 'assignment2.db'

# 파일 존재 여부 확인 (없으면 에러 메시지 출력 후 실행 중단)
if not os.path.exists(db_path):
    st.error("🚨 'assignment2.db' 파일을 찾을 수 없습니다! 현재 폴더(디렉토리)에 파일이 있는지 확인해 주세요.")
    st.stop()

# DB 연결 및 데이터 불러오기 함수 (캐싱을 통해 속도 향상)
@st.cache_data
def load_data(query):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ---------------------------------------------------------
# 3. 차트 1: 연령 및 성별 멤버십 분포 (누적 막대 차트)
# ---------------------------------------------------------
st.subheader("1. 연령 및 성별 멤버십 분포")

# [수정됨] 10대 미만 데이터 분류 및 분석에서 제외(필터링)하는 로직 추가
query1 = """
SELECT 
    CASE 
        WHEN CAST(나이 AS INTEGER) < 10 THEN '10대 미만'
        WHEN CAST(나이 AS INTEGER) BETWEEN 10 AND 19 THEN '10대'
        WHEN CAST(나이 AS INTEGER) BETWEEN 20 AND 29 THEN '20대'
        WHEN CAST(나이 AS INTEGER) BETWEEN 30 AND 39 THEN '30대'
        WHEN CAST(나이 AS INTEGER) BETWEEN 40 AND 49 THEN '40대'
        WHEN CAST(나이 AS INTEGER) BETWEEN 50 AND 59 THEN '50대'
        ELSE '60대 이상' 
    END AS 연령대,
    성별,
    SUM(골드 + 블루 + 그린) AS 유료멤버십,
    SUM(무료) AS 무료멤버십
FROM Customer
WHERE CAST(나이 AS INTEGER) >= 10  -- 10대 미만 데이터가 분석에 불필요하므로 제외
GROUP BY 연령대, 성별
ORDER BY 연령대, 성별
"""
df1 = load_data(query1)

if not df1.empty:
    df1_melt = df1.melt(id_vars=['연령대', '성별'], 
                        value_vars=['유료멤버십', '무료멤버십'], 
                        var_name='멤버십유형', 
                        value_name='회원수')
    df1_melt['연령_성별'] = df1_melt['연령대'] + " (" + df1_melt['성별'] + ")"

    fig1 = px.bar(df1_melt, x='연령_성별', y='회원수', color='멤버십유형', barmode='stack', 
                  title="연령/성별 유료 및 무료 멤버십 가입자 수 (10대 이상)",
                  labels={'연령_성별': '연령대 및 성별', '회원수': '가입자 수 (명)'})
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.warning("⚠️ 표시할 멤버십 데이터가 없습니다.")

with st.expander("💡 사용된 SQL 쿼리 및 비즈니스 인사이트 보기"):
    st.code(query1, language='sql')
    st.info("""
    **비즈니스 인사이트:**
    * 2030 세대의 경우 무료 멤버십 비중이 압도적으로 높을 것으로 예상되므로, 이들을 유료 멤버십으로 전환할 수 있는 '청년 할인 프로모션' 도입이 필요합니다.
    * 4050 세대는 유료 멤버십 가입 비중이 상대적으로 안정적이므로, 기존 유료 회원 이탈 방지를 위한 '프리미엄 혜택(우선 예매 등)'을 강화해야 합니다.
    """)

st.divider()

# ---------------------------------------------------------
# 4. 차트 2: 장르별 휠체어석 예매 현황 (파이 차트)
# ---------------------------------------------------------
st.subheader("2. 장르별 휠체어석 예매 현황")

# [수정됨] REPLACE 함수를 사용하여 띄어쓰기(공백)를 제거한 뒤 조인하여 매칭 확률 향상
query2 = """
SELECT 
    E.장르, 
    COUNT(*) AS 예매건수
FROM Wheelchair W
JOIN Exhibition E ON REPLACE(W.공연명, ' ', '') = REPLACE(E.제목, ' ', '')
GROUP BY E.장르
ORDER BY 예매건수 DESC
"""
df2 = load_data(query2)

# [수정됨] 데이터가 비어있을 경우 에러가 나지 않도록 예외 처리 추가
if df2.empty:
    st.warning("⚠️ Wheelchair와 Exhibition 테이블 간에 이름이 정확히 일치하는 공연이 없어 데이터를 연결하지 못했습니다.")
else:
    fig2 = px.pie(df2, names='장르', values='예매건수', 
                  title="장르별 휠체어석 예매 비율",
                  hole=0.3)
    st.plotly_chart(fig2, use_container_width=True)

with st.expander("💡 사용된 SQL 쿼리 및 비즈니스 인사이트 보기"):
    st.code(query2, language='sql')
    st.info("""
    **비즈니스 인사이트:**
    * 특정 장르(예: 클래식, 뮤지컬)에 휠체어석 예매가 집중되어 있다면, 해당 장르 공연 시 이동 지원 인력(안내원)을 평소보다 추가 배치해야 합니다.
    * 휠체어석 예매율이 저조한 장르의 경우, 장애인 단체 대상의 홍보 강화나 배리어프리(Barrier-Free) 자막/수어 서비스 확충을 고려해야 합니다.
    """)

st.divider()

# ---------------------------------------------------------
# 5. 차트 3: 인기 공연장 TOP 10 (가로 막대 차트)
# ---------------------------------------------------------
st.subheader("3. 인기 공연장 TOP 10 (휠체어석 예매 기준)")

query3 = """
SELECT 
    공간명, 
    COUNT(*) AS 예매건수
FROM Wheelchair
GROUP BY 공간명
ORDER BY 예매건수 DESC
LIMIT 10
"""
df3 = load_data(query3)

if not df3.empty:
    fig3 = px.bar(df3, x='예매건수', y='공간명', orientation='h', 
                  title="휠체어석 예매가 가장 많은 공연장 TOP 10",
                  labels={'예매건수': '총 예매 건수', '공간명': '공연장명'})
    fig3.update_layout(yaxis={'categoryorder':'total ascending'}) 
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("⚠️ 표시할 공연장 데이터가 없습니다.")

with st.expander("💡 사용된 SQL 쿼리 및 비즈니스 인사이트 보기"):
    st.code(query3, language='sql')
    st.info("""
    **비즈니스 인사이트:**
    * 상위 랭크된 공연장(메인 홀 등)은 휠체어 이용객의 방문 빈도가 가장 높으므로, 해당 공연장 주변의 경사로, 장애인 화장실 등 물리적 접근성 점검이 1순위로 이루어져야 합니다.
    * 예매가 집중되는 특정 공간에는 휠체어 전용 대기 구역을 신설하여 관람객의 대기 편의성을 높이는 전략이 필요합니다.
    """)
