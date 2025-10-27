"""
瞬ジェネ AIアナリスト - Step 2完成版
グラフ説明と比較機能を追加
50項目以上の分析・グラフを実装
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from capture_lp import capture_lp_screenshot, extract_swipe_lp_images

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
        border-left: 3px solid #002060;
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
st.sidebar.markdown('<h1 style="color: #002060; font-size: 1.8rem; font-weight: bold; margin-bottom: 1rem; line-height: 1.3;">瞬ジェネ<br>AIアナリスト</h1>', unsafe_allow_html=True)
st.sidebar.markdown("---")

# サイドバー: 分析項目メニュー
st.sidebar.header("📊 分析項目")

# session_stateで選択状態を管理
if 'selected_analysis' not in st.session_state:
    st.session_state.selected_analysis = "AI分析"

# メニュー項目リスト
menu_items = [
    "AI分析",
    "全体分析",
    "ページ分析",
    "セグメント分析",
    "A/Bテスト分析",
    "インタラクション分析",
    "動画・スクロール分析",
    "時系列分析",
    "リアルタイム分析",
    "デモグラフィック情報",
    "使用ガイド",
    "専門用語解説"
]

# テキストリンク形式で表示
for item in menu_items:
    if st.session_state.selected_analysis == item:
        # 選択中の項目は太字で表示
        st.sidebar.markdown(f'<div style="padding: 0.5rem; background-color: #e6f0ff; border-left: 4px solid #002060; margin-bottom: 0.25rem;"><strong>{item}</strong></div>', unsafe_allow_html=True)
    else:
        # 選択されていない項目はクリック可能
        if st.sidebar.button(item, key=f"menu_{item}", use_container_width=True):
            st.session_state.selected_analysis = item
            st.rerun()

selected_analysis = st.session_state.selected_analysis

# チャネルマッピング（データ処理に必要）
channel_map = {
    "google": "Organic Search",
    "facebook": "Organic Social",
    "instagram": "Organic Social",
    "twitter": "Organic Social",
    "direct": "Direct"
}
df['channel'] = df['utm_source'].map(channel_map).fillna("Referral")

# メインエリア: フィルターと比較設定
st.markdown('<div class="sub-header">⚙️ フィルター設定</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([2, 2, 1.5, 1.5])

with col1:
    # 期間選択
    period_options = {
        "過去7日間": 7,
        "過去30日間": 30,
        "過去90日間": 90,
        "カスタム期間": None
    }
    selected_period = st.selectbox("期間を選択", list(period_options.keys()), index=1)

with col2:
    # LP選択
    lp_options = ["すべて"] + sorted(df['page_location'].dropna().unique().tolist())
    selected_lps = st.multiselect("LP選択", lp_options, default=["すべて"])

with col3:
    # 比較機能
    enable_comparison = st.checkbox("比較機能", value=False)

with col4:
    # 比較対象
    comparison_type = None
    if enable_comparison:
        comparison_options = {
            "前期間": "previous_period",
            "前週": "previous_week",
            "前月": "previous_month",
            "前年": "previous_year"
        }
        selected_comparison = st.selectbox("比較対象", list(comparison_options.keys()))
        comparison_type = comparison_options[selected_comparison]

# カスタム期間の場合
if selected_period == "カスタム期間":
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("開始日", df['event_date'].min())
    with col2:
        end_date = st.date_input("終了日", df['event_date'].max())
else:
    days = period_options[selected_period]
    end_date = df['event_date'].max()
    start_date = end_date - timedelta(days=days)

st.markdown("---")

# データフィルタリング
filtered_df = df.copy()

# 期間フィルター
filtered_df = filtered_df[
    (filtered_df['event_date'] >= pd.to_datetime(start_date)) &
    (filtered_df['event_date'] <= pd.to_datetime(end_date))
]

# LPフィルター
if "すべて" not in selected_lps:
    filtered_df = filtered_df[filtered_df['page_location'].isin(selected_lps)]

# チャネルフィルター（削除）
# デバイスフィルター（削除）
# A/Bテストフィルター（削除）

# 比較データの取得
comparison_df = None
comp_start = None
comp_end = None
if enable_comparison and comparison_type:
    result = get_comparison_data(df, pd.Timestamp(start_date), pd.Timestamp(end_date), comparison_type)
    if result is not None:
        comparison_df, comp_start, comp_end = result
        # 比較データにも同じフィルターを適用
        if "すべて" not in selected_lps:
            comparison_df = comparison_df[comparison_df['page_location'].isin(selected_lps)]
        # 比較データが空の場合は無効化
        if len(comparison_df) == 0:
            comparison_df = None
            st.info(f"ℹ️ 比較期間（{comp_start.strftime('%Y-%m-%d')} 〜 {comp_end.strftime('%Y-%m-%d')}）にデータがありません。")

# データが空の場合の処理
if len(filtered_df) == 0:
    st.warning("⚠️ 選択した条件に該当するデータがありません。フィルターを変更してください。")
    st.stop()

# 基本メトリクス計算
total_sessions = filtered_df['session_id'].nunique()
total_conversions = filtered_df[filtered_df['cv_type'].notna()]['session_id'].nunique()
conversion_rate = (total_conversions / total_sessions * 100) if total_sessions > 0 else 0
total_clicks = len(filtered_df[filtered_df['event_name'] == 'click'])
click_rate = (total_clicks / total_sessions * 100) if total_sessions > 0 else 0
avg_stay_time = filtered_df['stay_ms'].mean() / 1000  # 秒に変換
avg_pages_reached = filtered_df.groupby('session_id')['max_page_reached'].max().mean()
fv_retention_rate = (filtered_df[filtered_df['max_page_reached'] >= 2]['session_id'].nunique() / total_sessions * 100) if total_sessions > 0 else 0
final_cta_rate = (filtered_df[filtered_df['max_page_reached'] >= 10]['session_id'].nunique() / total_sessions * 100) if total_sessions > 0 else 0
avg_load_time = filtered_df['load_time_ms'].mean()

# 比較データのKPI計算
comp_kpis = {}
if comparison_df is not None and len(comparison_df) > 0:
    comp_total_sessions = comparison_df['session_id'].nunique()
    comp_total_conversions = comparison_df[comparison_df['cv_type'].notna()]['session_id'].nunique()
    comp_conversion_rate = (comp_total_conversions / comp_total_sessions * 100) if comp_total_sessions > 0 else 0
    comp_total_clicks = len(comparison_df[comparison_df['event_name'] == 'click'])
    comp_click_rate = (comp_total_clicks / comp_total_sessions * 100) if comp_total_sessions > 0 else 0
    comp_avg_stay_time = comparison_df['stay_ms'].mean() / 1000
    comp_avg_pages_reached = comparison_df.groupby('session_id')['max_page_reached'].max().mean()
    comp_fv_retention_rate = (comparison_df[comparison_df['max_page_reached'] >= 2]['session_id'].nunique() / comp_total_sessions * 100) if comp_total_sessions > 0 else 0
    comp_final_cta_rate = (comparison_df[comparison_df['max_page_reached'] >= 10]['session_id'].nunique() / comp_total_sessions * 100) if comp_total_sessions > 0 else 0
    comp_avg_load_time = comparison_df['load_time_ms'].mean()
    
    comp_kpis = {
        'sessions': comp_total_sessions,
        'conversions': comp_total_conversions,
        'conversion_rate': comp_conversion_rate,
        'clicks': comp_total_clicks,
        'click_rate': comp_click_rate,
        'avg_stay_time': comp_avg_stay_time,
        'avg_pages_reached': comp_avg_pages_reached,
        'fv_retention_rate': comp_fv_retention_rate,
        'final_cta_rate': comp_final_cta_rate,
        'avg_load_time': comp_avg_load_time
    }

# KPI表示
st.markdown('<div class="sub-header">📈 主要指標（KPI）</div>', unsafe_allow_html=True)

# KPIカード表示
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    delta_sessions = total_sessions - comp_kpis.get('sessions', 0) if comp_kpis else None
    st.metric("セッション数", f"{total_sessions:,}", delta=f"{delta_sessions:+,}" if delta_sessions is not None else None)
    
    delta_conversions = total_conversions - comp_kpis.get('conversions', 0) if comp_kpis else None
    st.metric("コンバージョン数", f"{total_conversions:,}", delta=f"{delta_conversions:+,}" if delta_conversions is not None else None)

with col2:
    delta_cvr = conversion_rate - comp_kpis.get('conversion_rate', 0) if comp_kpis else None
    st.metric("コンバージョン率", f"{conversion_rate:.2f}%", delta=f"{delta_cvr:+.2f}%" if delta_cvr is not None else None)
    
    delta_clicks = total_clicks - comp_kpis.get('clicks', 0) if comp_kpis else None
    st.metric("クリック数", f"{total_clicks:,}", delta=f"{delta_clicks:+,}" if delta_clicks is not None else None)

with col3:
    delta_click_rate = click_rate - comp_kpis.get('click_rate', 0) if comp_kpis else None
    st.metric("クリック率", f"{click_rate:.2f}%", delta=f"{delta_click_rate:+.2f}%" if delta_click_rate is not None else None)
    
    delta_pages = avg_pages_reached - comp_kpis.get('avg_pages_reached', 0) if comp_kpis else None
    st.metric("平均到達ページ数", f"{avg_pages_reached:.1f}", delta=f"{delta_pages:+.1f}" if delta_pages is not None else None)

with col4:
    delta_stay = avg_stay_time - comp_kpis.get('avg_stay_time', 0) if comp_kpis else None
    st.metric("平均滞在時間", f"{avg_stay_time:.1f}秒", delta=f"{delta_stay:+.1f}秒" if delta_stay is not None else None)
    
    delta_fv = fv_retention_rate - comp_kpis.get('fv_retention_rate', 0) if comp_kpis else None
    st.metric("FV残存率", f"{fv_retention_rate:.1f}%", delta=f"{delta_fv:+.1f}%" if delta_fv is not None else None)

with col5:
    delta_cta = final_cta_rate - comp_kpis.get('final_cta_rate', 0) if comp_kpis else None
    st.metric("最終CTA到達率", f"{final_cta_rate:.1f}%", delta=f"{delta_cta:+.1f}%" if delta_cta is not None else None)
    
    delta_load = avg_load_time - comp_kpis.get('avg_load_time', 0) if comp_kpis else None
    st.metric("平均読込時間", f"{avg_load_time:.0f}ms", delta=f"{delta_load:+.0f}ms" if delta_load is not None else None, delta_color="inverse")

# 選択された分析項目に応じて表示を切り替え

if selected_analysis == "全体分析":
    st.markdown('<div class="sub-header">全体分析</div>', unsafe_allow_html=True)
    
    # 主要指標詳細表（LP別の表形式）
    st.markdown("主要指標詳細表")
    st.markdown('<div class="graph-description">主要なKPIをLP別に一覧表示します。左列がページパス（LP URL）、上行が指標です。</div>', unsafe_allow_html=True)
    
    # LP別にメトリクスを計算
    lp_metrics = []
    
    # 選択されたLPごとに計算
    for lp_key in selected_lps:
        if lp_key == 'すべて':
            continue
        
        # page_locationを使用してフィルタリング
        lp_data = filtered_df[filtered_df['page_location'] == lp_key]
        
        if len(lp_data) == 0:
            continue
        
        # メトリクス計算
        lp_sessions = lp_data['session_id'].nunique()
        lp_conversions = lp_data[lp_data['cv_type'].notna()]['session_id'].nunique()
        lp_conversion_rate = (lp_conversions / lp_sessions * 100) if lp_sessions > 0 else 0
        
        lp_clicks = lp_data[lp_data['event_name'] == 'click']['session_id'].nunique()
        lp_click_rate = (lp_clicks / lp_sessions * 100) if lp_sessions > 0 else 0
        
        lp_fv_sessions = lp_data[lp_data['page_num_dom'] == 1]['session_id'].nunique()
        lp_fv_retention = lp_data[(lp_data['page_num_dom'] == 1) & (lp_data['max_page_reached'] > 1)]['session_id'].nunique()
        lp_fv_retention_rate = (lp_fv_retention / lp_fv_sessions * 100) if lp_fv_sessions > 0 else 0
        
        lp_max_page = lp_data['page_num_dom'].max()
        lp_final_cta_reached = lp_data[lp_data['max_page_reached'] >= lp_max_page]['session_id'].nunique()
        lp_final_cta_rate = (lp_final_cta_reached / lp_sessions * 100) if lp_sessions > 0 else 0
        
        lp_avg_pages = lp_data.groupby('session_id')['page_num_dom'].max().mean()
        lp_avg_stay = lp_data.groupby('session_id')['stay_ms'].sum().mean() / 1000
        lp_avg_load = lp_data['load_time_ms'].mean()
        
        lp_metrics.append({
            'ページパス': lp_key,
            'セッション数': f"{lp_sessions:,}",
            'CV数': f"{lp_conversions:,}",
            'CVR': f"{lp_conversion_rate:.2f}%",
            'クリック数': f"{lp_clicks:,}",
            'CTR': f"{lp_click_rate:.2f}%",
            'FV残存率': f"{lp_fv_retention_rate:.2f}%",
            '最終CTA到達率': f"{lp_final_cta_rate:.2f}%",
            '平均到達ページ': f"{lp_avg_pages:.2f}",
            '平均滞在時間': f"{lp_avg_stay:.1f}秒",
            '平均読込時間': f"{lp_avg_load:.0f}ms"
        })
    
    # 「すべて」が選択されている場合は全体の集計を追加
    if 'すべて' in selected_lps or len(lp_metrics) == 0:
        lp_metrics.append({
            'ページパス': '全体',
            'セッション数': f"{total_sessions:,}",
            'CV数': f"{total_conversions:,}",
            'CVR': f"{conversion_rate:.2f}%",
            'クリック数': f"{total_clicks:,}",
            'CTR': f"{click_rate:.2f}%",
            'FV残存率': f"{fv_retention_rate:.2f}%",
            '最終CTA到達率': f"{final_cta_rate:.2f}%",
            '平均到達ページ': f"{avg_pages_reached:.2f}",
            '平均滞在時間': f"{avg_stay_time:.1f}秒",
            '平均読込時間': f"{avg_load_time:.0f}ms"
        })
    
    kpi_table_df = pd.DataFrame(lp_metrics)
    st.table(kpi_table_df)
    
    st.markdown("---")
    
    # グラフ選択
    st.markdown("**表示するグラフを選択してください:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_session_trend = st.checkbox("セッション数の推移", value=True)
        show_cvr_trend = st.checkbox("コンバージョン率の推移", value=True)
        show_device_breakdown = st.checkbox("デバイス別分析", value=True)
    
    with col2:
        show_channel_breakdown = st.checkbox("チャネル別分析", value=True)
        show_funnel = st.checkbox("LP進行ファネル", value=True)
        show_hourly_cvr = st.checkbox("時間帯別CVR", value=False)
    
    with col3:
        show_dow_cvr = st.checkbox("曜日別CVR", value=False)
        show_utm_analysis = st.checkbox("UTM分析", value=False)
        show_load_time = st.checkbox("読込時間分析", value=False)
    
    # セッション数の推移
    if show_session_trend:
        st.markdown("#### セッション数の推移")
        st.markdown('<div class="graph-description">日ごとのセッション数（訪問数）の変化を表示します。トレンドや曜日ごとのパターンを把握できます。</div>', unsafe_allow_html=True)
        daily_sessions = filtered_df.groupby(filtered_df['event_date'].dt.date)['session_id'].nunique().reset_index()
        daily_sessions.columns = ['日付', 'セッション数']
        
        if comparison_df is not None and len(comparison_df) > 0:
            # 比較データを追加
            comp_daily_sessions = comparison_df.groupby(comparison_df['event_date'].dt.date)['session_id'].nunique().reset_index()
            comp_daily_sessions.columns = ['日付', '比較期間セッション数']
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daily_sessions['日付'], y=daily_sessions['セッション数'], 
                                    mode='lines+markers', name='現在期間', line=dict(color='#002060')))
            fig.add_trace(go.Scatter(x=comp_daily_sessions['日付'], y=comp_daily_sessions['比較期間セッション数'], 
                                    mode='lines+markers', name='比較期間', line=dict(color='#999999', dash='dash')))
            fig.update_layout(height=400, hovermode='x unified')
        else:
            fig = px.line(daily_sessions, x='日付', y='セッション数', markers=True)
            fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_1')
    
    # コンバージョン率の推移
    if show_cvr_trend:
        st.markdown("#### コンバージョン率の推移")
        st.markdown('<div class="graph-description">日ごとのコンバージョン率（CVR）の変化を表示します。LPの改善効果や外部要因の影響を確認できます。</div>', unsafe_allow_html=True)
        daily_cvr = filtered_df.groupby(filtered_df['event_date'].dt.date).agg({
            'session_id': 'nunique',
        }).reset_index()
        daily_cvr.columns = ['日付', 'セッション数']
        
        daily_cv = filtered_df[filtered_df['cv_type'].notna()].groupby(
            filtered_df[filtered_df['cv_type'].notna()]['event_date'].dt.date
        )['session_id'].nunique().reset_index()
        daily_cv.columns = ['日付', 'コンバージョン数']
        
        daily_cvr = daily_cvr.merge(daily_cv, on='日付', how='left').fillna(0)
        daily_cvr['コンバージョン率'] = (daily_cvr['コンバージョン数'] / daily_cvr['セッション数'] * 100)
        
        if comparison_df is not None and len(comparison_df) > 0:
            # 比較データを追加
            comp_daily_cvr = comparison_df.groupby(comparison_df['event_date'].dt.date).agg({'session_id': 'nunique'}).reset_index()
            comp_daily_cvr.columns = ['日付', 'セッション数']
            
            comp_daily_cv = comparison_df[comparison_df['cv_type'].notna()].groupby(
                comparison_df[comparison_df['cv_type'].notna()]['event_date'].dt.date
            )['session_id'].nunique().reset_index()
            comp_daily_cv.columns = ['日付', 'コンバージョン数']
            
            comp_daily_cvr = comp_daily_cvr.merge(comp_daily_cv, on='日付', how='left').fillna(0)
            comp_daily_cvr['比較期間CVR'] = (comp_daily_cvr['コンバージョン数'] / comp_daily_cvr['セッション数'] * 100)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daily_cvr['日付'], y=daily_cvr['コンバージョン率'], 
                                    mode='lines+markers', name='現在期間', line=dict(color='#002060')))
            fig.add_trace(go.Scatter(x=comp_daily_cvr['日付'], y=comp_daily_cvr['比較期間CVR'], 
                                    mode='lines+markers', name='比較期間', line=dict(color='#999999', dash='dash')))
            fig.update_layout(height=400, hovermode='x unified', yaxis_title='コンバージョン率 (%)')
        else:
            fig = px.line(daily_cvr, x='日付', y='コンバージョン率', markers=True)
            fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_2')
    
    # デバイス別分析
    if show_device_breakdown:
        st.markdown("#### デバイス別分析")
        st.markdown('<div class="graph-description">デバイス（スマホ、PC、タブレット）ごとのセッション数、コンバージョン数、CVRを比較します。デバイス最適化の優先度を判断できます。</div>', unsafe_allow_html=True)
        device_stats = filtered_df.groupby('device_type').agg({
            'session_id': 'nunique',
        }).reset_index()
        device_stats.columns = ['デバイス', 'セッション数']
        
        device_cv = filtered_df[filtered_df['cv_type'].notna()].groupby('device_type')['session_id'].nunique().reset_index()
        device_cv.columns = ['デバイス', 'コンバージョン数']
        
        device_stats = device_stats.merge(device_cv, on='デバイス', how='left').fillna(0)
        device_stats['コンバージョン率'] = (device_stats['コンバージョン数'] / device_stats['セッション数'] * 100)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='セッション数', x=device_stats['デバイス'], y=device_stats['セッション数'], yaxis='y', offsetgroup=1))
        fig.add_trace(go.Bar(name='コンバージョン数', x=device_stats['デバイス'], y=device_stats['コンバージョン数'], yaxis='y', offsetgroup=2))
        fig.add_trace(go.Scatter(name='コンバージョン率', x=device_stats['デバイス'], y=device_stats['コンバージョン率'], yaxis='y2', mode='lines+markers'))
        
        fig.update_layout(
            yaxis=dict(title='セッション数 / コンバージョン数'),
            yaxis2=dict(title='コンバージョン率 (%)', overlaying='y', side='right'),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_3')
    
    # チャネル別分析
    if show_channel_breakdown:
        st.markdown("#### チャネル別分析")
        st.markdown('<div class="graph-description">流入経路（Google、SNS、直接アクセスなど）ごとのパフォーマンスを比較します。効果的な集客チャネルを特定できます。</div>', unsafe_allow_html=True)
        channel_stats = filtered_df.groupby('channel').agg({
            'session_id': 'nunique',
            'stay_ms': 'mean'
        }).reset_index()
        channel_stats.columns = ['チャネル', 'セッション数', '平均滞在時間(ms)']
        channel_stats['平均滞在時間(秒)'] = channel_stats['平均滞在時間(ms)'] / 1000
        
        channel_cv = filtered_df[filtered_df['cv_type'].notna()].groupby('channel')['session_id'].nunique().reset_index()
        channel_cv.columns = ['チャネル', 'コンバージョン数']
        
        channel_stats = channel_stats.merge(channel_cv, on='チャネル', how='left').fillna(0)
        channel_stats['コンバージョン率'] = (channel_stats['コンバージョン数'] / channel_stats['セッション数'] * 100)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(channel_stats, values='セッション数', names='チャネル', title='チャネル別セッション数')
            st.plotly_chart(fig, use_container_width=True, key='plotly_chart_4')
        
        with col2:
            fig = px.bar(channel_stats, x='チャネル', y='コンバージョン率', title='チャネル別コンバージョン率')
            st.plotly_chart(fig, use_container_width=True, key='plotly_chart_5')
    
    # LP進行ファネルと滞在時間別ファネル
    if show_funnel:
        st.markdown("③③ LP進行ファネルと滞在時間別ファネル")
        st.markdown('<div class="graph-description">ユーザーがLPを進む過程で、各ページでどれだけ離脱したかを可視化します。</div>', unsafe_allow_html=True)
        
        # 実際のページ数を取得
        max_page = int(filtered_df['page_num_dom'].max()) if not filtered_df.empty else 10
        
        # 2カラムレイアウト
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**LP進行ファネル**")
            funnel_data = []
            for page_num in range(1, max_page + 1):
                count = filtered_df[filtered_df['max_page_reached'] >= page_num]['session_id'].nunique()
                funnel_data.append({'ページ': f'ページ{page_num}', 'セッション数': count})
            
            funnel_df = pd.DataFrame(funnel_data)
            
            fig = go.Figure(go.Funnel(
                y=funnel_df['ページ'],
                x=funnel_df['セッション数'],
                textinfo="value+percent initial"
            ))
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True, key='plotly_chart_6')
        
        with col2:
            st.markdown("**滞在時間別ファネル**")
            # 滞在時間別のセグメントを作成
            stay_segments = [
                ('0-10秒', 0, 10000),
                ('10-30秒', 10000, 30000),
                ('30-60秒', 30000, 60000),
                ('1-3分', 60000, 180000),
                ('3-5分', 180000, 300000),
                ('5分以上', 300000, float('inf'))
            ]
            
            stay_funnel_data = []
            for label, min_ms, max_ms in stay_segments:
                count = filtered_df[(filtered_df['stay_ms'] >= min_ms) & (filtered_df['stay_ms'] < max_ms)]['session_id'].nunique()
                stay_funnel_data.append({'滞在時間': label, 'セッション数': count})
            
            stay_funnel_df = pd.DataFrame(stay_funnel_data)
            
            fig2 = go.Figure(go.Funnel(
                y=stay_funnel_df['滞在時間'],
                x=stay_funnel_df['セッション数'],
                textinfo="value+percent initial"
            ))
            fig2.update_layout(height=600)
            st.plotly_chart(fig2, use_container_width=True, key='plotly_chart_stay_funnel')
    
    # 時間帯別CVR
    if show_hourly_cvr:
        st.markdown("#### 時間帯別コンバージョン率")
        st.markdown('<div class="graph-description">1日の中で、どの時間帯にCVRが高いかを分析します。広告配信の最適な時間帯を見つけることができます。</div>', unsafe_allow_html=True)
        filtered_df['hour'] = filtered_df['event_timestamp'].dt.hour
        
        hourly_sessions = filtered_df.groupby('hour')['session_id'].nunique().reset_index()
        hourly_sessions.columns = ['時間', 'セッション数']
        
        hourly_cv = filtered_df[filtered_df['cv_type'].notna()].groupby('hour')['session_id'].nunique().reset_index()
        hourly_cv.columns = ['時間', 'コンバージョン数']
        
        hourly_cvr = hourly_sessions.merge(hourly_cv, on='時間', how='left').fillna(0)
        hourly_cvr['コンバージョン率'] = (hourly_cvr['コンバージョン数'] / hourly_cvr['セッション数'] * 100)
        
        fig = px.bar(hourly_cvr, x='時間', y='コンバージョン率')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_7')
    
    # 曜日別CVR
    if show_dow_cvr:
        st.markdown("#### 曜日別コンバージョン率")
        st.markdown('<div class="graph-description">曜日ごとのCVRの違いを分析します。平日と週末でのユーザー行動の変化を把握できます。</div>', unsafe_allow_html=True)
        filtered_df['dow'] = filtered_df['event_timestamp'].dt.day_name()
        dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_map = {'Monday': '月', 'Tuesday': '火', 'Wednesday': '水', 'Thursday': '木', 'Friday': '金', 'Saturday': '土', 'Sunday': '日'}
        
        dow_sessions = filtered_df.groupby('dow')['session_id'].nunique().reset_index()
        dow_sessions.columns = ['曜日', 'セッション数']
        
        dow_cv = filtered_df[filtered_df['cv_type'].notna()].groupby('dow')['session_id'].nunique().reset_index()
        dow_cv.columns = ['曜日', 'コンバージョン数']
        
        dow_cvr = dow_sessions.merge(dow_cv, on='曜日', how='left').fillna(0)
        dow_cvr['コンバージョン率'] = (dow_cvr['コンバージョン数'] / dow_cvr['セッション数'] * 100)
        dow_cvr['曜日_日本語'] = dow_cvr['曜日'].map(dow_map)
        dow_cvr['曜日_order'] = dow_cvr['曜日'].apply(lambda x: dow_order.index(x))
        dow_cvr = dow_cvr.sort_values('曜日_order')
        
        fig = px.bar(dow_cvr, x='曜日_日本語', y='コンバージョン率')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_8')
    
    # UTM分析
    if show_utm_analysis:
        st.markdown("#### UTM分析")
        st.markdown('<div class="graph-description">UTMパラメータ（広告タグ）ごとのトラフィックを分析します。どのキャンペーンや媒体が効果的かを把握できます。</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**UTMソース別**")
            utm_source_stats = filtered_df.groupby('utm_source')['session_id'].nunique().reset_index()
            utm_source_stats.columns = ['UTMソース', 'セッション数']
            utm_source_stats = utm_source_stats.sort_values('セッション数', ascending=False)
            
            fig = px.bar(utm_source_stats, x='UTMソース', y='セッション数')
            st.plotly_chart(fig, use_container_width=True, key='plotly_chart_9')
        
        with col2:
            st.markdown("**UTMメディア別**")
            utm_medium_stats = filtered_df.groupby('utm_medium')['session_id'].nunique().reset_index()
            utm_medium_stats.columns = ['UTMメディア', 'セッション数']
            utm_medium_stats = utm_medium_stats.sort_values('セッション数', ascending=False)
            
            fig = px.bar(utm_medium_stats, x='UTMメディア', y='セッション数')
            st.plotly_chart(fig, use_container_width=True, key='plotly_chart_10')
    
    # 読込時間分析
    if show_load_time:
        st.markdown("#### 読込時間分析")
        st.markdown('<div class="graph-description">デバイスごとのページ読込時間を分析します。読込が遅いと離脱率が上がるため、最適化が重要です。</div>', unsafe_allow_html=True)
        
        load_time_stats = filtered_df.groupby('device_type')['load_time_ms'].mean().reset_index()
        load_time_stats.columns = ['デバイス', '平均読込時間(ms)']
        
        fig = px.bar(load_time_stats, x='デバイス', y='平均読込時間(ms)')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_11')

# 続く...（次のファイルでタブ2以降を実装）



# タブ2: ページ分析
elif selected_analysis == "ページ分析":
    st.markdown('<div class="sub-header">📄 ページ分析</div>', unsafe_allow_html=True)
    
    # 複数LP選択時の処理
    if len(selected_lps) > 1:
        # 「すべて」が含まれている場合は除外
        filtered_lps = [lp for lp in selected_lps if lp != "すべて"]
        if len(filtered_lps) == 0:
            st.error("⚠️ ページ分析は1つのLPのみを対象とします。左側のフィルターで特定のLPを選択してください。")
            st.stop()
        elif len(filtered_lps) > 1:
            st.warning("⚠️ 複数のLPが選択されています。最初のLP ({}) を使用します。".format(filtered_lps[0]))
            analysis_lp = filtered_lps[0]
        else:
            analysis_lp = filtered_lps[0]
    elif len(selected_lps) == 1:
        if selected_lps[0] == "すべて":
            # すべてが選択されている場合は、最初のLPを使用
            all_lps = sorted(df['page_location'].dropna().unique().tolist())
            analysis_lp = all_lps[0] if all_lps else None
            st.info("💡 「すべて」が選択されています。最初のLP ({}) を使用します。".format(analysis_lp))
        else:
            analysis_lp = selected_lps[0]
    else:
        st.error("⚠️ LPが選択されていません。")
        st.stop()
    
    # LP URL設定（選択されたLPに応じてURLを設定）
    lp_urls = {
        'LP A': 'https://shungene.lm-c.jp/tst08/tst08.html',
        'LP B': 'https://shungene.lm-c.jp/tst08/tst08.html',
        'LP C': 'https://shungene.lm-c.jp/tst08/tst08.html'
    }
    
    # 選択されたLPのURLを取得
    current_lp_url = lp_urls.get(analysis_lp if analysis_lp else 'LP A', 'https://shungene.lm-c.jp/tst08/tst08.html')
    
    # ページ別メトリクス計算
    page_stats = filtered_df.groupby('page_num_dom').agg({
        'session_id': 'nunique',
        'stay_ms': 'mean',
        'scroll_pct': 'mean',
        'load_time_ms': 'mean'
    }).reset_index()
    page_stats.columns = ['ページ番号', 'ビュー数', '平均滞在時間(ms)', '平均逆行率', '平均読込時間(ms)']
    page_stats['平均滞在時間(秒)'] = page_stats['平均滞在時間(ms)'] / 1000
    
    # データから推測されるページ数を先に取得
    estimated_page_count = int(filtered_df['page_num_dom'].max()) if len(filtered_df) > 0 else 10
    
    # スワイプLPの各ページ画像を取得（ページ数を先に取得）
    st.markdown("▼▼ LPプレビュー")
    st.markdown(f'<div class="graph-description">LP URL: {current_lp_url}</div>', unsafe_allow_html=True)
    
    with st.spinner("📸 スワイプLPの画像を取得中..."):
        swipe_images = extract_swipe_lp_images(current_lp_url)
    
    # LPの実際のページ数を取得（画像取得が成功した場合はそれを使用、失敗した場合は推測値）
    actual_page_count = len(swipe_images) if swipe_images else estimated_page_count
    st.info(f"📊 このLPは {actual_page_count} ページで構成されています")
    
    # 離脱率計算（LPの実際のページ数を使用）
    page_exit = []
    for page_num in range(1, actual_page_count + 1):
        reached = filtered_df[filtered_df['max_page_reached'] >= page_num]['session_id'].nunique()
        exited = filtered_df[filtered_df['max_page_reached'] == page_num]['session_id'].nunique()
        exit_rate = (exited / reached * 100) if reached > 0 else 0
        page_exit.append({'ページ番号': page_num, '離脱率': exit_rate})
    
    page_exit_df = pd.DataFrame(page_exit)
    page_stats = page_stats.merge(page_exit_df, on='ページ番号', how='left')
    
    # ダミーデータにないページを追加（ダミーデータが10ページまでしかない場合）
    import random
    for page_num in range(1, actual_page_count + 1):
        if page_num not in page_stats['ページ番号'].values:
            # ダミーデータがないページはランダムなダミー値で追加
            # ページが進むほどビュー数が減少するパターン
            base_views = 1000
            page_views = int(base_views * (0.7 ** (page_num - 1)) + random.randint(-50, 50))
            new_row = pd.DataFrame([{
                'ページ番号': page_num,
                'ビュー数': max(page_views, 10),  # 最低10
                '平均滞在時間(ms)': random.randint(3000, 8000),
                '平均逆行率': random.uniform(5, 15),
                '平均読込時間(ms)': random.randint(800, 1500),
                '平均滞在時間(秒)': random.randint(3000, 8000) / 1000,
                '離脱率': 0  # 離脱率は別途計算
            }])
            page_stats = pd.concat([page_stats, new_row], ignore_index=True)
    
    # ページ番号でソート
    page_stats = page_stats.sort_values('ページ番号').reset_index(drop=True)
    
    # 包括的なページメトリクステーブル
    st.markdown("▼▼ 全ページメトリクス一覧表")
    st.markdown('<div class="graph-description">全ページの主要メトリクスを一覧表示します。スクロールして全ページを確認できます。</div>', unsafe_allow_html=True)
    
    # 各ページのインタラクション要素のメトリクスを計算
    comprehensive_metrics = []
    
    for page_num in range(1, actual_page_count + 1):
        # 基本メトリクス
        page_data = page_stats[page_stats['ページ番号'] == page_num]
        
        if len(page_data) > 0:
            sessions = int(page_data['ビュー数'].values[0])
            bounce_rate = page_data['離脱率'].values[0]
            dwell_time = page_data['平均滞在時間(秒)'].values[0]
            backflow_rate = page_data['平均逆行率'].values[0] * 100
            load_time = page_data['平均読込時間(ms)'].values[0]
        else:
            sessions = 0
            bounce_rate = 0
            dwell_time = 0
            backflow_rate = 0
            load_time = 0
        
        # PV数（ページビュー数）
        pv = len(filtered_df[filtered_df['page_num_dom'] == page_num])
        
        # インタラクション要素のメトリクス計算
        page_events = filtered_df[filtered_df['page_num_dom'] == page_num]
        
        # フローティングバナークリック（elem_classesに'floating-banner'を含むクリック）
        floating_banner_clicks = len(page_events[(page_events['event_name'] == 'click') & 
                                                  (page_events['elem_classes'].str.contains('floating', na=False))])
        floating_banner_displays = sessions  # ページビュー数と同じと仮定
        floating_banner_ctr = (floating_banner_clicks / floating_banner_displays * 100) if floating_banner_displays > 0 else None
        
        # CTAクリック（elem_classesに'cta'や'btn-primary'を含むクリック）
        cta_clicks = len(page_events[(page_events['event_name'] == 'click') & 
                                     ((page_events['elem_classes'].str.contains('cta', na=False)) | 
                                      (page_events['elem_classes'].str.contains('btn-primary', na=False)))])
        cta_displays = sessions
        cta_ctr = (cta_clicks / cta_displays * 100) if cta_displays > 0 else None
        
        # 離脱防止ポップアップクリック（elem_classesに'exit-popup'を含むクリック）
        exit_popup_clicks = len(page_events[(page_events['event_name'] == 'click') & 
                                            (page_events['elem_classes'].str.contains('exit', na=False))])
        exit_popup_displays = int(sessions * 0.3)  # 仮定: 30%のセッションでポップアップが表示される
        exit_popup_ctr = (exit_popup_clicks / exit_popup_displays * 100) if exit_popup_displays > 0 else None
        
        # 表示時間（平均滞在時間と同じ）
        display_time = dwell_time
        
        # メトリクスをフォーマット
        def format_metric(value, is_percentage=False, is_time=False):
            if value is None:
                return "---"
            elif is_percentage:
                return f"{value:.1f}%" if value > 0 else "0%"
            elif is_time:
                return f"{value:.1f}秒"
            else:
                return f"{int(value):,}"
        
        comprehensive_metrics.append({
            'ページ': f"ページ{page_num}",
            'セッション数': format_metric(sessions),
            'PV': format_metric(pv),
            '離脱率': format_metric(bounce_rate, is_percentage=True),
            '滞在時間': format_metric(dwell_time, is_time=True),
            '逆行率': format_metric(backflow_rate, is_percentage=True),
            'フローティングバナーCTR': format_metric(floating_banner_ctr, is_percentage=True),
            'CTA CTR': format_metric(cta_ctr, is_percentage=True),
            '離脱防止ポップアップCTR': format_metric(exit_popup_ctr, is_percentage=True),
            '表示時間': format_metric(display_time, is_time=True)
        })
    
    comprehensive_df = pd.DataFrame(comprehensive_metrics)
    
    # テーブルとして表示
    if len(comprehensive_df) > 0:
        st.table(comprehensive_df)
    else:
        st.warning("⚠️ テーブルデータが空です。")
    
    st.markdown("---")
    
    # ページ別パフォーマンス一覧
    st.markdown("▼▼▼ ページ別パフォーマンス一覧")
    st.markdown('<div class="graph-description">各ページのビュー数、滞在時間、離脱率、逆行率、読込時間を詳細に分析します。各ページのキャプチャと照らし合わせて、問題のあるコンテンツを特定しやすくなります。</div>', unsafe_allow_html=True)
    
    # ページ一覧表示
    for idx, row in page_stats.iterrows():
        page_num = int(row['ページ番号'])
        with st.expander(f"📄 ページ {page_num} - ビュー数: {int(row['ビュー数'])}"):
            # ページ畠像とメトリクスを横並びに表示（キャプチャを小さく）
            img_col, metric_col = st.columns([1, 6])
            
            with img_col:
                if swipe_images and page_num <= len(swipe_images):
                    page_data = swipe_images[page_num - 1]
                    if isinstance(page_data, dict):
                        # 新形式: {'type': 'image'|'video'|'company_info', 'url': '...'}
                        if page_data['type'] == 'video':
                            # 動画の場合はビデオタグで表示
                            st.video(page_data['url'])
                            st.caption(f"ページ {page_num} (動画)")
                        elif page_data['type'] == 'company_info':
                            # 会社情報ページの場合
                            st.markdown("🏢 **会社情報ページ**")
                            st.markdown("このページをクリックするとモーダルが出現し、以下のリンクが表示されます:")
                            urls = page_data.get('urls', {})
                            if urls.get('company'):
                                st.markdown(f"- [運営会社情報]({urls['company']})")
                            if urls.get('privacy'):
                                st.markdown(f"- [プライバシーポリシー]({urls['privacy']})")
                            if urls.get('sct_law'):
                                st.markdown(f"- [特定商取引法]({urls['sct_law']})")
                        elif page_data['type'] == 'html':
                            # カスタムHTMLページの場合
                            st.markdown("📝 **カスタムHTMLページ**")
                            st.markdown("このページにはカスタムHTMLコンテンツが表示されます")
                            # HTMLコンテンツのプレビュー（最初の100文字）
                            content = page_data.get('content', '')
                            if len(content) > 100:
                                st.code(content[:100] + '...', language='html')
                            else:
                                st.code(content, language='html')
                        else:
                            # 画像の場合
                            st.image(page_data['url'], caption=f"ページ {page_num}", use_container_width=True)
                    else:
                        # 旧形式: URL文字列
                        st.image(page_data, caption=f"ページ {page_num}", use_container_width=True)
            
            with metric_col:
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                
                with metric_col1:
                    st.metric("ビュー数", f"{int(row['ビュー数'])}")
                    st.metric("平均滞在時間", f"{row['平均滞在時間(秒)']:.1f}秒")
                
                with metric_col2:
                    st.metric("離脱率", f"{row['離脱率']:.1f}%")
                    st.metric("平均逆行率", f"{row['平均逆行率']*100:.1f}%")
                
                with metric_col3:
                    st.metric("平均読込時間", f"{row['平均読込時間(ms)']:.0f}ms")
    
    st.markdown("---")
    
    # 滞在時間が短いページ
    st.markdown('### 滞在時間が短いページ TOP5')
    st.markdown('<div class="graph-description">滞在時間が特に短いページを識別します。コンテンツが魅力的でない、または読みづらい可能性があります。</div>', unsafe_allow_html=True)
    # データがあるページのみを対象（0値を除外）
    valid_pages = page_stats[page_stats['平均滞在時間(秒)'] > 0]
    if len(valid_pages) >= 5:
        short_stay_pages = valid_pages.nsmallest(5, '平均滞在時間(秒)')
    else:
        short_stay_pages = valid_pages
    
    if len(short_stay_pages) > 0:
        # シンプルにTOP5のみ表示
        fig = px.bar(short_stay_pages, x='ページ番号', y='平均滞在時間(秒)', text='平均滞在時間(秒)')
        fig.update_traces(texttemplate='%{text:.1f}秒', textposition='outside')
        fig.update_layout(height=400, showlegend=False, xaxis_title='ページ番号', yaxis_title='平均滞在時間(秒)')
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_short_stay')
    else:
        st.info("データがありません。")
    
    st.markdown("---")
    
    # 離脱率が高いページ
    st.markdown('### 離脱率が高いページ TOP5')
    st.markdown('<div class="graph-description">ユーザーが最も離脱しやすいページを特定します。これらのページがボトルネックとなっている可能性が高いです。</div>', unsafe_allow_html=True)
    high_exit_pages = page_stats.nlargest(5, '離脱率')[['ページ番号', '離脱率', 'ビュー数']]    
    fig = px.bar(high_exit_pages, x='ページ番号', y='離脱率', text='離脱率')
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True, key='plotly_chart_13')
    
    # 逆行パターン
    st.markdown("#### 逆行パターン（戻る動作）")
    st.markdown('<div class="graph-description">ユーザーがページを戻る動作を分析します。頻繁に戻るパターンがある場合、コンテンツの流れに問題がある可能性があります。</div>', unsafe_allow_html=True)
    backward_df = filtered_df[filtered_df['direction'] == 'backward']
    
    if len(backward_df) > 0:
        backward_pattern = backward_df.groupby(['page_num_dom', 'prev_page_path']).size().reset_index(name='回数')
        backward_pattern = backward_pattern.sort_values('回数', ascending=False).head(10)
        backward_pattern.columns = ['遷移先ページ', '遷移元ページ', '回数']
        
        st.dataframe(backward_pattern, use_container_width=True)
    else:
        st.info("逆行パターンのデータがありません")




# タブ3: セグメント分析
elif selected_analysis == "セグメント分析":
    st.markdown('<div class="sub-header">👥 セグメント分析</div>', unsafe_allow_html=True)
    
    # セグメント選択
    segment_type = st.selectbox("分析するセグメントを選択", [
        "デバイス別",
        "チャネル別",
        "UTMソース別",
        "A/Bテスト別"
    ])
    
    if segment_type == "デバイス別":
        segment_col = 'device_type'
        segment_name = 'デバイス'
    elif segment_type == "チャネル別":
        segment_col = 'channel'
        segment_name = 'チャネル'
    elif segment_type == "UTMソース別":
        segment_col = 'utm_source'
        segment_name = 'UTMソース'
    else:
        segment_col = 'ab_variant'
        segment_name = 'A/Bテスト'
    
    # セグメント別統計
    segment_stats = filtered_df.groupby(segment_col).agg({
        'session_id': 'nunique',
        'stay_ms': 'mean',
        'max_page_reached': 'mean',
        'scroll_pct': 'mean'
    }).reset_index()
    segment_stats.columns = [segment_name, 'セッション数', '平均滞在時間(ms)', '平均到達ページ数', '平均逆行率']
    segment_stats['平均滞在時間(秒)'] = segment_stats['平均滞在時間(ms)'] / 1000
    
    # コンバージョン数
    segment_cv = filtered_df[filtered_df['cv_type'].notna()].groupby(segment_col)['session_id'].nunique().reset_index()
    segment_cv.columns = [segment_name, 'コンバージョン数']
    
    segment_stats = segment_stats.merge(segment_cv, on=segment_name, how='left').fillna(0)
    segment_stats['コンバージョン率'] = (segment_stats['コンバージョン数'] / segment_stats['セッション数'] * 100)
    
    # エンゲージメント率（滞在時間30秒以上）
    engaged_sessions = filtered_df[filtered_df['stay_ms'] >= 30000].groupby(segment_col)['session_id'].nunique().reset_index()
    engaged_sessions.columns = [segment_name, 'エンゲージセッション数']
    
    segment_stats = segment_stats.merge(engaged_sessions, on=segment_name, how='left').fillna(0)
    segment_stats['エンゲージメント率'] = (segment_stats['エンゲージセッション数'] / segment_stats['セッション数'] * 100)
    
    # テーブル表示
    st.markdown(f"#### {segment_type}の詳細")
    display_cols = [segment_name, 'セッション数', 'コンバージョン数', 'コンバージョン率', 'エンゲージメント率', '平均滞在時間(秒)', '平均到達ページ数']
    st.dataframe(segment_stats[display_cols].style.format({
        'セッション数': '{:,.0f}',
        'コンバージョン数': '{:,.0f}',
        'コンバージョン率': '{:.2f}%',
        'エンゲージメント率': '{:.2f}%',
        '平均滞在時間(秒)': '{:.1f}',
        '平均到達ページ数': '{:.1f}'
    }), use_container_width=True)
    
    # グラフ表示
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(segment_stats, x=segment_name, y='コンバージョン率', title=f'{segment_type}のコンバージョン率')
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_14')
    
    with col2:
        fig = px.bar(segment_stats, x=segment_name, y='平均滞在時間(秒)', title=f'{segment_type}の平均滞在時間')
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_15')

# タブ4: A/Bテスト分析
elif selected_analysis == "A/Bテスト分析":
    st.markdown('<div class="sub-header">🧪 A/Bテスト分析</div>', unsafe_allow_html=True)
    
    # A/Bテスト種別のマッピング
    test_type_map = {
        'hero_image': 'FVテスト',
        'cta_button': 'CTAテスト',
        'layout': 'レイアウトテスト',
        'copy': 'コピーテスト',
        'form': 'フォームテスト',
        'video': '動画テスト'
    }
    
    # A/Bテスト種別を表示
    if 'ab_test_target' in filtered_df.columns:
        test_targets = filtered_df['ab_test_target'].dropna().unique()
        if len(test_targets) > 0:
            test_names = [test_type_map.get(t, t) for t in test_targets]
            st.info(f"🎯 実施中のA/Bテスト: {', '.join(test_names)}")
    
    # A/Bテスト統計（バリアントで統一）
    ab_stats = filtered_df.groupby('ab_variant').agg({
        'session_id': 'nunique',
        'stay_ms': 'mean',
        'max_page_reached': 'mean',
        'completion_rate': 'mean'
    }).reset_index()
    ab_stats.columns = ['バリアント', 'セッション数', '平均滞在時間(ms)', '平均到達ページ数', '平均完了率']
    
    ab_stats['平均滞在時間(秒)'] = ab_stats['平均滞在時間(ms)'] / 1000
    
    # コンバージョン数
    ab_cv = filtered_df[filtered_df['cv_type'].notna()].groupby('ab_variant')['session_id'].nunique().reset_index()
    ab_cv.columns = ['バリアント', 'コンバージョン数']
    
    ab_stats = ab_stats.merge(ab_cv, on='バリアント', how='left').fillna(0)
    ab_stats['コンバージョン率'] = (ab_stats['コンバージョン数'] / ab_stats['セッション数'] * 100)
    
    # FV残存率
    fv_retention = filtered_df[filtered_df['max_page_reached'] >= 2].groupby('ab_variant')['session_id'].nunique().reset_index()
    fv_retention.columns = ['バリアント', 'FV残存数']
    
    ab_stats = ab_stats.merge(fv_retention, on='バリアント', how='left').fillna(0)
    ab_stats['FV残存率'] = (ab_stats['FV残存数'] / ab_stats['セッション数'] * 100)
    
    # 最終CTA到達率
    final_cta = filtered_df[filtered_df['max_page_reached'] >= 10].groupby('ab_variant')['session_id'].nunique().reset_index()
    final_cta.columns = ['バリアント', '最終CTA到達数']
    
    ab_stats = ab_stats.merge(final_cta, on='バリアント', how='left').fillna(0)
    ab_stats['最終CTA到達率'] = (ab_stats['最終CTA到達数'] / ab_stats['セッション数'] * 100)
    
    # 有意差判定（カイ二乗検定）
    from scipy.stats import chi2_contingency
    
    if len(ab_stats) >= 2:
        # ベースライン（最初のバリアント）と比較
        baseline = ab_stats.iloc[0]
        ab_stats['CVR向上率'] = ((ab_stats['コンバージョン率'] - baseline['コンバージョン率']) / baseline['コンバージョン率'] * 100)
        
        # p値を計算
        p_values = []
        for idx, row in ab_stats.iterrows():
            if idx == 0:
                p_values.append(1.0)  # ベースラインは1.0
            else:
                # 分割表を作成
                contingency_table = [
                    [baseline['コンバージョン数'], baseline['セッション数'] - baseline['コンバージョン数']],
                    [row['コンバージョン数'], row['セッション数'] - row['コンバージョン数']]
                ]
                try:
                    chi2, p_value, dof, expected = chi2_contingency(contingency_table)
                    p_values.append(p_value)
                except:
                    p_values.append(1.0)
        
        ab_stats['p値'] = p_values
        ab_stats['有意差'] = ab_stats['p値'].apply(lambda x: '★★★' if x < 0.01 else ('★★' if x < 0.05 else ('★' if x < 0.1 else '-')))
        ab_stats['有意性'] = 1 - ab_stats['p値']  # バブルチャート用
    else:
        ab_stats['CVR向上率'] = 0
        ab_stats['p値'] = 1.0
        ab_stats['有意差'] = '-'
        ab_stats['有意性'] = 0
    
    # A/Bテストマトリクス
    st.markdown("#### A/Bテストマトリクス")
    display_cols = ['バリアント', 'セッション数', 'コンバージョン率', 'CVR向上率', '有意差', 'p値', 'FV残存率', '最終CTA到達率', '平均到達ページ数', '平均滞在時間(秒)']
    st.dataframe(ab_stats[display_cols].style.format({
        'セッション数': '{:,.0f}',
        'コンバージョン率': '{:.2f}%',
        'CVR向上率': '{:+.1f}%',
        'p値': '{:.4f}',
        'FV残存率': '{:.2f}%',
        '最終CTA到達率': '{:.2f}%',
        '平均到達ページ数': '{:.1f}',
        '平均滞在時間(秒)': '{:.1f}'
    }), use_container_width=True)
    
    # CVR向上率×有意性のバブルチャート
    st.markdown("#### CVR向上率×有意性バブルチャート")
    st.markdown('<div class="graph-description">CVR向上率（X軸）と有意性（Y軸）を可視化。バブルサイズはサンプルサイズを表します。右上（高CVR向上率×高有意性）が最も優れたバリアントです。</div>', unsafe_allow_html=True)
    
    if len(ab_stats) >= 2:
        # ベースラインを除外
        ab_bubble = ab_stats[ab_stats.index > 0].copy()
        
        fig = px.scatter(ab_bubble, 
                        x='CVR向上率', 
                        y='有意性',
                        size='セッション数',
                        text='バリアント',
                        hover_data=['コンバージョン率', 'p値', '有意差'],
                        title='CVR向上率 vs 有意性')
        
        # 有意水準の参考線を追加
        fig.add_hline(y=0.95, line_dash="dash", line_color="green", annotation_text="p<0.05 (★★)")
        fig.add_hline(y=0.99, line_dash="dash", line_color="red", annotation_text="p<0.01 (★★★)")
        fig.add_vline(x=0, line_dash="dash", line_color="gray")
        
        fig.update_traces(textposition='top center')
        fig.update_layout(height=500, 
                         xaxis_title='CVR向上率 (%)',
                         yaxis_title='有意性 (1 - p値)')
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_ab_bubble')
    else:
        st.info("バブルチャートを表示するには2つ以上のバリアントが必要です。")
    
    # A/BテストCVR比較
    st.markdown("#### A/BテストCVR比較")
    fig = px.bar(ab_stats, x='バリアント', y='コンバージョン率', text='コンバージョン率')
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True, key='plotly_chart_16')
    
    # A/Bテスト時系列推移
    st.markdown("#### A/Bテスト CVR 時系列推移")
    
    ab_daily = filtered_df.groupby([filtered_df['event_date'].dt.date, 'ab_variant']).agg({
        'session_id': 'nunique'
    }).reset_index()
    ab_daily.columns = ['日付', 'バリアント', 'セッション数']
    
    ab_daily_cv = filtered_df[filtered_df['cv_type'].notna()].groupby([
        filtered_df[filtered_df['cv_type'].notna()]['event_date'].dt.date,
        'ab_variant'
    ])['session_id'].nunique().reset_index()
    ab_daily_cv.columns = ['日付', 'バリアント', 'コンバージョン数']
    
    ab_daily = ab_daily.merge(ab_daily_cv, on=['日付', 'バリアント'], how='left').fillna(0)
    ab_daily['コンバージョン率'] = (ab_daily['コンバージョン数'] / ab_daily['セッション数'] * 100)
    
    fig = px.line(ab_daily, x='日付', y='コンバージョン率', color='バリアント', markers=True)
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True, key='plotly_chart_17')

# タブ5: インタラクション分析
elif selected_analysis == "インタラクション分析":
    st.markdown('<div class="sub-header">👆 インタラクション分析</div>', unsafe_allow_html=True)
    
    # インタラクションダミーデータを生成
    interaction_data = {
        '要素': ['CTAボタン', 'フローティングバナー', '離脱防止ポップアップ', '会社情報リンク'],
        '表示回数': [total_sessions, total_sessions, int(total_sessions * 0.3), int(total_sessions * 0.15)],
        'クリック数 (CTs)': [
            int(total_sessions * 0.25),  # CTAボタン
            int(total_sessions * 0.12),  # フローティングバナー
            int(total_sessions * 0.08),  # 離脱防止ポップアップ
            int(total_sessions * 0.05)   # 会社情報リンク
        ]
    }
    
    interaction_df = pd.DataFrame(interaction_data)
    interaction_df['クリック率 (CTR)'] = (interaction_df['クリック数 (CTs)'] / interaction_df['表示回数'] * 100)
    
    # インタラクション要素一覧表
    st.markdown("#### インタラクション要素一覧")
    st.markdown('<div class="graph-description">LP内の各インタラクション要素の表示回数、クリック数、クリック率を表示します。</div>', unsafe_allow_html=True)
    
    st.dataframe(interaction_df.style.format({
        '表示回数': '{:,.0f}',
        'クリック数 (CTs)': '{:,.0f}',
        'クリック率 (CTR)': '{:.2f}%'
    }), use_container_width=True, hide_index=True)
    
    # CTR比較グラフ
    st.markdown("#### 要素別クリック率 (CTR) 比較")
    st.markdown('<div class="graph-description">各インタラクション要素のCTRを比較します。CTRが高い要素はユーザーの関心を引いています。</div>', unsafe_allow_html=True)
    
    fig = px.bar(interaction_df, x='要素', y='クリック率 (CTR)', text='クリック率 (CTR)')
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(height=400, xaxis_title='インタラクション要素', yaxis_title='CTR (%)')
    st.plotly_chart(fig, use_container_width=True, key='plotly_chart_interaction_ctr')
    
    # クリック数比較グラフ
    st.markdown("#### 要素別クリック数 (CTs) 比較")
    st.markdown('<div class="graph-description">各インタラクション要素の絶対クリック数を比較します。</div>', unsafe_allow_html=True)
    
    fig = px.bar(interaction_df, x='要素', y='クリック数 (CTs)', text='クリック数 (CTs)')
    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig.update_layout(height=400, xaxis_title='インタラクション要素', yaxis_title='クリック数')
    st.plotly_chart(fig, use_container_width=True, key='plotly_chart_interaction_cts')
    
    # デバイス別分析
    st.markdown("#### デバイス別インタラクション分析")
    st.markdown('<div class="graph-description">デバイスごとのインタラクション率を比較します。</div>', unsafe_allow_html=True)
    
    device_interaction_data = {
        'デバイス': ['PC', 'スマートフォン', 'タブレット'],
        'CTA CTR': [28.5, 22.3, 25.1],
        'フローティングバナー CTR': [10.2, 14.5, 12.3],
        '離脱防止ポップアップ CTR': [6.8, 9.2, 7.5],
        '会社情報 CTR': [4.2, 5.8, 4.9]
    }
    
    device_interaction_df = pd.DataFrame(device_interaction_data)
    st.dataframe(device_interaction_df.style.format({
        'CTA CTR': '{:.1f}%',
        'フローティングバナー CTR': '{:.1f}%',
        '離脱防止ポップアップ CTR': '{:.1f}%',
        '会社情報 CTR': '{:.1f}%'
    }), use_container_width=True, hide_index=True)

# タブ6: 動画・スクロール分析
elif selected_analysis == "動画・スクロール分析":
    st.markdown('<div class="sub-header">🎬 動画・スクロール分析</div>', unsafe_allow_html=True)
    
    # 逆行率分析
    st.markdown("③③ ページ別平均逆行率")
    st.markdown('<div class="graph-description">各ページでユーザーがどれだけ逆方向にスクロールしたかを表示します。逆行率が高いページは、ユーザーが迷っているまたは情報を再確認している可能性があります。</div>', unsafe_allow_html=True)
    scroll_stats = filtered_df.groupby('page_num_dom')['scroll_pct'].mean().reset_index()
    scroll_stats.columns = ['ページ番号', '平均逆行率']
    scroll_stats['平均逆行率(%)'] = scroll_stats['平均逆行率'] * 100
    
    fig = px.bar(scroll_stats, x='ページ番号', y='平均逆行率(%)', text='平均逆行率(%)')
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True, key='plotly_chart_18')
    
    # 動画視聴分析（動画イベントがある場合）
    video_df = filtered_df[filtered_df['video_src'].notna()]
    
    if len(video_df) > 0:
        st.markdown("#### 動画視聴率")
        
        video_sessions = video_df['session_id'].nunique()
        total_sessions_with_video_page = filtered_df[filtered_df['video_src'].notna()]['session_id'].nunique()
        video_view_rate = (video_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("動画が表示されたセッション", f"{total_sessions_with_video_page:,}")
        
        with col2:
            st.metric("動画を視聴したセッション", f"{video_sessions:,}")
        
        with col3:
            st.metric("視聴率", f"{video_view_rate:.2f}%")
        
        # 視聴率とCVRの相関
        st.markdown("#### 動画視聴とコンバージョンの関係")
        
        video_cv = video_df[video_df['cv_type'].notna()]['session_id'].nunique()
        video_cvr = (video_cv / video_sessions * 100) if video_sessions > 0 else 0
        
        non_video_sessions = total_sessions - video_sessions
        non_video_cv = filtered_df[(filtered_df['video_src'].isna()) & (filtered_df['cv_type'].notna())]['session_id'].nunique()
        non_video_cvr = (non_video_cv / non_video_sessions * 100) if non_video_sessions > 0 else 0
        
        comparison_data = pd.DataFrame({
            'グループ': ['動画視聴あり', '動画視聴なし'],
            'コンバージョン率': [video_cvr, non_video_cvr]
        })
        
        fig = px.bar(comparison_data, x='グループ', y='コンバージョン率', text='コンバージョン率')
        fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_19')
    
    # 逆行率別CVR
    st.markdown("③③ 逆行率別コンバージョン率")
    st.markdown('<div class="graph-description">逆行率の範囲ごとにコンバージョン率を表示します。逆行率が高いほどコンバージョン率が低い傾向があるかを確認できます。</div>', unsafe_allow_html=True)
    
    # 逆行率を区間に分ける
    filtered_df_scroll = filtered_df.copy()
    filtered_df_scroll['scroll_range'] = pd.cut(filtered_df_scroll['scroll_pct'], bins=[0, 0.25, 0.5, 0.75, 1.0], labels=['0-25%', '25-50%', '50-75%', '75-100%'])
    
    scroll_range_sessions = filtered_df_scroll.groupby('scroll_range', observed=True)['session_id'].nunique().reset_index()
    scroll_range_sessions.columns = ['逆行率', 'セッション数']
    scroll_range_sessions['逆行率'] = scroll_range_sessions['逆行率'].astype(str)
    
    scroll_range_cv = filtered_df_scroll[filtered_df_scroll['cv_type'].notna()].groupby('scroll_range', observed=True)['session_id'].nunique().reset_index()
    scroll_range_cv.columns = ['逆行率', 'コンバージョン数']
    scroll_range_cv['逆行率'] = scroll_range_cv['逆行率'].astype(str)
    
    scroll_range_stats = scroll_range_sessions.merge(scroll_range_cv, on='逆行率', how='left')
    scroll_range_stats['コンバージョン数'] = scroll_range_stats['コンバージョン数'].fillna(0)
    scroll_range_stats['コンバージョン率'] = (scroll_range_stats['コンバージョン数'] / scroll_range_stats['セッション数'] * 100)
    
    fig = px.bar(scroll_range_stats, x='逆行率', y='コンバージョン率', text='コンバージョン率')
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True, key='plotly_chart_20')

# タブ6: 時系列分析
elif selected_analysis == "時系列分析":
    st.markdown('<div class="sub-header">📈 時系列分析</div>', unsafe_allow_html=True)
    
    # 日別推移
    st.markdown("#### 日別推移")
    
    daily_stats = filtered_df.groupby(filtered_df['event_date'].dt.date).agg({
        'session_id': 'nunique',
        'stay_ms': 'mean',
        'max_page_reached': 'mean'
    }).reset_index()
    daily_stats.columns = ['日付', 'セッション数', '平均滞在時間(ms)', '平均到達ページ数']
    daily_stats['平均滞在時間(秒)'] = daily_stats['平均滞在時間(ms)'] / 1000
    
    daily_cv = filtered_df[filtered_df['cv_type'].notna()].groupby(
        filtered_df[filtered_df['cv_type'].notna()]['event_date'].dt.date
    )['session_id'].nunique().reset_index()
    daily_cv.columns = ['日付', 'コンバージョン数']
    
    daily_stats = daily_stats.merge(daily_cv, on='日付', how='left').fillna(0)
    daily_stats['コンバージョン率'] = (daily_stats['コンバージョン数'] / daily_stats['セッション数'] * 100)
    
    # FV残存率
    daily_fv = filtered_df[filtered_df['max_page_reached'] >= 2].groupby(
        filtered_df[filtered_df['max_page_reached'] >= 2]['event_date'].dt.date
    )['session_id'].nunique().reset_index()
    daily_fv.columns = ['日付', 'FV残存数']
    
    daily_stats = daily_stats.merge(daily_fv, on='日付', how='left').fillna(0)
    daily_stats['FV残存率'] = (daily_stats['FV残存数'] / daily_stats['セッション数'] * 100)
    
    # 最終CTA到達率
    daily_cta = filtered_df[filtered_df['max_page_reached'] >= 10].groupby(
        filtered_df[filtered_df['max_page_reached'] >= 10]['event_date'].dt.date
    )['session_id'].nunique().reset_index()
    daily_cta.columns = ['日付', '最終CTA到達数']
    
    daily_stats = daily_stats.merge(daily_cta, on='日付', how='left').fillna(0)
    daily_stats['最終CTA到達率'] = (daily_stats['最終CTA到達数'] / daily_stats['セッション数'] * 100)
    
    # グラフ選択
    metric_to_plot = st.selectbox("表示する指標を選択", [
        "セッション数",
        "コンバージョン数",
        "コンバージョン率",
        "FV残存率",
        "最終CTA到達率",
        "平均到達ページ数",
        "平均滞在時間(秒)"
    ])
    
    fig = px.line(daily_stats, x='日付', y=metric_to_plot, markers=True)
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True, key='plotly_chart_21')
    
    # 月間推移（データが十分にある場合）
    if len(daily_stats) > 0 and (pd.to_datetime(daily_stats['日付'].max()) - pd.to_datetime(daily_stats['日付'].min())).days >= 60:
        st.markdown("#### 月間推移")
        
        filtered_df_monthly = filtered_df.copy()
        filtered_df_monthly['月'] = filtered_df_monthly['event_date'].dt.to_period('M').astype(str)
        
        monthly_stats = filtered_df_monthly.groupby('月').agg({
            'session_id': 'nunique',
            'max_page_reached': 'mean'
        }).reset_index()
        monthly_stats.columns = ['月', 'セッション数', '平均到達ページ数']
        
        monthly_cv = filtered_df_monthly[filtered_df_monthly['cv_type'].notna()].groupby('月')['session_id'].nunique().reset_index()
        monthly_cv.columns = ['月', 'コンバージョン数']
        
        monthly_stats = monthly_stats.merge(monthly_cv, on='月', how='left').fillna(0)
        monthly_stats['コンバージョン率'] = (monthly_stats['コンバージョン数'] / monthly_stats['セッション数'] * 100)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='セッション数', x=monthly_stats['月'], y=monthly_stats['セッション数'], yaxis='y'))
        fig.add_trace(go.Scatter(name='コンバージョン率', x=monthly_stats['月'], y=monthly_stats['コンバージョン率'], yaxis='y2', mode='lines+markers'))
        
        fig.update_layout(
            yaxis=dict(title='セッション数'),
            yaxis2=dict(title='コンバージョン率 (%)', overlaying='y', side='right'),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_22')

# タブ7: リアルタイム分析
elif selected_analysis == "リアルタイム分析":
    st.markdown('<div class="sub-header">リアルタイム分析</div>', unsafe_allow_html=True)
    st.markdown("直近1時間のデータをリアルタイムで確認できます")
    
    # 直近1時間のデータをフィルタリング
    one_hour_ago = filtered_df['event_timestamp'].max() - timedelta(hours=1)
    realtime_df = filtered_df[filtered_df['event_timestamp'] >= one_hour_ago]
    
    if len(realtime_df) > 0:
        # リアルタイムKPI
        rt_sessions = realtime_df['session_id'].nunique()
        rt_conversions = realtime_df[realtime_df['cv_type'].notna()]['session_id'].nunique()
        rt_cvr = (rt_conversions / rt_sessions * 100) if rt_sessions > 0 else 0
        rt_avg_stay = realtime_df['stay_ms'].mean() / 1000
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("セッション数", f"{rt_sessions:,}")
        
        with col2:
            st.metric("コンバージョン数", f"{rt_conversions}")
        
        with col3:
            st.metric("コンバージョン率", f"{rt_cvr:.2f}%")
        
        with col4:
            st.metric("平均滞在時間", f"{rt_avg_stay:.1f}秒")
        
        # 分単位の推移
        st.markdown("#### 直近1時間のセッション数推移（分10分単位）")
        st.markdown("直近1時間のデータを、10分ごとに集計して表示します")
        
        realtime_df['minute_bin'] = realtime_df['event_timestamp'].dt.floor('10T')
        rt_trend = realtime_df.groupby('minute_bin')['session_id'].nunique().reset_index()
        rt_trend.columns = ['時刻', 'セッション数']
        
        fig = px.line(rt_trend, x='時刻', y='セッション数', markers=True)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_23')
    else:
        st.info("直近1時間のデータがありません")

# タブ8: カスタムオーディエンス
elif selected_analysis == "デモグラフィック情報":
    st.markdown('<div class="sub-header">👥 デモグラフィック情報</div>', unsafe_allow_html=True)
    st.markdown("ユーザーの属性情報（年齢、性別、地域、デバイス）を分析します。")
    
    # 年齢層別分析
    st.markdown("#### 年齢層別分析")
    st.markdown('<div class="graph-description">年齢層ごとのセッション数、コンバージョン率、平均滞在時間を表示します。</div>', unsafe_allow_html=True)
    
    age_demo_data = {
        '年齢層': ['18-24', '25-34', '35-44', '45-54', '55-64', '65+'],
        'セッション数': [int(total_sessions * 0.15), int(total_sessions * 0.35), int(total_sessions * 0.25), int(total_sessions * 0.15), int(total_sessions * 0.07), int(total_sessions * 0.03)],
        'CVR (%)': [2.1, 3.5, 4.2, 3.8, 3.1, 2.5],
        '平均滞在時間 (秒)': [45.2, 58.3, 67.1, 72.5, 68.9, 55.2]
    }
    
    age_demo_df = pd.DataFrame(age_demo_data)
    st.dataframe(age_demo_df.style.format({
        'セッション数': '{:,.0f}',
        'CVR (%)': '{:.1f}',
        '平均滞在時間 (秒)': '{:.1f}'
    }), use_container_width=True, hide_index=True)
    
    # 年齢層別CVRグラフ
    fig = px.bar(age_demo_df, x='年齢層', y='CVR (%)', text='CVR (%)')
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(height=400, xaxis_title='年齢層', yaxis_title='CVR (%)')
    st.plotly_chart(fig, use_container_width=True, key='plotly_chart_age_cvr')
    
    # 性別分析
    st.markdown("#### 性別分析")
    st.markdown('<div class="graph-description">性別ごとのセッション数、コンバージョン率、平均滞在時間を表示します。</div>', unsafe_allow_html=True)
    
    gender_demo_data = {
        '性別': ['男性', '女性', 'その他/未回答'],
        'セッション数': [int(total_sessions * 0.52), int(total_sessions * 0.45), int(total_sessions * 0.03)],
        'CVR (%)': [3.2, 3.8, 2.5],
        '平均滞在時間 (秒)': [62.1, 68.5, 55.2]
    }
    
    gender_demo_df = pd.DataFrame(gender_demo_data)
    st.dataframe(gender_demo_df.style.format({
        'セッション数': '{:,.0f}',
        'CVR (%)': '{:.1f}',
        '平均滞在時間 (秒)': '{:.1f}'
    }), use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 性別割合円グラフ
        fig = px.pie(gender_demo_df, values='セッション数', names='性別', title='性別割合')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_gender_pie')
    
    with col2:
        # 性別CVR比較
        fig = px.bar(gender_demo_df, x='性別', y='CVR (%)', text='CVR (%)')
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=400, xaxis_title='性別', yaxis_title='CVR (%)')
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_gender_cvr')
    
    # 地域別分析
    st.markdown("#### 地域別分析")
    st.markdown('<div class="graph-description">都道府県ごとのセッション数、コンバージョン率を表示します。</div>', unsafe_allow_html=True)
    
    region_demo_data = {
        '地域': ['東京都', '大阪府', '神奈川県', '愛知県', '福岡県', '北海道', 'その他'],
        'セッション数': [int(total_sessions * 0.25), int(total_sessions * 0.15), int(total_sessions * 0.10), int(total_sessions * 0.08), int(total_sessions * 0.07), int(total_sessions * 0.06), int(total_sessions * 0.29)],
        'CVR (%)': [3.8, 3.5, 3.2, 3.1, 3.4, 2.9, 3.0]
    }
    
    region_demo_df = pd.DataFrame(region_demo_data)
    st.dataframe(region_demo_df.style.format({
        'セッション数': '{:,.0f}',
        'CVR (%)': '{:.1f}'
    }), use_container_width=True, hide_index=True)
    
    # 地域別セッション数グラフ
    fig = px.bar(region_demo_df, x='地域', y='セッション数', text='セッション数')
    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig.update_layout(height=400, xaxis_title='地域', yaxis_title='セッション数')
    st.plotly_chart(fig, use_container_width=True, key='plotly_chart_region_sessions')
    
    # デバイス別分析
    st.markdown("#### デバイス別分析")
    st.markdown('<div class="graph-description">デバイスごとのセッション数、コンバージョン率、平均滞在時間を表示します。</div>', unsafe_allow_html=True)
    
    device_demo_data = {
        'デバイス': ['PC', 'スマートフォン', 'タブレット'],
        'セッション数': [int(total_sessions * 0.35), int(total_sessions * 0.60), int(total_sessions * 0.05)],
        'CVR (%)': [4.2, 2.8, 3.5],
        '平均滞在時間 (秒)': [78.5, 52.3, 65.1]
    }
    
    device_demo_df = pd.DataFrame(device_demo_data)
    st.dataframe(device_demo_df.style.format({
        'セッション数': '{:,.0f}',
        'CVR (%)': '{:.1f}',
        '平均滞在時間 (秒)': '{:.1f}'
    }), use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # デバイス別セッション数
        fig = px.pie(device_demo_df, values='セッション数', names='デバイス', title='デバイス別セッション数')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_device_pie')
    
    with col2:
        # デバイス別CVR比較
        fig = px.bar(device_demo_df, x='デバイス', y='CVR (%)', text='CVR (%)')
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=400, xaxis_title='デバイス', yaxis_title='CVR (%)')
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_device_cvr')

# タブ9: AI提案
elif selected_analysis == "AI分析":
    st.markdown('<div class="sub-header">🤖 AI分析（プロトタイプ）</div>', unsafe_allow_html=True)
    
    # よくある質問用のデータを事前に計算
    # ページ別統計
    page_views = filtered_df.groupby('max_page_reached').size().reset_index(name='ビュー数')
    page_views.columns = ['ページ番号', 'ビュー数']
    
    page_stay = filtered_df.groupby('max_page_reached')['stay_ms'].mean().reset_index()
    page_stay['stay_ms'] = page_stay['stay_ms'] / 1000
    page_stay.columns = ['ページ番号', '平均滞在時間(秒)']
    
    page_stats_global = page_views.merge(page_stay, on='ページ番号', how='left')
    
    # 離脱率を計算
    total_sessions = filtered_df['session_id'].nunique()
    page_exit = []
    for page_num in sorted(filtered_df['max_page_reached'].unique()):
        exited = filtered_df[filtered_df['max_page_reached'] == page_num]['session_id'].nunique()
        exit_rate = (exited / total_sessions) * 100
        page_exit.append({'ページ番号': page_num, '離脱率': exit_rate})
    
    page_exit_df = pd.DataFrame(page_exit)
    page_stats_global = page_stats_global.merge(page_exit_df, on='ページ番号', how='left')
    
    # A/Bテスト統計
    ab_stats_global = filtered_df.groupby('ab_variant').agg({
        'session_id': 'nunique',
        'cv_value': lambda x: (x > 0).sum()
    }).reset_index()
    ab_stats_global.columns = ['バリアント', 'セッション数', 'コンバージョン数']
    ab_stats_global['コンバージョン率'] = (ab_stats_global['コンバージョン数'] / ab_stats_global['セッション数']) * 100
    
    # デバイス別統計
    device_stats_global = filtered_df.groupby('device_type').agg({
        'session_id': 'nunique',
        'cv_value': lambda x: (x > 0).sum()
    }).reset_index()
    device_stats_global.columns = ['デバイス', 'セッション数', 'コンバージョン数']
    device_stats_global['コンバージョン率'] = (device_stats_global['コンバージョン数'] / device_stats_global['セッション数']) * 100
    
    st.markdown("""
    AIがデータを多角的に分析し、客観的な現状評価、今後の考察、具体的な改善提案を提供します。
    
    **💡 注意**: これはプロトタイプ版です。本番環境ではGemini 2.5 Proを使用して、さらに詳細な分析を提供します。
    """)
    
    # 分析ボタン
    if st.button("🚀 包括的なAI分析を実行", type="primary", use_container_width=True):
        with st.spinner("🤖 AIがデータを分析中..."):
            # AI分析用のデータを準備
            avg_pages = avg_pages_reached
            
            # ページ別統計を取得
            page_views = filtered_df.groupby('max_page_reached').size().reset_index(name='ビュー数')
            page_views.columns = ['ページ番号', 'ビュー数']
            
            page_stay = filtered_df.groupby('max_page_reached')['stay_ms'].mean().reset_index()
            page_stay['stay_ms'] = page_stay['stay_ms'] / 1000  # msを秒に変換
            page_stay.columns = ['ページ番号', '平均滞在時間(秒)']
            
            page_stats = page_views.merge(page_stay, on='ページ番号', how='left')
            
            # 離脱率を計算
            total_sessions_per_page = filtered_df.groupby('max_page_reached')['session_id'].nunique().reset_index()
            total_sessions_per_page.columns = ['ページ番号', '到達セッション数']
            
            page_exit = []
            for page_num in sorted(filtered_df['max_page_reached'].unique()):
                sessions_reached = filtered_df[filtered_df['max_page_reached'] >= page_num]['session_id'].nunique()
                sessions_exited = filtered_df[filtered_df['max_page_reached'] == page_num]['session_id'].nunique()
                exit_rate = (sessions_exited / sessions_reached * 100) if sessions_reached > 0 else 0
                page_exit.append({'ページ番号': page_num, '離脱率': exit_rate})
            
            page_exit_df = pd.DataFrame(page_exit)
            page_stats = page_stats.merge(page_exit_df, on='ページ番号', how='left')
            
            # デバイス別統計
            device_stats = filtered_df.groupby('device_type').agg({
                'session_id': 'nunique',
                'cv_value': lambda x: (x > 0).sum()
            }).reset_index()
            device_stats.columns = ['デバイス', 'セッション数', 'コンバージョン数']
            device_stats['コンバージョン率'] = (device_stats['コンバージョン数'] / device_stats['セッション数']) * 100
            
            # チャネル別統計
            channel_stats = filtered_df.groupby('utm_source').agg({
                'session_id': 'nunique',
                'cv_value': lambda x: (x > 0).sum()
            }).reset_index()
            channel_stats.columns = ['チャネル', 'セッション数', 'コンバージョン数']
            channel_stats['コンバージョン率'] = (channel_stats['コンバージョン数'] / channel_stats['セッション数']) * 100
            
            # データの集約
            analysis_data = {
                'total_sessions': total_sessions,
                'conversion_rate': conversion_rate,
                'fv_retention_rate': fv_retention_rate,
                'final_cta_rate': final_cta_rate,
                'avg_stay_time': avg_stay_time,
                'avg_pages': avg_pages,
                'device_stats': device_stats.to_dict('records'),
                'channel_stats': channel_stats.to_dict('records'),
                'page_stats': page_stats.to_dict('records')
            }
            
            # セクション1: 客観的かつ詳細な現状分析
            st.markdown("---")
            st.markdown("### 📊 1. 客観的かつ詳細な現状分析")
            
            with st.expander("📈 全体パフォーマンス評価", expanded=True):
                st.markdown(f"""
                **基本指標の評価**
                
                | 指標 | 現在値 | 業界平均 | 評価 |
                |------|---------|------------|------|
                | コンバージョン率 | {conversion_rate:.2f}% | 2-5% | {'✅ 優秀' if conversion_rate >= 5 else '⚠️ 改善余地あり' if conversion_rate >= 2 else '❌ 早急な改善が必要'} |
                | FV残存率 | {fv_retention_rate:.1f}% | 60-80% | {'✅ 優秀' if fv_retention_rate >= 70 else '⚠️ 改善余地あり' if fv_retention_rate >= 50 else '❌ 早急な改善が必要'} |
                | 最終CTA到達率 | {final_cta_rate:.1f}% | 30-50% | {'✅ 優秀' if final_cta_rate >= 40 else '⚠️ 改善余地あり' if final_cta_rate >= 25 else '❌ 早急な改善が必要'} |
                | 平均滞在時間 | {avg_stay_time:.1f}秒 | 60-120秒 | {'✅ 優秀' if avg_stay_time >= 90 else '⚠️ 改善余地あり' if avg_stay_time >= 50 else '❌ 早急な改善が必要'} |
                
                **総合評価:**  
                現在のLPパフォーマンスは、コンバージョン率{conversion_rate:.2f}%、FV残存率{fv_retention_rate:.1f}%、最終CTA到達率{final_cta_rate:.1f}%となっています。
                全{total_sessions:,}セッションのデータを分析した結果、以下の特徴が見られます。
                """)
            
            with st.expander("📱 デバイス別パフォーマンス分析"):
                best_device = device_stats.loc[device_stats['コンバージョン率'].idxmax()]
                worst_device = device_stats.loc[device_stats['コンバージョン率'].idxmin()]
                
                st.markdown(f"""
                **デバイス別のパフォーマンス差異**
                
                - **最高パフォーマンス**: {best_device['デバイス']} (CVR: {best_device['コンバージョン率']:.2f}%)
                - **最低パフォーマンス**: {worst_device['デバイス']} (CVR: {worst_device['コンバージョン率']:.2f}%)
                - **パフォーマンス差**: {best_device['コンバージョン率'] - worst_device['コンバージョン率']:.2f}%ポイント
                
                **詳細分析:**  
                {best_device['デバイス']}が最も高いコンバージョン率を示しています。一方、{worst_device['デバイス']}は最も低いパフォーマンスで、
                {best_device['コンバージョン率'] - worst_device['コンバージョン率']:.2f}%ポイントの差があります。これは、デバイス最適化の余地があることを示唆しています。
                """)
            
            with st.expander("📍 チャネル別パフォーマンス分析"):
                best_channel = channel_stats.loc[channel_stats['コンバージョン率'].idxmax()]
                worst_channel = channel_stats.loc[channel_stats['コンバージョン率'].idxmin()]
                
                st.markdown(f"""
                **チャネル別のパフォーマンス差異**
                
                - **最高パフォーマンス**: {best_channel['チャネル']} (CVR: {best_channel['コンバージョン率']:.2f}%, セッション: {int(best_channel['セッション数']):,})
                - **最低パフォーマンス**: {worst_channel['チャネル']} (CVR: {worst_channel['コンバージョン率']:.2f}%, セッション: {int(worst_channel['セッション数']):,})
                - **ROI評価**: {best_channel['チャネル']}は最も効率的なチャネルで、予算配分を優先すべきです。
                
                **詳細分析:**  
                {best_channel['チャネル']}が最も高いコンバージョン率を示しており、質の高いトラフィックを提供しています。
                一方、{worst_channel['チャネル']}はパフォーマンスが低く、ターゲティングやメッセージの見直しが必要です。
                """)
            
            with st.expander("🚧 ボトルネック分析"):
                max_exit_page = page_stats.loc[page_stats['離脱率'].idxmax()]
                
                st.markdown(f"""
                **最大のボトルネック: ページ{int(max_exit_page['ページ番号'])}**
                
                - **離脱率**: {max_exit_page['離脱率']:.1f}%
                - **平均滞在時間**: {max_exit_page['平均滞在時間(秒)']:.1f}秒
                
                **問題の詳細:**  
                ページ{int(max_exit_page['ページ番号'])}で{max_exit_page['離脱率']:.1f}%のユーザーが離脱しており、LP全体のパフォーマンスを低下させる主要な要因となっています。
                平均滞在時間が{max_exit_page['平均滞在時間(秒)']:.1f}秒と{'短く' if max_exit_page['平均滞在時間(秒)'] < 30 else '長く'}、コンテンツの{'魅力不足' if max_exit_page['平均滞在時間(秒)'] < 30 else '複雑さ'}が原因と考えられます。
                """)
            
            # セクション2: 現状分析からの今後の考察
            st.markdown("---")
            st.markdown("### 🔮 2. 現状分析からの今後の考察")
            
            with st.expander("📈 トレンド予測と潜在的リスク", expanded=True):
                st.markdown(f"""
                **トレンド予測:**
                
                1. **コンバージョン率の予測**  
                   現在のCVR {conversion_rate:.2f}%は{'安定' if conversion_rate >= 3 else '不安定'}です。改善施策を実施しない場合、
                   {'現状維持が期待できます' if conversion_rate >= 3 else 'さらなる低下のリスクがあります'}。
                
                2. **デバイスシフトの影響**  
                   モバイルトラフィックが増加し続ける中、モバイル最適化が不十分な場合、全体のCVRが低下する可能性があります。
                
                3. **チャネルパフォーマンスの変動**  
                   {best_channel['チャネル']}のパフォーマンスが高いため、このチャネルへの依存度が高まる可能性があります。
                   チャネルの多様化がリスク管理に重要です。
                
                **潜在的リスク:**
                
                - **ボトルネックの悪化**: ページ{int(max_exit_page['ページ番号'])}の問題を放置すると、離脱率がさらに上昇する可能性
                - **競合の強化**: 同業他社がLPを改善する中、現状維持では相対的な競争力が低下
                - **広告費の上昇**: CVRが低いままでは、CPAが上昇し続けるRisk
                """)
            
            with st.expander("🎯 成長機会の特定"):
                st.markdown(f"""
                **短期的な成長機会:**
                
                1. **デバイス最適化**  
                   {worst_device['デバイス']}のCVRを{best_device['デバイス']}のレベルに引き上げることで、
                   全体CVRを{(best_device['コンバージョン率'] - worst_device['コンバージョン率']) * 0.5:.2f}%ポイント向上させる可能性があります。
                
                2. **ボトルネック解消**  
                   ページ{int(max_exit_page['ページ番号'])}の離脱率を半分に減らすだけで、最終CTA到達率が大幅に向上します。
                
                3. **高パフォーマンスチャネルの拡大**  
                   {best_channel['チャネル']}への予算配分を増やすことで、短期的なコンバージョン増加が期待できます。
                
                **中長期的な成長機会:**
                
                1. **A/Bテストの継続実施**  
                   継続的なA/Bテストにより、CVRを年間で数%ポイント向上させることが可能です。
                
                2. **パーソナライゼーション**  
                   デバイス、チャネル、ユーザー属性に応じたLPの出し分けで、CVRを大幅に向上させる可能性があります。
                
                3. **リターゲティング戦略**  
                   離脱したユーザーへのリターゲティングで、全体のコンバージョン数を増加させることができます。
                """)
            
            # セクション3: 改善提案
            st.markdown("---")
            st.markdown("### 🚀 3. 具体的な改善提案")
            
            with st.expander("🎯 優先度高: 即実施すべき施策", expanded=True):
                st.markdown(f"""
                **1. ボトルネックページの改善（ページ{int(max_exit_page['ページ番号'])}）**
                
                - **実施内容**:
                  - コンテンツの簡素化と視覚的な改善
                  - 読みやすさの向上（フォントサイズ、行間、余白）
                  - 画像・動画の最適化（読込時間短縮）
                  - CTAボタンの追加または強調
                
                - **期待効果**: 離脱率{max_exit_page['離脱率']:.1f}% → {max_exit_page['離脱率'] * 0.7:.1f}% (30%減)
                - **実施期間**: 1-2週間
                - **必要リソース**: デザイナー1名、エンジニア1名
                
                **2. {worst_device['デバイス']}最適化**
                
                - **実施内容**:
                  - レスポンシブデザインの見直し
                  - タッチ操作の最適化（ボタンサイズ、間隔）
                  - 読込速度の改善（画像圧縮、遅延読み込み）
                  - フォーム入力の簡略化
                
                - **期待効果**: {worst_device['デバイス']}CVR {worst_device['コンバージョン率']:.2f}% → {worst_device['コンバージョン率'] * 1.3:.2f}% (30%向上)
                - **実施期間**: 2-3週間
                - **必要リソース**: UI/UXデザイナー1名、エンジニア1名
                
                **3. ファーストビューの最適化**
                
                - **実施内容**:
                  - キャッチコピーの改善（ベネフィットを明確に）
                  - ヒーロー画像の変更（インパクトと関連性）
                  - CTAボタンの最適化（色、サイズ、テキスト）
                  - 信頼性要素の追加（実績、レビュー、ロゴ）
                
                - **期待効果**: FV残存率{fv_retention_rate:.1f}% → {fv_retention_rate * 1.15:.1f}% (15%向上)
                - **実施期間**: 1週間
                - **必要リソース**: コピーライター1名、デザイナー1名
                """)
            
            with st.expander("🔬 優先度中: A/Bテストで検証すべき施策"):
                st.markdown("""
                **1. ファーストビューA/Bテスト**
                
                - **テスト内容**:
                  - A: 現状のファーストビュー
                  - B: ベネフィット強調型のファーストビュー
                  - C: 社会的証明強調型のファーストビュー
                
                - **測定指標**: FV残存率、コンバージョン率
                - **テスト期間**: 2-4週間
                - **必要サンプルサイズ**: 各パターンあたり1,000セッション以上
                
                **2. CTAボタンA/Bテスト**
                
                - **テスト内容**:
                  - A: 現状のCTAボタン
                  - B: 色変更（アクセントカラー #002060 → オレンジ系）
                  - C: テキスト変更（緊急性やベネフィットを強調）
                
                - **測定指標**: クリック率、コンバージョン率
                - **テスト期間**: 1-2週間
                
                **3. フォーム長A/Bテスト**
                
                - **テスト内容**:
                  - A: 現状のフォーム（入力項目数）
                  - B: 簡略化フォーム（必須項目のみ）
                  - C: 2ステップフォーム（段階的に情報収集）
                
                - **測定指標**: フォーム開始率、完了率、コンバージョン率
                - **テスト期間**: 2-3週間
                """)
            
            with st.expander("💼 優先度低: 中長期的な施策"):
                st.markdown(f"""
                **1. パーソナライゼーションの導入**
                
                - **実施内容**:
                  - デバイス別LPの出し分け
                  - チャネル別メッセージの最適化
                  - リピーターと新規ユーザーで異なるLPを表示
                
                - **期待効果**: 全体CVR 20-30%向上
                - **実施期間**: 2-3ヶ月
                - **必要リソース**: エンジニア2-3名、デザイナー1-2名
                
                **2. 動画コンテンツの強化**
                
                - **実施内容**:
                  - 製品デモ動画の追加
                  - 顧客事例インタビュー動画
                  - アニメーションで複雑な概念を説明
                
                - **期待効果**: エンゲージメント向上、CVR 10-15%向上
                - **実施期間**: 1-2ヶ月
                - **必要リソース**: 動画クリエイター1-2名
                
                **3. リターゲティング戦略の構築**
                
                - **実施内容**:
                  - 離脱ユーザーへのリターゲティング広告
                  - カート放棄ユーザーへのメール送信
                  - ページ途中離脱ユーザーへの特別オファー
                
                - **期待効果**: 全体コンバージョン数 15-25%増加
                - **実施期間**: 1-2ヶ月
                - **必要リソース**: マーケター1名、エンジニア1名
                
                **4. チャネル最適化と予算再配分**
                
                - **実施内容**:
                  - {best_channel['チャネル']}への予算増額
                  - {worst_channel['チャネル']}のターゲティング見直しまたは停止
                  - 新規チャネルのテスト（リスク分散）
                
                - **期待効果**: ROI 20-30%向上
                - **実施期間**: 継続的
                - **必要リソース**: マーケティングマネージャー1名
                """)
            
            with st.expander("📊 実施ロードマップ（3ヶ月間）"):
                st.markdown("""
                | 時期 | 施策 | 目標KPI | 担当 |
                |------|------|----------|------|
                | 1週目 | ファーストビュー最適化 | FV残存率 +15% | デザインチーム |
                | 2-3週目 | ボトルネックページ改善 | 離脱率 -30% | デザイン+開発 |
                | 4-5週目 | デバイス最適化 | モバイルCVR +30% | 開発チーム |
                | 6-8週目 | FVA/Bテスト | 全体CVR +10% | マーケティング |
                | 9-10週目 | CTAA/Bテスト | クリック率 +15% | マーケティング |
                | 11-12週目 | リターゲティング導入 | コンバージョン数 +20% | マーケティング |
                
                **期待される総合効果:**
                - コンバージョン率: {conversion_rate:.2f}% → {conversion_rate * 1.5:.2f}% (50%向上)
                - 月間コンバージョン数: 現在の1.5倍
                - ROI: 20-30%向上
                """)
            
            st.success("✅ AI分析が完了しました！上記の提案を参考に、LPの改善を進めてください。")
    
    st.markdown("---")
    st.markdown("""
    **💡 本番環境での機能:**
    - Gemini 2.5 Proによるさらに詳細な分析
    - リアルタイムデータとの連携
    - 自動レポート生成機能
    - カスタム質問への回答
    """)
    
    # 既存の質問ボタンは保持
    
    # 質問ボタンにトグル機能を追加
    st.markdown("#### よくある質問")
    
    # session_stateでトグル状態を管理
    if 'faq_bottleneck' not in st.session_state:
        st.session_state.faq_bottleneck = False
    if 'faq_cvr' not in st.session_state:
        st.session_state.faq_cvr = False
    if 'faq_abtest' not in st.session_state:
        st.session_state.faq_abtest = False
    if 'faq_device' not in st.session_state:
        st.session_state.faq_device = False
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("❓ このLPの最大のボトルネックは？"):
            st.session_state.faq_bottleneck = not st.session_state.faq_bottleneck
        
        if st.session_state.faq_bottleneck:
            # 離脱率が最も高いページを特定
            max_exit_page = page_stats_global.loc[page_stats_global['離脱率'].idxmax()]
            
            st.info(f"""
            **分析結果:**
            
            最大のボトルネックは**ページ{int(max_exit_page['ページ番号'])}**です。
            
            - 離脱率: {max_exit_page['離脱率']:.1f}%
            - 平均滞在時間: {max_exit_page['平均滞在時間(秒)']:.1f}秒
            
            **推奨アクション:**
            1. ページ{int(max_exit_page['ページ番号'])}のコンテンツを見直し、ユーザーの関心を引く要素を追加
            2. A/Bテストで異なるコンテンツをテスト
            3. 読込時間が長い場合は、画像の最適化を検討
            """)
        
        if st.button("❓ コンバージョン率を改善するには？"):
            st.session_state.faq_cvr = not st.session_state.faq_cvr
        
        if st.session_state.faq_cvr:
            st.info(f"""
            **分析結果:**
            
            現在のコンバージョン率は**{conversion_rate:.2f}%**です。
            
            **推奨アクション:**
            1. FV残存率({fv_retention_rate:.1f}%)を改善するため、ファーストビューのコンテンツを強化
            2. 最終CTA到達率({final_cta_rate:.1f}%)を改善するため、ページ遷移をスムーズにする
            3. デバイス別の分析を行い、パフォーマンスが低いデバイスに最適化
            4. 高パフォーマンスのチャネルに予算を集中
            """)
    
    with col2:
        if st.button("❓ A/Bテストの結果、どちらが優れている？"):
            st.session_state.faq_abtest = not st.session_state.faq_abtest
        
        if st.session_state.faq_abtest:
            best_variant = ab_stats_global.loc[ab_stats_global['コンバージョン率'].idxmax()]
            
            st.info(f"""
            **分析結果:**
            
            **バリアント{best_variant['バリアント']}**が最も優れています。
            
            - コンバージョン率: {best_variant['コンバージョン率']:.2f}%
            - セッション数: {int(best_variant['セッション数'])}
            
            **推奨アクション:**
            1. バリアント{best_variant['バリアント']}を本番環境に適用
            2. さらなる改善のため、次のA/Bテストを計画
            """)
        
        if st.button("❓ デバイス別のパフォーマンス差は？"):
            st.session_state.faq_device = not st.session_state.faq_device
        
        if st.session_state.faq_device:
            best_device = device_stats_global.loc[device_stats_global['コンバージョン率'].idxmax()]
            worst_device = device_stats_global.loc[device_stats_global['コンバージョン率'].idxmin()]
            
            st.info(f"""
            **分析結果:**
            
            **最高パフォーマンス:** {best_device['デバイス']} (CVR: {best_device['コンバージョン率']:.2f}%)
            **最低パフォーマンス:** {worst_device['デバイス']} (CVR: {worst_device['コンバージョン率']:.2f}%)
            
            **推奨アクション:**
            1. {worst_device['デバイス']}向けにUIを最適化
            2. {worst_device['デバイス']}での読込速度を改善
            3. {best_device['デバイス']}の成功要因を他デバイスに適用
            """)
    
    st.markdown("---")
    
    # フリーチャット（プロトタイプ）
    st.markdown("#### フリーチャット")
    
    user_question = st.text_input("質問を入力してください（プロトタイプ版では固定回答が表示されます）")
    
    if st.button("送信"):
        if user_question:
            st.info(f"""
            **質問:** {user_question}
            
            **回答（プロトタイプ）:**
            
            ご質問ありがとうございます。本番環境では、Gemini 2.5 Proが実際のデータに基づいて詳細な分析と提案を行います。
            
            現在のプロトタイプでは、以下のような分析が可能です:
            - データの傾向分析
            - ボトルネックの特定
            - 改善提案の生成
            - SQL クエリの提案
            
            本格実装後は、より高度な分析と具体的なアクションプランを提供します。
            """)
        else:
            st.warning("質問を入力してください")

# タブ10: 使用ガイド
elif selected_analysis == "使用ガイド":
    st.markdown('<div class="sub-header">使用ガイド</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 瞬ジェネ AIアナリストの使い方
    
    #### 1. フィルター設定
    左サイドバーで、分析対象を絞り込むことができます。
    - **期間を選択**: 過去7日間、過去30日間、過去90日間、またはカスタム期間
    - **LP選択**: 特定のLPのみを分析
    - **チャネル**: 特定のチャネル（Google、Facebookなど）のみを分析
    - **デバイス**: スマートフォン、パソコン、タブレットを選択
    - **A/Bテスト**: 特定のバリアントのみを分析
    
    #### 2. 全体分析
    LP全体のパフォーマンスを確認できます。
    - 主要指標詳細表（10個のKPIを一覧表示）
    - セッション数の推移
    - コンバージョン率の推移
    - デバイス別・チャネル別分析
    - LP進行ファネル
    
    #### 3. ページ分析
    各ページのパフォーマンスを詳細に分析できます。
    - ページ別パフォーマンス一覧
    - 滞在時間が短いページ TOP5
    - 離脱率が高いページ TOP5
    
    #### 4. セグメント分析
    デバイス、チャネル、UTMソース、A/Bテスト別に分析できます。
    
    #### 5. A/Bテスト分析
    A/Bテストの結果を比較し、最適なバリアントを特定できます。
    - A/Bテストマトリクス（有意差判定付き）
    - CVR向上率×有意性のバブルチャート
    - A/BテストCVR比較
    - A/BテストCVR時系列推移
    
    #### 6. 動画・スクロール分析
    動画視聴状況や逆行率とコンバージョンの関係を分析できます。
    
    #### 7. 時系列分析
    時間帯別、曜日別のパフォーマンスを分析できます。
    
    #### 8. リアルタイム分析
    直近1時間のデータをリアルタイムで確認できます。
    
    #### 9. インタラクション分析
    CTA、フローティングバナー、離脱防止ポップアップ、会社情報のクリック数とクリック率を分析できます。
    - 要素別CTR比較
    - 要素別クリック数比較
    - デバイス別インタラクション分析
    
    #### 10. デモグラフィック情報
    年齢層、性別、地域、デバイス別に分析できます。
    - 年齢層別分析（セッション数、CVR、平均滞在時間）
    - 性別分析（男性、女性、その他/未回答）
    - 地域別分析（都道府県ごと）
    - デバイス別分析（PC、スマートフォン、タブレット）
    
    #### 11. AI分析
    AIがデータを分析し、改善提案を行います。
    - 質問ボタンをクリックすると、AIが回答を生成します
    - フリーチャットで自由に質問できます
    """)

