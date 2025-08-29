#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="Titanic Survival Dashboard",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("default")

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

/* ✅ 메트릭 카드 스타일 (흰 배경 + 검정 글씨) */
[data-testid="stMetric"] {
    background-color: white;
    color: black;
    text-align: center;
    padding: 15px 0;
    border-radius: 10px;
    border: 1px solid #ddd;
    box-shadow: 1px 1px 5px rgba(0,0,0,0.1);
}

[data-testid="stMetric"] * {
    color: black !important;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"],
[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)


#######################
# Load data
df_reshaped = pd.read_csv('titanic.csv')

# ✅ 연령대 변수 생성 (0~9세 → "10세 미만")
df_reshaped["연령대"] = pd.cut(
    df_reshaped["Age"],
    bins=range(0, 91, 10),
    right=False,
    labels=["10세 미만"] + [f"{i}대" for i in range(10, 90, 10)]
)

#######################
# Sidebar
with st.sidebar:
    st.title("⚓ Titanic Survival Dashboard")

    # 성별 선택
    sex_filter = st.multiselect(
        "성별 선택:",
        options=df_reshaped["Sex"].unique(),
        default=df_reshaped["Sex"].unique()
    )

    # 연령대 선택
    age_group_filter = st.multiselect(
        "연령대 선택:",
        options=df_reshaped["연령대"].dropna().unique(),
        default=df_reshaped["연령대"].dropna().unique()
    )

    # 선실 등급 선택
    pclass_filter = st.multiselect(
        "선실 등급 선택:",
        options=sorted(df_reshaped["Pclass"].unique()),
        default=sorted(df_reshaped["Pclass"].unique())
    )

    # 승선 항구 선택
    embarked_filter = st.multiselect(
        "승선 항구 선택:",
        options=df_reshaped["Embarked"].dropna().unique(),
        default=df_reshaped["Embarked"].dropna().unique()
    )

    # ✅ 필터 적용
    filtered_df = df_reshaped[
        (df_reshaped["Sex"].isin(sex_filter)) &
        (df_reshaped["연령대"].isin(age_group_filter)) &
        (df_reshaped["Pclass"].isin(pclass_filter)) &
        (df_reshaped["Embarked"].isin(embarked_filter))
    ]


#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

# --------------------------
# Col1: 요약 지표
# --------------------------
with col[0]:
    st.subheader("📊 요약 지표")

    total_passengers = filtered_df.shape[0]
    st.metric("전체 인원", total_passengers)

    survived_count = filtered_df["Survived"].sum()
    st.metric("생존자 수", survived_count)

    dead_count = total_passengers - survived_count
    st.metric("사망자 수", dead_count)

    survival_rate = (survived_count / total_passengers * 100) if total_passengers > 0 else 0
    st.metric("생존율 (%)", f"{survival_rate:.1f}%")

    avg_age = filtered_df["Age"].mean()
    st.metric("평균 나이", f"{avg_age:.1f}" if not pd.isna(avg_age) else "N/A")

    avg_fare = filtered_df["Fare"].mean()
    st.metric("평균 운임 ($)", f"{avg_fare:.2f}" if not pd.isna(avg_fare) else "N/A")


# --------------------------
# Col2: 시각화
# --------------------------
with col[1]:
    st.subheader("📈 생존 패턴 시각화")

    # 1. 성별별 생존율 (female=분홍, male=파랑)
    sex_survival = filtered_df.groupby("Sex")["Survived"].mean().reset_index()
    sex_chart = alt.Chart(sex_survival).mark_bar().encode(
        x=alt.X("Sex:N", title="성별"),
        y=alt.Y("Survived:Q", title="생존율"),
        color=alt.Color(
            "Sex:N",
            scale=alt.Scale(domain=["female", "male"],
                            range=["#FF69B4", "#1E90FF"]),  # ✅ 색상 지정
            legend=alt.Legend(title="성별")
        ),
        tooltip=["Sex", alt.Tooltip("Survived:Q", format=".2f")]
    ).properties(title="성별별 생존율", width=300, height=250)
    st.altair_chart(sex_chart, use_container_width=True)

    # 2. 선실 등급별 생존율
    pclass_survival = filtered_df.groupby("Pclass")["Survived"].mean().reset_index()
    pclass_chart = alt.Chart(pclass_survival).mark_bar().encode(
        x=alt.X("Pclass:N", title="선실 등급"),
        y=alt.Y("Survived:Q", title="생존율"),
        color="Pclass:N",
        tooltip=["Pclass", alt.Tooltip("Survived:Q", format=".2f")]
    ).properties(title="선실 등급별 생존율", width=300, height=250)
    st.altair_chart(pclass_chart, use_container_width=True)

    # 3. 연령대별 생존 여부 분포 (1=파랑, 0=검정)
    age_group_chart = px.histogram(
        filtered_df,
        x="연령대",
        color="Survived",
        barmode="group",
        labels={"Survived": "생존 여부", "연령대": "연령대"},
        title="연령대별 생존 여부 분포",
        color_discrete_map={
            1: "blue",   # ✅ 생존자
            0: "black"   # ✅ 사망자
        }
    )
    st.plotly_chart(age_group_chart, use_container_width=True)


# --------------------------
# Col3: 상세 분석
# --------------------------
with col[2]:
    st.subheader("🔎 상세 분석")

    st.markdown("**성별 × 선실 등급별 생존율 Top 그룹**")
    survival_group = (
        filtered_df.groupby(["Sex", "Pclass"])["Survived"]
        .mean()
        .reset_index()
        .sort_values("Survived", ascending=False)
    )
    st.dataframe(survival_group, use_container_width=True)

    st.markdown("**승객 상세 데이터 (상위 10명)**")
    display_cols = ["Name", "Age", "연령대", "Sex", "Pclass", "Fare", "Survived"]
    st.dataframe(filtered_df[display_cols].head(10), use_container_width=True)

    st.markdown("---")
    st.markdown("### 📖 About")
    st.markdown(
        """
        이 대시보드는 **Kaggle Titanic 데이터셋**을 기반으로 제작되었습니다.  
        - 사이드바: 필터 선택  
        - Col1: 핵심 지표  
        - Col2: 생존 패턴 시각화 (성별/등급/연령대)  
        - Col3: 그룹별 분석 & 상세 데이터  
        """
    )
