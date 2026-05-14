import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# ---------------------------------------------------------
# 1. 페이지 기본 설정
# ---------------------------------------------------------
st.set_page_config(page_title="예술의전당 운영 전략 대시보드", layout="wide")
st.title("🏛️ 예술의전당 데이터 기반 운영 전략 대시보드")
st.markdown("""
이 대시보드는 **멤버십 데이터**, **장르별 예매 현황**, **공연장별 이용률**을 분석하여 
예술의전당의 서비스 품질 향상과 효율적인 운영을 위한 전략적 인사이트를 제공합니다.
""")
st.divider()

# ---------------------------------------------------------
# 2. 데이터베이스 연결
# ---------------------------------------------------------
db_path = 'Seoul Arts Center.db'

def load_data(query):
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ 데이터 불러오기 실패! (원인: {e})")
        st.stop()

if not os.path.exists(db_path):
    st.error(f"🚨 '{db_path}' 파일을 찾을 수 없습니다! 깃허브에 파일이 있는지 확인해주세요.")
    st.stop()

# ---------------------------------------------------------
# 3. [분석 1] 고객 세그먼트 분석 (멤버십)
# ---------------------------------------------------------
st.header("1. 고객 세그먼트 분석: 멤버십 분포")
col1, col2 = st.columns([2, 1]) # 차트 2 : 텍스트 1 비율로 화면 분할

with col1:
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
                  title="연령/성별 멤버십 가입 현황", color_discrete_map={'유료멤버십': '#1f77b4', '무료멤버십': '#aec7e8'})
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.info("**💡 멤버십 분석 인사이트**")
    st.markdown("""
    * **2030 세대의 잠재력:** 20대와 30대는 가입자 수는 많으나 **무료 회원 비중이 압도적**(특히 20대 여성 무료 회원 약 11,200명)입니다. 진입 장벽을 낮춘 '월 구독형 멤버십' 도입이 필요합니다.
    * **4050 핵심 고객층:** 유료 멤버십 가입이 가장 안정적인 수익원입니다. 가족 단위 관람을 지원하는 프리미엄 혜택 강화가 요구됩니다.
    * **여성 타겟팅:** 전 연령대에서 여성 회원이 남성보다 약 **1.5~2배** 많아 여성 고객 중심의 문화 마케팅이 유효함을 보여줍니다.
    """)

st.divider()

# ---------------------------------------------------------
# 4. [분석 2] 콘텐츠 분석 (장르별 수요)
# ---------------------------------------------------------
st.header("2. 콘텐츠 분석: 장르별 수요 (휠체어석 기준)")
col3, col4 = st.columns([1, 2]) # 텍스트 1 : 차트 2 비율

with col3:
    st.info("**💡 장르별 예매 인사이트**")
    st.markdown("""
    * **특정 장르 편중:** 휠체어석 예매는 **클래식(1539건)**과 **독주(1172건)** 장르에 압도적으로 집중되어 있습니다.
    * **운영 전략:** 해당 장르 공연 시에는 로비 안내 인력 및 휠체어 리프트 가동 요원을 일반 공연 대비 2배 이상 배치하는 집중 관리가 필요합니다.
    * **소외 장르 보완:** 오페라, 발레 등은 예매율이 저조하여, 교통 약자를 위한 접근성 홍보가 추가로 필요할 수 있습니다.
    """)

with col4:
    query2 = """
    SELECT E."장르", COUNT(*) AS 예매건수
    FROM Wheelchair W
    JOIN Exhibition E ON W."공연명" = E."제목"
    GROUP BY E."장르"
    ORDER BY 예매건수 DESC
    """
    df2 = load_data(query2)
    
    fig2 = px.pie(df2, names='장르', values='예매건수', title="장르별 예매 비중", hole=0.4, 
                  color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ---------------------------------------------------------
# 5. [분석 3] 시설 분석 (공연장별 이용 현황)
# ---------------------------------------------------------
st.header("3. 시설 분석: 주요 공연장 이용 현황")
col5, col6 = st.columns([2, 1])

with col5:
    query3 = """
    SELECT "공간명", COUNT(*) AS 예매건수
    FROM Wheelchair
    GROUP BY "공간명"
    ORDER BY 예매건수 DESC
    LIMIT 8
    """
    df3 = load_data(query3)
    
    fig3 = px.bar(df3, x='예매건수', y='공간명', orientation='h', title="이용률 상위 공연장 TOP 8", 
                  text='예매건수', color='예매건수', color_continuous_scale='Viridis')
    fig3.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig3, use_container_width=True)

with col6:
    st.success("**📌 시설 운영 핵심 제안**")
    st.markdown("""
    * **콘서트홀 집중 관리:** 이용자가 **1866건**으로 타 공연장 대비 압도적으로 많습니다. 공연 전후 엘리베이터 정체 해소를 위한 전담 요원 배치가 필수적입니다.
    * **중소형 공연장 동선 점검:** 오페라극장(617건), IBK챔버홀(560건) 등 중소규모 공연장에서도 상당한 수요가 발생하므로, 휠체어 이동을 위한 복도 내 적치물 제거 및 안전 확보가 요구됩니다.
    """)