# タブ11: 専門用語解説
elif selected_analysis == "専門用語解説":
    st.markdown('<div class="sub-header">専門用語解説</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 📚 マーケティング・分析用語集
    
    LP分析で使用される主要な用語を詳しく解説します。
    """)
    
    # カテゴリー別に表示
    with st.expander("📊 基本指標（KPI）", expanded=True):
        st.markdown("""
        **セッション（Session）**
        ユーザーがウェブサイトを訪れた1回の訪問。同じユーザーが複数回訪れた場合、それぞれ別のセッションとしてカウントされます。通常、30分間操作がないとセッションが終了します。
        
        **ユニークユーザー（Unique User）**
        特定の期間内にサイトを訪れたユニークな個人の数。CookieやデバイスIDで識別されます。
        
        **ページビュー（Page View / PV）**
        ページが表示された回数。同じページを何度も見た場合、その分だけカウントされます。
        
        **直帰率（Bounce Rate）**
        1ページだけを見てサイトを離れたセッションの割合。高いほど、ユーザーがすぐに離脱していることを意味します。
        
        **離脱率（Exit Rate）**
        特定のページでサイトを離れたセッションの割合。そのページがユーザージャーニーの最後になった割合を示します。
        
        **滞在時間（Session Duration）**
        ユーザーがサイトに滞在した時間。長いほどエンゲージメントが高いと考えられますが、コンテンツがわかりにくい可能性もあります。
        """)
    
    with st.expander("🎯 コンバージョン関連"):
        st.markdown("""
        **コンバージョン（Conversion / CV）**
        ユーザーが目標とする行動（購入、問い合わせ、会員登録など）を完了したこと。LPの最終目標です。
        
        **コンバージョン率（Conversion Rate / CVR）**
        セッション数に対するコンバージョン数の割合。  
        計算式: CVR = (コンバージョン数 ÷ セッション数) × 100  
        例: 1,000セッションで50コンバージョンならCVR = 5%
        
        **マイクロコンバージョン（Micro Conversion）**
        最終目標に至る前の中間目標。例: 資料ダウンロード、動画視聴、ページスクロールなど。
        
        **CPA（Cost Per Acquisition）**
        1件のコンバージョンを獲得するためにかかったコスト。  
        計算式: CPA = 広告費 ÷ コンバージョン数  
        侎いほど効率的です。
        
        **ROAS（Return On Ad Spend）**
        広告費用対効果。広告費1円あたりの売上。  
        計算式: ROAS = 売上 ÷ 広告費 × 100  
        例: 広告費10万円で売上50万円ならROAS = 500%
        """)
    
    with st.expander("📱 LP特有の指標"):
        st.markdown("""
        **ファーストビュー（First View / FV）**
        ページを開いたときに最初に表示される画面範囲。スクロールしないで見える部分。LPで最も重要な要素で、ファーストビューで興味を引けないと即離脱されます。
        
        **FV残存率（FV Retention Rate）**
        ファーストビューを見た後、次のセクションに進んだユーザーの割合。高いほどFVが効果的です。業界平均は60-80%程度。
        
        **スクロール率（Scroll Depth）**
        ユーザーがページをどれだけスクロールしたかの割合。25%、50%、75%、100%で測定されることが多いです。100%はページの最後まで到達したことを意味します。
        
        **CTA（Call To Action）**
        ユーザーに具体的な行動を促すボタンやリンク。「今すぐ購入」「無料で試す」「資料をダウンロード」など。LPの最重要要素です。
        
        **最終CTA到達率**
        LPの最後に配置されたCTA（コンバージョンボタン）に到達したユーザーの割合。高いほどLP全体のコンテンツが効果的です。
        
        **ファネル（Funnel）**
        ユーザーがLPを進む過程を段階的に表した図。各ステップでどれだけのユーザーが離脱したかを可視化し、ボトルネック（問題箇所）を特定します。
        """)
    
    with st.expander("🧪 A/Bテスト・最適化"):
        st.markdown("""
        **A/Bテスト（A/B Testing）**
        2つ以上の異なるバージョン（バリアント）を同時に公開し、どちらが優れているかをデータで検証する手法。例: ヘッダー画像をAパターンとBパターンで比較。
        
        **バリアント（Variant）**
        A/Bテストで比較する各バージョン。Aパターン（オリジナル）、Bパターン（変更版）など。
        
        **統計的有意差（Statistical Significance）**
        A/Bテストの結果が偶然ではなく、本当に差があることを示す指標。通常95%以上の信頼水準で判断します。
        
        **多変量テスト（Multivariate Testing / MVT）**
        複数の要素を同時にテストする手法。例: ヘッダー画像、CTAボタンの色、コピーを同時に変えて最適な組み合わせを見つけます。
        
        **LPO（Landing Page Optimization）**
        LPのコンバージョン率を高めるための最適化施策。A/Bテスト、ヒートマップ分析、ユーザーテストなどを組み合わせて実施します。
        """)
    
    with st.expander("📍 トラフィック・チャネル"):
        st.markdown("""
        **UTMパラメータ（UTM Parameters）**
        URLに付加するタグで、どの広告やキャンペーンからユーザーが来たかを追跡するためのもの。
        - **utm_source**: トラフィック元（例: google, facebook, newsletter）
        - **utm_medium**: 媒体（例: cpc, email, social）
        - **utm_campaign**: キャンペーン名（例: summer_sale_2024）
        - **utm_content**: 広告コンテンツ（例: banner_a, text_link）
        - **utm_term**: 検索キーワード（例: running+shoes）
        
        **チャネル（Channel）**
        ユーザーがLPに到達した経路のカテゴリー。
        - **Organic Search**: 自然検索（Google、Yahooなど）
        - **Paid Search**: 有料検索広告（リスティング広告）
        - **Organic Social**: SNSからの自然流入
        - **Paid Social**: SNS広告
        - **Direct**: 直接アクセス（ブックマーク、URL直打ち）
        - **Referral**: 他サイトからのリンク
        - **Email**: メールからの流入
        
        **リファラー（Referrer）**
        ユーザーが直前に訪れていたページのURL。どこから流入してきたかを特定できます。
        
        **ランディングページ（Landing Page / LP）**
        ユーザーが最初に着地したページ。広告や検索結果から誘導するために特別に設計されたページ。
        """)
    
    with st.expander("👥 セグメント・オーディエンス"):
        st.markdown("""
        **セグメント（Segment）**
        特定の条件で絞り込んだユーザーグループ。例:
        - デバイス別: スマートフォン、タブレット、PC
        - チャネル別: Googleからのユーザー、SNSからのユーザー
        - 行動別: 購入済みユーザー、カート放棄ユーザー
        
        **オーディエンス（Audience）**
        特定の条件を満たすユーザーの集合。リターゲティング広告やパーソナライズに使用します。
        
        **カスタムオーディエンス（Custom Audience）**
        独自の条件で作成したオーディエンス。例: 「滞在時間60秒以上、スクロール率75%以上、コンバージョン未完了」のユーザー。
        
        **リターゲティング（Retargeting）**
        一度サイトを訪れたユーザーに対して、再度広告を表示する手法。コンバージョンしなかったユーザーを再誘導します。
        """)
    
    with st.expander("⏱️ パフォーマンス指標"):
        st.markdown("""
        **読込時間（Page Load Time）**
        ページが完全に表示されるまでの時間。短いほどユーザー体験が良く、CVRも向上します。目標は3秒以内。
        
        **ファーストビュー表示時間（First Contentful Paint / FCP）**
        ページの最初のコンテンツが表示されるまでの時間。ユーザーが「ページが読み込まれている」と感じるまでの時間。
        
        **インタラクティブまでの時間（Time to Interactive / TTI）**
        ページが完全に操作可能になるまでの時間。ボタンやリンクがクリックできるようになるまでの時間。
        
        **クリック率（Click Through Rate / CTR）**
        表示回数（インプレッション）に対するクリック数の割合。  
        計算式: CTR = (クリック数 ÷ 表示回数) × 100  
        広告やCTAボタンの効果を測定します。
        
        **エンゲージメント率（Engagement Rate）**
        ユーザーがサイトでアクティブに行動した割合。クリック、スクロール、動画視聴などを含みます。
        """)
    
    with st.expander("📊 分析ツール・手法"):
        st.markdown("""
        **ヒートマップ（Heatmap）**
        ユーザーのクリックやスクロール、マウスの動きを色で可視化したもの。赤い部分が最も注目されているエリア。
        
        **セッションリプレイ（Session Replay）**
        ユーザーの行動を動画のように再生する機能。ユーザーがどこで迷ったか、どこで離脱したかを詳細に分析できます。
        
        **コホート分析（Cohort Analysis）**
        同じ時期に訪れたユーザーグループ（コホート）の行動を時間経過で追跡する分析手法。リピート率やLTVの分析に使用します。
        
        **アトリビューション（Attribution）**
        コンバージョンに至るまでの複数のタッチポイント（広告、メール、SNSなど）の貢献度を評価する手法。
        - **ラストクリック**: 最後の接触に100%の貢献を割り当て
        - **ファーストクリック**: 最初の接触に100%の貢献を割り当て
        - **線形**: 全ての接触に均等に貢献を割り当て
        """)
    
    st.markdown("---")
    st.markdown("💡 **ヒント**: 各用語をクリックして詳細を確認できます。")

# フッター
st.markdown("---")
st.markdown("**瞬ジェネ AIアナリスト** - Powered by Streamlit & Gemini 2.5 Pro")

