import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# ---------------------------------------------------------
# 1. 페이지 기본 설정
# ---------------------------------------------------------
st.set_page_config(page_title="예술의전당 운영 전략 대시보드", layout="wide")
st.title("🏛️ 예술의전당 운영 전략 대시보드")
st.markdown("데이터 분석을 통해 도출된 핵심 인사이트를 확인하세요.")

# ---------------------------------------------------------
# 2. 데이터베이스 연결 함수
# ---------------------------------------------------------
db_path = 'assignment2.db'

if not os.path.exists(db_path):
    st.error("🚨 'assignment2.db' 파일을 찾을 수 없습니다.")
    st.stop()

@st.cache_data
def load_data(query):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ---------------------------------------------------------
# 3. 차트 1: 연령 및 성별 멤버십 분포 (데이터 기반 고도화)
# ---------------------------------------------------------
st.subheader("1. 연령 및 성별 멤버십 분포 분석")

query1 = """
SELECT 
    CASE 
        WHEN CAST(나이 AS INTEGER) BETWEEN 10 AND 19 THEN '10대'
        WHEN CAST(나이 AS INTEGER) BETWEEN 20 AND 29 THEN '20대'
        WHEN CAST(나이 AS INTEGER) BETWEEN 30 AND 39 THEN '30대'
        WHEN CAST(나이 AS INTEGER) BETWEEN 40 AND 49 THEN '40대'
        WHEN CAST(나이 AS INTEGER) BETWEEN 50 AND 59 THEN '50대'
        WHEN CAST(나이 AS INTEGER) BETWEEN 60 AND 69 THEN '60대'
        WHEN CAST(나이 AS INTEGER) BETWEEN 70 AND 79 THEN '70대'
        WHEN CAST(나이 AS INTEGER) >= 80 THEN '80대 이상'
        ELSE '10대 미만' 
    END AS 연령대,
    성별,
    SUM(골드 + 블루 + 그린) AS 유료멤버십,
    SUM(무료) AS 무료멤버십
FROM Customer
GROUP BY 연령대, 성별
ORDER BY 연령대, 성별
"""
df1 = load_data(query1)

df1_melt = df1.melt(id_vars=['연령대', '성별'], 
                    value_vars=['유료멤버십', '무료멤버십'], 
                    var_name='멤버십유형', 
                    value_name='회원수')

fig1 = px.bar(df1_melt, x='연령대', y='회원수', color='멤버십유형', barmode='group',
              facet_col='성별', # 성별로 차트를 나눠서 비교하기 쉽게 만듭니다.
              title="연령별/성별 유료 및 무료 멤버십 현황",
              labels={'회원수': '가입자 수 (명)'})
st.plotly_chart(fig1, use_container_width=True)

with st.expander("💡 분석 결과 및 전략적 인사이트 (클릭하여 확인)"):
    st.info(f"""
    **✅ 주요 분석 결과:**
    * **2030 세대의 높은 잠재력:** 20대와 30대는 전체 회원 수는 많으나 **무료 멤버십 비중이 압도적**입니다. 
    * **4050 핵심 고객층:** 유료 멤버십 가입자 수가 가장 안정적이며 예술의전당의 주요 수익원 역할을 하고 있습니다.
    * **여성 고객의 높은 참여도:** 전 연령대에서 여성 회원이 남성보다 약 1.5~2배 많아 높은 문화 관여도를 보입니다.

    **🚀 제안 전략:**
    1. **[2030 타겟]** 초기 진입 장벽을 낮춘 '청년 전용 월 구독형 멤버십' 도입 필요.
    2. **[4050 타겟]** 가족 단위 관람을 지원하는 '가족 패키지' 및 프리미엄 서비스 강화.
    3. **[시니어 타겟]** 60대 이상 여성 고객을 위한 마티네(낮 시간) 공연 홍보 및 오프라인 예매 편의 제공.
    """)

# (이하 차트 2, 3 등 기존 코드는 유지)
