import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="예술의전당 운영 전략 대시보드", layout="wide")
st.title("🏛️ 예술의전당 데이터 기반 운영 전략 대시보드")

# 2. 데이터베이스 파일 이름 변경
# 사용자님의 실제 DB 파일 이름인 'Seoul Arts Center.db'로 설정합니다.
db_path = 'Seoul Arts Center.db'

def load_data(query):
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ 데이터 불러오기 실패! (원인: {e})")
        st.info(f"💡 팁: '{db_path}' 파일이 깃허브에 정상적으로 업로드되었는지 확인해주세요.")
        st.stop()

# 파일 존재 여부 확인
if not os.path.exists(db_path):
    st.error(f"🚨 '{db_path}' 파일을 찾을 수 없습니다!")
    st.markdown(f"""
    **✅ 해결 방법:**
    1. 내 컴퓨터에 있는 **{db_path}** 파일을 찾습니다.
    2. 깃허브 저장소에 이 파일을 업로드합니다.
    3. 파일 이름의 대소문자와 띄어쓰기가 정확한지 확인하세요.
    """)
    st.stop()

# ---------------------------------------------------------
# [분석 1] 멤버십 분포 (나이/성별/멤버십)
# ---------------------------------------------------------
st.header("1. 고객 세그먼트 분석: 멤버십 분포")

query1 = """
SELECT 
    CASE 
        WHEN CAST("나이" AS INTEGER) BETWEEN 20 AND 29 THEN '20대'
        WHEN CAST("나이" AS INTEGER) BETWEEN 30 AND 39 THEN '30대'
        WHEN CAST("나이" AS INTEGER) BETWEEN 40 AND 49 THEN '40대'
        WHEN CAST("나이" AS INTEGER) BETWEEN 50 AND 59 THEN '50대'
        WHEN CAST("나이" AS INTEGER) BETWEEN 60 AND 69 THEN '60대'
        ELSE '기타' 
    END AS 연령대,
    "성별",
    SUM("골드" + "블루" + "그린") AS 유료멤버십,
    SUM("무료") AS 무료멤버십
FROM Customer
GROUP BY 연령대, "성별"
"""
df1 = load_data(query1)
df1_melted = df1.melt(id_vars=['연령대', '성별'], value_vars=['유료멤버십', '무료멤버십'], var_name='유형', value_name='회원수')

fig1 = px.bar(df1_melted, x='연령대', y='회원수', color='유형', barmode='group', facet_col='성별', 
              title="연령/성별 멤버십 가입 현황")
st.plotly_chart(fig1, use_container_width=True)

# ---------------------------------------------------------
# [분석 2] 장르별 예매 현황 (JOIN 쿼리 수정)
# ---------------------------------------------------------
st.header("2. 콘텐츠 분석: 장르별 수요")

# 프로젝트 파일에 적힌 대로 E.공연명 대신 E.제목을 사용하여 JOIN 합니다.
query2 = """
SELECT E."장르", COUNT(*) AS 예매건수
FROM Wheelchair W
JOIN Exhibition E ON W."공연명" = E."제목"
GROUP BY E."장르"
ORDER BY 예매건수 DESC
"""
df2 = load_data(query2)

fig2 = px.pie(df2, names='장르', values='예매건수', title="장르별 수요 비중", hole=0.4)
st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------
# [분석 3] 공연장별 이용 현황
# ---------------------------------------------------------
st.header("3. 시설 분석: 공연장별 이용 현황")

query3 = """
SELECT "공간명", COUNT(*) AS 예매건수
FROM Wheelchair
GROUP BY "공간명"
ORDER BY 예매건수 DESC
LIMIT 8
"""
df3 = load_data(query3)

fig3 = px.bar(df3, x='예매건수', y='공간명', orientation='h', title="주요 공연장 이용 TOP 8", color='예매건수')
fig3.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig3, use_container_width=True)
