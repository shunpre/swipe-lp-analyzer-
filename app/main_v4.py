"""
瞬ジェネ AIアナリスト - Step 2完成版
グラフ説明と比較機能を追加
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# ページ設定
st.set_page_config(
    page_title="瞬ジェネ AIアナリスト",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #002060;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #002060;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .graph-description {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 1rem;
        padding: 0.5rem;
        background-color: #f8f9fa;
        border-radius: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# データ読み込み
@st.cache_data
def load_data():
    """ダミーデータを読み込む"""
    df = pd.read_csv("/home/ubuntu/swipe_lp_analyzer/app/dummy_data.csv")
    df['event_timestamp'] = pd.to_datetime(df['event_timestamp'])
    df['event_date'] = pd.to_datetime(df['event_date'])
    return df

# 比較期間のデータを取得する関数
def get_comparison_data(df, current_start, current_end, comparison_type):
    """
    比較期間のデータを取得
    comparison_type: 'previous_period', 'previous_week', 'previous_month', 'previous_year'
    """
    period_length = (current_end - current_start).days
    
    if comparison_type == 'previous_period':
        comp_end = current_start - timedelta(days=1)
        comp_start = comp_end - timedelta(days=period_length)
    elif comparison_type == 'previous_week':
        comp_end = current_end - timedelta(weeks=1)
        comp_start = current_start - timedelta(weeks=1)
    elif comparison_type == 'previous_month':
        comp_end = current_end - timedelta(days=30)
        comp_start = current_start - timedelta(days=30)
    elif comparison_type == 'previous_year':
        comp_end = current_end - timedelta(days=365)
        comp_start = current_start - timedelta(days=365)
    else:
        return None
    
    comparison_df = df[(df['event_date'] >= comp_start) & (df['event_date'] <= comp_end)]
    return comparison_df, comp_start, comp_end

# データ読み込み
df = load_data()

# サイドバー: タイトル
st.sidebar.markdown('<h1 style="color: #002060; font-size: 1.8rem; font-weight: bold; margin-bottom: 1rem;">瞬ジェネ AIアナリスト</h1>', unsafe_allow_html=True)
st.sidebar.markdown("---")

# サイドバー: フィルター
st.sidebar.header("フィルター設定")

# 期間選択（GA4スタイル）
period_options = day - timedelta(days=1)
elif selected_period == "過去7日間":
    start_date = today 
elif selected_period == "過去14日間":    start_date = today - timedelta(days=13)

elif selected_period == "過去30日間":
    start_date = today - timedelta(days=29)
    end_date = today
elif selected_period ==replace(day=1)
    end_date = today
elif selected_period == "先月":
    last_month_end = today.replace(day=1) - timedelta(days=1)
    start_date = last_month_end.replace(day=1)
    end_date = last_month_end
elif selected_period == "全期間":
    start_date = df['event_date'].min()
    end_date = df['event_date'].max()
elif selected_period == "カスタム":
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("開始日", df['event_date'].min())
    with col2:
        end_date = st.date_input("終了日", df['event_date'].max())

# LP選択
lp_options = ["すべて"] + sorted(df['page_location'].dropna().unique().tolist())
selected_lps = st.sidebar.multiselect("LP選択", lp_options, default=["すべて"])

# チャネル選択
channel_map = {
    "google": "Organic Search", wOrganic Social",
}
df['channel'] = df['utm_source'].map(channel_map).fillna("Other")

channel_options = ["すべて"] + sorted(df['channel'].unique().tolist())
selected_channels = st.sidebar.multiselect("チャネル", channel_options, default=["すべて"])

# デバイス選択
device_options = ["すべて"] + sorted(df['d#スnt'].dropna().unique().tolist())
selected_ab = st.sidebar.multiselect("A/Bテスト", ab_options, default=["すべて"])

# 比較機能の設定
st.sidebar.markdown("---")
st.sidebar.header("比較設定")
enable_comparison = st.sidebar.checkbox("比較機能を有効化", value=False)
comparison_type = None
if enable_comparison:
    comparison_options = {
        "前期間": "previous_period",
        "前週": "previous_week",
        "前月": "previous_month",
        "前年": "previous_year"
    }
    selected_comparison = st.sidebar.selectbox("比較対象", list(comparison_options.keys()))
    comparison_type = comparison_options[selected_comparison]

# データフィルタリング
filtered_df = df.copy()

# 期間フィルター
filtered_df = filtered_df[(filtered_df['event_date'] >= pd.Timestamp(start_date)) & 
                          (filtered_df['event_date'] <= pd.Timestamp(end_date))]

# LPフィルター
if "すべて" not in selected_lps:
    filtered_df = filtered_df[filtered_df['page_location'].isin(selected_lps)]

# チャネルフィルター
if "すべて" not in selected_channels:
    filtered_df = filtered_df[filtered_df['channel'].isin(selected_channels)]

# デバイスフィルター
if "すべて" not in selected_devices:
    filtered_df = filtered_df[filtered_df['device_type'].isin(selected_devices)]

# A/Bテストフィルター
if "すべて" not in selected_ab:
    filtered_df = filtered_df[filtered_df['ab_test_variant'].isin(selected_ab)]

# 比較データの取得
comparison_df = None
if enable_comparison and comparison_type:
    result = get_comparison_data(df, pd.Timestamp(start_date), pd.Timestamp(end_date), comparison_type)
    if result:
        comparison_df, comp_start, comp_end = result
        # 比較データにも同じフィルターを適用
        if "すべて" not in selected_lps:
            comparison_df = comparison_df[comparison_df['page_location'].isin(selected_lps)]
        if "すべて" not in selected_channels:
            comparison_df = comparison_df[comparison_df['channel'].isin(selected_channels)]
        if "すべて" not in selected_devices:
            comparison_df = comparison_df[comparison_df['device_type'].isin(selected_devices)]
        if "すべて" not in selected_ab:
            comparison_df = comparison_df[comparison_df['ab_test_variant'].isin(selected_ab)]

# メインタイトル
st.markdown('<div class="main-header">瞬ジェネ AIアナリスト</div>', unsafe_allow_html=True)
st.markdown(f"**分析期間:** {start_date} 〜 {end_date}")
if enable_comparison and comparison_df is not None:
    st.markdown(f"**比較期間:** {comp_start.date()} 〜 {comp_end.date()}")

# KPI計算
total_sessions = filtered_df['session_id'].nunique()
total_conversions = filtered_df[filtered_df['cv_type'].notna()]['session_id'].nunique()
conversion_rate = (total_conversions / total_sessions * 100) if total_sessions > 0 else 0

total_clicks = filtered_df[filtered_df['event_name'] == 'click']['session_id'].nunique()
click_rate = (total_clicks / total_sessions * 100) if total_sessions > 0 else 0

avg_pages_reached = filtered_df.groupby('session_id')['page_index'].max().mean()
avg_stay_time = filtered_df['stay_ms'].mean() / 1000

fv_sessions = filtered_df[filtered_df['page_index'] == 1]['session_id'].nunique()
fv_next_sessions = filtered_df[filtered_df['page_index'] > 1]['session_id'].nunique()
fv_retention_rate = (fv_next_sessions / fv_sessions * 100) if fv_sessions > 0 else 0

max_page_index = filtered_df['page_index'].max()
final_cta_sessions = filtered_df[filtered_df['page_index'] == max_page_index]['session_id'].nunique()
final_cta_rate = (final_cta_sessions / total_sessions * 100) if total_sessions > 0 else 0

avg_load_time = filtered_df['page_load_ms'].mean()

# 比較期間のKPI計算
if comparison_df is not None and len(comparison_df) > 0:
    comp_sessions = comparison_df['session_id'].nunique()
    comp_conversions = comparison_df[comparison_df['cv_type'].notna()]['session_id'].nunique()
    comp_cvr = (comp_conversions / comp_sessions * 100) if comp_sessions > 0 else 0
    
    comp_clicks = comparison_df[comparison_df['event_name'] == 'click']['session_id'].nunique()
    comp_ctr = (comp_clicks / comp_sessions * 100) if comp_sessions > 0 else 0
    
    comp_avg_pages = comparison_df.groupby('session_id')['page_index'].max().mean()
    comp_avg_stay = comparison_df['stay_ms'].mean() / 1000
    
    comp_fv_sessions = comparison_df[comparison_df['page_index'] == 1]['session_id'].nunique()
    comp_fv_next = comparison_df[comparison_df['page_index'] > 1]['session_id'].nunique()
    comp_fv_retention = (comp_fv_next / comp_fv_sessions * 100) if comp_fv_sessions > 0 else 0
    
    comp_max_page = comparison_df['page_index'].max()
    comp_final_cta = comparison_df[comparison_df['page_index'] == comp_max_page]['session_id'].nunique()
    comp_final_cta_rate = (comp_final_cta / comp_sessions * 100) if comp_sessions > 0 else 0
    
    comp_load_time = comparison_df['page_load_ms'].mean()

# KPI表示
st.markdown("### 主要指標")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if comparison_df is not None:
        delta_sessions = total_sessions - comp_sessions
        delta_sessions_pct = ((total_sessions - comp_sessions) / comp_sessions * 100) if comp_sessions > 0 else 0
        st.metric("セッション数", f"{total_sessions:,}", delta=f"{delta_sessions:+,} ({delta_sessions_pct:+.1f}%)")
        
        delta_conv = total_conversions - comp_conversions
        delta_conv_pct = ((total_conversions - comp_conversions) / comp_conversions * 100) if comp_conversions > 0 else 0
        st.metric("コンバージョン数", f"{total_conversions:,}", delta=f"{delta_conv:+,} ({delta_conv_pct:+.1f}%)")
    else:
        st.metric("セッション数", f"{total_sessions:,}")
        st.metric("コンバージョン数", f"{total_conversions:,}")

with col2:
    if comparison_df is not None:
        delta_cvr = conversion_rate - comp_cvr
        st.metric("コンバージョン率", f"{conversion_rate:.2f}%", delta=f"{delta_cvr:+.2f}%")
        
        delta_clicks = total_clicks - comp_clicks
        delta_clicks_pct = ((total_clicks - comp_clicks) / comp_clicks * 100) if comp_clicks > 0 else 0
        st.metric("クリック数", f"{total_clicks:,}", delta=f"{delta_clicks:+,} ({delta_clicks_pct:+.1f}%)")
    else:
        st.metric("コンバージョン率", f"{conversion_rate:.2f}%")
        st.metric("クリック数", f"{total_clicks:,}")

with col3:
    if comparison_df is not None:
        delta_ctr = click_rate - comp_ctr
        st.metric("クリック率", f"{click_rate:.2f}%", delta=f"{delta_ctr:+.2f}%")
        
        delta_pages = avg_pages_reached - comp_avg_pages
        st.metric("平均到達ページ数", f"{avg_pages_reached:.1f}", delta=f"{delta_pages:+.1f}")
    else:
        st.metric("クリック率", f"{click_rate:.2f}%")
        st.metric("平均到達ページ数", f"{avg_pages_reached:.1f}")

with col4:
    if comparison_df is not None:
        delta_stay = avg_stay_time - comp_avg_stay
        st.metric("平均滞在時間", f"{avg_stay_time:.1f}秒", delta=f"{delta_stay:+.1f}秒")
        
        delta_fv = fv_retention_rate - comp_fv_retention
        st.metric("FV残存率", f"{fv_retention_rate:.1f}%", delta=f"{delta_fv:+.1f}%")
    else:
        st.metric("平均滞在時間", f"{avg_stay_time:.1f}秒")
        st.metric("FV残存率", f"{fv_retention_rate:.1f}%")

with col5:
    if comparison_df is not None:
        delta_final = final_cta_rate - comp_final_cta_rate
        st.metric("最終CTA到達率", f"{final_cta_rate:.1f}%", delta=f"{delta_final:+.1f}%")
        
        delta_load = avg_load_time - comp_load_time
        st.metric("平均読込時間", f"{avg_load_time:.0f}ms", delta=f"{delta_load:+.0f}ms", delta_color="inverse")
    else:
        st.metric("最終CTA到達率", f"{final_cta_rate:.1f}%")
        st.metric("平均読込時間", f"{avg_load_time:.0f}ms")
