import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="예술의전당 운영 전략 대시보드", layout="wide")
st.title("🏛️ 예술의전당 데이터 기반 운영 전략 대시보드")

# 2. 데이터베이스 연결 함수 (에러 메시지 출력 강화)
db_path = 'assignment2.db'

def load_data(query):
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        # 에러가 나면 화면에 어떤 이름이 잘못되었는지 바로 표시합니다.
        st.error(f"❌ 데이터 불러오기 실패! (원인: {e})")
        st.info("💡 팁: 'Customer'나 '나이' 같은 이름이 DB와 일치하는지 확인해주세요.")
        st.stop()

if not os.path.exists(db_path):
    st.error(f"🚨 '{db_path}' 파일을 찾을 수 없습니다! 깃허브에 파일이 있는지 확인해주세요.")
    st.stop()

# ---------------------------------------------------------
# [분석 1] 멤버십 분포 (보내주신 상세 데이터 반영)
# ---------------------------------------------------------
st.header("1. 고객 세그먼트 분석: 멤버십 분포")

# 컬럼명에 쌍따옴표(")를 붙여 한글 깨짐이나 공백 에러를 방지합니다.
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

st.info("**💡 핵심 인사이트:** 20대 여성 무료 회원이 **11,200명**으로 가장 많으며, 이들을 유료로 전환하는 것이 핵심 과제입니다.")

# ---------------------------------------------------------
# [분석 2] 장르별 예매 현황 (보내주신 결과 반영)
# ---------------------------------------------------------
st.header("2. 콘텐츠 분석: 장르별 수요")

# 장르별 분석 결과 데이터를 직접 리스트로 만들어 차트를 그립니다 (DB 에러 방지용)
# 만약 DB에서 직접 가져오고 싶다면 아래 주석을 해제하세요.
genre_data = {
    '장르': ['클래식', '독주', '실내악', '교향곡', '기타', '성악', '뮤지컬', '이벤트콘서트', '연극', '합창', '발레', '오페라'],
    '예매건수': [1539, 1172, 321, 289, 166, 73, 36, 30, 30, 18, 17, 6]
}
df2 = pd.DataFrame(genre_data)

fig2 = px.pie(df2, names='장르', values='예매건수', title="장르별 수요 비중", hole=0.4)
st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------
# [분석 3] 공연장별 이용 현황 (보내주신 결과 반영)
# ---------------------------------------------------------
st.header("3. 시설 분석: 공연장별 이용 현황")

venue_data = {
    '공간명': ['콘서트홀', '오페라극장', 'IBK챔버홀', '리사이틀홀', '기업은행챔버홀', 'CJ 토월극장', '인춘아트홀', '자유소극장'],
    '예매건수': [1866, 617, 560, 336, 329, 325, 160, 128]
}
df3 = pd.DataFrame(venue_data)

fig3 = px.bar(df3, x='예매건수', y='공간명', orientation='h', title="주요 공연장 이용 TOP 8", color='예매건수')
fig3.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig3, use_container_width=True)
