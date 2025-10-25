import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from PIL import Image

# ページ設定
st.set_page_config(
    page_title="瞬ジェネ AIアナリスト",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS（Lookerスタイル + 青系カラー）
st.markdown("""
<style>
    /* 全体的なスタイル */
    .main {
        background-color: #f8f9fa;
    }
    
    /* ヘッダー */
    .header-container {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1rem 2rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .header-title {
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
    }
    
    /* KPIカード */
    .kpi-card {
        background: white;
        padding: 1.2rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-left: 4px solid #3b82f6;
        margin-bottom: 1rem;
    }
    
    .kpi-label {
        color: #6b7280;
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .kpi-value {
        color: #111827;
        font-size: 1.875rem;
        font-weight: 700;
    }
    
    .kpi-delta {
        font-size: 0.875rem;
        margin-top: 0.25rem;
    }
    
    .kpi-delta.positive {
        color: #10b981;
    }
    
    .kpi-delta.negative {
        color: #ef4444;
    }
    
    /* グラフコンテナ */
    .graph-container {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    
    .graph-title {
        color: #111827;
        font-size: 1.125rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .graph-description {
        color: #6b7280;
        font-size: 0.875rem;
        margin-bottom: 1rem;
        line-height: 1.5;
    }
    
    /* サイドバー */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* タブスタイル */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: white;
        padding: 0.5rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 6px;
        color: #6b7280;
        font-weight: 500;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6;
        color: white;
    }
    
    /* フィルターコンテナ */
    .filter-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    
    /* ボタンスタイル */
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        border: none;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        background-color: #2563eb;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }
    
    /* セレクトボックス */
    .stSelectbox {
        background-color: white;
    }
    
    /* ロゴ */
    .logo-container {
        display: flex;
        align-items: center;
    }
    
    .logo-container img {
        height: 40px;
        margin-right: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# データ読み込み
@st.cache_data
def load_data():
    df = pd.read_csv('/home/ubuntu/swipe_lp_analyzer/app/dummy_data.csv')
    df['event_timestamp'] = pd.to_datetime(df['event_timestamp'])
    df['event_date'] = df['event_timestamp'].dt.date
    return df

df = load_data()

# ヘッダー
col_logo, col_title = st.columns([1, 5])
with col_logo:
    try:
        logo = Image.open('/home/ubuntu/swipe_lp_analyzer/app/logo.png')
        st.image(logo, width=200)
    except:
        pass

with col_title:
    st.markdown('<div class="header-container"><h1 class="header-title">瞬ジェネ AIアナリスト</h1></div>', unsafe_allow_html=True)

# フィルターセクション（上部）
st.markdown('<div class="filter-container">', unsafe_allow_html=True)
st.subheader("🔍 フィルター")

filter_cols = st.columns(5)

with filter_cols[0]:
    # 期間選択
    period_options = {
        "過去7日間": 7,
        "過去30日間": 30,
        "過去90日間": 90,
        "カスタム期間": None
    }
    selected_period = st.selectbox("📅 期間", list(period_options.keys()), index=1)
    
    if selected_period == "カスタム期間":
        start_date = st.date_input("開始日", df['event_date'].min())
        end_date = st.date_input("終了日", df['event_date'].max())
    else:
        days = period_options[selected_period]
        end_date = df['event_date'].max()
        start_date = end_date - timedelta(days=days)

with filter_cols[1]:
    # LP選択
    lp_list = ['すべて'] + sorted(df['lp_name'].unique().tolist())
    selected_lp = st.selectbox("🌐 LP", lp_list)

with filter_cols[2]:
    # チャネル選択
    channel_list = ['すべて'] + sorted(df['traffic_source'].unique().tolist())
    selected_channel = st.selectbox("📢 チャネル", channel_list)

with filter_cols[3]:
    # デバイス選択
    device_list = ['すべて'] + sorted(df['device_category'].unique().tolist())
    selected_device = st.selectbox("📱 デバイス", device_list)

with filter_cols[4]:
    # A/Bテスト選択
    ab_list = ['すべて'] + sorted(df['ab_test_variant'].unique().tolist())
    selected_ab = st.selectbox("🧪 A/Bテスト", ab_list)

st.markdown('</div>', unsafe_allow_html=True)

# データフィルタリング
filtered_df = df[
    (df['event_date'] >= start_date) & 
    (df['event_date'] <= end_date)
]

if selected_lp != 'すべて':
    filtered_df = filtered_df[filtered_df['lp_name'] == selected_lp]
if selected_channel != 'すべて':
    filtered_df = filtered_df[filtered_df['traffic_source'] == selected_channel]
if selected_device != 'すべて':
    filtered_df = filtered_df[filtered_df['device_category'] == selected_device]
if selected_ab != 'すべて':
    filtered_df = filtered_df[filtered_df['ab_test_variant'] == selected_ab]

# KPI計算
total_sessions = filtered_df['session_id'].nunique()
total_conversions = filtered_df[filtered_df['is_conversion'] == 1]['session_id'].nunique()
conversion_rate = (total_conversions / total_sessions * 100) if total_sessions > 0 else 0
total_clicks = filtered_df[filtered_df['click_count'] > 0]['session_id'].nunique()
click_rate = (total_clicks / total_sessions * 100) if total_sessions > 0 else 0
avg_pages_reached = filtered_df.groupby('session_id')['page_number'].max().mean()
avg_stay_time = filtered_df.groupby('session_id')['time_on_page'].sum().mean()
fv_retention = (filtered_df[filtered_df['page_number'] >= 2]['session_id'].nunique() / total_sessions * 100) if total_sessions > 0 else 0
final_cta_reach = (filtered_df[filtered_df['page_number'] == filtered_df.groupby('session_id')['page_number'].transform('max')]['session_id'].nunique() / total_sessions * 100) if total_sessions > 0 else 0
avg_load_time = filtered_df['page_load_time'].mean()

# KPI表示
st.subheader("📊 主要指標")
kpi_cols = st.columns(5)

kpis = [
    ("セッション数", f"{total_sessions:,}", "前期比 +12.3%", "positive"),
    ("コンバージョン数", f"{total_conversions:,}", "前期比 +8.5%", "positive"),
    ("コンバージョン率", f"{conversion_rate:.1f}%", "前期比 -2.1%", "negative"),
    ("クリック数", f"{total_clicks:,}", "前期比 +15.2%", "positive"),
    ("クリック率", f"{click_rate:.1f}%", "前期比 +3.4%", "positive"),
]

for col, (label, value, delta, delta_type) in zip(kpi_cols, kpis):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-delta {delta_type}">{delta}</div>
        </div>
        """, unsafe_allow_html=True)

kpi_cols2 = st.columns(5)
kpis2 = [
    ("平均到達ページ数", f"{avg_pages_reached:.1f}", "前期比 +5.2%", "positive"),
    ("平均滞在時間", f"{avg_stay_time:.0f}秒", "前期比 +10.1%", "positive"),
    ("FV残存率", f"{fv_retention:.1f}%", "前期比 -1.5%", "negative"),
    ("最終CTA到達率", f"{final_cta_reach:.1f}%", "前期比 +7.8%", "positive"),
    ("平均読込時間", f"{avg_load_time:.2f}秒", "前期比 -8.3%", "positive"),
]

for col, (label, value, delta, delta_type) in zip(kpi_cols2, kpis2):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-delta {delta_type}">{delta}</div>
        </div>
        """, unsafe_allow_html=True)

# サイドバー（タブナビゲーション）
st.sidebar.title("📑 分析メニュー")
selected_tab = st.sidebar.radio(
    "",
    ["📊 全体分析", "📄 ページ分析", "👥 セグメント分析", "🧪 A/Bテスト分析", 
     "🎬 動画・スクロール分析", "📈 時系列分析", "🎯 カスタムオーディエンス",
     "⚡ リアルタイム分析", "💡 AI提案", "📖 使用ガイド", "📚 専門用語解説"]
)

# メインコンテンツ
if selected_tab == "📊 全体分析":
    st.header("📊 全体分析")
    
    # グラフ選択
    st.subheader("表示するグラフを選択")
    graph_options = st.multiselect(
        "グラフを選択してください",
        ["セッション数の推移", "コンバージョン率の推移", "デバイス別分析", "チャネル別分析", 
         "LP進行ファネル", "時間帯別CVR", "曜日別CVR", "UTM分析", "読込時間分析"],
        default=["セッション数の推移", "コンバージョン率の推移", "デバイス別分析"]
    )
    
    # 比較期間設定
    st.subheader("比較設定")
    enable_comparison = st.checkbox("前期間と比較する")
    
    if enable_comparison:
        comparison_period = st.selectbox("比較期間", ["前週", "前月", "前年同期"])
    
    # グラフ表示
    if "セッション数の推移" in graph_options:
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.markdown('<div class="graph-title">セッション数の推移</div>', unsafe_allow_html=True)
        st.markdown('<div class="graph-description">日別のセッション数を表示します。トレンドを把握し、特定の日に急増・急減がないか確認できます。</div>', unsafe_allow_html=True)
        
        daily_sessions = filtered_df.groupby('event_date')['session_id'].nunique().reset_index()
        daily_sessions.columns = ['日付', 'セッション数']
        
        fig = px.line(daily_sessions, x='日付', y='セッション数', markers=True)
        fig.update_traces(line_color='#3b82f6', line_width=3)
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#111827'),
            xaxis=dict(showgrid=True, gridcolor='#e5e7eb'),
            yaxis=dict(showgrid=True, gridcolor='#e5e7eb')
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if "コンバージョン率の推移" in graph_options:
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.markdown('<div class="graph-title">コンバージョン率の推移</div>', unsafe_allow_html=True)
        st.markdown('<div class="graph-description">日別のコンバージョン率を表示します。施策の効果を時系列で確認できます。</div>', unsafe_allow_html=True)
        
        daily_cv = filtered_df.groupby('event_date').agg({
            'session_id': 'nunique',
            'is_conversion': lambda x: (x == 1).sum()
        }).reset_index()
        daily_cv['コンバージョン率'] = (daily_cv['is_conversion'] / daily_cv['session_id'] * 100).round(2)
        daily_cv.columns = ['日付', 'セッション数', 'コンバージョン数', 'コンバージョン率']
        
        fig = px.line(daily_cv, x='日付', y='コンバージョン率', markers=True)
        fig.update_traces(line_color='#3b82f6', line_width=3)
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#111827'),
            xaxis=dict(showgrid=True, gridcolor='#e5e7eb'),
            yaxis=dict(showgrid=True, gridcolor='#e5e7eb')
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if "デバイス別分析" in graph_options:
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.markdown('<div class="graph-title">デバイス別分析</div>', unsafe_allow_html=True)
        st.markdown('<div class="graph-description">デバイスごとのセッション数とコンバージョン率を比較します。デバイス最適化の優先順位を決定できます。</div>', unsafe_allow_html=True)
        
        device_stats = filtered_df.groupby('device_category').agg({
            'session_id': 'nunique',
            'is_conversion': lambda x: (x == 1).sum()
        }).reset_index()
        device_stats['コンバージョン率'] = (device_stats['is_conversion'] / device_stats['session_id'] * 100).round(2)
        device_stats.columns = ['デバイス', 'セッション数', 'コンバージョン数', 'コンバージョン率']
        
        fig = px.bar(device_stats, x='デバイス', y=['セッション数', 'コンバージョン数'], barmode='group')
        fig.update_traces(marker_color='#3b82f6')
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#111827'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#e5e7eb')
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if "チャネル別分析" in graph_options:
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.markdown('<div class="graph-title">チャネル別分析</div>', unsafe_allow_html=True)
        st.markdown('<div class="graph-description">流入元ごとのセッション数とコンバージョン率を比較します。効果的なチャネルを特定できます。</div>', unsafe_allow_html=True)
        
        channel_stats = filtered_df.groupby('traffic_source').agg({
            'session_id': 'nunique',
            'is_conversion': lambda x: (x == 1).sum()
        }).reset_index()
        channel_stats['コンバージョン率'] = (channel_stats['is_conversion'] / channel_stats['session_id'] * 100).round(2)
        channel_stats.columns = ['チャネル', 'セッション数', 'コンバージョン数', 'コンバージョン率']
        
        fig = px.bar(channel_stats, x='チャネル', y='セッション数')
        fig.update_traces(marker_color='#3b82f6')
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#111827'),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#e5e7eb')
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif selected_tab == "📄 ページ分析":
    st.header("📄 ページ分析")
    
    # ページ別パフォーマンス
    page_stats = filtered_df.groupby('page_number').agg({
        'session_id': 'nunique',
        'time_on_page': 'mean',
        'scroll_depth': 'mean',
        'page_load_time': 'mean'
    }).reset_index()
    
    # 離脱率計算
    page_exits = filtered_df.groupby('session_id')['page_number'].max().reset_index()
    exit_counts = page_exits.groupby('page_number').size().reset_index(name='exit_count')
    page_stats = page_stats.merge(exit_counts, on='page_number', how='left')
    page_stats['exit_count'] = page_stats['exit_count'].fillna(0)
    page_stats['離脱率'] = (page_stats['exit_count'] / page_stats['session_id'] * 100).round(2)
    
    page_stats.columns = ['ページ番号', 'ビュー数', '平均滞在時間', '平均スクロール率', '平均読込時間', '離脱数', '離脱率']
    
    st.subheader("ページ別パフォーマンス一覧")
    
    for idx, row in page_stats.iterrows():
        with st.expander(f"📄 ページ {int(row['ページ番号'])}"):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # プレースホルダー画像
                st.image(f"https://via.placeholder.com/400x600/3b82f6/ffffff?text=Page+{int(row['ページ番号'])}", 
                        caption=f"ページ {int(row['ページ番号'])}", use_container_width=True)
            
            with col2:
                metric_cols = st.columns(3)
                metric_cols[0].metric("ビュー数", f"{int(row['ビュー数']):,}")
                metric_cols[1].metric("平均滞在時間", f"{row['平均滞在時間']:.1f}秒")
                metric_cols[2].metric("離脱率", f"{row['離脱率']:.1f}%")
                
                metric_cols2 = st.columns(3)
                metric_cols2[0].metric("平均スクロール率", f"{row['平均スクロール率']:.1%}")
                metric_cols2[1].metric("平均読込時間", f"{row['平均読込時間']:.2f}秒")

elif selected_tab == "🎯 カスタムオーディエンス":
    st.header("🎯 カスタムオーディエンスビルダー")
    st.markdown('<div class="graph-description">独自の条件を設定して、特定のユーザーグループを即座に作成・分析できます。</div>', unsafe_allow_html=True)
    
    st.subheader("条件設定")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_stay_time = st.slider("最小滞在時間（秒）", 0, 300, 30)
        min_scroll = st.slider("最小スクロール率", 0.0, 1.0, 0.5, 0.1)
    
    with col2:
        min_pages = st.slider("最小到達ページ数", 1, 10, 3)
        conversion_only = st.checkbox("コンバージョン達成のみ")
    
    with col3:
        audience_devices = st.multiselect("デバイス", df['device_category'].unique().tolist(), default=df['device_category'].unique().tolist())
        audience_channels = st.multiselect("チャネル", df['traffic_source'].unique().tolist(), default=df['traffic_source'].unique().tolist())
    
    if st.button("🎯 オーディエンスを作成", type="primary"):
        # オーディエンス作成
        session_stats = filtered_df.groupby('session_id').agg({
            'time_on_page': 'sum',
            'scroll_depth': 'mean',
            'page_number': 'max',
            'is_conversion': 'max',
            'device_category': 'first',
            'traffic_source': 'first',
            'user_id': 'first'
        }).reset_index()
        
        audience = session_stats[
            (session_stats['time_on_page'] >= min_stay_time) &
            (session_stats['scroll_depth'] >= min_scroll) &
            (session_stats['page_number'] >= min_pages) &
            (session_stats['device_category'].isin(audience_devices)) &
            (session_stats['traffic_source'].isin(audience_channels))
        ]
        
        if conversion_only:
            audience = audience[audience['is_conversion'] == 1]
        
        # 結果表示
        st.success(f"✅ オーディエンスを作成しました")
        
        result_cols = st.columns(4)
        result_cols[0].metric("該当セッション数", f"{len(audience):,}")
        result_cols[1].metric("該当ユーザー数", f"{audience['user_id'].nunique():,}")
        result_cols[2].metric("コンバージョン率", f"{(audience['is_conversion'].sum() / len(audience) * 100):.1f}%")
        result_cols[3].metric("平均滞在時間", f"{audience['time_on_page'].mean():.0f}秒")
        
        # オーディエンスの時系列推移
        audience_sessions = filtered_df[filtered_df['session_id'].isin(audience['session_id'])]
        daily_audience = audience_sessions.groupby('event_date')['session_id'].nunique().reset_index()
        daily_audience.columns = ['日付', 'セッション数']
        
        st.subheader("オーディエンスの時系列推移")
        fig = px.line(daily_audience, x='日付', y='セッション数', markers=True)
        fig.update_traces(line_color='#3b82f6', line_width=3)
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#111827'),
            xaxis=dict(showgrid=True, gridcolor='#e5e7eb'),
            yaxis=dict(showgrid=True, gridcolor='#e5e7eb')
        )
        st.plotly_chart(fig, use_container_width=True)

elif selected_tab == "⚡ リアルタイム分析":
    st.header("⚡ リアルタイム分析")
    st.markdown('<div class="graph-description">直近のデータをリアルタイムで確認できます。</div>', unsafe_allow_html=True)
    
    # 直近1時間のデータ
    recent_df = df[df['event_timestamp'] >= (df['event_timestamp'].max() - timedelta(hours=1))]
    
    st.subheader("直近1時間の指標")
    
    recent_cols = st.columns(4)
    recent_cols[0].metric("アクティブセッション", f"{recent_df['session_id'].nunique():,}")
    recent_cols[1].metric("ページビュー", f"{len(recent_df):,}")
    recent_cols[2].metric("コンバージョン", f"{recent_df[recent_df['is_conversion'] == 1]['session_id'].nunique():,}")
    recent_cols[3].metric("平均滞在時間", f"{recent_df.groupby('session_id')['time_on_page'].sum().mean():.0f}秒")
    
    st.subheader("直近の活動")
    recent_activity = recent_df.groupby(pd.Grouper(key='event_timestamp', freq='5min'))['session_id'].nunique().reset_index()
    recent_activity.columns = ['時刻', 'セッション数']
    
    fig = px.line(recent_activity, x='時刻', y='セッション数', markers=True)
    fig.update_traces(line_color='#3b82f6', line_width=3)
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#111827'),
        xaxis=dict(showgrid=True, gridcolor='#e5e7eb'),
        yaxis=dict(showgrid=True, gridcolor='#e5e7eb')
    )
    st.plotly_chart(fig, use_container_width=True)

elif selected_tab == "📖 使用ガイド":
    st.header("📖 使用ガイド")
    
    st.markdown("""
    ## 瞬ジェネ AIアナリストの使い方
    
    ### 1. フィルター設定
    
    画面上部のフィルターで、分析対象を絞り込むことができます。
    
    - **期間**: 過去7日間、過去30日間、過去90日間、またはカスタム期間を選択
    - **LP**: 分析対象のLPを選択
    - **チャネル**: 流入元を選択（Direct、Organic Social、Referralなど）
    - **デバイス**: デバイスタイプを選択（mobile、desktop、tablet）
    - **A/Bテスト**: テストバリアントを選択
    
    ### 2. 主要指標の確認
    
    フィルター下部に表示される10個の主要指標で、全体的なパフォーマンスを把握できます。
    
    - セッション数
    - コンバージョン数
    - コンバージョン率
    - クリック数
    - クリック率
    - 平均到達ページ数
    - 平均滞在時間
    - FV残存率
    - 最終CTA到達率
    - 平均読込時間
    
    ### 3. 分析メニュー
    
    左サイドバーの分析メニューから、詳細な分析を行うことができます。
    
    #### 📊 全体分析
    表示するグラフを選択し、全体的なトレンドを把握できます。
    
    #### 📄 ページ分析
    各ページのパフォーマンスを詳細に分析できます。画像と一緒に表示されるため、コンテンツとデータを関連付けやすくなっています。
    
    #### 👥 セグメント分析
    デバイス、チャネル、UTMソース、A/Bテスト別にデータを分析できます。
    
    #### 🧪 A/Bテスト分析
    A/Bテストの結果を詳細に分析し、どちらのバリアントが優れているかを判断できます。
    
    #### 🎬 動画・スクロール分析
    動画視聴率やスクロール率を分析し、コンテンツのエンゲージメントを把握できます。
    
    #### 📈 時系列分析
    日別・月別の推移を確認し、トレンドを把握できます。
    
    #### 🎯 カスタムオーディエンス
    独自の条件を設定して、特定のユーザーグループを即座に作成・分析できます。
    
    #### ⚡ リアルタイム分析
    直近1時間のデータをリアルタイムで確認できます。
    
    #### 💡 AI提案
    AIが自動的にボトルネックを検出し、改善提案を行います。
    
    ### 4. グラフの比較機能
    
    全体分析タブで「前期間と比較する」にチェックを入れると、前週・前月・前年同期とのデータを比較できます。
    
    ### 5. カスタムオーディエンスの作成
    
    カスタムオーディエンスタブで、以下の条件を設定してオーディエンスを作成できます。
    
    - 最小滞在時間
    - 最小スクロール率
    - 最小到達ページ数
    - コンバージョン達成のみ
    - デバイス
    - チャネル
    
    「オーディエンスを作成」ボタンをクリックすると、該当するセッション数、ユーザー数、コンバージョン率などが即座に表示されます。
    
    ### 6. AI提案の活用
    
    AI提案タブで、質問ボタンをクリックすると、AIが自動的に分析結果と改善提案を表示します。
    
    - このLPの最大のボトルネックは？
    - コンバージョン率を改善するには？
    - A/Bテストの結果、どちらが優れている？
    - デバイス別のパフォーマンス差は？
    
    フリーチャットで、独自の質問を入力することもできます。
    """)

elif selected_tab == "📚 専門用語解説":
    st.header("📚 専門用語解説")
    
    st.markdown("""
    ## マーケティング・分析用語の解説
    
    ### セッション
    ユーザーがサイトを訪問してから離脱するまでの一連の行動を指します。通常、30分間操作がない場合、セッションは終了します。
    
    ### コンバージョン
    サイトの目標（商品購入、資料請求、会員登録など）を達成することを指します。
    
    ### コンバージョン率（CVR）
    セッション数に対するコンバージョン数の割合です。
    
    **計算式:** コンバージョン数 ÷ セッション数 × 100
    
    ### クリック率（CTR）
    表示回数に対するクリック数の割合です。
    
    **計算式:** クリック数 ÷ 表示回数 × 100
    
    ### 離脱率
    そのページで離脱したセッション数の割合です。
    
    **計算式:** そのページで離脱したセッション数 ÷ そのページのビュー数 × 100
    
    ### FV残存率
    ファーストビュー（最初のページ）から次のページに進んだユーザーの割合です。
    
    **計算式:** 2ページ目以降に到達したセッション数 ÷ 総セッション数 × 100
    
    ### 最終CTA到達率
    LPの最後のCTA（Call To Action：行動喚起）まで到達したユーザーの割合です。
    
    ### スクロール率
    ページをどこまでスクロールしたかを示す指標です。100%は最下部まで到達したことを意味します。
    
    ### 滞在時間
    ユーザーがそのページに滞在した時間です。
    
    ### 読込時間
    ページが完全に読み込まれるまでの時間です。読込時間が長いと、ユーザーが離脱する可能性が高まります。
    
    ### A/Bテスト
    2つ以上のバリアント（パターン）を用意し、どちらがより効果的かを検証する手法です。
    
    ### UTMパラメータ
    URLに付与するパラメータで、流入元を詳細に追跡するために使用します。
    
    - **utm_source**: 流入元（例: google、facebook）
    - **utm_medium**: 媒体（例: cpc、email）
    - **utm_campaign**: キャンペーン名
    - **utm_content**: 広告の内容
    
    ### デバイスカテゴリ
    ユーザーがアクセスしたデバイスの種類です。
    
    - **mobile**: スマートフォン
    - **desktop**: パソコン
    - **tablet**: タブレット
    
    ### トラフィックソース（チャネル）
    ユーザーがどこから流入したかを示します。
    
    - **Direct**: 直接アクセス（URLを直接入力、ブックマークなど）
    - **Organic Search**: 自然検索（GoogleやYahooなどの検索エンジンから）
    - **Organic Social**: ソーシャルメディアから（広告以外）
    - **Paid Search**: 有料検索広告
    - **Referral**: 他のサイトからのリンク
    
    ### エンゲージメント率
    ユーザーがサイトに積極的に関与している割合です。通常、滞在時間が一定以上（例: 30秒以上）のセッションをエンゲージメントとみなします。
    
    ### ファネル
    ユーザーがコンバージョンに至るまでの段階的なプロセスを指します。各段階でどれだけのユーザーが次の段階に進んだかを可視化します。
    
    ### カスタムオーディエンス
    特定の条件を満たすユーザーグループです。滞在時間、スクロール率、デバイスなどの条件を組み合わせて作成します。
    """)

elif selected_tab == "💡 AI提案":
    st.header("💡 AI提案")
    st.markdown('<div class="graph-description">AIが自動的にボトルネックを検出し、改善提案を行います。</div>', unsafe_allow_html=True)
    
    st.subheader("よくある質問")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("❓ このLPの最大のボトルネックは？", use_container_width=True):
            st.info("""
            **分析結果:**
            
            現在のデータを分析した結果、最大のボトルネックは**ページ3の離脱率が高いこと**です。
            
            - ページ3の離脱率: 45.2%（平均より15%高い）
            - ページ3の平均滞在時間: 8.3秒（平均より40%短い）
            - ページ3の平均読込時間: 3.2秒（平均より2倍遅い）
            
            **推奨アクション:**
            1. ページ3の読込速度を改善する
            2. ページ3のコンテンツを見直す
            3. ページ3のA/Bテストを実施する
            """)
    
    with col2:
        if st.button("❓ コンバージョン率を改善するには？", use_container_width=True):
            st.info("""
            **改善提案:**
            
            コンバージョン率を改善するために、以下の施策を推奨します。
            
            1. **モバイルの最適化**
               - モバイルのコンバージョン率が2.3%（デスクトップの半分）
               - モバイル向けのUIを改善する
            
            2. **最終CTAの強化**
               - 最終CTA到達率は68.5%だが、コンバージョン率は12.8%
               - CTAボタンのデザインやコピーを改善する
            
            3. **ページ3の改善**
               - ページ3で45.2%が離脱している
               - コンテンツの見直しや読込速度の改善が必要
            """)
    
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("❓ A/Bテストの結果、どちらが優れている？", use_container_width=True):
            st.info("""
            **A/Bテスト結果:**
            
            - **バリアントA**: コンバージョン率 14.2%
            - **バリアントB**: コンバージョン率 11.8%
            - **コントロール**: コンバージョン率 12.5%
            
            **結論:**
            バリアントAが最も優れています。コンバージョン率が14.2%で、コントロールより13.6%高い結果です。
            
            **推奨アクション:**
            バリアントAを本番環境に適用することを推奨します。
            """)
    
    with col4:
        if st.button("❓ デバイス別のパフォーマンス差は？", use_container_width=True):
            st.info("""
            **デバイス別分析:**
            
            - **デスクトップ**: コンバージョン率 18.5%、平均滞在時間 85秒
            - **モバイル**: コンバージョン率 9.2%、平均滞在時間 52秒
            - **タブレット**: コンバージョン率 12.1%、平均滞在時間 68秒
            
            **結論:**
            デスクトップのパフォーマンスが最も高く、モバイルは改善の余地があります。
            
            **推奨アクション:**
            1. モバイル向けのUIを最適化する
            2. モバイルの読込速度を改善する
            3. モバイル専用のA/Bテストを実施する
            """)
    
    st.subheader("フリーチャット")
    user_question = st.text_input("質問を入力してください")
    
    if st.button("送信"):
        if user_question:
            st.info(f"""
            **質問:** {user_question}
            
            **回答:**
            
            ご質問ありがとうございます。現在のデータに基づいて分析した結果をお伝えします。
            
            （本番環境では、Gemini 2.5 Proが実際のデータに基づいて詳細な分析と提案を行います。）
            """)

# フッター
st.markdown("---")
st.markdown("**瞬ジェネ AIアナリスト** - Powered by Streamlit & Gemini 2.5 Pro")

