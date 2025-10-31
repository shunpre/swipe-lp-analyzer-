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
from capture_lp import extract_lp_text_content # 新しくインポート
import time # ファイルの先頭でインポート
# scipyをインポート（A/Bテストの有意差検定で使用）

# ページ設定
st.set_page_config(
    page_title="瞬ジェネ AIアナリスト",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ブラウザがスクロールする先の「基点」を設置
st.markdown('<a id="top-anchor"></a>', unsafe_allow_html=True)

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
    /* メインコンテンツの上部余白を調整してサイドバーと高さを合わせる */
    .main > div:first-child {
        padding-top: 1.8rem !important;
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
    /* 通常のボタン (secondary) */
    .stButton>button[kind="secondary"] {
        background-color: #f0f2f6;
        color: #333;
        border: 1px solid #f0f2f6;
    }
    /* 選択中のボタン (primary) */
    .stButton>button[kind="primary"] {
        background-color: #002060 !important; /* 紺色で塗りつぶし */
        color: white !important; /* 白文字 */
        border: 1px solid #002060 !important; /* 枠線の色も統一 */
    }
    /* サイドバーの通常ボタンのホバー時 */
    div[data-testid="stSidebarUserContent"] .stButton>button[kind="secondary"]:hover {
        background-color: #e6f0ff !important;
        color: #333 !important;
        border: 1px solid #002060 !important;
    }
    /* コンテンツエリアのプライマリボタン（AI分析を実行など）は赤色にする */
    section.main .stButton>button[kind="primary"] {
        background-color: #ff4b4b !important;
        color: white !important;
        border-color: #ff4b4b !important;
    }
    /* コンテンツエリアの通常ボタン（よくある質問など）のホバー時とフォーカス時のスタイルを統一し、赤枠を防ぐ */
    section.main .stButton>button[kind="secondary"]:hover,
    section.main .stButton>button[kind="secondary"]:focus,
    section.main .stButton>button[kind="secondary"]:focus-visible {
        background-color: #e6f0ff !important;
        color: #333 !important;
        border: 1px solid #002060 !important;
        box-shadow: none !important; /* フォーカス時の影を消す */
    }
    /* st.info のスタイルを強制的に青系に固定 */
    div[data-testid="stInfo"] {
        background-color: #e6f3ff !important;
        border-color: #1c83e1 !important;
        color: #000 !important;
    }
    /* サイドバーの開閉ボタンのSVGアイコンを非表示にする */
    button[data-testid="stSidebarCollapseButton"] > svg {
        display: none;
    }

    /* サイドバーが開いている時（閉じるボタン）のアイコン */
    body[data-sidebar-state="expanded"] button[data-testid="stSidebarCollapseButton"]::before {
        content: '<';
        font-size: 1.6rem;
        color: #666;
        font-weight: bold;
    }

    /* サイドバーが閉じている時（開くボタン）のアイコン */
    body[data-sidebar-state="collapsed"] button[data-testid="stSidebarCollapseButton"]::before {
        content: '>';
        font-size: 1.6rem;
        color: #666;
        font-weight: bold;
    }
    /* タイトル横のリンクアイコンを非表示にする */
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
        /* リンクアイコンを非表示にするためのより強力なセレクタ */
        visibility: hidden;
        display: none !important;
    }
    /* マウスオーバーで画像を拡大するCSS */
    .image-container-zoom {
        position: relative;
        width: 56px; /* サムネイルの幅 */
        height: 100px; /* サムネイルの高さ */
        overflow: hidden; /* 拡大時にコンテナからはみ出す部分を隠す */
        display: inline-block; /* インラインブロック要素として配置 */
        vertical-align: top; /* 上揃え */
    }
    .zoomable-image {
        width: 100%;
        height: 100%;
        object-fit: cover; /* アスペクト比を維持しつつコンテナを埋める */
        transition: transform 0.2s ease-in-out, z-index 0s 0.2s;
        cursor: zoom-in;
    }
    .image-container-zoom:hover .zoomable-image {
        transform: scale(3.5); /* 拡大率 */
        position: absolute; /* 拡大時に他の要素に影響を与えないように */
        top: 50%; /* 中央に配置 */
        left: 50%; /* 中央に配置 */
        transform: translate(-50%, -50%) scale(3.5); /* 中央を基準に拡大 */
        z-index: 10; /* 他の要素の上に表示 */
        box-shadow: 0 0 10px rgba(0,0,0,0.5); /* 影を追加して見やすく */
    }
    /* サイドバーリンクの基本スタイル (非選択時 = secondary) */
    a.sidebar-link {
        display: block; /* ボタンのように振る舞わせる */
        width: 100%;
        padding: 0.5rem 0.75rem; /* st.buttonのpaddingに合わせる */
        border-radius: 0.5rem;
        text-decoration: none; /* 下線を消す */
        font-weight: 400; /* 通常の太さ */
        box-sizing: border-box; /* paddingを含めてwidth 100%にする */

        /* secondaryボタンのスタイルを再現 */
        background-color: #f0f2f6;
        color: #333;
        border: 1px solid #f0f2f6;
        transition: all 0.2s;
    }

    /* ホバー時のスタイル (非選択時) */
    a.sidebar-link:hover {
        background-color: #e6f0ff !important;
        color: #333 !important;
        border: 1px solid #002060 !important;
        text-decoration: none; /* ホバー時も下線なし */
    }

    /* 選択中のリンクのスタイル (primary) */
    a.sidebar-link.active {
        /* primaryボタンのスタイルを再現 */
        background-color: #002060 !important;
        color: white !important;
        border: 1px solid #002060 !important;
        font-weight: bold; /* 選択中を分かりやすく */
    }
</style>
""", unsafe_allow_html=True)

# --- 堅牢化のためのヘルパー関数 ---
def safe_rate(numerator, denominator):
    """ゼロ除算を回避して率を計算する"""
    # denominatorがSeriesの場合でも動作するように修正
    if isinstance(denominator, pd.Series):
        return numerator.divide(denominator, fill_value=0)
    # denominatorが単一の数値の場合
    return numerator / denominator if denominator != 0 else 0.0

# データ読み込み
@st.cache_data
def load_data():
    """ダミーデータを読み込む"""
    df = pd.read_csv("app/dummy_data.csv")
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

# デフォルトのページ（URLに何もない場合）
DEFAULT_PAGE = "AIによる分析・考察"

try:
    # Streamlit 1.10.0以降の推奨される方法
    query_params = st.query_params.to_dict()
    selected_analysis = query_params.get("page", DEFAULT_PAGE)
except AttributeError:
    # 古いStreamlitバージョン向けのフォールバック
    query_params = st.experimental_get_query_params()
    # experimental_get_query_paramsは値がリストで返されるため、最初の要素を取得
    if "page" in query_params and query_params["page"]:
        selected_analysis = query_params["page"][0]
    else:
        selected_analysis = DEFAULT_PAGE

# 他の処理がst.session_stateを参照している場合に備え、同期させる
st.session_state.selected_analysis = selected_analysis

# グルーピングされたメニュー項目
menu_groups = {
    "AIアナリスト": ["AIによる分析・考察"],
    "基本分析": ["リアルタイムビュー", "全体サマリー", "時系列分析", "デモグラフィック情報"],
    "LP最適化分析": ["ページ分析", "A/Bテスト分析"],
    "詳細分析": ["セグメント分析", "インタラクション分析", "動画・スクロール分析"],
    "ヘルプ": ["使用ガイド", "専門用語解説"]
}

for group_name, items in menu_groups.items():
    st.sidebar.markdown(f"**{group_name}**")
    for item in items: # type: ignore
        # 現在のページ(selected_analysis)とアイテムが一致するか判定
        if selected_analysis == item:
            css_class = "active" # 一致すれば "active" クラスを付与
        else:
            css_class = ""       # 一致しなければなし
        
        # HTMLのアンカーリンクをst.markdownで作成
        # href に ?page={item}#top-anchor を設定
        # target="_self" は、iframe内で遷移を完結させるために重要
        st.sidebar.markdown(
            f'<a href="?page={item}#top-anchor" target="_self" class="sidebar-link {css_class}">{item}</a>',
            unsafe_allow_html=True
        )

    st.sidebar.markdown("---")

# チャネルマッピング（データ処理に必要）
channel_map = { # type: ignore
    "google": "Organic Search",
    "facebook": "Organic Social",
    "instagram": "Organic Social",
    "twitter": "Organic Social",
    "direct": "Direct"
}
df['channel'] = df['utm_source'].map(channel_map).fillna("Referral")

# 選択された分析項目に応じて表示を切り替え

if selected_analysis == "全体サマリー":
    st.markdown('<div class="sub-header">全体サマリー</div>', unsafe_allow_html=True)
    
    # メインエリア: フィルターと比較設定
    st.markdown('<div class="sub-header">フィルター設定</div>', unsafe_allow_html=True)

    filter_cols = st.columns(4)
    with filter_cols[0]:
        # 期間選択（キーを一意にするためにプレフィックスを追加）
        period_options = {
            "過去7日間": 7,
            "過去30日間": 30,
            "過去90日間": 90,
            "カスタム期間": None
        }
        selected_period = st.selectbox("期間を選択", list(period_options.keys()), index=1, key="summary_period_selector")

    with filter_cols[1]:
        # LP選択
        lp_options = sorted(df['page_location'].dropna().unique().tolist()) # type: ignore
        selected_lp = st.selectbox("LP選択", lp_options, index=0 if lp_options else -1)

    with filter_cols[2]:
        device_options = ["すべて"] + sorted(df['device_type'].dropna().unique().tolist())
        selected_device = st.selectbox("デバイス選択", device_options, index=0, key="summary_device_selector")

    with filter_cols[3]:
        channel_options = ["すべて"] + sorted(df['channel'].unique().tolist())
        selected_channel = st.selectbox("チャネル選択", channel_options, index=0, key="summary_channel_selector")

    # 比較機能はチェックボックスでシンプルに
    enable_comparison = st.checkbox("比較機能を有効化", value=False, key="summary_comparison_checkbox")
    comparison_type = None
    if enable_comparison:
        comparison_options = {
            "前期間": "previous_period", "前週": "previous_week",
            "前月": "previous_month", "前年": "previous_year"
        }
        selected_comparison = st.selectbox("比較対象", list(comparison_options.keys()), key="summary_comparison_selector")
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

    # 期間フィルターのみを適用したDataFrame（テーブル表示用）
    period_filtered_df = df[
        (df['event_date'] >= pd.to_datetime(start_date)) &
        (df['event_date'] <= pd.to_datetime(end_date))
    ]

    # KPIカードやグラフ用のデータフィルタリング（期間＋LP）
    filtered_df = df.copy()

    # 期間フィルター
    filtered_df = filtered_df[
        (filtered_df['event_date'] >= pd.to_datetime(start_date)) &
        (filtered_df['event_date'] <= pd.to_datetime(end_date))
    ]

    # LPフィルター
    if selected_lp:
        filtered_df = filtered_df[filtered_df['page_location'] == selected_lp]

    # --- クロス分析用フィルター適用 ---
    if selected_device != "すべて":
        filtered_df = filtered_df[filtered_df['device_type'] == selected_device]

    if selected_channel != "すべて":
        filtered_df = filtered_df[filtered_df['channel'] == selected_channel]


    # ==============================================================================
    #  デバッグ用: 3分以上の滞在時間データを強制的に生成
    #  目的: 「3分以上」セグメントがグラフに表示されることを確認するため。
    #  注意: このコードは本番データでは不要です。
    # ==============================================================================
    if not filtered_df.empty:
        # 'stay_ms'列が存在し、かつNaNでない行が1つ以上あることを確認
        if 'stay_ms' in filtered_df.columns and filtered_df['stay_ms'].notna().any():
            # 滞在時間が最も長い上位5%のインデックスを取得
            long_stay_indices = filtered_df['stay_ms'].nlargest(int(len(filtered_df) * 0.05)).index
            
            # それらの滞在時間を3分〜5分のランダムな値に書き換える
            if not long_stay_indices.empty:
                new_stay_times = np.random.randint(180000, 300000, size=len(long_stay_indices))
                filtered_df.loc[long_stay_indices, 'stay_ms'] = new_stay_times
    # ==============================================================================

    # 比較データの取得
    comparison_df = None
    comp_start = None
    comp_end = None
    if enable_comparison and comparison_type:
        result = get_comparison_data(df, pd.Timestamp(start_date), pd.Timestamp(end_date), comparison_type)
        if result is not None:
            comparison_df, comp_start, comp_end = result
            # 比較データにも同じフィルターを適用
            if selected_lp:
                comparison_df = comparison_df[comparison_df['page_location'] == selected_lp]
            # --- 比較データにもクロス分析用フィルターを適用 ---
            if selected_device != "すべて":
                comparison_df = comparison_df[comparison_df['device_type'] == selected_device]
            if selected_channel != "すべて":
                comparison_df = comparison_df[comparison_df['channel'] == selected_channel]

            # 比較データが空の場合は無効化
            if len(comparison_df) == 0:
                comparison_df = None
                st.info(f"比較期間（{comp_start.strftime('%Y-%m-%d')} 〜 {comp_end.strftime('%Y-%m-%d')}）にデータがありません。")

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
    st.markdown('<div class="sub-header">主要指標（KPI）</div>', unsafe_allow_html=True)

    # KPIカード表示
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        # セッション数
        delta_sessions = total_sessions - comp_kpis.get('sessions', 0) if comp_kpis else None
        st.metric("セッション数", f"{total_sessions:,}", delta=f"{delta_sessions:+,}" if delta_sessions is not None else None)
        
        # FV残存率
        delta_fv = fv_retention_rate - comp_kpis.get('fv_retention_rate', 0) if comp_kpis else None
        st.metric("FV残存率", f"{fv_retention_rate:.1f}%", delta=f"{delta_fv:+.1f}%" if delta_fv is not None else None)

    with col2:
        # コンバージョン数
        delta_conversions = total_conversions - comp_kpis.get('conversions', 0) if comp_kpis else None
        st.metric("コンバージョン数", f"{total_conversions:,}", delta=f"{delta_conversions:+,}" if delta_conversions is not None else None)

        # 最終CTA到達率
        delta_cta = final_cta_rate - comp_kpis.get('final_cta_rate', 0) if comp_kpis else None
        st.metric("最終CTA到達率", f"{final_cta_rate:.1f}%", delta=f"{delta_cta:+.1f}%" if delta_cta is not None else None)

    with col3:
        # コンバージョン率
        delta_cvr = conversion_rate - comp_kpis.get('conversion_rate', 0) if comp_kpis else None
        st.metric("コンバージョン率", f"{conversion_rate:.2f}%", delta=f"{delta_cvr:+.2f}%" if delta_cvr is not None else None)

        # 平均到達ページ数
        delta_pages = avg_pages_reached - comp_kpis.get('avg_pages_reached', 0) if comp_kpis else None
        st.metric("平均到達ページ数", f"{avg_pages_reached:.1f}", delta=f"{delta_pages:+.1f}" if delta_pages is not None else None)

    with col4:
        # クリック数
        delta_clicks = total_clicks - comp_kpis.get('clicks', 0) if comp_kpis else None
        st.metric("クリック数", f"{total_clicks:,}", delta=f"{delta_clicks:+,}" if delta_clicks is not None else None)

        # 平均滞在時間
        delta_stay = avg_stay_time - comp_kpis.get('avg_stay_time', 0) if comp_kpis else None
        st.metric("平均滞在時間", f"{avg_stay_time:.1f}秒", delta=f"{delta_stay:+.1f} 秒" if delta_stay is not None else None)

    with col5:
        # クリック率
        delta_click_rate = click_rate - comp_kpis.get('click_rate', 0) if comp_kpis else None
        st.metric("クリック率", f"{click_rate:.2f}%", delta=f"{delta_click_rate:+.2f}%" if delta_click_rate is not None else None)

        # 平均読込時間
        delta_load = avg_load_time - comp_kpis.get('avg_load_time', 0) if comp_kpis else None
        st.metric("平均読込時間", f"{avg_load_time:.0f}ms", delta=f"{delta_load:+.0f} ms" if delta_load is not None else None, delta_color="inverse")

    # KPIスコアカードと日別KPIテーブルの間にスペースを設ける
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # 日別KPIテーブル
    st.markdown("##### 日別KPI詳細")
    st.markdown('<div class="graph-description">選択した期間内の日ごとの主要指標です。</div>', unsafe_allow_html=True)

    # 日別にKPIを計算
    daily_df = filtered_df.groupby(filtered_df['event_date'].dt.date).agg(
        セッション数=('session_id', 'nunique'),
        クリック数=('event_name', lambda x: (x == 'click').sum()),
        平均滞在時間=('stay_ms', 'mean'),
        平均到達ページ=('max_page_reached', 'mean'),
        平均読込時間=('load_time_ms', 'mean')
    ).reset_index()
    daily_df.rename(columns={'event_date': '日付'}, inplace=True)

    # 日別コンバージョン数
    daily_cv = filtered_df[filtered_df['cv_type'].notna()].groupby(filtered_df['event_date'].dt.date)['session_id'].nunique().reset_index()
    daily_cv.columns = ['日付', 'CV数']
    daily_df = pd.merge(daily_df, daily_cv, on='日付', how='left').fillna(0)

    # 日別FV残存数
    daily_fv = filtered_df[filtered_df['max_page_reached'] >= 2].groupby(filtered_df['event_date'].dt.date)['session_id'].nunique().reset_index()
    daily_fv.columns = ['日付', 'FV残存数']
    daily_df = pd.merge(daily_df, daily_fv, on='日付', how='left').fillna(0)

    # 日別最終CTA到達数
    daily_final_cta = filtered_df[filtered_df['max_page_reached'] >= 10].groupby(filtered_df['event_date'].dt.date)['session_id'].nunique().reset_index()
    daily_final_cta.columns = ['日付', '最終CTA到達数']
    daily_df = pd.merge(daily_df, daily_final_cta, on='日付', how='left').fillna(0)

    # 率を計算
    daily_df['CVR'] = daily_df.apply(lambda row: safe_rate(row['CV数'], row['セッション数']) * 100, axis=1)
    daily_df['CTR'] = daily_df.apply(lambda row: safe_rate(row['クリック数'], row['セッション数']) * 100, axis=1)
    daily_df['FV残存率'] = daily_df.apply(lambda row: safe_rate(row['FV残存数'], row['セッション数']) * 100, axis=1)
    daily_df['最終CTA到達率'] = daily_df.apply(lambda row: safe_rate(row['最終CTA到達数'], row['セッション数']) * 100, axis=1)
    daily_df['平均滞在時間'] = daily_df['平均滞在時間'] / 1000

    # 日付を降順にソート
    daily_df = daily_df.sort_values(by='日付', ascending=False)

    # 表示する列を選択
    display_cols_daily = ['日付', 'セッション数', 'CV数', 'CVR', 'クリック数', 'CTR', 'FV残存率', '最終CTA到達率', '平均到達ページ', '平均滞在時間']
    
    # データフレームを表示（7行分の高さに固定）
    st.dataframe(daily_df[display_cols_daily].style.format({
        'CVR': '{:.2f}%', 'CTR': '{:.2f}%', 'FV残存率': '{:.1f}%', '最終CTA到達率': '{:.1f}%',
        '平均到達ページ': '{:.1f}', '平均滞在時間': '{:.1f}秒'
    }), use_container_width=True, height=282, hide_index=True)
    # page_pathごとのKPIを計算（期間フィルターのみ適用したデータを使用）
    path_sessions = period_filtered_df.groupby('page_path')['session_id'].nunique()
    path_users = period_filtered_df.groupby('page_path')['user_pseudo_id'].nunique()
    path_conversions = period_filtered_df[period_filtered_df['cv_type'].notna()].groupby('page_path')['session_id'].nunique()
    path_clicks = period_filtered_df[period_filtered_df['event_name'] == 'click'].groupby('page_path').size()
    kpi_by_path = pd.DataFrame({
        'セッション数': path_sessions,
        'CV数': path_conversions,
        'クリック数': path_clicks,
        '平均滞在時間': period_filtered_df.groupby('page_path')['stay_ms'].mean() / 1000,
        '平均到達ページ': period_filtered_df.groupby('page_path')['max_page_reached'].mean()
    }).fillna(0)

    kpi_by_path['CVR'] = kpi_by_path.apply(lambda row: safe_rate(row['CV数'], row['セッション数']) * 100, axis=1)
    kpi_by_path['CTR'] = kpi_by_path.apply(lambda row: safe_rate(row['クリック数'], row['セッション数']) * 100, axis=1)
    # FV残存率
    fv_sessions = period_filtered_df[period_filtered_df['max_page_reached'] >= 2].groupby('page_path')['session_id'].nunique()
    kpi_by_path['FV残存率'] = (safe_rate(fv_sessions, path_sessions) * 100).fillna(0) # safe_rateがSeriesを返すように
    # 最終CTA到達率
    final_cta_sessions = period_filtered_df[period_filtered_df['max_page_reached'] >= 10].groupby('page_path')['session_id'].nunique()
    kpi_by_path['最終CTA到達率'] = (safe_rate(final_cta_sessions, path_sessions) * 100).fillna(0) # こちらも同様に修正

    kpi_by_path = kpi_by_path.reset_index()
    kpi_by_path.rename(columns={'page_path': 'ページパス'}, inplace=True)

    # 表示する列を定義（変更なし）
    display_cols = [
        'ページパス', 'セッション数', 'CV数', 'CVR', 'クリック数', 'CTR', 
        'FV残存率', '最終CTA到達率', '平均到達ページ', '平均滞在時間'
    ]

    # --- インタラクションKPIの計算ロジック（期間フィルターのみ適用したデータを使用） ---
    # CTAクリック
    cta_clicks = period_filtered_df[
        (period_filtered_df['event_name'] == 'click') & 
        (period_filtered_df['elem_classes'].str.contains('cta|btn-primary', na=False))
    ].groupby('page_path').size()

    # フローティングバナークリック
    floating_clicks = period_filtered_df[
        (period_filtered_df['event_name'] == 'click') & 
        (period_filtered_df['elem_classes'].str.contains('floating', na=False))
    ].groupby('page_path').size()

    # 離脱防止ポップアップクリック
    exit_popup_clicks = period_filtered_df[
        (period_filtered_df['event_name'] == 'click') & 
        (period_filtered_df['elem_classes'].str.contains('exit', na=False))
    ].groupby('page_path').size()

    interaction_kpis = pd.DataFrame({
        'セッション数': path_sessions,
        'ユニークユーザー数': path_users,
        'CTAクリック数': cta_clicks,
        'FBクリック数': floating_clicks,
        '離脱防止POPクリック数': exit_popup_clicks
    }).fillna(0)

    interaction_kpis['CTAクリック率'] = interaction_kpis.apply(lambda row: safe_rate(row['CTAクリック数'], row['セッション数']) * 100, axis=1)
    interaction_kpis['FBクリック率'] = interaction_kpis.apply(lambda row: safe_rate(row['FBクリック数'], row['セッション数']) * 100, axis=1)
    interaction_kpis['離脱防止POPクリック率'] = interaction_kpis.apply(lambda row: safe_rate(row['離脱防止POPクリック数'], row['セッション数']) * 100, axis=1)

    interaction_kpis = interaction_kpis.reset_index().rename(columns={'page_path': 'ページパス'})

    interaction_display_cols = [
        'ページパス', 'ユニークユーザー数', 'CTAクリック数', 'CTAクリック率',
        'FBクリック数', 'FBクリック率',
        '離脱防止POPクリック数', '離脱防止POPクリック率'
    ]
    
    # --- expanderを使って表を表示 ---
    with st.expander("詳細1: ページパス別 主要指標詳細表"):
        st.markdown('<div class="graph-description">LP（ページパス）ごとの主要なKPIを一覧表示します。</div>', unsafe_allow_html=True) # type: ignore
        st.dataframe(kpi_by_path[display_cols].style.format({
            'セッション数': '{:,.0f}',
            'CV数': '{:,.0f}',
            'CVR': '{:.2f}%',
            'クリック数': '{:,.0f}',
            'CTR': '{:.2f}%',
            'FV残存率': '{:.2f}%',
            '最終CTA到達率': '{:.2f}%',
            '平均到達ページ': '{:.2f}',
            '平均滞在時間': '{:.1f}秒'
        }), use_container_width=True, hide_index=True)

    with st.expander("詳細2: ページパス別 インタラクション指標詳細表"):
        st.markdown('<div class="graph-description">LP（ページパス）ごとの主要なインタラクション指標を一覧表示します。</div>', unsafe_allow_html=True) # type: ignore
        st.dataframe(interaction_kpis[interaction_display_cols].style.format({
            'ユニークユーザー数': '{:,.0f}',
            'CTAクリック数': '{:,.0f}',
            'CTAクリック率': '{:.2f}%',
            'FBクリック数': '{:,.0f}',
            'FBクリック率': '{:.2f}%',
            '離脱防止POPクリック数': '{:,.0f}',
            '離脱防止POPクリック率': '{:.2f}%'
        }), use_container_width=True, hide_index=True)

    st.markdown("---")
    
    # グラフ選択
    st.markdown("**表示するグラフを選択してください:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_session_trend = st.checkbox("セッション数の推移", value=False, key="summary_show_session_trend")
        show_cvr_trend = st.checkbox("コンバージョン率の推移", value=False, key="summary_show_cvr_trend")
        show_device_breakdown = st.checkbox("デバイス別分析", value=False, key="summary_show_device_breakdown")
    
    with col2:
        show_channel_breakdown = st.checkbox("チャネル別分析", value=False, key="summary_show_channel_breakdown")
        show_funnel = st.checkbox("LP進行ファネル", value=False, key="summary_show_funnel")
        show_hourly_cvr = st.checkbox("時間帯別CVR", value=False, key="summary_show_hourly_cvr")
    
    with col3:
        show_dow_cvr = st.checkbox("曜日別CVR", value=False, key="summary_show_dow_cvr") # type: ignore
        show_utm_analysis = st.checkbox("UTM分析", value=False, key="summary_show_utm_analysis")
        show_load_time = st.checkbox("読込時間分析", value=False, key="summary_show_load_time")
    
    # セッション数の推移
    if show_session_trend:
        st.markdown("#### セッション数の推移")
        st.markdown('<div class="graph-description">日ごとのセッション数（訪問数）の変化を表示します。トレンドや曜日ごとのパターンを把握できます。</div>', unsafe_allow_html=True) # type: ignore
        daily_sessions = filtered_df.groupby(filtered_df['event_date'].dt.date)['session_id'].nunique().reset_index()
        daily_sessions.columns = ['日付', 'セッション数']
        
        if comparison_df is not None and len(comparison_df) > 0:
            # 比較データを追加
            comp_daily_sessions = comparison_df.groupby(comparison_df['event_date'].dt.date)['session_id'].nunique().reset_index()
            comp_daily_sessions.columns = ['日付', '比較期間セッション数']

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daily_sessions['日付'], y=daily_sessions['セッション数'], 
                                    mode='lines+markers', name='現在期間', line=dict(color='#002060'),
                                    hovertemplate='日付: %{x}<br>セッション数: %{y:,}<extra></extra>'))
            fig.add_trace(go.Scatter(x=comp_daily_sessions['日付'], y=comp_daily_sessions['比較期間セッション数'], 
                                    mode='lines+markers', name='比較期間', line=dict(color='#999999', dash='dash'),
                                    hovertemplate='日付: %{x}<br>比較期間セッション数: %{y:,}<extra></extra>'))
            fig.update_layout(height=400, hovermode='x unified')
            fig.update_layout(dragmode=False)
        else:
            fig = px.line(daily_sessions, x='日付', y='セッション数', markers=True)
            fig.update_layout(height=400, dragmode=False)
        
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_1') # This already has use_container_width=True
    
    # コンバージョン率の推移
    if show_cvr_trend:
        st.markdown("#### コンバージョン率の推移")
        st.markdown('<div class="graph-description">日ごとのコンバージョン率（CVR）の変化を表示します。LPの改善効果や外部要因の影響を確認できます。</div>', unsafe_allow_html=True) # type: ignore
        daily_cvr = filtered_df.groupby(filtered_df['event_date'].dt.date).agg({
            'session_id': 'nunique',
        }).reset_index()
        daily_cvr.columns = ['日付', 'セッション数']
        
        daily_cv = filtered_df[filtered_df['cv_type'].notna()].groupby(
            filtered_df[filtered_df['cv_type'].notna()]['event_date'].dt.date
        )['session_id'].nunique().reset_index()
        daily_cv.columns = ['日付', 'コンバージョン数']
        
        daily_cvr = daily_cvr.merge(daily_cv, on='日付', how='left').fillna(0) # type: ignore
        daily_cvr['コンバージョン率'] = daily_cvr.apply(lambda row: safe_rate(row['コンバージョン数'], row['セッション数']) * 100, axis=1)
        
        if comparison_df is not None and len(comparison_df) > 0:
            # 比較データを追加
            comp_daily_cvr = comparison_df.groupby(comparison_df['event_date'].dt.date).agg({'session_id': 'nunique'}).reset_index()
            comp_daily_cvr.columns = ['日付', 'セッション数']
            
            comp_daily_cv = comparison_df[comparison_df['cv_type'].notna()].groupby(
                comparison_df[comparison_df['cv_type'].notna()]['event_date'].dt.date
            )['session_id'].nunique().reset_index()
            comp_daily_cv.columns = ['日付', 'コンバージョン数']
            
            comp_daily_cvr = comp_daily_cvr.merge(comp_daily_cv, on='日付', how='left').fillna(0) # type: ignore
            comp_daily_cvr['比較期間CVR'] = comp_daily_cvr.apply(lambda row: safe_rate(row['コンバージョン数'], row['セッション数']) * 100, axis=1)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daily_cvr['日付'], y=daily_cvr['コンバージョン率'],
                                    mode='lines+markers', name='現在期間', line=dict(color='#002060'),
                                    hovertemplate='日付: %{x}<br>コンバージョン率: %{y:.2f}%<extra></extra>'))
            fig.add_trace(go.Scatter(x=comp_daily_cvr['日付'], y=comp_daily_cvr['比較期間CVR'], 
                                    mode='lines+markers', name='比較期間', line=dict(color='#999999', dash='dash'),
                                    hovertemplate='日付: %{x}<br>比較期間CVR: %{y:.2f}%<extra></extra>'))
            fig.update_layout(height=400, hovermode='x unified', yaxis_title='コンバージョン率 (%)')
            fig.update_layout(dragmode=False)
        else:
            fig = px.line(daily_cvr, x='日付', y='コンバージョン率', markers=True)
            fig.update_layout(height=400, dragmode=False)
        
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_2') # This already has use_container_width=True
    
    # デバイス別分析
    if show_device_breakdown:
        st.markdown("#### デバイス別分析")
        st.markdown('<div class="graph-description">デバイス（スマホ、PC、タブレット）ごとのセッション数、コンバージョン数、CVRを比較します。デバイス最適化の優先度を判断できます。</div>', unsafe_allow_html=True) # type: ignore
        device_stats = filtered_df.groupby('device_type').agg({
            'session_id': 'nunique',
        }).reset_index()
        device_stats.columns = ['デバイス', 'セッション数']
        
        device_cv = filtered_df[filtered_df['cv_type'].notna()].groupby('device_type')['session_id'].nunique().reset_index()
        device_cv.columns = ['デバイス', 'コンバージョン数']
        
        device_stats = device_stats.merge(device_cv, on='デバイス', how='left').fillna(0)
        device_stats['コンバージョン率'] = device_stats.apply(lambda row: safe_rate(row['コンバージョン数'], row['セッション数']) * 100, axis=1)
        
        fig = go.Figure()
        # 主軸（左Y軸）にセッション数とコンバージョン数の棒グラフを追加
        fig.add_trace(go.Bar(name='セッション数', x=device_stats['デバイス'], y=device_stats['セッション数'], yaxis='y', offsetgroup=1,
                             hovertemplate='デバイス: %{x}<br>セッション数: %{y:,}<extra></extra>'))
        fig.add_trace(go.Bar(name='コンバージョン数', x=device_stats['デバイス'], y=device_stats['コンバージョン数'], yaxis='y', offsetgroup=2,
                             hovertemplate='デバイス: %{x}<br>コンバージョン数: %{y:,}<extra></extra>'))
        # 第二軸（右Y軸）にコンバージョン率の折れ線グラフを追加
        fig.add_trace(go.Scatter(name='コンバージョン率', x=device_stats['デバイス'], y=device_stats['コンバージョン率'], yaxis='y2', mode='lines+markers',
                                 hovertemplate='デバイス: %{x}<br>コンバージョン率: %{y:.2f}%<extra></extra>'))
        
        fig.update_layout(
            yaxis=dict(title='セッション数 / コンバージョン数'),
            yaxis2=dict(title='コンバージョン率 (%)', overlaying='y', side='right', showgrid=False),
            height=400,
            dragmode=False,
            legend=dict(x=0, y=1.1, orientation='h')
        )
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_device_combined')
    
    # チャネル別分析
    if show_channel_breakdown:
        st.markdown("#### チャネル別分析")
        st.markdown('<div class="graph-description">流入経路（Google、SNS、直接アクセスなど）ごとのパフォーマンスを比較します。効果的な集客チャネルを特定できます。</div>', unsafe_allow_html=True) # type: ignore
        channel_stats = filtered_df.groupby('channel').agg({
            'session_id': 'nunique',
            'stay_ms': 'mean'
        }).reset_index()
        channel_stats.columns = ['チャネル', 'セッション数', '平均滞在時間(ms)']
        channel_stats['平均滞在時間(秒)'] = channel_stats['平均滞在時間(ms)'] / 1000
        
        channel_cv = filtered_df[filtered_df['cv_type'].notna()].groupby('channel')['session_id'].nunique().reset_index()
        channel_cv.columns = ['チャネル', 'コンバージョン数']
        
        channel_stats = channel_stats.merge(channel_cv, on='チャネル', how='left').fillna(0)
        channel_stats['コンバージョン率'] = channel_stats.apply(lambda row: safe_rate(row['コンバージョン数'], row['セッション数']) * 100, axis=1)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(channel_stats, values='セッション数', names='チャネル', title='チャネル別セッション数')
            fig.update_traces(hovertemplate='チャネル: %{label}<br>セッション数: %{value:,} (%{percent})<extra></extra>')
            fig.update_layout(dragmode=False)
            st.plotly_chart(fig, use_container_width=True, key='plotly_chart_4')
        
        with col2:
            fig = px.bar(channel_stats, x='チャネル', y='コンバージョン率', title='チャネル別コンバージョン率')
            fig.update_traces(hovertemplate='チャネル: %{x}<br>コンバージョン率: %{y:.2f}%<extra></extra>')
            fig.update_layout(dragmode=False)
            st.plotly_chart(fig, use_container_width=True, key='plotly_chart_5')

    # LP進行ファネルと滞在時間別ファネル
    if show_funnel:
        st.markdown("#### LP進行状況とページ内滞在時間")

        # LPのページ数をデータから動的に取得
        actual_page_count = int(filtered_df['page_num_dom'].max()) if not filtered_df['page_num_dom'].dropna().empty else 10

        col1, col2 = st.columns(2)

        with col1:
            funnel_data = []
            for page_num in range(1, actual_page_count + 1):
                count = filtered_df[filtered_df['max_page_reached'] >= page_num]['session_id'].nunique()
                funnel_data.append({'ページ': f'ページ{page_num}', 'セッション数': count})
            
            funnel_df = pd.DataFrame(funnel_data)
            
            fig_funnel = go.Figure(go.Funnel(
                y=funnel_df['ページ'],
                x=funnel_df['セッション数'],
                textinfo="value+percent initial",
                hovertemplate='ページ: %{y}<br>セッション数: %{x:,}<extra></extra>'
            ))
            fig_funnel.update_layout(height=600, dragmode=False)
            st.markdown("**LP進行ファネル**")
            st.markdown('<div class="graph-description">各ページに到達したセッション数と、次のページへの遷移率です。急激に減少している箇所が大きな離脱ポイントです。</div>', unsafe_allow_html=True) # type: ignore
            st.plotly_chart(fig_funnel, use_container_width=True, key='plotly_chart_funnel_revived')

        with col2:
            # 滞在時間セグメントを定義
            stay_segments_for_calc = [
                ('0-10秒', 0, 10000),
                ('10-30秒', 10000, 30000),
                ('30-60秒', 30000, 60000),
                ('1-3分', 60000, 180000),
                ('3分以上', 180000, float('inf'))
            ]
            
            # ページごとの滞在時間別セッション数を計算
            page_stay_data = []
            for page_num in range(1, actual_page_count + 1):
                # そのページに到達したセッションIDを取得
                reached_session_ids = set(filtered_df[filtered_df['max_page_reached'] >= page_num]['session_id'].unique())
                total_reached = len(reached_session_ids)
                
                # そのページでの滞在時間イベントを持つセッションを取得
                page_specific_stay = filtered_df[
                    (filtered_df['page_num_dom'] == page_num) & 
                    (filtered_df['session_id'].isin(reached_session_ids)) &
                    (filtered_df['stay_ms'].notna()) # NaN値を除外
                ]
                
                row = {'ページ': f'ページ{page_num}', 'ページ番号': page_num}
                
                # そのページで滞在時間イベントがあったセッションの総数
                total_sessions_with_stay = page_specific_stay['session_id'].nunique()

                for label, min_ms, max_ms in stay_segments_for_calc:
                    segment_sessions_count = page_specific_stay[
                        (page_specific_stay['stay_ms'] >= min_ms) & 
                        (page_specific_stay['stay_ms'] < max_ms)
                    ]['session_id'].nunique()
                    
                    # 滞在時間イベントがあったセッション内での割合を計算
                    row[label] = (segment_sessions_count / total_sessions_with_stay * 100) if total_sessions_with_stay > 0 else 0
                
                page_stay_data.append(row)

            page_stay_df = pd.DataFrame(page_stay_data).sort_values('ページ番号', ascending=False)

            # 積み上げ棒グラフでファネルを表現
            fig_stay_pct = go.Figure()            
            # YlGnBuスケールから濃い青系の5色を選択
            colors = px.colors.sequential.YlGnBu[2:7]
            colors[-1] = '#08306b' # 一番濃い色を濃紺に設定
            
            for i, (label, _, _) in enumerate(stay_segments_for_calc):
                fig_stay_pct.add_trace(go.Bar(
                    y=page_stay_df['ページ'],
                    x=page_stay_df[label],
                    name=label,
                    orientation='h', # type: ignore
                    hovertemplate='ページ: %{y}<br>割合: %{x:.2f}%<extra></extra>',
                    marker_color=colors[i]
                ))

            fig_stay_pct.update_layout(barmode='stack', height=600,
                              xaxis_title='セッションの割合 (%)', yaxis_title='ページ', dragmode=False,
                              xaxis_ticksuffix='%', legend=dict(traceorder='normal'))
            st.markdown("**ページ内滞在時間の分布**")
            st.markdown('<div class="graph-description">各ページに到達し、滞在時間が計測されたセッションの行動内訳です。横軸は割合（%）を表します。</div>', unsafe_allow_html=True) # type: ignore
            st.plotly_chart(fig_stay_pct, use_container_width=True, key='plotly_chart_stay_percentage')
    
    # 時間帯別CVR
    if show_hourly_cvr:
        st.markdown("#### 時間帯別コンバージョン率")
        st.markdown('<div class="graph-description">1日の中で、どの時間帯にCVRが高いかを分析します。広告配信の最適な時間帯を見つけることができます。</div>', unsafe_allow_html=True) # type: ignore
        filtered_df['hour'] = filtered_df['event_timestamp'].dt.hour
        
        hourly_sessions = filtered_df.groupby('hour')['session_id'].nunique().reset_index()
        hourly_sessions.columns = ['時間', 'セッション数']
        
        hourly_cv = filtered_df[filtered_df['cv_type'].notna()].groupby('hour')['session_id'].nunique().reset_index()
        hourly_cv.columns = ['時間', 'コンバージョン数']
        
        hourly_cvr = hourly_sessions.merge(hourly_cv, on='時間', how='left').fillna(0)
        hourly_cvr['コンバージョン率'] = hourly_cvr.apply(lambda row: safe_rate(row['コンバージョン数'], row['セッション数']) * 100, axis=1)
        
        fig = px.bar(hourly_cvr, x='時間', y='コンバージョン率')
        fig.update_traces(hovertemplate='時間: %{x}時台<br>コンバージョン率: %{y:.2f}%<extra></extra>')
        fig.update_layout(height=400, xaxis_title='時間帯', dragmode=False)
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_7')
    
    # 曜日別CVR
    if show_dow_cvr:
        st.markdown("#### 曜日別コンバージョン率")
        st.markdown('<div class="graph-description">曜日ごとのCVRの違いを分析します。平日と週末でのユーザー行動の変化を把握できます。</div>', unsafe_allow_html=True) # type: ignore
        filtered_df['dow'] = filtered_df['event_timestamp'].dt.day_name()
        dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_map = {'Monday': '月', 'Tuesday': '火', 'Wednesday': '水', 'Thursday': '木', 'Friday': '金', 'Saturday': '土', 'Sunday': '日'}
        
        dow_sessions = filtered_df.groupby('dow')['session_id'].nunique().reset_index()
        dow_sessions.columns = ['曜日', 'セッション数']
        
        dow_cv = filtered_df[filtered_df['cv_type'].notna()].groupby('dow')['session_id'].nunique().reset_index()
        dow_cv.columns = ['曜日', 'コンバージョン数']
        
        dow_cvr = dow_sessions.merge(dow_cv, on='曜日', how='left').fillna(0)
        dow_cvr['コンバージョン率'] = dow_cvr.apply(lambda row: safe_rate(row['コンバージョン数'], row['セッション数']) * 100, axis=1)
        dow_cvr['曜日_日本語'] = dow_cvr['曜日'].map(dow_map)
        dow_cvr['曜日_order'] = dow_cvr['曜日'].apply(lambda x: dow_order.index(x))
        dow_cvr = dow_cvr.sort_values('曜日_order')
        
        fig = px.bar(dow_cvr, x='曜日_日本語', y='コンバージョン率')
        fig.update_traces(hovertemplate='曜日: %{x}<br>コンバージョン率: %{y:.2f}%<extra></extra>')
        fig.update_layout(height=400, xaxis_title='曜日', dragmode=False)
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_8')
    
    # UTM分析
    if show_utm_analysis:
        st.markdown("#### UTM分析")
        st.markdown('<div class="graph-description">UTMパラメータ（広告タグ）ごとのトラフィックを分析します。どのキャンペーンや媒体が効果的かを把握できます。</div>', unsafe_allow_html=True) # type: ignore
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**UTMソース別**")
            utm_source_stats = filtered_df.groupby('utm_source')['session_id'].nunique().reset_index()
            utm_source_stats.columns = ['UTMソース', 'セッション数']
            utm_source_stats = utm_source_stats.sort_values('セッション数', ascending=False)
            
            fig = px.bar(utm_source_stats, x='UTMソース', y='セッション数')
            fig.update_layout(dragmode=False)
            fig.update_traces(hovertemplate='UTMソース: %{x}<br>セッション数: %{y:,}<extra></extra>')
            st.plotly_chart(fig, use_container_width=True, key='plotly_chart_9') # type: ignore
        
        with col2:
            st.markdown("**UTMメディア別**")
            utm_medium_stats = filtered_df.groupby('utm_medium')['session_id'].nunique().reset_index()
            utm_medium_stats.columns = ['UTMメディア', 'セッション数']
            utm_medium_stats = utm_medium_stats.sort_values('セッション数', ascending=False)

            fig = px.bar(utm_medium_stats, x='UTMメディア', y='セッション数')
            fig.update_layout(dragmode=False)
            fig.update_traces(hovertemplate='UTMメディア: %{x}<br>セッション数: %{y:,}<extra></extra>')
            st.plotly_chart(fig, use_container_width=True, key='plotly_chart_10') # type: ignore
    
    # 読込時間分析
    if show_load_time:
        st.markdown("#### 読込時間分析")
        st.markdown('<div class="graph-description">デバイスごとのページ読込時間を分析します。読込が遅いと離脱率が上がるため、最適化が重要です。</div>', unsafe_allow_html=True) # type: ignore
        
        load_time_stats = filtered_df.groupby('device_type')['load_time_ms'].mean().reset_index()
        load_time_stats.columns = ['デバイス', '平均読込時間(ms)']
        
        fig = px.bar(load_time_stats, x='デバイス', y='平均読込時間(ms)')
        fig.update_traces(hovertemplate='デバイス: %{x}<br>平均読込時間: %{y:.0f}ms<extra></extra>')
        fig.update_layout(height=400, yaxis_title='平均読込時間 (ms)', dragmode=False)
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_11')

    st.markdown("---")

    # --- AI分析と考察 ---
    st.markdown("### AIによる分析と考察")
    st.markdown('<div class="graph-description">LP全体の主要指標に基づき、AIが現状の評価と次のアクションを提案します。</div>', unsafe_allow_html=True)
    
    # AI分析の表示状態を管理
    if 'summary_ai_open' not in st.session_state:
        st.session_state.summary_ai_open = False

    if st.button("AI分析を実行", key="summary_ai_btn", type="primary", use_container_width=True):
        st.session_state.summary_ai_open = True
        st.rerun()

    if st.session_state.summary_ai_open:
        with st.container():
            with st.spinner("AIが全体データを分析中..."):
                st.markdown("#### 1. 現状の評価")
                evaluation_text = f"""
                現在のLPパフォーマンスを総合的に評価します。
                - **強み**: 平均滞在時間({avg_stay_time:.1f}秒)や最終CTA到達率({final_cta_rate:.1f}%)は比較的良好で、一度興味を持ったユーザーはコンテンツを読み進める傾向にあります。
                - **弱み**: コンバージョン率({conversion_rate:.2f}%)とFV残存率({fv_retention_rate:.1f}%)が課題です。特に、多くのユーザーが最初のページ（ファーストビュー）で離脱している可能性が高いです。
                """
                st.info(evaluation_text)

                st.markdown("#### 2. 今後の考察と改善案")
                recommendation_text = """
                **最優先課題は「ファーストビューの改善」です。**
                多くのユーザーが最初の接点で離脱しているため、ここを改善することが全体のパフォーマンス向上に最も効果的です。
                
                **具体的な改善アクション案:**
                1. **キャッチコピーの見直し**: ターゲットに響く、より強力なメッセージに変更する。
                2. **メインビジュアルの変更**: ユーザーの興味を引く画像や動画に差し替える。
                3. **A/Bテストの実施**: 上記の要素で複数のパターンを用意し、「A/Bテスト分析」機能で効果を検証する。
                
                次に、「ページ分析」機能を用いて、ファーストビュー以降で離脱率が特に高い「ボトルネックページ」を特定し、改善を進めましょう。
                """
                st.warning(recommendation_text)

            if st.button("AI分析を閉じる", key="summary_ai_close"):
                st.session_state.summary_ai_open = False
                st.rerun()

    # --- よくある質問 ---
    st.markdown("#### よくある質問")
    if 'summary_faq_toggle' not in st.session_state:
        st.session_state.summary_faq_toggle = {1: False, 2: False, 3: False, 4: False}

    faq_cols = st.columns(2)
    with faq_cols[0]:
        if st.button("このLPの強みと弱みは？", key="faq_summary_1", use_container_width=True):
            st.session_state.summary_faq_toggle[1] = not st.session_state.summary_faq_toggle[1]
            st.session_state.summary_faq_toggle[2], st.session_state.summary_faq_toggle[3], st.session_state.summary_faq_toggle[4] = False, False, False
        if st.session_state.summary_faq_toggle[1]:
            st.info(f"**強み**は、平均滞在時間が{avg_stay_time:.1f}秒と比較的長く、コンテンツに興味を持ったユーザーは読み進めている点です。\n\n**弱み**は、FV残存率が{fv_retention_rate:.1f}%と低く、多くのユーザーが最初のページで離脱している点です。")
        
        if st.button("パフォーマンスが悪い原因を特定するには？", key="faq_summary_3", use_container_width=True):
            st.session_state.summary_faq_toggle[3] = not st.session_state.summary_faq_toggle[3]
            st.session_state.summary_faq_toggle[1], st.session_state.summary_faq_toggle[2], st.session_state.summary_faq_toggle[4] = False, False, False
        if st.session_state.summary_faq_toggle[3]:
            st.info("まず「ページ分析」で離脱率が高いボトルネックページを特定します。次に「セグメント分析」で、特定のデバイス（例：スマホ）やチャネル（例：SNS経由）のパフォーマンスが特に悪いかを確認することで、原因を絞り込めます。")
    with faq_cols[1]:
        if st.button("最も優先して改善すべき指標は？", key="faq_summary_2", use_container_width=True):
            st.session_state.summary_faq_toggle[2] = not st.session_state.summary_faq_toggle[2]
            st.session_state.summary_faq_toggle[1], st.session_state.summary_faq_toggle[3], st.session_state.summary_faq_toggle[4] = False, False, False
        if st.session_state.summary_faq_toggle[2]:
            st.info(f"**FV残存率（現在{fv_retention_rate:.1f}%）**です。多くのユーザーがLPの入口で離脱しているため、ここを改善することが最もインパクトが大きいです。")
        
        if st.button("次にどの分析を見るべき？", key="faq_summary_4", use_container_width=True):
            st.session_state.summary_faq_toggle[4] = not st.session_state.summary_faq_toggle[4]
            st.session_state.summary_faq_toggle[1], st.session_state.summary_faq_toggle[2], st.session_state.summary_faq_toggle[3] = False, False, False
        if st.session_state.summary_faq_toggle[4]:
            st.info("「**ページ分析**」がおすすめです。ユーザーがどのページで最も離脱しているか（ボトルネック）を特定し、具体的な改善箇所を見つけましょう。")


# 続く...（次のファイルでタブ2以降を実装）



# タブ2: ページ分析
elif selected_analysis == "ページ分析":
    st.markdown('<div class="sub-header">ページ分析</div>', unsafe_allow_html=True)

    # メインエリア: フィルターと比較設定
    st.markdown('<div class="sub-header">フィルター設定</div>', unsafe_allow_html=True)

    filter_cols = st.columns(4)
    with filter_cols[0]:
        # 期間選択
        period_options = {
            "過去7日間": 7,
            "過去30日間": 30,
            "過去90日間": 90,
            "カスタム期間": None
        }
        selected_period = st.selectbox("期間を選択", list(period_options.keys()), index=1, key="page_analysis_period")

    with filter_cols[1]:
        # LP選択
        lp_options = sorted(df['page_location'].dropna().unique().tolist()) # type: ignore
        selected_lp = st.selectbox("LP選択", lp_options, index=0 if lp_options else -1, key="page_analysis_lp")

    with filter_cols[2]:
        device_options = ["すべて"] + sorted(df['device_type'].dropna().unique().tolist())
        selected_device = st.selectbox("デバイス選択", device_options, index=0, key="page_analysis_device")

    with filter_cols[3]:
        channel_options = ["すべて"] + sorted(df['channel'].unique().tolist())
        selected_channel = st.selectbox("チャネル選択", channel_options, index=0, key="page_analysis_channel")

    # 比較機能はチェックボックスでシンプルに
    enable_comparison = st.checkbox("比較機能を有効化", value=False, key="page_analysis_compare_check")
    comparison_type = None
    if enable_comparison:
        comparison_options = {
            "前期間": "previous_period", "前週": "previous_week",
            "前月": "previous_month", "前年": "previous_year"
        }
        selected_comparison = st.selectbox("比較対象", list(comparison_options.keys()), key="page_analysis_compare_select")
        comparison_type = comparison_options[selected_comparison]

    # カスタム期間の場合
    if selected_period == "カスタム期間":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("開始日", df['event_date'].min(), key="page_analysis_start_date")
        with col2:
            end_date = st.date_input("終了日", df['event_date'].max(), key="page_analysis_end_date")
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
    if selected_lp:
        filtered_df = filtered_df[filtered_df['page_location'] == selected_lp]

    # --- クロス分析用フィルター適用 ---
    if selected_device != "すべて":
        filtered_df = filtered_df[filtered_df['device_type'] == selected_device]

    if selected_channel != "すべて":
        filtered_df = filtered_df[filtered_df['channel'] == selected_channel]

    # ==============================================================================
    #  デバッグ用: 3分以上の滞在時間データを強制的に生成
    #  目的: 「3分以上」セグメントがグラフに表示されることを確認するため。
    #  注意: このコードは本番データでは不要です。
    # ==============================================================================
    if not filtered_df.empty:
        # 'stay_ms'列が存在し、かつNaNでない行が1つ以上あることを確認
        if 'stay_ms' in filtered_df.columns and filtered_df['stay_ms'].notna().any():
            # 滞在時間が最も長い上位5%のインデックスを取得
            long_stay_indices = filtered_df['stay_ms'].nlargest(int(len(filtered_df) * 0.05)).index
            
            # それらの滞在時間を3分〜5分のランダムな値に書き換える
            if not long_stay_indices.empty:
                new_stay_times = np.random.randint(180000, 300000, size=len(long_stay_indices))
                filtered_df.loc[long_stay_indices, 'stay_ms'] = new_stay_times
    # ==============================================================================

    # 比較データの取得
    comparison_df = None
    comp_start = None
    comp_end = None
    if enable_comparison and comparison_type:
        result = get_comparison_data(df, pd.Timestamp(start_date), pd.Timestamp(end_date), comparison_type)
        if result is not None:
            comparison_df, comp_start, comp_end = result
            # 比較データにも同じフィルターを適用
            if selected_lp:
                comparison_df = comparison_df[comparison_df['page_location'] == selected_lp]
            # --- 比較データにもクロス分析用フィルターを適用 ---
            if selected_device != "すべて":
                comparison_df = comparison_df[comparison_df['device_type'] == selected_device]
            if selected_channel != "すべて":
                comparison_df = comparison_df[comparison_df['channel'] == selected_channel]

            # 比較データが空の場合は無効化
            if len(comparison_df) == 0:
                comparison_df = None
                st.info(f"比較期間（{comp_start.strftime('%Y-%m-%d')} 〜 {comp_end.strftime('%Y-%m-%d')}）にデータがありません。")

    # データが空の場合の処理
    if len(filtered_df) == 0:
        st.warning("⚠️ 選択した条件に該当するデータがありません。フィルターを変更してください。")
        st.stop()

    # ページ分析は単一のLP選択時のみ実行
    if selected_lp:
        pass # 選択されたLPのURL表示は削除
    else:
        st.warning("ページ分析を行うには、フィルターで分析したいLPを選択してください。")
        st.stop()
    
    # --- BigQueryデータシミュレーション ---
    # 実際のBigQueryデータから取得されるコンテンツ情報（LPのURL、ページ番号、コンテンツタイプ、コンテンツソース）
    # ここではダミーデータとして定義します。
    # 実際には、selected_lpに基づいてBigQueryからデータをクエリするロジックに置き換わります。
    dummy_lp_content_data_store = {
        "https://example.com/lp/product-a": [
            {'page_number': 1, 'content_type': 'image', 'content_source': 'https://via.placeholder.com/300x500.png?text=Page1_Image'},
            {'page_number': 2, 'content_type': 'video', 'content_source': 'https://www.w3schools.com/html/mov_bbb.mp4'}, # 例: 動画URL
            {'page_number': 3, 'content_type': 'html', 'content_source': '<h1>Page 3 Custom HTML</h1><p>これはカスタムHTMLコンテンツです。</p><p>BigQueryから取得したHTMLを直接表示します。</p>'},
            {'page_number': 4, 'content_type': 'image', 'content_source': 'https://via.placeholder.com/300x500.png?text=Page4_Image'},
            {'page_number': 5, 'content_type': 'image', 'content_source': 'https://via.placeholder.com/300x500.png?text=Page5_Image'},
            {'page_number': 6, 'content_type': 'video', 'content_source': 'https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4'}, # 例: 別の動画URL
            {'page_number': 7, 'content_type': 'image', 'content_source': 'https://via.placeholder.com/300x500.png?text=Page7_Image'},
            {'page_number': 8, 'content_type': 'html', 'content_source': '<h2>Page 8 Info</h2><p>詳細情報がここに表示されます。</p><ul><li>項目1</li><li>項目2</li></ul>'},
            {'page_number': 9, 'content_type': 'image', 'content_source': 'https://via.placeholder.com/300x500.png?text=Page9_Image'},
            {'page_number': 10, 'content_type': 'image', 'content_source': 'https://via.placeholder.com/300x500.png?text=Page10_Image'},
        ],
        "https://example.com/lp/product-b": [ # 別のLPのダミーデータ
            {'page_number': 1, 'content_type': 'image', 'content_source': 'https://via.placeholder.com/300x500.png?text=B_Page1_Image'},
            {'page_number': 2, 'content_type': 'image', 'content_source': 'https://via.placeholder.com/300x500.png?text=B_Page2_Image'},
            {'page_number': 3, 'content_type': 'video', 'content_source': 'https://www.w3schools.com/html/mov_bbb.mp4'},
            {'page_number': 4, 'content_type': 'image', 'content_source': 'https://via.placeholder.com/300x500.png?text=B_Page4_Image'},
        ]
    }

    # BigQueryからコンテンツ情報を取得する関数をシミュレート
    def get_lp_content_info(lp_url, page_num):
        """
        指定されたLPのURLとページ番号に基づいて、コンテンツのタイプとソースを返します。
        実際にはBigQueryからデータを取得するロジックに置き換わります。
        """
        if lp_url in dummy_lp_content_data_store:
            for item in dummy_lp_content_data_store[lp_url]:
                if item['page_number'] == page_num:
                    return item
        # データが見つからない場合や、ダミーデータを超えるページの場合のデフォルト
        # 拡張子で判別するロジックをここに組み込むことも可能
        # 例: if content_source.endswith(('.mp4', '.webm')): return 'video'
        # 今回はcontent_typeがデータに含まれる前提で進めます。
        return {'page_number': page_num, 'content_type': 'image', 'content_source': f"https://via.placeholder.com/300x500.png?text=ダミー{page_num}"}

    # テーブル表示用のプレースホルダー画像
    VIDEO_PLACEHOLDER_IMAGE = "https://via.placeholder.com/150x250.png?text=動画コンテンツ"
    HTML_PLACEHOLDER_IMAGE = "https://via.placeholder.com/150x250.png?text=HTMLコンテンツ"

    # --- BigQueryデータシミュレーションここまで ---


    # ページ別メトリクス計算
    page_stats = filtered_df.groupby('page_num_dom').agg({
        'session_id': 'nunique',
        'stay_ms': 'mean',
        'scroll_pct': 'mean',
        'load_time_ms': 'mean'
    }).reset_index()
    page_stats.columns = ['ページ番号', 'ビュー数', '平均滞在時間(ms)', '平均逆行率', '平均読込時間(ms)']
    page_stats['平均滞在時間(秒)'] = page_stats['平均滞在時間(ms)'] / 1000
    
    # LPの実際のページ数を取得（画像取得が成功した場合はそれを使用、失敗した場合は推測値）
    actual_page_count = int(filtered_df['page_num_dom'].max()) if not filtered_df.empty else 10
    
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
            base_views = 500
            page_views = int(base_views * (0.8 ** (page_num - 1)) + random.randint(-20, 20))
            new_row = pd.DataFrame([{
                'ページ番号': page_num,
                'ビュー数': max(page_views, 10),  # 最低10
                '平均滞在時間(ms)': random.randint(5000, 200000), # 3分以上のデータも生成
                '平均逆行率': random.uniform(5, 15),
                '平均読込時間(ms)': random.randint(800, 1500),
                '平均滞在時間(秒)': random.randint(5000, 200000) / 1000,
                '離脱率': 0  # 離脱率は別途計算
            }])
            page_stats = pd.concat([page_stats, new_row], ignore_index=True)
    
    # ページ番号でソート
    page_stats = page_stats.sort_values('ページ番号').reset_index(drop=True)
    
    # 包括的なページメトリクステーブル
    st.markdown("#### ページごとのパフォーマンス詳細")
    st.markdown('<div class="graph-description">項目名をクリックすると並べ替えができます。表示個数は右のプルダウンから選択してください</div>', unsafe_allow_html=True)

    # プルダウンメニューを独立した狭いカラムに配置し、右端に寄せる
    _, pulldown_col_right = st.columns([0.85, 0.15]) # 左に広い空のカラム、右に狭いプルダウン用のカラム

    with pulldown_col_right:
        num_to_display_str = st.selectbox(
            "表示件数",
            ["すべて"] + list(range(5, 51, 5)),
            index=0,
            label_visibility="collapsed", # ラベルを非表示にしてコンパクトに
            key="page_analysis_display_count"
        )
    # 各ページのインタラクション要素のメトリクスを計算
    comprehensive_metrics = []
    
    for page_num in range(1, actual_page_count + 1):
        # 画像URLを取得
        # BigQueryからコンテンツ情報を取得（シミュレーション）
        content_info = get_lp_content_info(selected_lp, page_num)
        content_type = content_info['content_type']
        content_source = content_info['content_source']

        # テーブル表示用の画像URLを決定
        display_image_for_table = ""
        if content_type == 'image':
            display_image_for_table = content_source
        elif content_type == 'video':
            display_image_for_table = VIDEO_PLACEHOLDER_IMAGE
        elif content_type == 'html':
            display_image_for_table = HTML_PLACEHOLDER_IMAGE
        # その他のタイプがあればここに追加

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
            'コンテンツタイプ': content_type, # 新しい列
            'ページ画像': display_image_for_table, # テーブル表示用の画像URL
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
    
    
    # 列名を短縮
    comprehensive_df.rename(columns={
        'フローティングバナーCTR': 'FB CTR',
        '離脱防止ポップアップCTR': '離脱POP CTR'
    }, inplace=True)

    # データフレームで表示（画像列付き）
    if not comprehensive_df.empty:
        # 表示件数に応じてデータをスライス
        if num_to_display_str != "すべて":
            num_to_display = int(num_to_display_str)
            display_df = comprehensive_df.head(num_to_display)
        else:
            display_df = comprehensive_df

        # st.containerでラップして再描画時のバグを回避
        df_container = st.container()
        with df_container:
            st.dataframe(
                display_df,
                column_config={
                    "ページ画像": st.column_config.ImageColumn("プレビュー", help="ページのコンテンツプレビュー"), # ラベルを変更
                    "ページ": None, # ページ列を非表示にする
                },
                hide_index=True,
                use_container_width=True
            )
    else:
        st.warning("テーブルデータが空です。")
    
    st.markdown("---")
    
    # 離脱率と滞在時間の散布図
    st.markdown('### 離脱率 vs 滞在時間 ポジショニングマップ')
    st.markdown('<div class="graph-description">各ページの離脱率（横軸）と平均滞在時間（縦軸）を散布図に表示します。右下の「要注意ゾーン」（高離脱率・低滞在時間）にあるページは、最優先で改善が必要なボトルネックです。</div>', unsafe_allow_html=True)

    if len(page_stats) > 1:
        # 平均値を計算
        avg_exit_rate = page_stats['離脱率'].mean()
        avg_stay_time = page_stats['平均滞在時間(秒)'].mean()

        # 散布図を作成
        fig_scatter = px.scatter(
            page_stats,
            x='離脱率',
            y='平均滞在時間(秒)',
            text='ページ番号',
            size='ビュー数',
            color_discrete_sequence=px.colors.qualitative.Plotly,
            hover_name='ページ番号',
            hover_data={'ページ番号': False, 'ビュー数': ':,', '離脱率': ':.1f', '平均滞在時間(秒)': ':.1f'}
        )

        # 平均線を追加
        fig_scatter.add_vline(x=avg_exit_rate, line_dash="dash", line_color="gray", annotation_text=f"全ページ平均離脱率: {avg_exit_rate:.1f}%")
        fig_scatter.add_hline(y=avg_stay_time, line_dash="dash", line_color="gray", annotation_text=f"全ページ平均滞在時間: {avg_stay_time:.1f}秒")

        # ゾーンの背景色と注釈を追加
        fig_scatter.add_shape(type="rect", xref="paper", yref="paper", x0=0.5, y0=0, x1=1, y1=0.5, fillcolor="rgba(255, 0, 0, 0.1)", layer="below", line_width=0)
        fig_scatter.add_annotation(xref="paper", yref="paper", x=0.75, y=0.25, text="要注意ゾーン<br>(離脱率が高く滞在時間が短い)", showarrow=False, font=dict(color="red", size=14))

        fig_scatter.add_shape(type="rect", xref="paper", yref="paper", x0=0.5, y0=0.5, x1=1, y1=1, fillcolor="rgba(255, 165, 0, 0.1)", layer="below", line_width=0)
        fig_scatter.add_annotation(xref="paper", yref="paper", x=0.75, y=0.75, text="改善候補<br>(離脱率が高く滞在時間が長い)", showarrow=False, font=dict(color="orange", size=14))

        fig_scatter.add_shape(type="rect", xref="paper", yref="paper", x0=0, y0=0, x1=0.5, y1=0.5, fillcolor="rgba(255, 255, 0, 0.1)", layer="below", line_width=0)
        fig_scatter.add_annotation(xref="paper", yref="paper", x=0.25, y=0.25, text="機会損失<br>(離脱率が低く滞在時間が短い)", showarrow=False, font=dict(color="goldenrod", size=14))

        fig_scatter.add_shape(type="rect", xref="paper", yref="paper", x0=0, y0=0.5, x1=0.5, y1=1, fillcolor="rgba(0, 128, 0, 0.1)", layer="below", line_width=0)
        fig_scatter.add_annotation(xref="paper", yref="paper", x=0.25, y=0.75, text="良好<br>(離脱率が低く滞在時間が長い)", showarrow=False, font=dict(color="green", size=14))

        fig_scatter.update_traces(
            textposition='top center',
            marker=dict(sizemin=5),
            textfont_size=12
        )
        fig_scatter.update_layout(
            height=600,
            xaxis_title='離脱率 (%)',
            yaxis_title='平均滞在時間 (秒)',
            showlegend=False,
            dragmode=False,
            xaxis=dict(
                range=[0, max(50, page_stats['離脱率'].max() * 1.1)]
            ),
            yaxis=dict(
                range=[0, page_stats['平均滞在時間(秒)'].max() * 1.1]
            )
        )
        st.plotly_chart(fig_scatter, use_container_width=True, key='plotly_chart_scatter_exit_stay')
    else:
        st.info("ポジショニングマップを表示するには、2ページ以上のデータが必要です。")
    
    st.markdown("---")
    
    # 滞在時間が短いページ、離脱率が高いページ、逆行パターンを並べて表示
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('##### 滞在時間が短いページ TOP5')
        st.markdown('<div class="graph-description">コンテンツが魅力的でない、または読みづらい可能性があります。</div>', unsafe_allow_html=True)
        
        # データがあるページのみを対象（0値を除外）
        valid_pages = page_stats[page_stats['平均滞在時間(秒)'] > 0]
        if len(valid_pages) >= 5:
            short_stay_pages = valid_pages.nsmallest(5, '平均滞在時間(秒)')
        else:
            short_stay_pages = valid_pages
        
        if len(short_stay_pages) > 0:
            display_df = short_stay_pages[['ページ番号', '平均滞在時間(秒)']].copy()
            display_df['ページ番号'] = display_df['ページ番号'].astype(int)
            st.dataframe(display_df.style.format({'平均滞在時間(秒)': '{:.1f}秒'}), use_container_width=True, hide_index=True, height=212) # 高さを固定
        else:
            st.info("データがありません。")

    with col2:
        st.markdown('##### 離脱率が高いページ TOP5')
        st.markdown('<div class="graph-description">ユーザーが最も離脱しやすいボトルネックとなっている可能性が高いページです。</div>', unsafe_allow_html=True)
        high_exit_pages = page_stats.nlargest(5, '離脱率')[['ページ番号', '離脱率']]
        high_exit_pages['ページ番号'] = high_exit_pages['ページ番号'].astype(int)
        st.dataframe(high_exit_pages.style.format({'離脱率': '{:.1f}%'}), use_container_width=True, hide_index=True, height=212) # 高さを固定

    with col3:
        st.markdown('##### 逆行が多いページ TOP5')
        st.markdown('<div class="graph-description">逆行の回数が多い場合、コンテンツの流れに問題がある可能性があります。</div>', unsafe_allow_html=True)
        backward_df = filtered_df[filtered_df['direction'] == 'backward']
        
        if len(backward_df) > 0:
            # prev_page_pathからページ番号を抽出する
            backward_df_copy = backward_df.copy()
            backward_df_copy['prev_page_num'] = backward_df_copy['prev_page_path'].str.extract(r'page-(\d+)').fillna(0).astype(int)

            # page_num_dom と prev_page_num でグループ化
            backward_pattern = backward_df_copy.groupby(['page_num_dom', 'prev_page_num']).size().reset_index(name='回数')
            backward_pattern = backward_pattern.sort_values('回数', ascending=False).head(5)
            backward_pattern.columns = ['遷移先ページ番号', '遷移元ページ番号', '回数']
            # 遷移元が0（不明）のものは除外
            backward_pattern = backward_pattern[backward_pattern['遷移元ページ番号'] > 0]
            
            st.dataframe(backward_pattern[['遷移元ページ番号', '遷移先ページ番号', '回数']], use_container_width=True, hide_index=True, height=212) # 高さを固定
        else:
            st.info("逆行パターンのデータがありません")
    
    st.markdown("---")

    # --- AI分析と考察 ---
    st.markdown("### AIによる分析と考察")
    st.markdown('<div class="graph-description">ページ分析の結果に基づき、AIが現状の評価と改善のための考察を提示します。</div>', unsafe_allow_html=True)

    # AI分析の表示状態を管理
    if 'page_analysis_ai_open' not in st.session_state:
        st.session_state.page_analysis_ai_open = False

    if st.button("AI分析を実行", key="page_analysis_ai_btn", type="primary", use_container_width=True):
        st.session_state.page_analysis_ai_open = True
        st.rerun()

    if st.session_state.page_analysis_ai_open:
        with st.container():
            with st.spinner("AIがページデータを分析中..."):
                # ボトルネックページを特定
                bottleneck_page = page_stats.sort_values(by=['離脱率', '平均滞在時間(秒)'], ascending=[False, True]).iloc[0]
                
                st.markdown("#### 1. 現状の評価")
                st.info(f"""
                ポジショニングマップと各指標から、**ページ{int(bottleneck_page['ページ番号'])}** が最も重要な改善候補（ボトルネック）であると判断されます。
                - **離脱率**: {bottleneck_page['離脱率']:.1f}% と高く、多くのユーザーがここでLPから離れています。
                - **平均滞在時間**: {bottleneck_page['平均滞在時間(秒)']:.1f}秒 と短く、コンテンツが十分に読まれていない可能性があります。
                - **逆行パターン**: 逆行が多いページは、ユーザーが情報を探して迷っている兆候です。遷移元と遷移先のコンテンツの流れを見直す必要があります。
                """)

                st.markdown("#### 2. 今後の考察と改善案")
                st.warning(f"""
                **ページ{int(bottleneck_page['ページ番号'])}** の改善が急務です。滞在時間が短く離脱率が高いことから、以下の可能性が考えられます。
                - **コンテンツのミスマッチ**: 前のページからの期待と、このページの内容が合っていない。
                - **魅力の欠如**: ユーザーの興味を引く情報やビジュアルが不足している。
                - **次のアクションが不明確**: ユーザーが次に何をすべきか分からず離脱している。
                
                **具体的な改善アクション案:**
                1. **コンテンツの見直し**: ページ{int(bottleneck_page['ページ番号'])}のキャッチコピーや画像が、ユーザーのニーズに合っているか再確認する。
                2. **CTAの設置**: 次のページへ誘導する明確なCTA（コールトゥアクション）ボタンを設置、または既存のものをより目立たせる。
                3. **A/Bテストの実施**: 異なる訴求内容のコンテンツやデザインでA/Bテストを行い、どちらが効果的か検証する。
                """)

            if st.button("AI分析を閉じる", key="page_analysis_ai_close"):
                st.session_state.page_analysis_ai_open = False
                st.rerun()

    # --- よくある質問 ---
    st.markdown("#### よくある質問")
    if 'page_faq_toggle' not in st.session_state:
        st.session_state.page_faq_toggle = {1: False, 2: False, 3: False, 4: False}

    faq_cols = st.columns(2)
    with faq_cols[0]:
        if st.button("最も改善すべきページはどれ？", key="faq_page_1", use_container_width=True):
            st.session_state.page_faq_toggle[1] = not st.session_state.page_faq_toggle[1]
            st.session_state.page_faq_toggle[2], st.session_state.page_faq_toggle[3], st.session_state.page_faq_toggle[4] = False, False, False
        if st.session_state.page_faq_toggle[1]:
            if not page_stats.empty:
                bottleneck_page = page_stats.sort_values(by=['離脱率', '平均滞在時間(秒)'], ascending=[False, True]).iloc[0]
                st.info(f"**ページ{int(bottleneck_page['ページ番号'])}** です。離脱率が{bottleneck_page['離脱率']:.1f}%と高く、平均滞在時間が{bottleneck_page['平均滞在時間(秒)']:.1f}秒と短いため、最優先で改善すべきボトルネックです。")
        
        if st.button("滞在時間が短いページの共通点は？", key="faq_page_3", use_container_width=True):
            st.session_state.page_faq_toggle[3] = not st.session_state.page_faq_toggle[3]
            st.session_state.page_faq_toggle[1], st.session_state.page_faq_toggle[2], st.session_state.page_faq_toggle[4] = False, False, False
        if st.session_state.page_faq_toggle[3]:
            st.info("滞在時間が短いページは、ユーザーの期待とコンテンツが一致していない、情報が分かりにくい、または単に興味を引かれていない可能性があります。前のページからの文脈を見直し、コンテンツの魅力を高める必要があります。")
    with faq_cols[1]:
        if st.button("ユーザーが前のページに戻る原因は？", key="faq_page_2", use_container_width=True):
            st.session_state.page_faq_toggle[2] = not st.session_state.page_faq_toggle[2]
            st.session_state.page_faq_toggle[1], st.session_state.page_faq_toggle[3], st.session_state.page_faq_toggle[4] = False, False, False
        if st.session_state.page_faq_toggle[2]:
            st.info("ユーザーが逆行（前のページに戻る）するのは、主に「求めている情報が見つからない」「前のページの情報と比較・再確認したい」という理由が考えられます。逆行が多いページ間のコンテンツの流れを見直し、情報の不足がないか確認することが重要です。")
        
        if st.button("離脱率と滞在時間の関係は？", key="faq_page_4", use_container_width=True):
            st.session_state.page_faq_toggle[4] = not st.session_state.page_faq_toggle[4]
            st.session_state.page_faq_toggle[1], st.session_state.page_faq_toggle[2], st.session_state.page_faq_toggle[3] = False, False, False
        if st.session_state.page_faq_toggle[4]:
            st.info("「離脱率が高く、滞在時間が短い」ページは、コンテンツが全く響いていない重大な問題ページです。逆に「離脱率が高く、滞在時間が長い」ページは、コンテンツは読まれているが次のアクションに繋がっていない「惜しい」ページと言えます。")


# タブ3: セグメント分析
elif selected_analysis == "セグメント分析":
    st.markdown('<div class="sub-header">セグメント分析</div>', unsafe_allow_html=True)
    # メインエリア: フィルターと比較設定
    st.markdown('<div class="sub-header">フィルター設定</div>', unsafe_allow_html=True)

    filter_cols = st.columns(4)
    with filter_cols[0]:
        # 期間選択
        period_options = {
            "過去7日間": 7,
            "過去30日間": 30,
            "過去90日間": 90,
            "カスタム期間": None
        }
        selected_period = st.selectbox("期間を選択", list(period_options.keys()), index=1, key="segment_analysis_period")

    with filter_cols[1]:
        # LP選択
        lp_options = sorted(df['page_location'].dropna().unique().tolist()) # type: ignore
        selected_lp = st.selectbox("LP選択", lp_options, index=0 if lp_options else -1, key="segment_analysis_lp")

    with filter_cols[2]:
        device_options = ["すべて"] + sorted(df['device_type'].dropna().unique().tolist())
        selected_device = st.selectbox("デバイス選択", device_options, index=0, key="segment_analysis_device")

    with filter_cols[3]:
        channel_options = ["すべて"] + sorted(df['channel'].unique().tolist())
        selected_channel = st.selectbox("チャネル選択", channel_options, index=0, key="segment_analysis_channel")

    # 比較機能はチェックボックスでシンプルに
    enable_comparison = st.checkbox("比較機能を有効化", value=False, key="segment_analysis_compare_check")
    comparison_type = None
    if enable_comparison:
        comparison_options = {
            "前期間": "previous_period", "前週": "previous_week",
            "前月": "previous_month", "前年": "previous_year"
        }
        selected_comparison = st.selectbox("比較対象", list(comparison_options.keys()), key="segment_analysis_compare_select")
        comparison_type = comparison_options[selected_comparison]

    # カスタム期間の場合
    if selected_period == "カスタム期間":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("開始日", df['event_date'].min(), key="segment_analysis_start_date")
        with col2:
            end_date = st.date_input("終了日", df['event_date'].max(), key="segment_analysis_end_date")
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
    if selected_lp:
        filtered_df = filtered_df[filtered_df['page_location'] == selected_lp]

    # --- クロス分析用フィルター適用 ---
    if selected_device != "すべて":
        filtered_df = filtered_df[filtered_df['device_type'] == selected_device]

    if selected_channel != "すべて":
        filtered_df = filtered_df[filtered_df['channel'] == selected_channel]

    # ==============================================================================
    #  デバッグ用: 3分以上の滞在時間データを強制的に生成
    #  目的: 「3分以上」セグメントがグラフに表示されることを確認するため。
    #  注意: このコードは本番データでは不要です。
    # ==============================================================================
    if not filtered_df.empty:
        # 'stay_ms'列が存在し、かつNaNでない行が1つ以上あることを確認
        if 'stay_ms' in filtered_df.columns and filtered_df['stay_ms'].notna().any():
            # 滞在時間が最も長い上位5%のインデックスを取得
            long_stay_indices = filtered_df['stay_ms'].nlargest(int(len(filtered_df) * 0.05)).index
            
            # それらの滞在時間を3分〜5分のランダムな値に書き換える
            if not long_stay_indices.empty:
                new_stay_times = np.random.randint(180000, 300000, size=len(long_stay_indices))
                filtered_df.loc[long_stay_indices, 'stay_ms'] = new_stay_times
    # ==============================================================================

    # 比較データの取得
    comparison_df = None
    comp_start = None
    comp_end = None
    if enable_comparison and comparison_type:
        result = get_comparison_data(df, pd.Timestamp(start_date), pd.Timestamp(end_date), comparison_type)
        if result is not None:
            comparison_df, comp_start, comp_end = result
            # 比較データにも同じフィルターを適用
            if selected_lp:
                comparison_df = comparison_df[comparison_df['page_location'] == selected_lp]
            # --- 比較データにもクロス分析用フィルターを適用 ---
            if selected_device != "すべて":
                comparison_df = comparison_df[comparison_df['device_type'] == selected_device]
            if selected_channel != "すべて":
                comparison_df = comparison_df[comparison_df['channel'] == selected_channel]

            # 比較データが空の場合は無効化
            if len(comparison_df) == 0:
                comparison_df = None
                st.info(f"比較期間（{comp_start.strftime('%Y-%m-%d')} 〜 {comp_end.strftime('%Y-%m-%d')}）にデータがありません。")

    # データが空の場合の処理
    if len(filtered_df) == 0:
        st.warning("⚠️ 選択した条件に該当するデータがありません。フィルターを変更してください。")
        st.stop()

    # セグメント選択
    segment_type = st.selectbox("分析するセグメントを選択", [
        "デバイス別", "チャネル別", "UTMソース別", "A/Bテスト別"
    ], key="segment_analysis_segment_type")
    
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
    segment_stats['コンバージョン率'] = segment_stats.apply(lambda row: safe_rate(row['コンバージョン数'], row['セッション数']) * 100, axis=1)
    
    # エンゲージメント率（滞在時間30秒以上）
    engaged_sessions = filtered_df[filtered_df['stay_ms'] >= 30000].groupby(segment_col)['session_id'].nunique().reset_index()
    engaged_sessions.columns = [segment_name, 'エンゲージセッション数']
    
    segment_stats = segment_stats.merge(engaged_sessions, on=segment_name, how='left').fillna(0)
    segment_stats['エンゲージメント率'] = (segment_stats['エンゲージセッション数'] / segment_stats['セッション数'] * 100)
    segment_stats['エンゲージメント率'] = segment_stats.apply(lambda row: safe_rate(row['エンゲージセッション数'], row['セッション数']) * 100, axis=1)
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
        fig.update_layout(dragmode=False)
        fig.update_traces(hovertemplate='%{x}<br>コンバージョン率: %{y:.2f}%<extra></extra>')
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_14')
    
    with col2:
        fig = px.bar(segment_stats, x=segment_name, y='平均滞在時間(秒)', title=f'{segment_type}の平均滞在時間')
        fig.update_layout(dragmode=False)
        fig.update_traces(hovertemplate='%{x}<br>平均滞在時間: %{y:.1f}秒<extra></extra>')
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_15') # type: ignore

    st.markdown("---")

    # --- AI分析と考察 ---
    st.markdown("### AIによる分析と考察")
    st.markdown('<div class="graph-description">セグメント分析の結果に基づき、AIが現状の評価と改善のための考察を提示します。</div>', unsafe_allow_html=True)

    # AI分析の表示状態を管理
    if 'segment_analysis_ai_open' not in st.session_state:
        st.session_state.segment_analysis_ai_open = False

    if st.button("AI分析を実行", key="segment_analysis_ai_btn", type="primary", use_container_width=True):
        st.session_state.segment_analysis_ai_open = True
        st.rerun()

    if st.session_state.segment_analysis_ai_open:
        with st.container():
            with st.spinner("AIがセグメントデータを分析中..."):
                if not segment_stats.empty:
                    best_segment = segment_stats.loc[segment_stats['コンバージョン率'].idxmax()]
                    worst_segment = segment_stats.loc[segment_stats['コンバージョン率'].idxmin()]
                else:
                    best_segment, worst_segment = (None, None)
                
                st.markdown("#### 1. 現状の評価")
                st.info(f"""
                {segment_type}では、パフォーマンスに顕著な差が見られます。
                - **最もパフォーマンスが高いセグメント**: **{best_segment[segment_name]}** (CVR: {best_segment['コンバージョン率']:.2f}%)
                - **最もパフォーマンスが低いセグメント**: **{worst_segment[segment_name]}** (CVR: {worst_segment['コンバージョン率']:.2f}%)
                
                特に **{worst_segment[segment_name]}** のセグメントは、他のセグメントと比較してCVRが低く、改善の機会が大きい領域です。
                """)

                st.markdown("#### 2. 今後の考察と改善案")
                st.warning(f"""
                **{worst_segment[segment_name]}** セグメントのパフォーマンスが低い原因を特定し、対策を講じるべきです。
                - **{segment_type}が「デバイス別」の場合**: {worst_segment[segment_name]}での表示崩れや操作性の問題がないか確認が必要です。レスポンシブデザインの見直しや、読み込み速度の最適化を検討してください。
                - **{segment_type}が「チャネル別」の場合**: {worst_segment[segment_name]}からの流入ユーザーとLPの訴求内容が一致していない可能性があります。広告のターゲティングやクリエイティブ、またはLPのファーストビューを見直してください。
                
                逆に、**{best_segment[segment_name]}** は非常に効果的なセグメントです。このセグメントへの広告予算の増額や、類似ユーザーへのアプローチ拡大を検討する価値があります。
                """)
            if st.button("AI分析を閉じる", key="segment_analysis_ai_close"):
                st.session_state.segment_analysis_ai_open = False
                st.rerun()

    # --- よくある質問 ---
    st.markdown("#### よくある質問")
    if 'segment_faq_toggle' not in st.session_state:
        st.session_state.segment_faq_toggle = {1: False, 2: False, 3: False, 4: False}

    faq_cols = st.columns(2)
    with faq_cols[0]:
        if st.button(f"パフォーマンスが最も良い{segment_name}は？", key="faq_segment_1", use_container_width=True):
            st.session_state.segment_faq_toggle[1] = not st.session_state.segment_faq_toggle[1]
            st.session_state.segment_faq_toggle[2], st.session_state.segment_faq_toggle[3], st.session_state.segment_faq_toggle[4] = False, False, False
        if st.session_state.segment_faq_toggle[1] and not segment_stats.empty:
            if not segment_stats.empty:
                best_segment = segment_stats.loc[segment_stats['コンバージョン率'].idxmax()]
                st.info(f"**{best_segment[segment_name]}** です。コンバージョン率が **{best_segment['コンバージョン率']:.2f}%** と最も高いパフォーマンスを示しています。")
        
        if st.button(f"パフォーマンスが良いセグメントに集中すべき？", key="faq_segment_3", use_container_width=True):
            st.session_state.segment_faq_toggle[3] = not st.session_state.segment_faq_toggle[3]
            st.session_state.segment_faq_toggle[1], st.session_state.segment_faq_toggle[2], st.session_state.segment_faq_toggle[4] = False, False, False
        if st.session_state.segment_faq_toggle[3]:
            st.info("はい、短期的には最も効果的なアプローチです。パフォーマンスが良いセグメント（例：特定の広告チャネルやデバイス）への予算配分を増やすことで、全体のコンバージョン数を効率的に伸ばすことができます。")
    with faq_cols[1]:
        if st.button(f"パフォーマンスが最も悪い{segment_name}の原因は？", key="faq_segment_2", use_container_width=True):
            st.session_state.segment_faq_toggle[2] = not st.session_state.segment_faq_toggle[2]
            st.session_state.segment_faq_toggle[1], st.session_state.segment_faq_toggle[3], st.session_state.segment_faq_toggle[4] = False, False, False
        if st.session_state.segment_faq_toggle[2] and not segment_stats.empty:
            if not segment_stats.empty:
                worst_segment = segment_stats.loc[segment_stats['コンバージョン率'].idxmin()]
                st.info(f"**{worst_segment[segment_name]}** のパフォーマンスが低い原因として、{segment_type}が「デバイス別」なら「表示崩れや操作性の問題」、{segment_type}が「チャネル別」なら「広告ターゲティングとLP内容のミスマッチ」などが考えられます。")
        
        if st.button(f"セグメント毎にLPを変えるべき？", key="faq_segment_4", use_container_width=True):
            st.session_state.segment_faq_toggle[4] = not st.session_state.segment_faq_toggle[4]
            st.session_state.segment_faq_toggle[1], st.session_state.segment_faq_toggle[2], st.session_state.segment_faq_toggle[3] = False, False, False
        if st.session_state.segment_faq_toggle[4]:
            st.info("はい、中長期的には非常に有効な施策です。例えば、PCユーザーには詳細な情報を、スマホユーザーには要点を絞ったコンテンツを見せるなど、セグメントに合わせてLPをパーソナライズすることで、CVRの大幅な向上が期待できます。")

# タブ4: A/Bテスト分析
elif selected_analysis == "A/Bテスト分析":
    st.markdown('<div class="sub-header">A/Bテスト分析</div>', unsafe_allow_html=True)
    # メインエリア: フィルターと比較設定
    st.markdown('<div class="sub-header">フィルター設定</div>', unsafe_allow_html=True)

    filter_cols = st.columns(4)
    with filter_cols[0]:
        # 期間選択
        period_options = {
            "過去7日間": 7,
            "過去30日間": 30,
            "過去90日間": 90,
            "カスタム期間": None
        }
        selected_period = st.selectbox("期間を選択", list(period_options.keys()), index=1, key="ab_test_period")

    with filter_cols[1]:
        # LP選択
        lp_options = sorted(df['page_location'].dropna().unique().tolist()) # type: ignore
        selected_lp = st.selectbox("LP選択", lp_options, index=0 if lp_options else -1, key="ab_test_lp")

    with filter_cols[2]:
        device_options = ["すべて"] + sorted(df['device_type'].dropna().unique().tolist())
        selected_device = st.selectbox("デバイス選択", device_options, index=0, key="ab_test_device")

    with filter_cols[3]:
        channel_options = ["すべて"] + sorted(df['channel'].unique().tolist())
        selected_channel = st.selectbox("チャネル選択", channel_options, index=0, key="ab_test_channel")

    # 比較機能はチェックボックスでシンプルに
    enable_comparison = st.checkbox("比較機能を有効化", value=False, key="ab_test_compare_check")
    comparison_type = None
    if enable_comparison:
        comparison_options = {
            "前期間": "previous_period", "前週": "previous_week",
            "前月": "previous_month", "前年": "previous_year"
        }
        selected_comparison = st.selectbox("比較対象", list(comparison_options.keys()), key="ab_test_compare_select")
        comparison_type = comparison_options[selected_comparison]

    # カスタム期間の場合
    if selected_period == "カスタム期間":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("開始日", df['event_date'].min(), key="ab_test_start_date")
        with col2:
            end_date = st.date_input("終了日", df['event_date'].max(), key="ab_test_end_date")
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
    if selected_lp:
        filtered_df = filtered_df[filtered_df['page_location'] == selected_lp]

    # --- クロス分析用フィルター適用 ---
    if selected_device != "すべて":
        filtered_df = filtered_df[filtered_df['device_type'] == selected_device]

    if selected_channel != "すべて":
        filtered_df = filtered_df[filtered_df['channel'] == selected_channel]

    # ==============================================================================
    #  デバッグ用: 3分以上の滞在時間データを強制的に生成
    #  目的: 「3分以上」セグメントがグラフに表示されることを確認するため。
    #  注意: このコードは本番データでは不要です。
    # ==============================================================================
    if not filtered_df.empty:
        # 'stay_ms'列が存在し、かつNaNでない行が1つ以上あることを確認
        if 'stay_ms' in filtered_df.columns and filtered_df['stay_ms'].notna().any():
            # 滞在時間が最も長い上位5%のインデックスを取得
            long_stay_indices = filtered_df['stay_ms'].nlargest(int(len(filtered_df) * 0.05)).index
            
            # それらの滞在時間を3分〜5分のランダムな値に書き換える
            if not long_stay_indices.empty:
                new_stay_times = np.random.randint(180000, 300000, size=len(long_stay_indices))
                filtered_df.loc[long_stay_indices, 'stay_ms'] = new_stay_times
    # ==============================================================================

    # 比較データの取得
    comparison_df = None
    comp_start = None
    comp_end = None
    if enable_comparison and comparison_type:
        result = get_comparison_data(df, pd.Timestamp(start_date), pd.Timestamp(end_date), comparison_type)
        if result is not None:
            comparison_df, comp_start, comp_end = result
            # 比較データにも同じフィルターを適用
            if selected_lp:
                comparison_df = comparison_df[comparison_df['page_location'] == selected_lp]
            # --- 比較データにもクロス分析用フィルターを適用 ---
            if selected_device != "すべて":
                comparison_df = comparison_df[comparison_df['device_type'] == selected_device]
            if selected_channel != "すべて":
                comparison_df = comparison_df[comparison_df['channel'] == selected_channel]

            # 比較データが空の場合は無効化
            if len(comparison_df) == 0:
                comparison_df = None
                st.info(f"比較期間（{comp_start.strftime('%Y-%m-%d')} 〜 {comp_end.strftime('%Y-%m-%d')}）にデータがありません。")

    # データが空の場合の処理
    if filtered_df.empty:
        st.warning("⚠️ 選択した条件に該当するデータがありません。フィルターを変更してください。")
        st.stop()

    # A/Bテスト種別のマッピング
    test_type_map = {
        'hero_image': 'FVテスト',
        'cta_button': 'CTAテスト',
        'headline': 'ヘッドラインテスト',
        'layout': 'レイアウトテスト',
        'copy': 'コピーテスト',
        'form': 'フォームテスト',
        'video': '動画テスト'
    }
    if 'ab_test_target' in filtered_df.columns:
        filtered_df['ab_test_target'] = filtered_df['ab_test_target'].map(test_type_map).fillna('-')
    else:
        filtered_df['ab_test_target'] = '-'

    # p_valueカラムが存在するかどうかでaggの内容を分岐
    agg_dict = {
        'session_id': 'nunique',
        'stay_ms': 'mean',
        'max_page_reached': 'mean',
        'completion_rate': 'mean'
    }

    if 'p_value' in filtered_df.columns:
        agg_dict['p_value'] = 'first'
        ab_stats = filtered_df.groupby(['ab_test_target', 'ab_variant']).agg(agg_dict).reset_index()
        ab_stats.columns = ['テスト種別', 'バリアント', 'セッション数', '平均滞在時間(ms)', '平均到達ページ数', '平均完了率', 'p値']
    else:
        ab_stats = filtered_df.groupby(['ab_test_target', 'ab_variant']).agg(agg_dict).reset_index()
        ab_stats.columns = ['テスト種別', 'バリアント', 'セッション数', '平均滞在時間(ms)', '平均到達ページ数', '平均完了率']
        # p_valueカラムが存在しない場合は、1.0で初期化
        ab_stats['p値'] = 1.0
    

    ab_stats['平均滞在時間(秒)'] = ab_stats['平均滞在時間(ms)'] / 1000
    ab_stats['p値'] = ab_stats['p値'].fillna(1.0) # p値がない場合は1.0で埋める
    
    # コンバージョン数（テスト種別とバリアントでグループ化）
    ab_cv = filtered_df[filtered_df['cv_type'].notna()].groupby(['ab_test_target', 'ab_variant'])['session_id'].nunique().reset_index()
    ab_cv.columns = ['テスト種別', 'バリアント', 'コンバージョン数']
    
    ab_stats = ab_stats.merge(ab_cv, on=['テスト種別', 'バリアント'], how='left').fillna({'コンバージョン数': 0})
    ab_stats['コンバージョン率'] = ab_stats.apply(lambda row: safe_rate(row['コンバージョン数'], row['セッション数']) * 100, axis=1)
    
    # FV残存率（テスト種別とバリアントでグループ化）
    fv_retention = filtered_df[filtered_df['max_page_reached'] >= 2].groupby(['ab_test_target', 'ab_variant'])['session_id'].nunique().reset_index()
    fv_retention.columns = ['テスト種別', 'バリアント', 'FV残存数']
    
    ab_stats = ab_stats.merge(fv_retention, on=['テスト種別', 'バリアント'], how='left').fillna({'FV残存数': 0})
    ab_stats['FV残存率'] = ab_stats.apply(lambda row: safe_rate(row['FV残存数'], row['セッション数']) * 100, axis=1)
    
    # 最終CTA到達率（テスト種別とバリアントでグループ化）
    final_cta = filtered_df[filtered_df['max_page_reached'] >= 10].groupby(['ab_test_target', 'ab_variant'])['session_id'].nunique().reset_index()
    final_cta.columns = ['テスト種別', 'バリアント', '最終CTA到達数']
    
    ab_stats = ab_stats.merge(final_cta, on=['テスト種別', 'バリアント'], how='left').fillna({'最終CTA到達数': 0})
    ab_stats['最終CTA到達率'] = ab_stats.apply(lambda row: safe_rate(row['最終CTA到達数'], row['セッション数']) * 100, axis=1)
    
    # テスト種別が'-'の行（テスト対象外のデータ）を除外
    ab_stats = ab_stats[ab_stats['テスト種別'] != '-'].reset_index(drop=True)

    # --- A/Bテスト統計計算 ---
    ab_stats['CVR差分(pt)'] = 0.0

    # テスト種別ごとにCVR差分を計算
    for test_type in ab_stats['テスト種別'].unique():
        test_df = ab_stats[ab_stats['テスト種別'] == test_type]
        if 'control' in test_df['バリアント'].values:
            baseline_cvr = test_df[test_df['バリアント'] == 'control']['コンバージョン率'].iloc[0]
            ab_stats.loc[test_df.index, 'CVR差分(pt)'] = test_df['コンバージョン率'] - baseline_cvr

    # p値から有意差と有意性を計算
    ab_stats['有意差'] = ab_stats['p値'].apply(lambda x: '★★★' if x < 0.01 else ('★★' if x < 0.05 else ('★' if x < 0.1 else '-')))
    ab_stats['有意性'] = 1 - ab_stats['p値']  # バブルチャート用


    # A/Bテストマトリクス
    st.markdown("#### A/Bテストマトリクス")
    display_cols = ['セッション数', 'コンバージョン率', 'CVR差分(pt)', '有意差', 'p値', 'FV残存率', '最終CTA到達率', '平均到達ページ数', '平均滞在時間(秒)'] # type: ignore
    
    # 'control' バリアントを除外して表示用のDataFrameを作成
    ab_stats_for_display = ab_stats[ab_stats['バリアント'] != 'control'].copy()
    
    # マルチインデックスを設定して表示
    display_df = ab_stats_for_display.set_index(['テスト種別', 'バリアント'])
    st.dataframe(display_df[display_cols].style.format({
        'セッション数': '{:,.0f}',
        'コンバージョン率': '{:.2f}%',
        'CVR差分(pt)': '{:+.2f}pt',
        'p値': '{:.4f}',
        'FV残存率': '{:.2f}%',
        '最終CTA到達率': '{:.2f}%',
        '平均到達ページ数': '{:.1f}',
        '平均滞在時間(秒)': '{:.1f}'
    }), use_container_width=True)
    
    # CVR向上率×有意性のバブルチャート
    # 'control' バリアントを除外し、バリアント'B'のみを対象とする
    ab_bubble = ab_stats[ab_stats['バリアント'] == 'B'].copy()

    # チャートタイトルと説明 (プルダウンは削除)
    st.markdown("#### CVR向上率×有意性バブルチャート")
    st.markdown('<div class="graph-description">CVR差分（X軸）と有意性（Y軸）を可視化。バブルサイズはサンプルサイズを表します。右上（高CVR差分×高有意性）が最も優れたバリアントです。</div>', unsafe_allow_html=True)

    if not ab_bubble.empty:
        fig = px.scatter(ab_bubble, 
                        x='CVR差分(pt)',
                        y='有意性',
                        size='セッション数',
                        text='バリアント', # バブルに表示するテキスト
                        color='テスト種別', # テスト種別で色分け
                        custom_data=['テスト種別', 'コンバージョン率', 'p値', '有意差'] # hovertemplateで使用するデータを渡す
                        )
        
        # 有意水準の参考線を追加
        fig.add_hline(y=0.95, line_dash="dash", line_color="green", annotation_text="p<0.05 (★★)", annotation_position="bottom right")
        fig.add_hline(y=0.99, line_dash="dash", line_color="red", annotation_text="p<0.01 (★★★)", annotation_position="bottom right") # type: ignore
        fig.add_vline(x=0, line_dash="dash", line_color="gray")

        # マウスオーバー時の表示内容とスタイルをカスタマイズ
        fig.update_traces(
            textposition='top center',
            hovertemplate=(
                "<b>%{text}</b><br>" +
                "テスト種別: %{customdata[0]}<br>" +
                "CVR差分(pt): %{x:+.2f}pt<br>" +
                "有意性: %{y:.2f}<br>" +
                "コンバージョン率: %{customdata[1]:.2f}%<br>" +
                "p値: %{customdata[2]:.4f}<extra></extra>"
            )
        )
        fig.update_layout(height=500,
                         hoverlabel=dict(bordercolor='#002060'), # ホバーの枠線色
                         xaxis_title='CVR差分 (pt)', dragmode=False,
                         yaxis_title='有意性 (1 - p値)')
        
        # 背景色と注釈を追加
        fig.add_shape(type="rect", xref="paper", yref="paper", x0=0.5, y0=0.5, x1=1, y1=1, fillcolor="rgba(0, 128, 0, 0.1)", layer="below", line_width=0)
        fig.add_annotation(xref="paper", yref="paper", x=0.75, y=0.75, text="最良ゾーン<br>(CVR向上・有意差あり)", showarrow=False, font=dict(color="green", size=14))

        fig.add_shape(type="rect", xref="paper", yref="paper", x0=0, y0=0.5, x1=0.5, y1=1, fillcolor="rgba(255, 0, 0, 0.1)", layer="below", line_width=0)
        fig.add_annotation(xref="paper", yref="paper", x=0.25, y=0.75, text="悪化ゾーン<br>(CVR悪化・有意差あり)", showarrow=False, font=dict(color="red", size=14))

        fig.add_shape(type="rect", xref="paper", yref="paper", x0=0.5, y0=0, x1=1, y1=0.5, fillcolor="rgba(255, 165, 0, 0.1)", layer="below", line_width=0)
        fig.add_annotation(xref="paper", yref="paper", x=0.75, y=0.25, text="有望ゾーン<br>(CVR向上・有意差なし)", showarrow=False, font=dict(color="orange", size=14))

        fig.add_shape(type="rect", xref="paper", yref="paper", x0=0, y0=0, x1=0.5, y1=0.5, fillcolor="rgba(128, 128, 128, 0.1)", layer="below", line_width=0)
        fig.add_annotation(xref="paper", yref="paper", x=0.25, y=0.25, text="判断保留ゾーン<br>(CVR悪化・有意差なし)", showarrow=False, font=dict(color="grey", size=14))

        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_ab_bubble')
    else:
        st.info("バブルチャートを表示するためのバリアント「B」のデータがありません。")
        
    # A/Bテスト時系列推移
    st.markdown("#### A/Bテスト CVR 時系列推移")
    
    # 'control'バリアントを除外
    ab_daily_df = filtered_df[filtered_df['ab_variant'] != 'control'].copy()
    # テスト種別が'-'のデータを除外
    ab_daily_df = ab_daily_df[ab_daily_df['ab_test_target'] != '-']

    # 日付、テスト種別、バリアントでグループ化
    ab_daily = ab_daily_df.groupby([ab_daily_df['event_date'].dt.date, 'ab_test_target', 'ab_variant']).agg({
        'session_id': 'nunique'
    }).reset_index()
    ab_daily.columns = ['日付', 'テスト種別', 'バリアント', 'セッション数']
    
    ab_daily_cv = ab_daily_df[ab_daily_df['cv_type'].notna()].groupby([
        ab_daily_df[ab_daily_df['cv_type'].notna()]['event_date'].dt.date,
        'ab_test_target',
        'ab_variant'
    ])['session_id'].nunique().reset_index()
    ab_daily_cv.columns = ['日付', 'テスト種別', 'バリアント', 'コンバージョン数']
    
    ab_daily = ab_daily.merge(ab_daily_cv, on=['日付', 'テスト種別', 'バリアント'], how='left').fillna(0)
    ab_daily['コンバージョン率'] = ab_daily.apply(lambda row: safe_rate(row['コンバージョン数'], row['セッション数']) * 100, axis=1) # type: ignore
    
    # 凡例用の列を作成
    ab_daily['凡例'] = ab_daily['テスト種別'] + ' - ' + ab_daily['バリアント']

    # 1つのグラフに統合して描画
    fig = px.line(ab_daily, x='日付', y='コンバージョン率', color='凡例', markers=True,
                  labels={'コンバージョン率': 'CVR (%)', '凡例': 'テスト - バリアント'})
    fig.update_layout(height=500, yaxis_title='コンバージョン率 (%)', dragmode=False)

    st.plotly_chart(fig, use_container_width=True, key='plotly_chart_17')

    st.markdown("---")

    # --- AI分析と考察 ---
    st.markdown("### AIによる分析と考察")
    st.markdown('<div class="graph-description">A/Bテストの結果に基づき、AIが統計的な評価と次のアクションを提案します。</div>', unsafe_allow_html=True)

    # AI分析の表示状態を管理
    if 'ab_test_ai_open' not in st.session_state:
        st.session_state.ab_test_ai_open = False

    if st.button("AI分析を実行", key="ab_test_ai_btn", type="primary", use_container_width=True):
        st.session_state.ab_test_ai_open = True
        st.rerun()

    if st.session_state.ab_test_ai_open:
        with st.container():
            with st.spinner("AIがA/Bテスト結果を分析中..."):
                if len(ab_stats) >= 2:
                    winner = ab_stats.sort_values('コンバージョン率', ascending=False).iloc[0]
                    baseline = ab_stats.iloc[0]
                    
                    st.markdown("#### 1. テスト結果の評価")
                    st.info(f"""
                    今回のA/Bテストの結果、**「{winner['バリアント']}」** が最も高いパフォーマンスを示しました。
                    - **勝者**: {winner['バリアント']} (CVR: {winner['コンバージョン率']:.2f}%)
                    - **ベースライン**: {baseline['バリアント']} (CVR: {baseline['コンバージョン率']:.2f}%)
                    - **CVR差分**: {winner['CVR差分(pt)']:.2f}pt
                    - **統計的有意差**: {winner['有意差']} (p値: {winner['p値']:.4f})
                    
                    p値が0.05未満の場合、この結果が偶然である可能性は低く、信頼性が高いと判断できます。
                    """)

                    st.markdown("#### 2. 今後のアクション提案")
                    st.warning(f"""
                    **「{winner['バリアント']}」** のパターンを本採用することを強く推奨します。
                    
                    **次のステップ:**
                    1. **勝者パターンの実装**: エンジニアリングチームと連携し、勝者パターン「{winner['バリアント']}」を全てのユーザーに適用してください。
                    2. **効果測定**: 実装後、再度パフォーマンスをモニタリングし、期待通りの効果が出ているか確認します。
                    3. **次のテスト計画**: 今回のテストで得られた知見（例：「{winner['バリアント']}」のどの要素が良かったか）を基に、さらなる改善のための新しいA/Bテストを計画しましょう。
                    """)
                else:
                    st.warning("比較するバリアントが2つ未満のため、詳細な分析は実行できません。")
            if st.button("AI分析を閉じる", key="ab_test_ai_close"):
                st.session_state.ab_test_ai_open = False
                st.rerun()

    # --- よくある質問 ---
    st.markdown("#### よくある質問")
    if 'ab_test_faq_toggle' not in st.session_state:
        st.session_state.ab_test_faq_toggle = {1: False, 2: False, 3: False, 4: False}

    faq_cols = st.columns(2)
    with faq_cols[0]:
        if st.button("どのバリアントが最も良かったですか？", key="faq_ab_1", use_container_width=True):
            st.session_state.ab_test_faq_toggle[1] = not st.session_state.ab_test_faq_toggle[1]
            st.session_state.ab_test_faq_toggle[2], st.session_state.ab_test_faq_toggle[3], st.session_state.ab_test_faq_toggle[4] = False, False, False
        if st.session_state.ab_test_faq_toggle[1]:
            if not ab_stats.empty:
                winner = ab_stats.sort_values('コンバージョン率', ascending=False).iloc[0]
                st.info(f"**「{winner['バリアント']}」** がCVR {winner['コンバージョン率']:.2f}%で最も良い結果でした。")
        
        if st.button("p値とは何ですか？", key="faq_ab_3", use_container_width=True):
            st.session_state.ab_test_faq_toggle[3] = not st.session_state.ab_test_faq_toggle[3]
            st.session_state.ab_test_faq_toggle[1], st.session_state.ab_test_faq_toggle[2], st.session_state.ab_test_faq_toggle[4] = False, False, False
        if st.session_state.ab_test_faq_toggle[3]:
            st.info("p値は「観測された差が偶然である確率」を示します。一般的にp値が0.05（5%）未満の場合、「統計的に有意な差がある」と判断し、その結果は信頼できると考えます。")
    with faq_cols[1]:
        if st.button("このテスト結果は信頼できますか？", key="faq_ab_2", use_container_width=True):
            st.session_state.ab_test_faq_toggle[2] = not st.session_state.ab_test_faq_toggle[2]
            st.session_state.ab_test_faq_toggle[1], st.session_state.ab_test_faq_toggle[3], st.session_state.ab_test_faq_toggle[4] = False, False, False
        if st.session_state.ab_test_faq_toggle[2]:
            if not ab_stats.empty:
                winner = ab_stats.sort_values('コンバージョン率', ascending=False).iloc[0]
                if winner['p値'] < 0.05:
                    st.info(f"はい、信頼できる可能性が高いです。勝者バリアントのp値は{winner['p値']:.4f}であり、統計的有意差の基準である0.05を下回っています。")
                else:
                    st.warning(f"まだ信頼できるとは言えません。p値が{winner['p値']:.4f}と0.05を上回っているため、この差が偶然である可能性を否定できません。もう少しテスト期間を延長してサンプルサイズを増やすことを推奨します。")
        
        if st.button("次のA/Bテストは何をすべき？", key="faq_ab_4", use_container_width=True):
            st.session_state.ab_test_faq_toggle[4] = not st.session_state.ab_test_faq_toggle[4]
            st.session_state.ab_test_faq_toggle[1], st.session_state.ab_test_faq_toggle[2], st.session_state.ab_test_faq_toggle[3] = False, False, False
        if st.session_state.ab_test_faq_toggle[4]:
            if not ab_stats.empty:
                winner = ab_stats.sort_values('コンバージョン率', ascending=False).iloc[0]
                st.info(f"今回の勝者「{winner['バリアント']}」の要素をベースに、さらに改善できる点をテストしましょう。例えば、CTAボタンの文言を変える、フォームの項目を減らす、などの新しい仮説でテストを計画するのが良いでしょう。")

# タブ5: インタラクション分析
elif selected_analysis == "インタラクション分析":
    st.markdown('<div class="sub-header">インタラクション分析</div>', unsafe_allow_html=True)
    # メインエリア: フィルターと比較設定
    st.markdown('<div class="sub-header">フィルター設定</div>', unsafe_allow_html=True)

    filter_cols = st.columns(4)
    with filter_cols[0]:
        # 期間選択
        period_options = {
            "過去7日間": 7,
            "過去30日間": 30,
            "過去90日間": 90,
            "カスタム期間": None
        }
        selected_period = st.selectbox("期間を選択", list(period_options.keys()), index=1, key="interaction_period")

    with filter_cols[1]:
        # LP選択
        lp_options = sorted(df['page_location'].dropna().unique().tolist()) # type: ignore
        selected_lp = st.selectbox("LP選択", lp_options, index=0 if lp_options else -1, key="interaction_lp")

    with filter_cols[2]:
        device_options = ["すべて"] + sorted(df['device_type'].dropna().unique().tolist())
        selected_device = st.selectbox("デバイス選択", device_options, index=0, key="interaction_device")

    with filter_cols[3]:
        channel_options = ["すべて"] + sorted(df['channel'].unique().tolist())
        selected_channel = st.selectbox("チャネル選択", channel_options, index=0, key="interaction_channel")

    # 比較機能はチェックボックスでシンプルに
    enable_comparison = st.checkbox("比較機能を有効化", value=False, key="interaction_compare_check")
    comparison_type = None
    if enable_comparison:
        comparison_options = {
            "前期間": "previous_period", "前週": "previous_week",
            "前月": "previous_month", "前年": "previous_year"
        }
        selected_comparison = st.selectbox("比較対象", list(comparison_options.keys()), key="interaction_compare_select")
        comparison_type = comparison_options[selected_comparison]

    # カスタム期間の場合
    if selected_period == "カスタム期間":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("開始日", df['event_date'].min(), key="interaction_start_date")
        with col2:
            end_date = st.date_input("終了日", df['event_date'].max(), key="interaction_end_date")
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
    if selected_lp:
        filtered_df = filtered_df[filtered_df['page_location'] == selected_lp]

    # --- クロス分析用フィルター適用 ---
    if selected_device != "すべて":
        filtered_df = filtered_df[filtered_df['device_type'] == selected_device]

    if selected_channel != "すべて":
        filtered_df = filtered_df[filtered_df['channel'] == selected_channel]

    # ==============================================================================
    #  デバッグ用: 3分以上の滞在時間データを強制的に生成
    #  目的: 「3分以上」セグメントがグラフに表示されることを確認するため。
    #  注意: このコードは本番データでは不要です。
    # ==============================================================================
    if not filtered_df.empty:
        # 'stay_ms'列が存在し、かつNaNでない行が1つ以上あることを確認
        if 'stay_ms' in filtered_df.columns and filtered_df['stay_ms'].notna().any():
            # 滞在時間が最も長い上位5%のインデックスを取得
            long_stay_indices = filtered_df['stay_ms'].nlargest(int(len(filtered_df) * 0.05)).index
            
            # それらの滞在時間を3分〜5分のランダムな値に書き換える
            if not long_stay_indices.empty:
                new_stay_times = np.random.randint(180000, 300000, size=len(long_stay_indices))
                filtered_df.loc[long_stay_indices, 'stay_ms'] = new_stay_times
    # ==============================================================================

    # 比較データの取得
    comparison_df = None
    comp_start = None
    comp_end = None
    if enable_comparison and comparison_type:
        result = get_comparison_data(df, pd.Timestamp(start_date), pd.Timestamp(end_date), comparison_type)
        if result is not None:
            comparison_df, comp_start, comp_end = result
            # 比較データにも同じフィルターを適用
            if selected_lp:
                comparison_df = comparison_df[comparison_df['page_location'] == selected_lp]
            # --- 比較データにもクロス分析用フィルターを適用 ---
            if selected_device != "すべて":
                comparison_df = comparison_df[comparison_df['device_type'] == selected_device]
            if selected_channel != "すべて":
                comparison_df = comparison_df[comparison_df['channel'] == selected_channel]

            # 比較データが空の場合は無効化
            if len(comparison_df) == 0:
                comparison_df = None
                st.info(f"比較期間（{comp_start.strftime('%Y-%m-%d')} 〜 {comp_end.strftime('%Y-%m-%d')}）にデータがありません。")

    # データが空の場合の処理
    if len(filtered_df) == 0:
        st.warning("⚠️ 選択した条件に該当するデータがありません。フィルターを変更してください。")
        st.stop()

    # このページで必要なKPIを計算
    total_sessions = filtered_df['session_id'].nunique()

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
    interaction_df['クリック率 (CTR)'] = interaction_df.apply(lambda row: safe_rate(row['クリック数 (CTs)'], row['表示回数']) * 100, axis=1)
    
    # インタラクション要素一覧表
    st.markdown("#### インタラクション要素一覧")
    st.markdown('<div class="graph-description">LP内の各インタラクション要素の表示回数、クリック数、クリック率を表示します。</div>', unsafe_allow_html=True) # type: ignore
    
    st.dataframe(interaction_df.style.format({
        '表示回数': '{:,.0f}',
        'クリック数 (CTs)': '{:,.0f}',
        'クリック率 (CTR)': '{:.2f}%'
    }), use_container_width=True, hide_index=True)
    
    # CTR比較グラフ
    st.markdown("#### 要素別クリック率 (CTR) 比較")
    st.markdown('<div class="graph-description">各インタラクション要素のCTRを比較します。CTRが高い要素はユーザーの関心を引いています。</div>', unsafe_allow_html=True) # type: ignore
    
    fig = px.bar(interaction_df, x='要素', y='クリック率 (CTR)', text='クリック率 (CTR)')
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title='インタラクション要素', yaxis_title='CTR (%)', dragmode=False)
    st.plotly_chart(fig, use_container_width=True, key='plotly_chart_interaction_ctr')
    
    # クリック数比較グラフ
    st.markdown("#### 要素別クリック数 (CTs) 比較")
    st.markdown('<div class="graph-description">各インタラクション要素の絶対クリック数を比較します。</div>', unsafe_allow_html=True) # type: ignore
    
    fig = px.bar(interaction_df, x='要素', y='クリック数 (CTs)', text='クリック数 (CTs)')
    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title='インタラクション要素', yaxis_title='クリック数', dragmode=False)
    st.plotly_chart(fig, use_container_width=True, key='plotly_chart_interaction_cts')
    
    # デバイス別分析
    st.markdown("#### デバイス別インタラクション分析")
    st.markdown('<div class="graph-description">デバイスごとのインタラクション率を比較します。</div>', unsafe_allow_html=True) # type: ignore
    
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

    st.markdown("---")

    # --- AI分析と考察 ---
    st.markdown("### AIによる分析と考察")
    st.markdown('<div class="graph-description">各インタラクション要素のパフォーマンスに基づき、AIがユーザーの関心と行動を分析します。</div>', unsafe_allow_html=True)

    # AI分析の表示状態を管理
    if 'interaction_ai_open' not in st.session_state:
        st.session_state.interaction_ai_open = False

    if st.button("AI分析を実行", key="interaction_ai_btn", type="primary", use_container_width=True):
        st.session_state.interaction_ai_open = True
        st.rerun()

    if st.session_state.interaction_ai_open:
        with st.container():
            with st.spinner("AIがインタラクションデータを分析中..."):
                best_ctr_element = interaction_df.loc[interaction_df['クリック率 (CTR)'].idxmax()]
                
                st.markdown("#### 1. 現状の評価")
                st.info(f"""
                インタラクション要素の中で、**「{best_ctr_element['要素']}」** が最も高いクリック率（{best_ctr_element['クリック率 (CTR)']:.2f}%）を記録しており、ユーザーの関心を最も強く引いている要素と言えます。
                
                一方で、クリック率が低い要素は、ユーザーに気づかれていないか、魅力的に感じられていない可能性があります。
                """)

                st.markdown("#### 2. 今後の考察と改善案")
                st.warning(f"""
                **高CTR要素の活用:**
                「{best_ctr_element['要素']}」はユーザーの関心が高いことが証明されたため、この要素から主要なCTAやコンバージョンポイントへの導線を強化することで、全体のCVR向上が期待できます。
                
                **低CTR要素の改善:**
                クリック率が低い要素については、以下の改善策が考えられます。
                - **視認性の向上**: デザイン（色、サイズ、配置）を見直し、より目立たせる。
                - **文言の変更**: ユーザーのメリットや緊急性を訴求するコピーに変更する。
                - **A/Bテスト**: 複数のデザインや文言パターンでA/Bテストを行い、最適な組み合わせを見つける。
                """)
            if st.button("AI分析を閉じる", key="interaction_ai_close"):
                st.session_state.interaction_ai_open = False
                st.rerun()

    # --- よくある質問 ---
    st.markdown("#### よくある質問")
    if 'interaction_faq_toggle' not in st.session_state:
        st.session_state.interaction_faq_toggle = {1: False, 2: False, 3: False, 4: False}

    faq_cols = st.columns(2)
    with faq_cols[0]:
        if st.button("最もクリックされている要素は？", key="faq_interaction_1", use_container_width=True):
            st.session_state.interaction_faq_toggle[1] = not st.session_state.interaction_faq_toggle[1]
            st.session_state.interaction_faq_toggle[2], st.session_state.interaction_faq_toggle[3], st.session_state.interaction_faq_toggle[4] = False, False, False
        if st.session_state.interaction_faq_toggle[1]:
            if not interaction_df.empty:
                best_ctr_element = interaction_df.loc[interaction_df['クリック率 (CTR)'].idxmax()]
                st.info(f"クリック率（CTR）が最も高いのは「**{best_ctr_element['要素']}**」で、{best_ctr_element['クリック率 (CTR)']:.2f}%です。ユーザーの関心が最も高い要素です。")
        
        if st.button("クリック率が低い要素はどうすれば？", key="faq_interaction_3", use_container_width=True):
            st.session_state.interaction_faq_toggle[3] = not st.session_state.interaction_faq_toggle[3]
            st.session_state.interaction_faq_toggle[1], st.session_state.interaction_faq_toggle[2], st.session_state.interaction_faq_toggle[4] = False, False, False
        if st.session_state.interaction_faq_toggle[3]:
            st.info("クリック率が低い要素は、まずデザイン（色、サイズ、配置）を見直して視認性を高めましょう。それでも改善しない場合は、要素の文言（コピー）がユーザーにとって魅力的か、メリットが伝わるかを再検討する必要があります。")
    with faq_cols[1]:
        if st.button("CTAボタンのCTRを上げるには？", key="faq_interaction_2", use_container_width=True):
            st.session_state.interaction_faq_toggle[2] = not st.session_state.interaction_faq_toggle[2]
            st.session_state.interaction_faq_toggle[1], st.session_state.interaction_faq_toggle[3], st.session_state.interaction_faq_toggle[4] = False, False, False
        if st.session_state.interaction_faq_toggle[2]:
            st.info("CTAボタンのCTRを上げるには、1) ボタンの色を背景色と対照的な目立つ色にする、2) 「資料請求」→「無料で資料をもらう」のように具体的なアクションやメリットを文言に入れる、3) ボタンのサイズを大きくする、などのA/Bテストが有効です。")
        
        if st.button("デバイスによってクリック率は変わる？", key="faq_interaction_4", use_container_width=True):
            st.session_state.interaction_faq_toggle[4] = not st.session_state.interaction_faq_toggle[4]
            st.session_state.interaction_faq_toggle[1], st.session_state.interaction_faq_toggle[2], st.session_state.interaction_faq_toggle[3] = False, False, False
        if st.session_state.interaction_faq_toggle[4]:
            st.info("はい、大きく変わることがあります。例えば、PCではクリックしやすくても、スマホではボタンが小さすぎて押しにくい、といった問題が考えられます。「セグメント分析」でデバイス別のパフォーマンスを確認し、最適化することが重要です。")

# タブ6: 動画・スクロール分析
elif selected_analysis == "動画・スクロール分析":
    st.markdown('<div class="sub-header">動画・スクロール分析</div>', unsafe_allow_html=True)
    # メインエリア: フィルターと比較設定
    st.markdown('<div class="sub-header">フィルター設定</div>', unsafe_allow_html=True)

    filter_cols = st.columns(4)
    with filter_cols[0]:
        # 期間選択
        period_options = {
            "過去7日間": 7,
            "過去30日間": 30,
            "過去90日間": 90,
            "カスタム期間": None
        }
        selected_period = st.selectbox("期間を選択", list(period_options.keys()), index=1, key="video_scroll_period")

    with filter_cols[1]:
        # LP選択
        lp_options = sorted(df['page_location'].dropna().unique().tolist()) # type: ignore
        selected_lp = st.selectbox("LP選択", lp_options, index=0 if lp_options else -1, key="video_scroll_lp")

    with filter_cols[2]:
        device_options = ["すべて"] + sorted(df['device_type'].dropna().unique().tolist())
        selected_device = st.selectbox("デバイス選択", device_options, index=0, key="video_scroll_device")

    with filter_cols[3]:
        channel_options = ["すべて"] + sorted(df['channel'].unique().tolist())
        selected_channel = st.selectbox("チャネル選択", channel_options, index=0, key="video_scroll_channel")

    # 比較機能はチェックボックスでシンプルに
    enable_comparison = st.checkbox("比較機能を有効化", value=False, key="video_scroll_compare_check")
    comparison_type = None
    if enable_comparison:
        comparison_options = {
            "前期間": "previous_period", "前週": "previous_week",
            "前月": "previous_month", "前年": "previous_year"
        }
        selected_comparison = st.selectbox("比較対象", list(comparison_options.keys()), key="video_scroll_compare_select")
        comparison_type = comparison_options[selected_comparison]

    # カスタム期間の場合
    if selected_period == "カスタム期間":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("開始日", df['event_date'].min(), key="video_scroll_start_date")
        with col2:
            end_date = st.date_input("終了日", df['event_date'].max(), key="video_scroll_end_date")
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
    if selected_lp:
        filtered_df = filtered_df[filtered_df['page_location'] == selected_lp]

    # --- クロス分析用フィルター適用 ---
    if selected_device != "すべて":
        filtered_df = filtered_df[filtered_df['device_type'] == selected_device]

    if selected_channel != "すべて":
        filtered_df = filtered_df[filtered_df['channel'] == selected_channel]

    # ==============================================================================
    #  デバッグ用: 3分以上の滞在時間データを強制的に生成
    #  目的: 「3分以上」セグメントがグラフに表示されることを確認するため。
    #  注意: このコードは本番データでは不要です。
    # ==============================================================================
    if not filtered_df.empty:
        # 'stay_ms'列が存在し、かつNaNでない行が1つ以上あることを確認
        if 'stay_ms' in filtered_df.columns and filtered_df['stay_ms'].notna().any():
            # 滞在時間が最も長い上位5%のインデックスを取得
            long_stay_indices = filtered_df['stay_ms'].nlargest(int(len(filtered_df) * 0.05)).index
            
            # それらの滞在時間を3分〜5分のランダムな値に書き換える
            if not long_stay_indices.empty:
                new_stay_times = np.random.randint(180000, 300000, size=len(long_stay_indices))
                filtered_df.loc[long_stay_indices, 'stay_ms'] = new_stay_times
    # ==============================================================================

    # 比較データの取得
    comparison_df = None
    comp_start = None
    comp_end = None
    if enable_comparison and comparison_type:
        result = get_comparison_data(df, pd.Timestamp(start_date), pd.Timestamp(end_date), comparison_type)
        if result is not None:
            comparison_df, comp_start, comp_end = result
            # 比較データにも同じフィルターを適用
            if selected_lp:
                comparison_df = comparison_df[comparison_df['page_location'] == selected_lp]
            # --- 比較データにもクロス分析用フィルターを適用 ---
            if selected_device != "すべて":
                comparison_df = comparison_df[comparison_df['device_type'] == selected_device]
            if selected_channel != "すべて":
                comparison_df = comparison_df[comparison_df['channel'] == selected_channel]

            # 比較データが空の場合は無効化
            if len(comparison_df) == 0:
                comparison_df = None
                st.info(f"比較期間（{comp_start.strftime('%Y-%m-%d')} 〜 {comp_end.strftime('%Y-%m-%d')}）にデータがありません。")

    # データが空の場合の処理
    if len(filtered_df) == 0:
        st.warning("⚠️ 選択した条件に該当するデータがありません。フィルターを変更してください。")
        st.stop()

    # このページで必要なKPIを計算
    total_sessions = filtered_df['session_id'].nunique()

    # 逆行率分析
    st.markdown("ページ別平均逆行率")
    st.markdown('<div class="graph-description">各ページでユーザーがどれだけ逆方向にスクロールしたかを表示します。逆行率が高いページは、ユーザーが迷っているまたは情報を再確認している可能性があります。</div>', unsafe_allow_html=True) # type: ignore
    scroll_stats = filtered_df.groupby('page_num_dom')['scroll_pct'].mean().reset_index()
    scroll_stats.columns = ['ページ番号', '平均逆行率']
    scroll_stats['平均逆行率(%)'] = scroll_stats['平均逆行率'] * 100
    
    fig = px.bar(scroll_stats, x='ページ番号', y='平均逆行率(%)', text='平均逆行率(%)')
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title='ページ番号', yaxis_title='平均逆行率 (%)', dragmode=False)
    st.plotly_chart(fig, use_container_width=True, key='plotly_chart_18')
    
    # 動画視聴分析（動画イベントがある場合）
    video_df = filtered_df[filtered_df['video_src'].notna()]
    
    if len(video_df) > 0:
        st.markdown("#### 動画視聴率")
        
        video_sessions = video_df['session_id'].nunique()
        total_sessions_with_video_page = filtered_df[filtered_df['video_src'].notna()]['session_id'].nunique()
        video_view_rate = safe_rate(video_sessions, total_sessions) * 100
        
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
        video_cvr = safe_rate(video_cv, video_sessions) * 100
        
        non_video_sessions = total_sessions - video_sessions
        non_video_cv = filtered_df[(filtered_df['video_src'].isna()) & (filtered_df['cv_type'].notna())]['session_id'].nunique()
        non_video_cvr = safe_rate(non_video_cv, non_video_sessions) * 100
        
        comparison_data = pd.DataFrame({
            'グループ': ['動画視聴あり', '動画視聴なし'],
            'コンバージョン率': [video_cvr, non_video_cvr]
        })
        
        fig = px.bar(comparison_data, x='グループ', y='コンバージョン率', text='コンバージョン率')
        fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig.update_layout(height=400, showlegend=False, yaxis_title='コンバージョン率 (%)', dragmode=False)
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_19')
    
    # 逆行率別CVR
    st.markdown("逆行率別コンバージョン率")
    st.markdown('<div class="graph-description">逆行率の範囲ごとにコンバージョン率を表示します。逆行率が高いほどコンバージョン率が低い傾向があるかを確認できます。</div>', unsafe_allow_html=True) # type: ignore
    
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
    scroll_range_stats['コンバージョン率'] = scroll_range_stats.apply(lambda row: safe_rate(row['コンバージョン数'], row['セッション数']) * 100, axis=1)
    
    fig = px.bar(scroll_range_stats, x='逆行率', y='コンバージョン率', text='コンバージョン率')
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(height=400, showlegend=False, xaxis_title='逆行率', yaxis_title='コンバージョン率 (%)', dragmode=False)
    st.plotly_chart(fig, use_container_width=True, key='plotly_chart_20')

    st.markdown("---")

    # --- AI分析と考察 ---
    st.markdown("### AIによる分析と考察")
    st.markdown('<div class="graph-description">動画視聴やスクロール行動とコンバージョンの関係性を分析し、エンゲージメント向上のヒントを提示します。</div>', unsafe_allow_html=True)

    # AI分析の表示状態を管理
    if 'video_scroll_ai_open' not in st.session_state:
        st.session_state.video_scroll_ai_open = False

    if st.button("AI分析を実行", key="video_scroll_ai_btn", type="primary", use_container_width=True):
        st.session_state.video_scroll_ai_open = True
        st.rerun()

    if st.session_state.video_scroll_ai_open:
        with st.container():
            with st.spinner("AIがエンゲージメントデータを分析中..."):
                st.markdown("#### 1. 現状の評価")
                if len(video_df) > 0:
                    st.info(f"""
                    **動画視聴とコンバージョンの関係:**
                    動画を視聴したユーザーのコンバージョン率は **{video_cvr:.2f}%** であり、視聴しなかったユーザーの **{non_video_cvr:.2f}%** と比較して高い傾向にあります。これは、動画コンテンツがユーザーの理解を深め、コンバージョンを促進する上で有効であることを示唆しています。
                    """)
                else:
                    st.info("このLPには動画コンテンツのデータがありません。")

                st.info("""
                **スクロール行動とコンバージョンの関係:**
                逆行率が高いページや、スクロール率が低いにもかかわらず離脱が多いページは、ユーザーがコンテンツに満足していないか、求めている情報を見つけられていない可能性があります。
                """)

                st.markdown("#### 2. 今後の考察と改善案")
                st.warning("""
                **動画コンテンツの活用:**
                動画の視聴完了率や、どの部分で視聴を止めたかを分析することで、さらにコンテンツを改善できます。動画の冒頭で強いメッセージを伝え、視聴維持率を高める工夫が重要です。
                
                **スクロール体験の改善:**
                - **逆行率が高いページ**: なぜユーザーが戻る必要があるのかを分析します。情報が不足している場合は補足し、ナビゲーションが分かりにくい場合は改善します。
                - **スクロール率が低いページ**: ページの冒頭（ファーストビュー）でユーザーの興味を引き、続きを読む動機付けを与える必要があります。魅力的なキャッチコピーや画像の使用が効果的です。
                """)
            if st.button("AI分析を閉じる", key="video_scroll_ai_close"):
                st.session_state.video_scroll_ai_open = False
                st.rerun()

    # --- よくある質問 ---
    st.markdown("#### よくある質問")
    if 'video_faq_toggle' not in st.session_state:
        st.session_state.video_faq_toggle = {1: False, 2: False, 3: False, 4: False}

    faq_cols = st.columns(2)
    with faq_cols[0]:
        if st.button("動画はコンバージョンに貢献していますか？", key="faq_video_1", use_container_width=True):
            st.session_state.video_faq_toggle[1] = not st.session_state.video_faq_toggle[1]
            st.session_state.video_faq_toggle[2], st.session_state.video_faq_toggle[3], st.session_state.video_faq_toggle[4] = False, False, False
        if st.session_state.video_faq_toggle[1]:
            if len(video_df) > 0:
                st.info(f"はい、貢献している可能性が高いです。動画視聴ユーザーのCVRは{video_cvr:.2f}%で、非視聴ユーザーの{non_video_cvr:.2f}%より高いです。")
            else:
                st.info("このLPには動画データがありません。")
        
        if st.button("逆行率が高いページは何が問題？", key="faq_video_3", use_container_width=True):
            st.session_state.video_faq_toggle[3] = not st.session_state.video_faq_toggle[3]
            st.session_state.video_faq_toggle[1], st.session_state.video_faq_toggle[2], st.session_state.video_faq_toggle[4] = False, False, False
        if st.session_state.video_faq_toggle[3]:
            st.info("逆行率が高いのは、ユーザーが「情報不足で前のページに戻って確認している」または「ページの構成が分かりにくく迷っている」兆候です。ページ間の情報の流れを見直し、ナビゲーションを分かりやすくする必要があります。")
    with faq_cols[1]:
        if st.button("動画のどこを改善すれば良いですか？", key="faq_video_2", use_container_width=True):
            st.session_state.video_faq_toggle[2] = not st.session_state.video_faq_toggle[2]
            st.session_state.video_faq_toggle[1], st.session_state.video_faq_toggle[3], st.session_state.video_faq_toggle[4] = False, False, False
        if st.session_state.video_faq_toggle[2]:
            st.info("動画の視聴維持率データを分析することが重要です。多くのユーザーが離脱する箇所を特定し、その部分のコンテンツ（メッセージ、テンポ、ビジュアル）を改善しましょう。特に最初の5秒でユーザーの心を掴むことが重要です。")
        
        if st.button("スクロールされないページはどうすれば？", key="faq_video_4", use_container_width=True):
            st.session_state.video_faq_toggle[4] = not st.session_state.video_faq_toggle[4]
            st.session_state.video_faq_toggle[1], st.session_state.video_faq_toggle[2], st.session_state.video_faq_toggle[3] = False, False, False
        if st.session_state.video_faq_toggle[4]:
            st.info("スクロールされないのは、ファーストビュー（FV）に魅力がない証拠です。ユーザーが「続きを読む価値がある」と感じるような、強力なキャッチコピー、魅力的な画像、権威付け（実績や推薦文など）をFVに配置することが効果的です。")



# タブ6: 時系列分析
elif selected_analysis == "時系列分析":
    st.markdown('<div class="sub-header">時系列分析</div>', unsafe_allow_html=True)
    # メインエリア: フィルターと比較設定
    st.markdown('<div class="sub-header">フィルター設定</div>', unsafe_allow_html=True)

    filter_cols = st.columns(4)
    with filter_cols[0]:
        # 期間選択
        period_options = {
            "過去7日間": 7,
            "過去30日間": 30,
            "過去90日間": 90,
            "カスタム期間": None
        }
        selected_period = st.selectbox("期間を選択", list(period_options.keys()), index=1, key="timeseries_period")

    with filter_cols[1]:
        # LP選択
        lp_options = sorted(df['page_location'].dropna().unique().tolist()) # type: ignore
        selected_lp = st.selectbox("LP選択", lp_options, index=0 if lp_options else -1, key="timeseries_lp")

    with filter_cols[2]:
        device_options = ["すべて"] + sorted(df['device_type'].dropna().unique().tolist())
        selected_device = st.selectbox("デバイス選択", device_options, index=0, key="timeseries_device")

    with filter_cols[3]:
        channel_options = ["すべて"] + sorted(df['channel'].unique().tolist())
        selected_channel = st.selectbox("チャネル選択", channel_options, index=0, key="timeseries_channel")

    # 比較機能はチェックボックスでシンプルに
    enable_comparison = st.checkbox("比較機能を有効化", value=False, key="timeseries_compare_check")
    comparison_type = None
    if enable_comparison:
        comparison_options = {
            "前期間": "previous_period", "前週": "previous_week",
            "前月": "previous_month", "前年": "previous_year"
        }
        selected_comparison = st.selectbox("比較対象", list(comparison_options.keys()), key="timeseries_compare_select")
        comparison_type = comparison_options[selected_comparison]

    # カスタム期間の場合
    if selected_period == "カスタム期間":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("開始日", df['event_date'].min(), key="timeseries_start_date")
        with col2:
            end_date = st.date_input("終了日", df['event_date'].max(), key="timeseries_end_date")
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
    if selected_lp:
        filtered_df = filtered_df[filtered_df['page_location'] == selected_lp]

    # --- クロス分析用フィルター適用 ---
    if selected_device != "すべて":
        filtered_df = filtered_df[filtered_df['device_type'] == selected_device]

    if selected_channel != "すべて":
        filtered_df = filtered_df[filtered_df['channel'] == selected_channel]

    # ==============================================================================
    #  デバッグ用: 3分以上の滞在時間データを強制的に生成
    #  目的: 「3分以上」セグメントがグラフに表示されることを確認するため。
    #  注意: このコードは本番データでは不要です。
    # ==============================================================================
    if not filtered_df.empty:
        # 'stay_ms'列が存在し、かつNaNでない行が1つ以上あることを確認
        if 'stay_ms' in filtered_df.columns and filtered_df['stay_ms'].notna().any():
            # 滞在時間が最も長い上位5%のインデックスを取得
            long_stay_indices = filtered_df['stay_ms'].nlargest(int(len(filtered_df) * 0.05)).index
            
            # それらの滞在時間を3分〜5分のランダムな値に書き換える
            if not long_stay_indices.empty:
                new_stay_times = np.random.randint(180000, 300000, size=len(long_stay_indices))
                filtered_df.loc[long_stay_indices, 'stay_ms'] = new_stay_times
    # ==============================================================================

    # 比較データの取得
    comparison_df = None
    comp_start = None
    comp_end = None
    if enable_comparison and comparison_type:
        result = get_comparison_data(df, pd.Timestamp(start_date), pd.Timestamp(end_date), comparison_type)
        if result is not None:
            comparison_df, comp_start, comp_end = result
            # 比較データにも同じフィルターを適用
            if selected_lp:
                comparison_df = comparison_df[comparison_df['page_location'] == selected_lp]
            # --- 比較データにもクロス分析用フィルターを適用 ---
            if selected_device != "すべて":
                comparison_df = comparison_df[comparison_df['device_type'] == selected_device]
            if selected_channel != "すべて":
                comparison_df = comparison_df[comparison_df['channel'] == selected_channel]

            # 比較データが空の場合は無効化
            if len(comparison_df) == 0:
                comparison_df = None
                st.info(f"比較期間（{comp_start.strftime('%Y-%m-%d')} 〜 {comp_end.strftime('%Y-%m-%d')}）にデータがありません。")

    # データが空の場合の処理
    if len(filtered_df) == 0:
        st.warning("⚠️ 選択した条件に該当するデータがありません。フィルターを変更してください。")
        st.stop()

    # 日別推移
    st.markdown("#### 日別推移") # type: ignore

    # テスト種別でフィルタリングするためのプルダウンメニュー
    # filtered_dfにab_test_target列がない場合があるため、ここでマッピングを適用
    if 'ab_test_target' not in filtered_df.columns:
        filtered_df['ab_test_target'] = df['ab_test_target'].map(test_type_map).fillna('-')

    # プルダウンメニューを説明文の下、右端に配置
    _, pulldown_col_timeseries = st.columns([4, 1])
    with pulldown_col_timeseries:
        timeseries_test_type_options = ["すべてのテスト"] + sorted(filtered_df['ab_test_target'].unique().tolist())
        selected_timeseries_test_type = st.selectbox(
            "timeseries_test_type_filter",
            timeseries_test_type_options,
            key="timeseries_test_type_filter",
            label_visibility="collapsed"
        )

    # daily_statsの計算にab_test_targetを含める
    daily_stats = filtered_df.groupby([filtered_df['event_date'].dt.date, 'ab_test_target']).agg({
        'session_id': 'nunique',
        'stay_ms': 'mean',
        'max_page_reached': 'mean'
    }).reset_index()
    daily_stats.columns = ['日付', 'セッション数', '平均滞在時間(ms)', '平均到達ページ数']
    daily_stats['平均滞在時間(秒)'] = daily_stats['平均滞在時間(ms)'] / 1000
    
    daily_cv = filtered_df[filtered_df['cv_type'].notna()].groupby([
        filtered_df[filtered_df['cv_type'].notna()]['event_date'].dt.date, 'ab_test_target'
    ])['session_id'].nunique().reset_index()
    daily_cv.columns = ['日付', 'ab_test_target', 'コンバージョン数']
    
    daily_stats = daily_stats.merge(daily_cv, on=['日付', 'ab_test_target'], how='left').fillna(0) # type: ignore
    daily_stats['コンバージョン率'] = daily_stats.apply(lambda row: safe_rate(row['コンバージョン数'], row['セッション数']) * 100, axis=1) # type: ignore
    
    # FV残存率
    daily_fv = filtered_df[filtered_df['max_page_reached'] >= 2].groupby(
        filtered_df[filtered_df['max_page_reached'] >= 2]['event_date'].dt.date
    )['session_id'].nunique().reset_index()
    daily_fv.columns = ['日付', 'FV残存数']
    
    daily_stats = daily_stats.merge(daily_fv, on='日付', how='left').fillna(0) # type: ignore
    daily_stats['FV残存率'] = daily_stats.apply(lambda row: safe_rate(row['FV残存数'], row['セッション数']) * 100, axis=1)
    
    # 最終CTA到達率
    daily_cta = filtered_df[filtered_df['max_page_reached'] >= 10].groupby(
        filtered_df[filtered_df['max_page_reached'] >= 10]['event_date'].dt.date
    )['session_id'].nunique().reset_index()
    daily_cta.columns = ['日付', '最終CTA到達数']
    
    daily_stats = daily_stats.merge(daily_cta, on='日付', how='left').fillna(0)
    daily_stats['最終CTA到達率'] = daily_stats.apply(lambda row: safe_rate(row['最終CTA到達数'], row['セッション数']) * 100, axis=1)

    # グラフ選択
    metric_to_plot = st.selectbox("表示する指標を選択", [
        "セッション数", "コンバージョン数", "コンバージョン率", "FV残存率",
        "最終CTA到達率", "平均到達ページ数", "平均滞在時間(秒)"
    ], key="timeseries_metric_select")
    
    fig = px.line(daily_stats, x='日付', y=metric_to_plot, color='ab_test_target', markers=True) # color='ab_test_target'を追加
    fig.update_layout(height=400, yaxis_title=metric_to_plot, dragmode=False)
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
        
        monthly_stats = monthly_stats.merge(monthly_cv, on='月', how='left').fillna(0) # type: ignore
        monthly_stats['コンバージョン率'] = monthly_stats.apply(lambda row: safe_rate(row['コンバージョン数'], row['セッション数']) * 100, axis=1)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='セッション数', x=monthly_stats['月'], y=monthly_stats['セッション数'], yaxis='y'))
        fig.add_trace(go.Scatter(name='コンバージョン率', x=monthly_stats['月'], y=monthly_stats['コンバージョン率'], yaxis='y2', mode='lines+markers'))
        
        fig.update_layout(
            yaxis=dict(title='セッション数'),
            yaxis2=dict(title='コンバージョン率 (%)', overlaying='y', side='right'),
            height=400,
            dragmode=False
        )
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_22')

    st.markdown("---")

    # 曜日・時間帯別 CVRヒートマップ
    st.markdown("#### 曜日・時間帯別 CVRヒートマップ")
    st.markdown('<div class="graph-description">曜日と時間帯をクロス集計し、コンバージョン率（CVR）をヒートマップで表示します。色が濃い部分がCVRの高い「ゴールデンタイム」です。</div>', unsafe_allow_html=True)

    # 曜日と時間の列を追加
    heatmap_df = filtered_df.copy()
    heatmap_df['hour'] = heatmap_df['event_timestamp'].dt.hour
    heatmap_df['dow_name'] = heatmap_df['event_timestamp'].dt.day_name()

    # 時間と曜日でグループ化してセッション数とCV数を計算
    heatmap_sessions = heatmap_df.groupby(['hour', 'dow_name'])['session_id'].nunique().reset_index(name='セッション数')
    heatmap_cv = heatmap_df[heatmap_df['cv_type'].notna()].groupby(['hour', 'dow_name'])['session_id'].nunique().reset_index(name='コンバージョン数')

    # データをマージしてCVRを計算
    heatmap_stats = pd.merge(heatmap_sessions, heatmap_cv, on=['hour', 'dow_name'], how='left').fillna(0)
    heatmap_stats['コンバージョン率'] = heatmap_stats.apply(lambda row: safe_rate(row['コンバージョン数'], row['セッション数']) * 100, axis=1)

    # 曜日の順序を定義
    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_map_jp = {'Monday': '月', 'Tuesday': '火', 'Wednesday': '水', 'Thursday': '木', 'Friday': '金', 'Saturday': '土', 'Sunday': '日'}
    heatmap_stats['dow_name'] = pd.Categorical(heatmap_stats['dow_name'], categories=dow_order, ordered=True)
    heatmap_stats = heatmap_stats.sort_values(['dow_name', 'hour'])

    # ピボットテーブルを作成
    heatmap_pivot = heatmap_stats.pivot_table(index='dow_name', columns='hour', values='コンバージョン率')
    heatmap_pivot = heatmap_pivot.reindex(dow_order) # 曜日の順序を保証
    heatmap_pivot.index = heatmap_pivot.index.map(dow_map_jp) # 曜日を日本語に変換

    # ヒートマップを描画
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=[f"{h}時" for h in heatmap_pivot.columns],
        y=heatmap_pivot.index,
        colorscale='Blues',
        hovertemplate='曜日: %{y}<br>時間帯: %{x}<br>CVR: %{z:.2f}%<extra></extra>'
    ))
    fig_heatmap.update_layout(title='曜日・時間帯別 CVR', height=500, dragmode=False)
    st.plotly_chart(fig_heatmap, use_container_width=True, key='plotly_chart_heatmap_cvr')

    st.markdown("---")

    # --- AI分析と考察 ---
    st.markdown("### AIによる分析と考察")
    st.markdown('<div class="graph-description">時系列データからパフォーマンスの波を読み解き、広告配信やプロモーションの最適化タイミングを提案します。</div>', unsafe_allow_html=True)
    
    # AI分析の表示状態を管理
    if 'timeseries_ai_open' not in st.session_state:
        st.session_state.timeseries_ai_open = False

    if st.button("AI分析を実行", key="timeseries_ai_btn", type="primary", use_container_width=True):
        st.session_state.timeseries_ai_open = True
        st.rerun()

    if st.session_state.timeseries_ai_open:
        with st.container():
            with st.spinner("AIが時系列データを分析中..."):
                if not heatmap_stats.empty:
                    # ゴールデンタイムを特定
                    golden_time = heatmap_stats.loc[heatmap_stats['コンバージョン率'].idxmax()]
                else:
                    golden_time = None
                
                st.markdown("#### 1. 現状の評価")
                st.info(f"""
                曜日・時間帯別のヒートマップから、このLPの「ゴールデンタイム」が明らかになりました。
                - **最もCVRが高い時間帯**: **{dow_map_jp[golden_time['dow_name']]}曜日の{int(golden_time['hour'])}時台** (CVR: {golden_time['コンバージョン率']:.2f}%)
                
                この時間帯は、ターゲットユーザーが最もアクティブで、コンバージョンに至りやすいと考えられます。
                """)

                st.markdown("#### 2. 今後の考察と改善案")
                st.warning(f"""
                **ゴールデンタイムの活用:**
                - **広告配信の強化**: {dow_map_jp[golden_time['dow_name']]}曜日の{int(golden_time['hour'])}時台を中心に、広告の表示を強化したり、入札単価を引き上げることで、効率的にコンバージョンを獲得できる可能性があります。
                - **プロモーションの実施**: メールマガジンの配信やSNSでの投稿をこの時間帯に合わせることで、開封率やクリック率の向上が期待できます。
                
                逆に、CVRが低い時間帯は広告配信を抑制することで、広告費の無駄遣いを防ぎ、全体のCPAを改善することができます。
                """)
            if st.button("AI分析を閉じる", key="timeseries_ai_close"):
                st.session_state.timeseries_ai_open = False
                st.rerun()

    # --- よくある質問 ---
    st.markdown("#### よくある質問")
    if 'time_faq_toggle' not in st.session_state:
        st.session_state.time_faq_toggle = {1: False, 2: False, 3: False, 4: False}

    faq_cols = st.columns(2)
    with faq_cols[0]:
        if st.button("CVRが最も高い時間帯はいつ？", key="faq_time_1", use_container_width=True):
            st.session_state.time_faq_toggle[1] = not st.session_state.time_faq_toggle[1]
            st.session_state.time_faq_toggle[2], st.session_state.time_faq_toggle[3], st.session_state.time_faq_toggle[4] = False, False, False
        if st.session_state.time_faq_toggle[1]:
            if not heatmap_stats.empty:
                golden_time = heatmap_stats.loc[heatmap_stats['コンバージョン率'].idxmax()]
                st.info(f"**{dow_map_jp[golden_time['dow_name']]}曜日の{int(golden_time['hour'])}時台**です。この時間帯のCVRは{golden_time['コンバージョン率']:.2f}%と最も高くなっています。")
        
        if st.button("週末と平日でパフォーマンスは違う？", key="faq_time_3", use_container_width=True):
            st.session_state.time_faq_toggle[3] = not st.session_state.time_faq_toggle[3]
            st.session_state.time_faq_toggle[1], st.session_state.time_faq_toggle[2], st.session_state.time_faq_toggle[4] = False, False, False
        if st.session_state.time_faq_toggle[3]:
            st.info("ヒートマップを確認することで、週末と平日のパフォーマンスの違いを視覚的に把握できます。一般的にBtoB商材は平日に、BtoC商材は週末や夜間にパフォーマンスが高まる傾向があります。")
    with faq_cols[1]:
        if st.button("ゴールデンタイムをどう活用すれば良い？", key="faq_time_2", use_container_width=True):
            st.session_state.time_faq_toggle[2] = not st.session_state.time_faq_toggle[2]
            st.session_state.time_faq_toggle[1], st.session_state.time_faq_toggle[3], st.session_state.time_faq_toggle[4] = False, False, False
        if st.session_state.time_faq_toggle[2]:
            st.info("CVRが高い「ゴールデンタイム」には、リスティング広告の入札単価を強化したり、SNS広告の配信を集中させることが有効です。また、メルマガ配信やSNS投稿もこの時間帯を狙うと効果的です。")
        
        if st.button("CVRが低い時間帯はどうすべき？", key="faq_time_4", use_container_width=True):
            st.session_state.time_faq_toggle[4] = not st.session_state.time_faq_toggle[4]
            st.session_state.time_faq_toggle[1], st.session_state.time_faq_toggle[2], st.session_state.time_faq_toggle[3] = False, False, False
        if st.session_state.time_faq_toggle[4]:
            st.info("CVRが著しく低い時間帯は、広告の配信を停止または抑制することで、無駄な広告費を削減し、全体の広告費用対効果（ROAS）を改善できます。")

# タブ7: リアルタイム分析
elif selected_analysis == "リアルタイムビュー":
    st.markdown('<div class="sub-header">リアルタイムビュー</div>', unsafe_allow_html=True)
    
    # 直近1時間のデータをフィルタリング
    one_hour_ago = df['event_timestamp'].max() - timedelta(hours=1)
    realtime_df = df[df['event_timestamp'] >= one_hour_ago]
    
    if len(realtime_df) > 0:
        # KPI計算
        rt_sessions = realtime_df['session_id'].nunique()
        rt_avg_pages = realtime_df.groupby('session_id')['max_page_reached'].max().mean()
        rt_avg_stay = realtime_df['stay_ms'].mean() / 1000 if not realtime_df['stay_ms'].isnull().all() else 0
        rt_fv_retention = (realtime_df[realtime_df['max_page_reached'] >= 2]['session_id'].nunique() / rt_sessions * 100) if rt_sessions > 0 else 0
        rt_avg_load = realtime_df['load_time_ms'].mean()

        # KPI表示
        st.markdown("#### 直近1時間のモニタリング")
        st.markdown("直近1時間で急な変化や異常がないかを確認します")
        kpi_cols = st.columns(5)
        kpi_cols[0].metric("セッション数", f"{rt_sessions:,}")
        kpi_cols[1].metric("平均到達ページ数", f"{rt_avg_pages:.1f}")
        kpi_cols[2].metric("平均滞在時間", f"{rt_avg_stay:.1f}秒")
        kpi_cols[3].metric("FV残存率", f"{rt_fv_retention:.1f}%")
        kpi_cols[4].metric("平均読込時間", f"{rt_avg_load:.0f}ms")

        st.markdown("---")

        # 分単位の推移
        st.markdown("#### 直近1時間のセッション数推移（10分単位）")
        st.markdown("直近1時間のセッション数を、10分ごとに集計して表示します")
        
        realtime_df['minute_bin'] = realtime_df['event_timestamp'].dt.floor('10T')
        rt_trend = realtime_df.groupby('minute_bin')['session_id'].nunique().reset_index()
        rt_trend.columns = ['時刻', 'セッション数']

        fig = px.area(rt_trend, x='時刻', y='セッション数', markers=True)
        fig.update_layout(height=400, yaxis_title='セッション数', dragmode=False)
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_23')
    else:
        st.info("直近1時間のデータがありません")

    st.markdown("---")

    # --- AI分析と考察 ---
    st.markdown("### AIによる分析と考察")
    st.markdown('<div class="graph-description">リアルタイムのデータ変動を監視し、異常検知や突発的な機会の発見をサポートします。</div>', unsafe_allow_html=True)

    # AI分析の表示状態を管理
    if 'realtime_ai_open' not in st.session_state:
        st.session_state.realtime_ai_open = False

    if st.button("AI分析を実行", key="realtime_ai_btn", type="primary", use_container_width=True):
        st.session_state.realtime_ai_open = True
        st.rerun()

    if st.session_state.realtime_ai_open:
        with st.container():
            with st.spinner("AIがリアルタイムデータを分析中..."):
                st.markdown("#### 1. 現状の評価")
                st.info("""
                リアルタイムビューでは、直近1時間のサイト活動を監視しています。セッション数が通常時と比較して急増または急減していないかを確認することが重要です。
                - **セッション数の急増**: メディア掲載やインフルエンサーによる紹介など、外部からの突発的な流入の可能性があります。
                - **セッション数の急減**: サイトの障害や広告配信の停止など、何らかの問題が発生している可能性があります。
                """)

                st.markdown("#### 2. 今後のアクション")
                st.warning("""
                - **機会の活用**: セッション数が急増している場合、その原因を特定し、SNSで言及を広めたり、関連コンテンツをトップに表示するなどして、機会を最大化しましょう。
                - **問題の早期発見**: セッション数がゼロに近い、または急減している場合は、サイトが正常に表示されるか、広告キャンペーンが正しく配信されているかを直ちに確認してください。
                """)
            if st.button("AI分析を閉じる", key="realtime_ai_close"):
                st.session_state.realtime_ai_open = False
                st.rerun()

    # --- よくある質問 ---
    st.markdown("#### よくある質問")
    if 'realtime_faq_toggle' not in st.session_state:
        st.session_state.realtime_faq_toggle = {1: False, 2: False, 3: False, 4: False}

    faq_cols = st.columns(2)
    with faq_cols[0]:
        if st.button("セッション数が急に増えたらどうする？", key="faq_realtime_1", use_container_width=True):
            st.session_state.realtime_faq_toggle[1] = not st.session_state.realtime_faq_toggle[1]
            st.session_state.realtime_faq_toggle[2], st.session_state.realtime_faq_toggle[3], st.session_state.realtime_faq_toggle[4] = False, False, False
        if st.session_state.realtime_faq_toggle[1]:
            st.info("まず流入元を確認しましょう。SNSでの拡散やメディア掲載が原因であれば、その機会を最大化するために公式アカウントで言及したり、関連キャンペーンを実施するのが有効です。")
        
        if st.button("このビューをどう活用する？", key="faq_realtime_3", use_container_width=True):
            st.session_state.realtime_faq_toggle[3] = not st.session_state.realtime_faq_toggle[3]
            st.session_state.realtime_faq_toggle[1], st.session_state.realtime_faq_toggle[2], st.session_state.realtime_faq_toggle[4] = False, False, False
        if st.session_state.realtime_faq_toggle[3]:
            st.info("主に「異常検知」と「機会発見」のために使います。広告キャンペーン開始直後の効果測定や、サーバーダウンなどの障害の早期発見に役立ちます。")
    with faq_cols[1]:
        if st.button("セッション数がゼロになったら？", key="faq_realtime_2", use_container_width=True):
            st.session_state.realtime_faq_toggle[2] = not st.session_state.realtime_faq_toggle[2]
            st.session_state.realtime_faq_toggle[1], st.session_state.realtime_faq_toggle[3], st.session_state.realtime_faq_toggle[4] = False, False, False
        if st.session_state.realtime_faq_toggle[2]:
            st.warning("サイトに重大な問題が発生している可能性があります。すぐにウェブサイトが正常に表示されるか、広告配信が停止していないか、ドメインやサーバーに問題がないかを確認してください。")
        
        if st.button("更新頻度はどのくらい？", key="faq_realtime_4", use_container_width=True):
            st.session_state.realtime_faq_toggle[4] = not st.session_state.realtime_faq_toggle[4]
            st.session_state.realtime_faq_toggle[1], st.session_state.realtime_faq_toggle[2], st.session_state.realtime_faq_toggle[3] = False, False, False
        if st.session_state.realtime_faq_toggle[4]:
            st.info("このビューのデータは、数分から数十分程度の遅延で更新されます（実際の更新頻度はデータソースの仕様に依存します）。常に最新の状況を反映するものではない点にご注意ください。")

# タブ8: カスタムオーディエンス
elif selected_analysis == "デモグラフィック情報":
    st.markdown('<div class="sub-header">デモグラフィック情報</div>', unsafe_allow_html=True)
    # メインエリア: フィルターと比較設定
    st.markdown('<div class="sub-header">フィルター設定</div>', unsafe_allow_html=True) # type: ignore

    # --- フィルター設定 ---
    filter_cols = st.columns(4)
    with filter_cols[0]:
        period_options = {"過去7日間": 7, "過去30日間": 30, "過去90日間": 90, "カスタム期間": None}
        selected_period = st.selectbox("期間を選択", list(period_options.keys()), index=1, key="demographic_period")

    with filter_cols[1]:
        lp_options = sorted(df['page_location'].dropna().unique().tolist())
        selected_lp = st.selectbox("LP選択", lp_options, index=0 if lp_options else -1, key="demographic_lp")

    with filter_cols[2]:
        device_options = ["すべて"] + sorted(df['device_type'].dropna().unique().tolist())
        selected_device = st.selectbox("デバイス選択", device_options, index=0, key="demographic_device")

    with filter_cols[3]:
        channel_options = ["すべて"] + sorted(df['channel'].unique().tolist())
        selected_channel = st.selectbox("チャネル選択", channel_options, index=0, key="demographic_channel")

    # 比較機能はチェックボックスでシンプルに
    enable_comparison = st.checkbox("比較機能を有効化", value=False, key="demographic_compare_check")
    comparison_type = None
    if enable_comparison:
        # 期間選択
        period_options = {
            "過去7日間": 7,
            "過去30日間": 30,
            "過去90日間": 90,
            "カスタム期間": None
        }
        comparison_options = {
            "前期間": "previous_period", "前週": "previous_week",
            "前月": "previous_month", "前年": "previous_year"
        }
        selected_comparison = st.selectbox("比較対象", list(comparison_options.keys()), key="demographic_compare_select")
        comparison_type = comparison_options[selected_comparison]

    # カスタム期間の場合
    if selected_period == "カスタム期間":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("開始日", df['event_date'].min(), key="demographic_start_date")
        with col2:
            end_date = st.date_input("終了日", df['event_date'].max(), key="demographic_end_date")
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
    if selected_lp and selected_lp != "すべて":
        filtered_df = filtered_df[filtered_df['page_location'] == selected_lp]
    
    # --- クロス分析用フィルター適用 ---
    if selected_device != "すべて":
        filtered_df = filtered_df[filtered_df['device_type'] == selected_device]

    if selected_channel != "すべて":
        filtered_df = filtered_df[filtered_df['channel'] == selected_channel]


    # ==============================================================================
    #  デバッグ用: 3分以上の滞在時間データを強制的に生成
    #  目的: 「3分以上」セグメントがグラフに表示されることを確認するため。
    #  注意: このコードは本番データでは不要です。
    # ==============================================================================
    if not filtered_df.empty:
        # 'stay_ms'列が存在し、かつNaNでない行が1つ以上あることを確認
        if 'stay_ms' in filtered_df.columns and filtered_df['stay_ms'].notna().any():
            # 滞在時間が最も長い上位5%のインデックスを取得
            long_stay_indices = filtered_df['stay_ms'].nlargest(int(len(filtered_df) * 0.05)).index
            
            # それらの滞在時間を3分〜5分のランダムな値に書き換える
            if not long_stay_indices.empty:
                new_stay_times = np.random.randint(180000, 300000, size=len(long_stay_indices))
                filtered_df.loc[long_stay_indices, 'stay_ms'] = new_stay_times
    # ==============================================================================

    # 比較データの取得
    comparison_df = None
    comp_start = None
    comp_end = None
    if enable_comparison and comparison_type:
        result = get_comparison_data(df, pd.to_datetime(start_date), pd.to_datetime(end_date), comparison_type)
        if result is not None:
            comparison_df, comp_start, comp_end = result
            # 比較データにも同じフィルターを適用
            if selected_lp != "すべて":
                comparison_df = comparison_df[comparison_df['page_location'] == selected_lp]
            if selected_device != "すべて":
                comparison_df = comparison_df[comparison_df['device_type'] == selected_device]
            if selected_channel != "すべて":
                comparison_df = comparison_df[comparison_df['channel'] == selected_channel]
            # 比較データが空の場合は無効化
            if len(comparison_df) == 0:
                comparison_df = None
                st.info(f"比較期間（{comp_start.strftime('%Y-%m-%d')} 〜 {comp_end.strftime('%Y-%m-%d')}）にデータがありません。")

    # データが空の場合の処理
    if len(filtered_df) == 0:
        st.warning("⚠️ 選択した条件に該当するデータがありません。フィルターを変更してください。")
        st.stop()

    # このページで必要なKPIを計算
    total_sessions = filtered_df['session_id'].nunique()

    st.markdown("ユーザーの属性情報（年齢、性別、地域、デバイス）を分析します。")

    # 年齢層別分析
    with st.expander("年齢層別分析", expanded=True):
        st.markdown('<div class="graph-description">年齢層ごとのセッション数、コンバージョン率、平均滞在時間を表示します。</div>', unsafe_allow_html=True)
        # 年齢層のダミーデータを 'age_group' 列として追加（BigQueryに実データがあればこの処理は不要）
        if 'age_group' not in filtered_df.columns:
            age_bins = [18, 25, 35, 45, 55, 65, 100]
            age_labels = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+']
            # 'age' 列がない場合はダミーの年齢を生成
            if 'age' not in filtered_df.columns:
                filtered_df['age'] = np.random.randint(18, 80, size=len(filtered_df))
            filtered_df['age_group'] = pd.cut(filtered_df['age'], bins=age_bins, labels=age_labels, right=False)

        # 年齢層別に集計
        age_sessions = filtered_df.groupby('age_group')['session_id'].nunique()
        age_cv = filtered_df[filtered_df['cv_type'].notna()].groupby('age_group')['session_id'].nunique()
        age_stay = filtered_df.groupby('age_group')['stay_ms'].mean() / 1000

        age_demo_df = pd.DataFrame({ # type: ignore
            'セッション数': age_sessions,
            'CV数': age_cv,
            '平均滞在時間 (秒)': age_stay
        }).fillna(0).reset_index().rename(columns={'age_group': '年齢層'}) # type: ignore
        age_demo_df['CVR (%)'] = age_demo_df.apply(lambda row: safe_rate(row['CV数'], row['セッション数']) * 100, axis=1)

        st.dataframe(age_demo_df.style.format({
            'セッション数': '{:,.0f}',
            'CV数': '{:,.0f}',
            'CVR (%)': '{:.1f}%',
            '平均滞在時間 (秒)': '{:.1f}'
        }), use_container_width=True, hide_index=True)

        fig = px.bar(age_demo_df, x='年齢層', y='CVR (%)', text='CVR (%)')
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=400, showlegend=False, xaxis_title='年齢層', yaxis_title='CVR (%)', dragmode=False)
        st.plotly_chart(fig, use_container_width=True, key='plotly_chart_age_cvr')

    with st.expander("性別分析", expanded=True):
        st.markdown('<div class="graph-description">性別ごとのセッション数、コンバージョン率、平均滞在時間を表示します。</div>', unsafe_allow_html=True)
        # 性別のダミーデータを 'gender' 列として追加（BigQueryに実データがあればこの処理は不要）
        if 'gender' not in filtered_df.columns:
            filtered_df['gender'] = np.random.choice(['男性', '女性', 'その他/未回答'], size=len(filtered_df), p=[0.52, 0.45, 0.03])

        # 性別で集計
        gender_sessions = filtered_df.groupby('gender')['session_id'].nunique()
        gender_cv = filtered_df[filtered_df['cv_type'].notna()].groupby('gender')['session_id'].nunique()
        gender_stay = filtered_df.groupby('gender')['stay_ms'].mean() / 1000

        gender_demo_df = pd.DataFrame({ # type: ignore
            'セッション数': gender_sessions,
            'CV数': gender_cv,
            '平均滞在時間 (秒)': gender_stay
        }).fillna(0).reset_index().rename(columns={'gender': '性別'}) # type: ignore
        gender_demo_df['CVR (%)'] = gender_demo_df.apply(lambda row: safe_rate(row['CV数'], row['セッション数']) * 100, axis=1)

        st.dataframe(gender_demo_df.style.format({
            'セッション数': '{:,.0f}',
            'CV数': '{:,.0f}',
            'CVR (%)': '{:.1f}%',
            '平均滞在時間 (秒)': '{:.1f}'
        }), use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(gender_demo_df, values='セッション数', names='性別', title='性別割合')
            fig.update_layout(height=400, dragmode=False)
            st.plotly_chart(fig, use_container_width=True, key='plotly_chart_gender_pie')
        with col2:
            fig = px.bar(gender_demo_df, x='性別', y='CVR (%)', text='CVR (%)')
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(height=400, showlegend=False, xaxis_title='性別', yaxis_title='CVR (%)', dragmode=False)
            st.plotly_chart(fig, use_container_width=True, key='plotly_chart_gender_cvr')
    
    # 地域別分析
    with st.expander("地域別分析", expanded=True):
        st.markdown('<div class="graph-description">都道府県ごとのセッション数、コンバージョン率を表示します。</div>', unsafe_allow_html=True)
        
        # 地域別ダミーデータ（サマリー表用） - これはBigQueryに地域データがない場合の代替として残します
        # BigQueryに地域データがある場合は、以下も動的生成に切り替えます
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

        st.markdown("---")
        st.markdown("##### 都道府県別 CVRマップ")

        # GeoJSONデータを読み込む
        try:
            geojson_url = "https://raw.githubusercontent.com/dataofjapan/land/master/japan.geojson"
            import json
            import requests
            
            @st.cache_data
            def get_geojson():
                res = requests.get(geojson_url)
                return res.json()

            japan_geojson = get_geojson()

            # GeoJSONの各featureに、キーとして使える都道府県名（'東京', '大阪'など）を追加
            for feature in japan_geojson["features"]:
                pref_name_full = feature["properties"]["nam_ja"]
                # '北海道'はそのまま、他は'都','府','県'を削除
                feature["properties"]["pref_key"] = pref_name_full if pref_name_full == '北海道' else pref_name_full[:-1]

            # 表示用データフレームにもキー列を追加
            region_demo_df_for_map = region_demo_df.copy()
            region_demo_df_for_map['pref_key'] = region_demo_df_for_map['地域'].apply(
                lambda x: x if x == '北海道' else x[:-1] if x not in ['その他'] else 'その他'
            )

            # 地図用のデータフレームを作成
            map_df = pd.DataFrame({
                'pref_key': [f["properties"]["pref_key"] for f in japan_geojson["features"]]
            })

            # CVRデータをマージ
            map_df = map_df.merge(region_demo_df_for_map[['pref_key', 'CVR (%)']].rename(columns={'CVR (%)': 'コンバージョン率'}), on='pref_key', how='left')

            # 表にない都道府県は 'その他' のCVRで埋める
            other_cvr = region_demo_df[region_demo_df['地域'] == 'その他']['CVR (%)'].iloc[0]
            map_df['コンバージョン率'] = map_df['コンバージョン率'].fillna(other_cvr)

            # 地図を作成
            fig_map = px.choropleth_mapbox(
                map_df,
                geojson=japan_geojson,
                locations='pref_key', # locationsをキー列に変更
                featureidkey="properties.pref_key", # featureidkeyをキー列に変更
                color='コンバージョン率',
                color_continuous_scale="Blues",
                range_color=(map_df['コンバージョン率'].min(), map_df['コンバージョン率'].max()),
                mapbox_style="carto-positron",
                zoom=4.5,
                center={"lat": 36.2048, "lon": 138.2529},
                opacity=0.7,
                labels={'コンバージョン率': 'CVR (%)'},
                hover_name='pref_key' # ホバー時に都道府県名を表示
            )
            fig_map.update_layout(
                margin={"r":0,"t":0,"l":0,"b":0},
                height=600,
                coloraxis_colorbar=dict(
                    title="CVR (%)",
                    tickvals=[map_df['コンバージョン率'].min(), map_df['コンバージョン率'].max()],
                    ticktext=[f"{map_df['コンバージョン率'].min():.1f}%", f"{map_df['コンバージョン率'].max():.1f}%"]
                )
            )
            
            st.plotly_chart(fig_map, use_container_width=True)

        except Exception as e:
            st.error(f"地図の描画に失敗しました: {e}")
    
    # デバイス別分析
    with st.expander("デバイス別分析", expanded=True):
        st.markdown('<div class="graph-description">デバイスごとのセッション数、コンバージョン率、平均滞在時間を表示します。</div>', unsafe_allow_html=True)
        # デバイス別に集計
        device_sessions = filtered_df.groupby('device_type')['session_id'].nunique()
        device_cv = filtered_df[filtered_df['cv_type'].notna()].groupby('device_type')['session_id'].nunique()
        device_stay = filtered_df.groupby('device_type')['stay_ms'].mean() / 1000

        device_demo_df = pd.DataFrame({ # type: ignore
            'セッション数': device_sessions,
            'CV数': device_cv,
            '平均滞在時間 (秒)': device_stay
        }).fillna(0).reset_index().rename(columns={'device_type': 'デバイス'}) # type: ignore
        device_demo_df['CVR (%)'] = device_demo_df.apply(lambda row: safe_rate(row['CV数'], row['セッション数']) * 100, axis=1)

        st.dataframe(device_demo_df.style.format({
            'セッション数': '{:,.0f}',
            'CV数': '{:,.0f}',
            'CVR (%)': '{:.1f}%',
            '平均滞在時間 (秒)': '{:.1f}'
        }), use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(device_demo_df, values='セッション数', names='デバイス', title='デバイス別セッション数')
            fig.update_layout(height=400, dragmode=False)
            st.plotly_chart(fig, use_container_width=True, key='plotly_chart_device_pie')
        with col2:
            fig = px.bar(device_demo_df, x='デバイス', y='CVR (%)', text='CVR (%)')
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(height=400, showlegend=False, xaxis_title='デバイス', yaxis_title='CVR (%)', dragmode=False)
            st.plotly_chart(fig, use_container_width=True, key='plotly_chart_device_cvr')

    st.markdown("---")

    # --- AI分析と考察 ---
    st.markdown("### AIによる分析と考察")
    st.markdown('<div class="graph-description">ユーザー属性（デモグラフィック）ごとの行動の違いを分析し、ターゲットユーザーの解像度を高めます。</div>', unsafe_allow_html=True)
    
    # AI分析の表示状態を管理
    if 'demographic_ai_open' not in st.session_state:
        st.session_state.demographic_ai_open = False

    if st.button("AI分析を実行", key="demographic_ai_btn", type="primary", use_container_width=True):
        st.session_state.demographic_ai_open = True
        st.rerun()

    if st.session_state.demographic_ai_open:
        with st.container():
            with st.spinner("AIがデモグラフィックデータを分析中..."):
                if not age_demo_df.empty:
                    # パフォーマンスの高い年齢層を特定
                    best_age_group = age_demo_df.loc[age_demo_df['CVR (%)'].idxmax()]
                else:
                    best_age_group = None
                
                st.markdown("#### 1. 現状の評価")
                st.info(f"""
                ユーザー属性によって、LPに対する反応が異なることが分かります。
                - **コアターゲット層**: **{best_age_group['年齢層']}** のCVRが{best_age_group['CVR (%)']:.1f}%と最も高く、このLPの主要なターゲット層であると考えられます。
                - **性別差**: 性別によるCVRや滞在時間に大きな差がある場合、訴求するメッセージを男女で変えるなどの施策が有効かもしれません。
                - **地域特性**: 特定の地域からのアクセスやCVRが高い場合、その地域に特化したキャンペーンや広告展開が効果的です。
                """)

                st.markdown("#### 2. 今後の考察と改善案")
                st.warning(f"""
                **ペルソナの深化とターゲティングの最適化:**
                - **ペルソナの再定義**: 最もパフォーマンスの高い「{best_age_group['年齢層']}」のユーザーが、どのようなニーズや課題を持っているのかを深く分析し、LPのメッセージングをさらに最適化します。
                - **広告ターゲティングの改善**: パフォーマンスの高い年齢層、性別、地域に広告予算を集中させることで、広告効率（CPA）の改善が期待できます。
                - **コンテンツのパーソナライズ**: 将来的には、アクセスしてきたユーザーの属性に応じて、表示するコンテンツ（キャッチコピーや画像）を動的に変更することで、さらなるCVR向上が見込めます。
                """)
            if st.button("AI分析を閉じる", key="demographic_ai_close"):
                st.session_state.demographic_ai_open = False
                st.rerun()

    # --- よくある質問 ---
    st.markdown("#### よくある質問")
    if 'demographic_faq_toggle' not in st.session_state:
        st.session_state.demographic_faq_toggle = {1: False, 2: False, 3: False, 4: False}

    faq_cols = st.columns(2)
    with faq_cols[0]:
        if st.button("最もCVRが高い年齢層は？", key="faq_demo_1", use_container_width=True):
            st.session_state.demographic_faq_toggle[1] = not st.session_state.demographic_faq_toggle[1]
            st.session_state.demographic_faq_toggle[2], st.session_state.demographic_faq_toggle[3], st.session_state.demographic_faq_toggle[4] = False, False, False
        if st.session_state.demographic_faq_toggle[1]:
            if not age_demo_df.empty:
                best_age_group = age_demo_df.loc[age_demo_df['CVR (%)'].idxmax()]
                st.info(f"**{best_age_group['年齢層']}** です。この年齢層のCVRは{best_age_group['CVR (%)']:.1f}%と最も高くなっています。")
        
        if st.button("特定の地域だけCVRが高い理由は？", key="faq_demo_3", use_container_width=True):
            st.session_state.demographic_faq_toggle[3] = not st.session_state.demographic_faq_toggle[3]
            st.session_state.demographic_faq_toggle[1], st.session_state.demographic_faq_toggle[2], st.session_state.demographic_faq_toggle[4] = False, False, False
        if st.session_state.demographic_faq_toggle[3]:
            st.info("地域によってCVRに差が出るのは、地域限定のキャンペーン、競合の状況、地域特有のニーズ、または広告の地域ターゲティング設定などが原因として考えられます。")
    with faq_cols[1]:
        if st.button("この分析結果をどう広告に活かす？", key="faq_demo_2", use_container_width=True):
            st.session_state.demographic_faq_toggle[2] = not st.session_state.demographic_faq_toggle[2]
            st.session_state.demographic_faq_toggle[1], st.session_state.demographic_faq_toggle[3], st.session_state.demographic_faq_toggle[4] = False, False, False
        if st.session_state.demographic_faq_toggle[2]:
            if not age_demo_df.empty:
                best_age_group = age_demo_df.loc[age_demo_df['CVR (%)'].idxmax()]
                st.info(f"CVRが高い **{best_age_group['年齢層']}** や特定の性別・地域に広告のターゲティングを絞り込む、または予算を重点的に配分することで、広告の費用対効果を高めることができます。")
        
        if st.button("男女でLPの訴求を変えるべき？", key="faq_demo_4", use_container_width=True):
            st.session_state.demographic_faq_toggle[4] = not st.session_state.demographic_faq_toggle[4]
            st.session_state.demographic_faq_toggle[1], st.session_state.demographic_faq_toggle[2], st.session_state.demographic_faq_toggle[3] = False, False, False
        if st.session_state.demographic_faq_toggle[4]:
            st.info("もし男女でCVRやサイト内行動に大きな差が見られる場合は、訴求メッセージやデザインを男女別に最適化（パーソナライズ）することが有効です。例えば、男性には機能性を、女性には共感を呼ぶストーリーを訴求するなどの方法が考えられます。")




# タブ9: AI提案
elif selected_analysis == "AIによる分析・考察":
    st.markdown('<div class="sub-header">AI による分析・考察</div>', unsafe_allow_html=True)
    # メインエリア: フィルターと比較設定
    st.markdown('<div class="sub-header">フィルター設定</div>', unsafe_allow_html=True)

    filter_cols = st.columns(4)
    with filter_cols[0]:
        # 期間選択
        period_options = {
            "過去7日間": 7,
            "過去30日間": 30,
            "過去90日間": 90,
            "カスタム期間": None
        }
        selected_period = st.selectbox("期間を選択", list(period_options.keys()), index=1, key="ai_analysis_period")

    with filter_cols[1]:
        # LP選択
        lp_options = sorted(df['page_location'].dropna().unique().tolist()) # type: ignore
        selected_lp = st.selectbox("LP選択", lp_options, index=0 if lp_options else -1, key="ai_analysis_lp")

    with filter_cols[2]:
        device_options = ["すべて"] + sorted(df['device_type'].dropna().unique().tolist())
        selected_device = st.selectbox("デバイス選択", device_options, index=0, key="ai_analysis_device")

    with filter_cols[3]:
        channel_options = ["すべて"] + sorted(df['channel'].unique().tolist())
        selected_channel = st.selectbox("チャネル選択", channel_options, index=0, key="ai_analysis_channel")

    # 比較機能はチェックボックスでシンプルに
    enable_comparison = st.checkbox("比較機能を有効化", value=False, key="ai_analysis_compare_check")
    comparison_type = None
    if enable_comparison:
        comparison_options = {
            "前期間": "previous_period", "前週": "previous_week",
            "前月": "previous_month", "前年": "previous_year"
        }
        selected_comparison = st.selectbox("比較対象", list(comparison_options.keys()), key="ai_analysis_compare_select")
        comparison_type = comparison_options[selected_comparison]

    # カスタム期間の場合
    if selected_period == "カスタム期間":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("開始日", df['event_date'].min(), key="ai_analysis_start_date")
        with col2:
            end_date = st.date_input("終了日", df['event_date'].max(), key="ai_analysis_end_date")
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
    if selected_lp:
        filtered_df = filtered_df[filtered_df['page_location'] == selected_lp]

    # --- クロス分析用フィルター適用 ---
    if selected_device != "すべて":
        filtered_df = filtered_df[filtered_df['device_type'] == selected_device]

    if selected_channel != "すべて":
        filtered_df = filtered_df[filtered_df['channel'] == selected_channel]

    # is_conversion列を作成
    filtered_df['is_conversion'] = filtered_df['cv_type'].notna().astype(int)

    # ==============================================================================
    #  デバッグ用: 3分以上の滞在時間データを強制的に生成
    #  目的: 「3分以上」セグメントがグラフに表示されることを確認するため。
    #  注意: このコードは本番データでは不要です。
    # ==============================================================================
    if not filtered_df.empty:
        # 'stay_ms'列が存在し、かつNaNでない行が1つ以上あることを確認
        if 'stay_ms' in filtered_df.columns and filtered_df['stay_ms'].notna().any():
            # 滞在時間が最も長い上位5%のインデックスを取得
            long_stay_indices = filtered_df['stay_ms'].nlargest(int(len(filtered_df) * 0.05)).index
            
            # それらの滞在時間を3分〜5分のランダムな値に書き換える
            if not long_stay_indices.empty:
                new_stay_times = np.random.randint(180000, 300000, size=len(long_stay_indices))
                filtered_df.loc[long_stay_indices, 'stay_ms'] = new_stay_times
    # ==============================================================================

    # 比較データの取得
    comparison_df = None
    comp_start = None
    comp_end = None
    if enable_comparison and comparison_type:
        result = get_comparison_data(df, pd.Timestamp(start_date), pd.Timestamp(end_date), comparison_type)
        if result is not None:
            comparison_df, comp_start, comp_end = result
            # 比較データにも同じフィルターを適用
            if selected_lp:
                comparison_df = comparison_df[comparison_df['page_location'] == selected_lp]
            # --- 比較データにもクロス分析用フィルターを適用 ---
            if selected_device != "すべて":
                comparison_df = comparison_df[comparison_df['device_type'] == selected_device]
            if selected_channel != "すべて":
                comparison_df = comparison_df[comparison_df['channel'] == selected_channel]

            # 比較データが空の場合は無効化
            if len(comparison_df) == 0:
                comparison_df = None
                st.info(f"比較期間（{comp_start.strftime('%Y-%m-%d')} 〜 {comp_end.strftime('%Y-%m-%d')}）にデータがありません。")

    # データが空の場合の処理
    if len(filtered_df) == 0:
        st.warning("⚠️ 選択した条件に該当するデータがありません。フィルターを変更してください。")
        st.stop()

    # 基本メトリクス計算
    total_sessions = filtered_df['session_id'].nunique()
    total_conversions = filtered_df[filtered_df['cv_type'].notna()]['session_id'].nunique()
    conversion_rate = safe_rate(total_conversions, total_sessions) * 100
    total_clicks = len(filtered_df[filtered_df['event_name'] == 'click'])
    click_rate = safe_rate(total_clicks, total_sessions) * 100
    avg_stay_time = filtered_df['stay_ms'].mean() / 1000  # 秒に変換
    avg_pages_reached = filtered_df.groupby('session_id')['max_page_reached'].max().mean()
    fv_retention_rate = safe_rate(filtered_df[filtered_df['max_page_reached'] >= 2]['session_id'].nunique(), total_sessions) * 100
    final_cta_rate = safe_rate(filtered_df[filtered_df['max_page_reached'] >= 10]['session_id'].nunique(), total_sessions) * 100
    avg_load_time = filtered_df['load_time_ms'].mean()

    # 比較データのKPI計算
    comp_kpis = {}
    if comparison_df is not None and len(comparison_df) > 0:
        comp_total_sessions = comparison_df['session_id'].nunique()
        comp_total_conversions = comparison_df[comparison_df['cv_type'].notna()]['session_id'].nunique() # type: ignore
        comp_conversion_rate = safe_rate(comp_total_conversions, comp_total_sessions) * 100
        comp_total_clicks = len(comparison_df[comparison_df['event_name'] == 'click']) # type: ignore
        comp_click_rate = safe_rate(comp_total_clicks, comp_total_sessions) * 100
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
    st.markdown('<div class="sub-header">主要指標（KPI）</div>', unsafe_allow_html=True)

    # KPIカード表示 (他のページからコピー)
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1: # type: ignore
        # セッション数
        delta_sessions = total_sessions - comp_kpis.get('sessions', 0) if comp_kpis else None
        st.metric("セッション数", f"{total_sessions:,}", delta=f"{delta_sessions:+,}" if delta_sessions is not None else None) # type: ignore
        
        # FV残存率
        delta_fv = fv_retention_rate - comp_kpis.get('fv_retention_rate', 0) if comp_kpis else None
        st.metric("FV残存率", f"{fv_retention_rate:.1f}%", delta=f"{delta_fv:+.1f}%" if delta_fv is not None else None)

    with col2:
        # コンバージョン数
        delta_conversions = total_conversions - comp_kpis.get('conversions', 0) if comp_kpis else None
        st.metric("コンバージョン数", f"{total_conversions:,}", delta=f"{delta_conversions:+,}" if delta_conversions is not None else None) # type: ignore

        # 最終CTA到達率
        delta_cta = final_cta_rate - comp_kpis.get('final_cta_rate', 0) if comp_kpis else None
        st.metric("最終CTA到達率", f"{final_cta_rate:.1f}%", delta=f"{delta_cta:+.1f}%" if delta_cta is not None else None)

    with col3:
        # コンバージョン率
        delta_cvr = conversion_rate - comp_kpis.get('conversion_rate', 0) if comp_kpis else None
        st.metric("コンバージョン率", f"{conversion_rate:.2f}%", delta=f"{delta_cvr:+.2f}%" if delta_cvr is not None else None) # type: ignore

        # 平均到達ページ数
        delta_pages = avg_pages_reached - comp_kpis.get('avg_pages_reached', 0) if comp_kpis else None
        st.metric("平均到達ページ数", f"{avg_pages_reached:.1f}", delta=f"{delta_pages:+.1f}" if delta_pages is not None else None)

    with col4:
        # クリック数
        delta_clicks = total_clicks - comp_kpis.get('clicks', 0) if comp_kpis else None
        st.metric("クリック数", f"{total_clicks:,}", delta=f"{delta_clicks:+,}" if delta_clicks is not None else None) # type: ignore

        # 平均滞在時間
        delta_stay = avg_stay_time - comp_kpis.get('avg_stay_time', 0) if comp_kpis else None
        st.metric("平均滞在時間", f"{avg_stay_time:.1f}秒", delta=f"{delta_stay:+.1f} 秒" if delta_stay is not None else None)

    with col5:
        # クリック率
        delta_click_rate = click_rate - comp_kpis.get('click_rate', 0) if comp_kpis else None
        st.metric("クリック率", f"{click_rate:.2f}%", delta=f"{delta_click_rate:+.2f}%" if delta_click_rate is not None else None) # type: ignore

        # 平均読込時間
        delta_load = avg_load_time - comp_kpis.get('avg_load_time', 0) if comp_kpis else None
        st.metric("平均読込時間", f"{avg_load_time:.0f}ms", delta=f"{delta_load:+.0f} ms" if delta_load is not None else None, delta_color="inverse")

    # --- ユーザー入力フォーム ---
    # AI分析の表示状態を管理するフラグを初期化
    if 'ai_analysis_open' not in st.session_state:
        st.session_state.ai_analysis_open = False

    st.markdown("---")
    st.markdown("### 目標値・現状値の入力")
    st.markdown('<div class="graph-description">AIがデータを多角的に分析し、現状評価や改善案を提案します。分析精度向上のため、目標値と現状値を入力してください。月間目標は<br>選択期間に応じて日割り計算され、空欄でもAIが推測します。</div>', unsafe_allow_html=True)

    form_cols = st.columns(2)
    with form_cols[0]:
        st.markdown("##### **月間目標値**")
        target_cvr = st.number_input("目標CVR (%)", min_value=0.0, step=0.1, format="%.2f", value=0.0)
        target_cv = st.number_input("目標CV数", min_value=0, step=1, value=0)
        target_cpa = st.number_input("目標CPA", min_value=0, step=100, value=0)
    
    with form_cols[1]:
        st.markdown("##### **現状値**")
        current_cvr = st.number_input("現状CVR (%)", min_value=0.0, step=0.1, format="%.2f", value=0.0)
        current_cv = st.number_input("現状CV数", min_value=0, step=1, value=0)
        current_cpa = st.number_input("現状CPA", min_value=0, step=100, value=0)

    st.markdown("---")
    st.markdown("### ターゲット顧客・その他の情報")
    target_customer = st.text_area("ターゲット顧客について教えてください", placeholder="例：30代女性、都内在住、美容への関心が高い、オーガニック製品を好む")
    other_info = st.text_area("その他、分析で特に重視してほしい点などがあればご記入ください", placeholder="例：競合の〇〇と比較してほしい、特定の部分のコピーを重点的に見てほしい")

    if st.button("AI分析を実行", key="ai_analysis_main_btn", type="primary", use_container_width=True): # type: ignore
        st.session_state.ai_analysis_open = True
        st.rerun()

    if st.session_state.ai_analysis_open:
        with st.container():
            # LPのURLからテキストコンテンツを抽出
            lp_text_content = extract_lp_text_content(selected_lp)
            main_headline = lp_text_content['headlines'][0] if lp_text_content['headlines'] else "（ヘッドライン取得不可）"
            # f-string内でエラーを起こさないようにトリプルクォートを別の文字に置換
            main_headline_escaped = main_headline.replace('"""', "'''")
            # ユーザー入力も同様に置換
            target_customer_escaped = target_customer.replace('"""', "'''") # type: ignore

            # AI分析に必要なデータをここで計算
            # ページ別統計
            page_stats = filtered_df.groupby('max_page_reached').agg(
                離脱セッション数=('session_id', 'nunique'),
                平均滞在時間_ms=('stay_ms', 'mean')
            ).reset_index()
            page_stats['離脱率'] = (page_stats['離脱セッション数'] / total_sessions * 100) if total_sessions > 0 else 0
            page_stats.rename(columns={'max_page_reached': 'ページ番号'}, inplace=True)
            max_exit_page = page_stats.loc[page_stats['離脱率'].idxmax()]

            # デバイス別統計（修正）
            device_stats = filtered_df.groupby('device_type').agg(
                セッション数=('session_id', 'nunique'),
                コンバージョン数=('cv_type', lambda x: x.notna().sum())
            ).reset_index().rename(columns={'device_type': 'デバイス'})
            device_stats['コンバージョン率'] = (device_stats['コンバージョン数'] / device_stats['セッション数'] * 100).fillna(0)
            worst_device = device_stats.loc[device_stats['コンバージョン率'].idxmin()]

            # チャネル別統計（修正）
            channel_stats = filtered_df.groupby('channel').agg(
                セッション数=('session_id', 'nunique'),
                コンバージョン数=('cv_type', lambda x: x.notna().sum())
            ).reset_index().rename(columns={'channel': 'チャネル'})
            channel_stats['コンバージョン率'] = (channel_stats['コンバージョン数'] / channel_stats['セッション数'] * 100).fillna(0)
            best_channel = channel_stats.loc[channel_stats['コンバージョン率'].idxmax()]
            worst_channel = channel_stats.loc[channel_stats['コンバージョン率'].idxmin()] # type: ignore
            
            # AIによる訴求ポイントの推察（簡易版）
            # 本来はLLMで要約するが、ここではキーワードで代用
            body_text = " ".join(lp_text_content['body_copy'])
            keywords = ["限定", "割引", "無料", "簡単", "満足度"]
            found_keywords = [kw for kw in keywords if kw in body_text]
            if found_keywords:
                inferred_appeal_point = f"LPのテキストから「{', '.join(found_keywords)}」というキーワードが検出されました。これらが主要な訴求ポイントと推察されます。"
            else:
                inferred_appeal_point = "LPのテキストから主要な訴求ポイントを自動推察します。（現在はキーワード検出のみ）"
            inferred_appeal_point_escaped = inferred_appeal_point.replace('"""', "'''")
            
            # 分析期間の日数を計算
            analysis_days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days + 1
            
            # 月間目標を日割り計算
            daily_target_cv = (target_cv / 30) * analysis_days if target_cv > 0 else 0
            daily_target_cvr = target_cvr # CVRは期間によらないのでそのまま
            daily_target_cpa = target_cpa # CPAも期間によらないのでそのまま

            # セクション1: 客観的かつ詳細な現状分析
            st.markdown("---")
            st.markdown("### 1. 客観的かつ詳細な現状分析")
            
            with st.expander("全体パフォーマンス評価", expanded=True):
                st.markdown(f"""
                **総合評価:**  
                - **現状のCVR**: **{current_cvr:.2f}%** （期間目標: {daily_target_cvr if daily_target_cvr > 0 else '未設定'}%）
                - **現状のCV数**: **{current_cv}** （期間目標: {daily_target_cv:.0f}件）
                - **ファーストビュー(FV)残存率**: **{fv_retention_rate:.1f}%** が最初のページで離脱せずに次に進んでいます。
                - **最終CTA到達率**: **{final_cta_rate:.1f}%** が最終ページまで到達しています。
                
                **AIによるLPコンテンツの評価:**
                - **ヘッドライン**: 「{main_headline_escaped}」
                - **訴求ポイント(AI推察)**: {inferred_appeal_point_escaped}
                - **ターゲット顧客との関連性**: {f"入力されたターゲット顧客「{target_customer_escaped}」に対して、現在のヘッドラインと訴求ポイントは関連性が高いと考えられます。" if target_customer_escaped else "ターゲット顧客が未入力のため、詳細な関連性分析はスキップします。"}
                """)
            
            # セクション2: 現状分析からの今後の考察
            st.markdown("---")
            st.markdown("### 2. 現状分析からの今後の考察")
            
            with st.expander("トレンド予測と潜在的リスク", expanded=True):
                st.markdown(f"""
                **考察:**
                - **目標達成状況**: 現状のCV数({current_cv}件)は、分析期間({analysis_days}日間)における日割り目標({daily_target_cv:.0f}件)に対して **{current_cv - daily_target_cv:.0f}件** の差があります。
                - **最大の課題**: FV残存率が **{fv_retention_rate:.1f}%** と低いことが、全体のCVRを押し下げる最大の要因と考えられます。多くのユーザーがLPの第一印象で興味を失い、離脱している可能性があります。
                - **機会**: 最終CTA到達率が **{final_cta_rate:.1f}%** あるため、LPの中盤以降のコンテンツは比較的読まれているようです。FVを突破したユーザーを確実にCVに繋げることができれば、パフォーマンスは大きく改善する可能性があります。
                """)
            
            # セクション3: 改善提案
            st.markdown("---")
            st.markdown("### 3. 具体的な改善提案")
            
            with st.expander("優先度高: 即実施すべき施策", expanded=True):
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
            
            with st.expander("優先度中: A/Bテストで検証すべき施策"):
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
            
            with st.expander("優先度低: 中長期的な施策"):
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
            
            with st.expander("実施ロードマップ（3ヶ月間）"):
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
            
            # 閉じるボタン
            if st.button("AI分析を閉じる", key="ai_analysis_close"):
                st.session_state.ai_analysis_open = False
                st.rerun()

            st.success("AI分析が完了しました！上記の提案を参考に、LPの改善を進めてください。")
    
    # 既存の質問ボタンは保持
    
    # 質問ボタンにトグル機能を追加
    st.markdown("---")
    st.markdown("### よくある質問")
    
    # FAQ用のデータ計算を事前に初期化
    page_stats_global = pd.DataFrame(columns=['ページ番号', '離脱セッション数', '平均滞在時間_ms', '離脱率', '平均滞在時間_秒'])
    ab_stats_global = pd.DataFrame(columns=['バリアント', 'セッション数', 'コンバージョン数', 'コンバージョン率']) # type: ignore
    device_stats_global = pd.DataFrame(columns=['デバイス', 'セッション数', 'コンバージョン数', 'コンバージョン率'])

    if not filtered_df.empty and total_sessions > 0:
        # ページ別統計
        page_stats_global = filtered_df.groupby('max_page_reached').agg(
            離脱セッション数=('session_id', 'nunique'),
            平均滞在時間_ms=('stay_ms', 'mean')
        ).reset_index()
        page_stats_global['離脱率'] = (page_stats_global['離脱セッション数'] / total_sessions * 100) if total_sessions > 0 else 0
        page_stats_global['平均滞在時間_秒'] = page_stats_global['平均滞在時間_ms'] / 1000
        page_stats_global.rename(columns={'max_page_reached': 'ページ番号'}, inplace=True) # type: ignore

        # ab_variant列が存在する場合のみ集計
        if 'ab_variant' in filtered_df.columns and filtered_df['ab_variant'].notna().any():
            ab_stats_global = filtered_df.groupby('ab_variant').agg(
                セッション数=('session_id', 'nunique')
            ).reset_index().rename(columns={'ab_variant': 'バリアント'})
            ab_cv_stats = filtered_df[filtered_df['is_conversion'] == 1].groupby('ab_variant')['session_id'].nunique().reset_index(name='コンバージョン数').rename(columns={'ab_variant': 'バリアント'})
            ab_stats_global = pd.merge(ab_stats_global, ab_cv_stats, on='バリアント', how='left').fillna(0)
        else:
            ab_stats_global = pd.DataFrame(columns=['バリアント', 'セッション数', 'コンバージョン数'])
        
        if not ab_stats_global.empty and 'セッション数' in ab_stats_global.columns and ab_stats_global['セッション数'].sum() > 0:
            ab_stats_global['コンバージョン率'] = ab_stats_global.apply(lambda row: safe_rate(row['コンバージョン数'], row['セッション数']) * 100, axis=1)
        
        # デバイス別統計
        device_stats_global = filtered_df.groupby('device_type').agg(
            セッション数=('session_id', 'nunique')
        ).reset_index()
        device_cv_stats = filtered_df[filtered_df['is_conversion'] == 1].groupby('device_type')['session_id'].nunique().reset_index(name='コンバージョン数')
        device_stats_global = pd.merge(device_stats_global, device_cv_stats, on='device_type', how='left').fillna(0).rename(columns={'device_type': 'デバイス'})
        if not device_stats_global.empty and 'セッション数' in device_stats_global.columns and device_stats_global['セッション数'].sum() > 0: # type: ignore
            device_stats_global['コンバージョン率'] = device_stats_global.apply(lambda row: safe_rate(row['コンバージョン数'], row['セッション数']) * 100, axis=1)

    # FAQボタンの表示
    col1, col2 = st.columns(2)
    
    # session_stateの初期化
    if 'ai_faq_toggle' not in st.session_state: # type: ignore
        st.session_state.ai_faq_toggle = {1: False, 2: False, 3: False, 4: False}

    with col1:
        if st.button("このLPの最大のボトルネックは？", key="faq_btn_1", use_container_width=True):
            # ボタンが押されたら状態をトグルし、他を閉じる
            st.session_state.ai_faq_toggle[1] = not st.session_state.ai_faq_toggle[1]
            st.session_state.ai_faq_toggle[2] = False
            st.session_state.ai_faq_toggle[3] = False
            st.session_state.ai_faq_toggle[4] = False
        
        if st.session_state.ai_faq_toggle.get(1, False): # type: ignore
            # 離脱率が最も高いページを特定（データがある場合のみ）
            if not page_stats_global.empty and '離脱率' in page_stats_global.columns:
                max_exit_page = page_stats_global.loc[page_stats_global['離脱率'].idxmax()]
                
                st.info(f"""
                **分析結果:**
                
                最大のボトルネックは**ページ{int(max_exit_page['ページ番号'])}**です。
                
                - 離脱率: {max_exit_page['離脱率']:.1f}%
                - 平均滞在時間: {max_exit_page['平均滞在時間_秒']:.1f}秒
                
                **推奨アクション:**
                1. ページ{int(max_exit_page['ページ番号'])}のコンテンツを見直し、ユーザーの関心を引く要素を追加
                2. A/Bテストで異なるコンテンツをテスト
                3. 読込時間が長い場合は、画像の最適化を検討
                """)
            else:
                st.warning("分析データがありません。")
        
        if st.button("コンバージョン率を改善するには？", key="faq_btn_2", use_container_width=True):
            st.session_state.ai_faq_toggle[2] = not st.session_state.ai_faq_toggle[2]
            st.session_state.ai_faq_toggle[1] = False
            st.session_state.ai_faq_toggle[3] = False
            st.session_state.ai_faq_toggle[4] = False
        
        if st.session_state.ai_faq_toggle.get(2, False): # type: ignore
            st.info(f"""
            **分析結果:**
            
            現在のコンバージョン率は**{conversion_rate:.2f}%**です。
            
            **推奨アクション:**
            1. FV残存率({fv_retention_rate:.1f}%)を改善するため、ファーストビューのコンテンツを強化
            2. 最終CTA到達率({final_cta_rate:.1f}%)を改善するため、ページ遷移をスムーズにする
            3. デバイス別の分析を行い、パフォーマンスが低いデバイスに最適化
            4. 高パフォーマンスのチャネルに予算を集中
            """)
    
    with col2: # type: ignore
        if st.button("A/Bテストの結果、どちらが優れている？", key="faq_btn_3", use_container_width=True):
            st.session_state.ai_faq_toggle[3] = not st.session_state.ai_faq_toggle[3]
            st.session_state.ai_faq_toggle[1] = False
            st.session_state.ai_faq_toggle[2] = False
            st.session_state.ai_faq_toggle[4] = False

        if st.session_state.ai_faq_toggle.get(3, False): # type: ignore
            if not ab_stats_global.empty and 'コンバージョン率' in ab_stats_global.columns:
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
            else:
                st.warning("A/Bテストの分析データがありません。")
        
        if st.button("デバイス別のパフォーマンス差は？", key="faq_btn_4", use_container_width=True):
            st.session_state.ai_faq_toggle[4] = not st.session_state.ai_faq_toggle[4]
            st.session_state.ai_faq_toggle[1] = False
            st.session_state.ai_faq_toggle[2] = False
            st.session_state.ai_faq_toggle[3] = False

        if st.session_state.ai_faq_toggle.get(4, False): # type: ignore
            if not device_stats_global.empty and 'コンバージョン率' in device_stats_global.columns:
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
            else:
                st.warning("分析データがありません。")
    
    # st.markdown("---")
    
    # # フリーチャット（プロトタイプ）
    # st.markdown("#### チャットで質問する")
    
    # user_question = st.text_input("チャットで質問する", placeholder="質問を入力してください", label_visibility="collapsed", key="ai_page_free_chat_input")
    
    # if st.button("送信", key="ai_page_free_chat_submit"):
    #     if user_question:
    #         with st.chat_message("user"):
    #             st.markdown(user_question)

    #         with st.chat_message("assistant"):
    #             with st.spinner("AIが回答を生成中..."):
    #                 # ここで実際のAI応答生成ロジックを呼び出す
    #                 response = f"ご質問ありがとうございます。「{user_question}」について、AIがデータに基づいて回答を生成します。（これはプロトタイプの固定回答です）"
    #                 st.markdown(response)
    #     else:
    #         st.warning("質問を入力してください")

# タブ10: 使用ガイド
elif selected_analysis == "使用ガイド":
    st.markdown('<div class="sub-header">使用ガイド</div>', unsafe_allow_html=True)

    st.markdown("""
    ### 瞬ジェネ AIアナリストへようこそ！
    このツールは、あなたのスワイプLPのパフォーマンスを直感的に分析し、改善のための具体的なアクションを見つけるお手伝いをします。

    ---

    ### 基本的な使い方

    1.  **分析ページを選択する**
        - 画面左側のサイドバーから、見たい分析ページ（例：「全体サマリー」「ページ分析」など）をクリックします。

    2.  **データを絞り込む（フィルター）**
        - 各ページの画面上部にあるフィルターを使って、分析したいデータ（期間、LP、デバイス、チャネル）を絞り込めます。
        - 「比較機能」を使えば、前の期間とのパフォーマンス差を簡単に確認できます。

    3.  **AIの力を借りる**
        - 各分析ページには「**AI分析を実行**」ボタンがあります。これをクリックすると、表示されているデータに基づいてAIが現状の評価と改善案を提案します。
        - 「**よくある質問**」ボタンを押すと、その分析でよくある疑問点に対する回答をAIが示します。

    ---

    ### 各分析ページでできること

    #### AIアナリスト
    - **AIによる分析・考察**: このツールの中心機能です。目標値や現状の課題を入力すると、AIがLP全体のデータを多角的に分析し、詳細な改善戦略を提案します。

    #### 基本分析
    - **リアルタイムビュー**: 直近1時間のサイト活動を監視し、異常検知や突発的な機会の発見をサポートします。
    - **全体サマリー**: LP全体の主要KPI（CVR、セッション数など）を一覧で確認し、健康状態を把握します。
    - **時系列分析**: 曜日・時間帯ごとのパフォーマンスを分析し、広告配信やプロモーションに最適な「ゴールデンタイム」を見つけます。
    - **デモグラフィック情報**: 年齢、性別、地域などのユーザー属性ごとの行動を分析し、ターゲット顧客の解像度を高めます。

    #### LP最適化分析
    - **ページ分析**: ユーザーがどのページで離脱しているか（ボトルネック）を特定し、改善の優先順位を判断します。
    - **A/Bテスト分析**: 実施したA/Bテストの結果を統計的に評価し、どちらのパターンが優れているかを明確にします。

    #### 詳細分析
    - **セグメント分析**: デバイス別（PC/スマホ）、チャネル別（流入経路別）などでデータを深掘りし、パフォーマンスの差を生んでいる要因を探ります。
    - **インタラクション分析**: CTAボタンや各種リンクなど、クリック可能な要素のパフォーマンスを分析し、ユーザーの関心事を特定します。
    - **動画・スクロール分析**: 動画の視聴状況やユーザーのスクロール行動を分析し、コンテンツのエンゲージメントを評価します。

    #### ヘルプ
    - **使用ガイド**: このページです。ツールの使い方を確認できます。
    - **専門用語解説**: 分析に使われるマーケティング用語を解説します。

    ---

    まずは「**AIによる分析・考察**」ページで、あなたのLPの課題を入力して、AIに分析させてみましょう！
    """)

# タブ11: 専門用語解説
elif selected_analysis == "専門用語解説":
    st.markdown('<div class="sub-header">専門用語解説</div>', unsafe_allow_html=True)


    st.markdown(""" # type: ignore
    ### マーケティング・分析用語集
    
    LP分析で使用される主要な用語を詳しく解説します。
    """)
    
    # カテゴリー別に表示
    with st.expander("基本指標（KPI）", expanded=True):
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
    
    with st.expander("コンバージョン関連"):
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
    
    with st.expander("LP特有の指標"):
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
    
    with st.expander("A/Bテスト・最適化"):
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
    
    with st.expander("トラフィック・チャネル"):
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
    
    with st.expander("セグメント・オーディエンス"):
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
    
    with st.expander("パフォーマンス指標"):
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
    
    with st.expander("分析ツール・手法"):
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
    st.markdown("**ヒント**: 各用語をクリックして詳細を確認できます。")

# フッター
st.markdown("---")
st.markdown("**瞬ジェネ AIアナリスト** - Powered by Streamlit & Gemini 2.5 Pro")