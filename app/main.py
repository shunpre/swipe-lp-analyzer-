import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# ページ設定
st.set_page_config(
    page_title="スワイプLP分析ツール",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# タイトル
st.title("📊 スワイプLP分析ツール")
st.markdown("LPのパフォーマンスを分かりやすく分析します")

# ==================== サイドバー設定 ====================
st.sidebar.header("📅 期間選択")

# GA4スタイルの期間プリセット
period_option = st.sidebar.radio(
    "期間を選択",
    ["過去7日", "過去30日", "過去90日", "カスタム期間"],
    horizontal=False
)

if period_option == "過去7日":
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
elif period_option == "過去30日":
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
elif period_option == "過去90日":
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
else:  # カスタム期間
    date_range = st.sidebar.date_input(
        "期間を指定",
        value=(datetime.now() - timedelta(days=7), datetime.now()),
        max_value=datetime.now()
    )
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()

# ==================== ダミーデータ生成 ====================
@st.cache_data
def generate_dummy_data(start_date, end_date, num_pages=10):
    """ダミーデータを生成"""
    num_days = (end_date - start_date).days + 1
    dates = [start_date + timedelta(days=i) for i in range(num_days)]
    
    # ページ情報
    pages = [f"ページ {i+1}" for i in range(num_pages)]
    
    data_list = []
    for page_idx, page in enumerate(pages):
        for date in dates:
            # ベースの値（ページによって異なる）
            base_views = 100 + page_idx * 15
            base_clicks = 70 - page_idx * 8
            
            # 日によるランダム変動
            daily_variation = np.random.uniform(0.8, 1.2)
            
            views = int(base_views * daily_variation)
            clicks = int(base_clicks * daily_variation)
            
            data_list.append({
                'date': date,
                'page': page,
                'ページビュー': views,
                'クリック': clicks,
                'ページから出た割合': np.random.uniform(0.1, 0.4),
                'ページ滞在時間（秒）': np.random.uniform(20, 120),
                'ページ読込時間（秒）': np.random.uniform(1, 5),
                'スクロール率': np.random.uniform(0.3, 1.0),
                'デバイス': np.random.choice(['スマートフォン', 'パソコン', 'タブレット']),
                'トラフィック元': np.random.choice(['Google', 'Facebook', 'Instagram', 'Twitter', 'その他']),
                'テスト版': np.random.choice(['A', 'B', 'コントロール']),
            })
    
    df = pd.DataFrame(data_list)
    df['コンバージョン率'] = (df['クリック'] / df['ページビュー']).round(3)
    return df

# データ取得
df = generate_dummy_data(start_date, end_date)

# ==================== メインコンテンツ ====================
tab1, tab2, tab3, tab4 = st.tabs(["📈 全体分析", "📋 ページ詳細", "💡 改善提案", "💬 チャット"])

# ==================== タブ1: 全体分析 ====================
with tab1:
    st.subheader("📊 全体のパフォーマンス")
    
    # KPI表示
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_views = df['ページビュー'].sum()
        st.metric("合計ページビュー", f"{total_views:,}")
    
    with col2:
        total_clicks = df['クリック'].sum()
        st.metric("合計クリック", f"{total_clicks:,}")
    
    with col3:
        avg_conv_rate = df['コンバージョン率'].mean()
        st.metric("平均コンバージョン率", f"{avg_conv_rate:.1%}")
    
    with col4:
        avg_stay_time = df['ページ滞在時間（秒）'].mean()
        st.metric("平均滞在時間", f"{avg_stay_time:.0f}秒")
    
    st.markdown("---")
    
    # グラフ選択
    st.subheader("📊 グラフを選択")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_page_views = st.checkbox("ページビュー数", value=True, key="graph_views")
        show_conversion = st.checkbox("コンバージョン率", value=True, key="graph_conv")
        show_stay_time = st.checkbox("滞在時間", value=True, key="graph_stay")
    
    with col2:
        show_bounce = st.checkbox("ページから出た割合", value=False, key="graph_bounce")
        show_load_time = st.checkbox("ページ読込時間", value=False, key="graph_load")
        show_scroll = st.checkbox("スクロール率", value=False, key="graph_scroll")
    
    with col3:
        show_device = st.checkbox("デバイス別", value=False, key="graph_device")
        show_traffic = st.checkbox("トラフィック元別", value=False, key="graph_traffic")
        show_test = st.checkbox("テスト版別", value=False, key="graph_test")
    
    st.markdown("---")
    
    # グラフ表示
    col1, col2 = st.columns(2)
    
    if show_page_views:
        with col1:
            page_views = df.groupby('page')['ページビュー'].sum().reset_index().sort_values('ページビュー', ascending=False)
            fig = px.bar(
                page_views,
                x='page',
                y='ページビュー',
                title='ページ別ページビュー数',
                labels={'page': 'ページ', 'ページビュー': 'ビュー数'},
                color='ページビュー',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    if show_conversion:
        with col2:
            page_conv = df.groupby('page')['コンバージョン率'].mean().reset_index().sort_values('コンバージョン率', ascending=False)
            fig = px.bar(
                page_conv,
                x='page',
                y='コンバージョン率',
                title='ページ別コンバージョン率',
                labels={'page': 'ページ', 'コンバージョン率': 'コンバージョン率'},
                color='コンバージョン率',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    if show_stay_time:
        with col1:
            page_stay = df.groupby('page')['ページ滞在時間（秒）'].mean().reset_index().sort_values('ページ滞在時間（秒）', ascending=False)
            fig = px.bar(
                page_stay,
                x='page',
                y='ページ滞在時間（秒）',
                title='ページ別平均滞在時間',
                labels={'page': 'ページ', 'ページ滞在時間（秒）': '滞在時間（秒）'},
                color='ページ滞在時間（秒）',
                color_continuous_scale='Purples'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    if show_bounce:
        with col2:
            page_bounce = df.groupby('page')['ページから出た割合'].mean().reset_index().sort_values('ページから出た割合', ascending=False)
            fig = px.bar(
                page_bounce,
                x='page',
                y='ページから出た割合',
                title='ページ別ページから出た割合',
                labels={'page': 'ページ', 'ページから出た割合': '出た割合'},
                color='ページから出た割合',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    if show_load_time:
        with col1:
            page_load = df.groupby('page')['ページ読込時間（秒）'].mean().reset_index().sort_values('ページ読込時間（秒）')
            fig = px.bar(
                page_load,
                x='page',
                y='ページ読込時間（秒）',
                title='ページ別ページ読込時間',
                labels={'page': 'ページ', 'ページ読込時間（秒）': '読込時間（秒）'},
                color='ページ読込時間（秒）',
                color_continuous_scale='Oranges'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    if show_scroll:
        with col2:
            page_scroll = df.groupby('page')['スクロール率'].mean().reset_index().sort_values('スクロール率', ascending=False)
            fig = px.bar(
                page_scroll,
                x='page',
                y='スクロール率',
                title='ページ別スクロール率',
                labels={'page': 'ページ', 'スクロール率': 'スクロール率'},
                color='スクロール率',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    if show_device:
        with col1:
            device_data = df.groupby('デバイス')['ページビュー'].sum().reset_index()
            fig = px.pie(
                device_data,
                names='デバイス',
                values='ページビュー',
                title='デバイス別ページビュー'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    if show_traffic:
        with col2:
            traffic_data = df.groupby('トラフィック元')['ページビュー'].sum().reset_index()
            fig = px.pie(
                traffic_data,
                names='トラフィック元',
                values='ページビュー',
                title='トラフィック元別ページビュー'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    if show_test:
        with col1:
            test_data = df.groupby('テスト版')['コンバージョン率'].mean().reset_index()
            fig = px.bar(
                test_data,
                x='テスト版',
                y='コンバージョン率',
                title='テスト版別コンバージョン率',
                labels={'テスト版': 'テスト版', 'コンバージョン率': 'コンバージョン率'},
                color='テスト版'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # 時系列グラフ
    st.markdown("---")
    st.subheader("📈 時間による変化")
    
    time_series = df.groupby('date').agg({
        'ページビュー': 'sum',
        'クリック': 'sum',
        'ページから出た割合': 'mean',
        'コンバージョン率': 'mean'
    }).reset_index()
    
    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(
        x=time_series['date'],
        y=time_series['ページビュー'],
        mode='lines+markers',
        name='ページビュー',
        yaxis='y1'
    ))
    fig_time.add_trace(go.Scatter(
        x=time_series['date'],
        y=time_series['ページから出た割合'],
        mode='lines+markers',
        name='ページから出た割合',
        yaxis='y2'
    ))
    fig_time.update_layout(
        title='ページビュー数とページから出た割合の推移',
        xaxis_title='日付',
        yaxis=dict(title='ページビュー数'),
        yaxis2=dict(title='ページから出た割合', overlaying='y', side='right'),
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig_time, use_container_width=True)

# ==================== タブ2: ページ詳細 ====================
with tab2:
    st.subheader("📋 ページ別詳細データ")
    
    # ページ一覧表示（プルダウンではなく一覧）
    st.markdown("#### ページ一覧")
    
    # ページ別の集計データ
    page_summary = df.groupby('page').agg({
        'ページビュー': 'sum',
        'クリック': 'sum',
        'コンバージョン率': 'mean',
        'ページ滞在時間（秒）': 'mean',
        'ページから出た割合': 'mean',
        'ページ読込時間（秒）': 'mean',
        'スクロール率': 'mean'
    }).reset_index().sort_values('ページビュー', ascending=False)
    
    # 見やすいフォーマットに変換
    page_summary_display = page_summary.copy()
    page_summary_display['コンバージョン率'] = page_summary_display['コンバージョン率'].apply(lambda x: f"{x:.1%}")
    page_summary_display['ページ滞在時間（秒）'] = page_summary_display['ページ滞在時間（秒）'].apply(lambda x: f"{x:.0f}秒")
    page_summary_display['ページから出た割合'] = page_summary_display['ページから出た割合'].apply(lambda x: f"{x:.1%}")
    page_summary_display['ページ読込時間（秒）'] = page_summary_display['ページ読込時間（秒）'].apply(lambda x: f"{x:.1f}秒")
    page_summary_display['スクロール率'] = page_summary_display['スクロール率'].apply(lambda x: f"{x:.1%}")
    
    st.dataframe(
        page_summary_display.rename(columns={
            'ページビュー': 'ビュー数',
            'クリック': 'クリック数'
        }),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    
    # ページ詳細表示
    st.markdown("#### ページ詳細")
    
    selected_page = st.selectbox(
        "詳細を見るページを選択",
        df['page'].unique(),
        index=0
    )
    
    page_data = df[df['page'] == selected_page]
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("##### ページ画像")
        st.info(f"📷 {selected_page}の画像\n\n（API仕様確定後、実際の画像を表示）")
    
    with col2:
        st.markdown("##### メトリクス")
        
        metrics_data = {
            'メトリクス': [
                'ビュー数',
                'クリック数',
                'コンバージョン率',
                'ページから出た割合',
                '平均滞在時間',
                'ページ読込時間',
                'スクロール率'
            ],
            '値': [
                f"{page_data['ページビュー'].sum():,}",
                f"{page_data['クリック'].sum():,}",
                f"{page_data['コンバージョン率'].mean():.1%}",
                f"{page_data['ページから出た割合'].mean():.1%}",
                f"{page_data['ページ滞在時間（秒）'].mean():.0f}秒",
                f"{page_data['ページ読込時間（秒）'].mean():.1f}秒",
                f"{page_data['スクロール率'].mean():.1%}"
            ]
        }
        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)

# ==================== タブ3: 改善提案 ====================
with tab3:
    st.subheader("💡 改善提案")
    
    st.markdown("### 📊 現状分析")
    
    # ボトルネック検出
    lowest_conv_page = df.groupby('page')['コンバージョン率'].mean().idxmin()
    lowest_conv_rate = df.groupby('page')['コンバージョン率'].mean().min()
    
    highest_bounce_page = df.groupby('page')['ページから出た割合'].mean().idxmax()
    highest_bounce_rate = df.groupby('page')['ページから出た割合'].mean().max()
    
    longest_load_page = df.groupby('page')['ページ読込時間（秒）'].mean().idxmax()
    longest_load_time = df.groupby('page')['ページ読込時間（秒）'].mean().max()
    
    analysis_text = f"""
    **検出された改善ポイント:**
    
    1. **コンバージョン率が低いページ:** {lowest_conv_page}
       - 現在のコンバージョン率: {lowest_conv_rate:.1%}
       - 改善の余地あり
    
    2. **ページから出た割合が高いページ:** {highest_bounce_page}
       - 現在の割合: {highest_bounce_rate:.1%}
       - ユーザーが興味を持ちにくい可能性
    
    3. **読込が遅いページ:** {longest_load_page}
       - 現在の読込時間: {longest_load_time:.1f}秒
       - ユーザー体験を損なっている可能性
    """
    st.markdown(analysis_text)
    
    st.markdown("---")
    st.markdown("### 🎯 推奨アクション")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 A/Bテストを実施", key="ab_test", use_container_width=True):
            st.success("✅ A/Bテストの実施フローに移動します")
            st.info(f"テスト対象: {lowest_conv_page}")
            st.markdown("""
            **推奨テスト内容:**
            - ページのタイトルやキャッチコピーの変更
            - ボタンの色やサイズの変更
            - ページレイアウトの変更
            """)
    
    with col2:
        if st.button("✏️ コンテンツ改善", key="content_improve", use_container_width=True):
            st.success("✅ コンテンツ改善フローに移動します")
            st.info(f"改善対象: {highest_bounce_page}")
            st.markdown("""
            **推奨改善内容:**
            - テキストをより分かりやすく
            - 画像やビデオを追加
            - ユーザーの関心に合わせた内容に変更
            """)
    
    with col3:
        if st.button("⚡ 読込速度改善", key="speed_improve", use_container_width=True):
            st.success("✅ 読込速度改善フローに移動します")
            st.info(f"改善対象: {longest_load_page}")
            st.markdown("""
            **推奨改善内容:**
            - 画像の最適化
            - キャッシュの設定
            - 不要なスクリプトの削除
            """)

# ==================== タブ4: チャット ====================
with tab4:
    st.subheader("💬 分析チャット")
    
    st.markdown("""
    このセクションでは、LPのデータについて自由に質問できます。
    
    **質問例:**
    - 「ページ2のコンバージョン率が低い理由は？」
    - 「最も改善効果が高いページはどれ？」
    - 「スマートフォンユーザーの行動は？」
    """)
    
    # チャット入力
    user_input = st.text_input(
        "質問を入力してください:",
        placeholder="例: ページ1の改善案は？"
    )
    
    if user_input:
        st.info(f"**質問:** {user_input}")
        st.success("""
        **AI回答:**
        
        ご質問ありがとうございます。ページ1のデータを分析した結果、以下の改善案を提案します：
        
        1. **ビジュアルの改善**: 現在のデザインをより目立つものに変更
        2. **テキストの簡潔化**: ユーザーの滞在時間が短いため、メッセージを明確に
        3. **ボタンの最適化**: ボタンの配置と色を改善
        
        これらの改善により、コンバージョン率が5～10%向上する可能性があります。
        """)

# ==================== フッター ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888;'>
    <small>スワイプLP分析ツール | データは定期的に更新されます</small>
</div>
""", unsafe_allow_html=True)

