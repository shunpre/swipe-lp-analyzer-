#!/usr/bin/env python3
"""
LP URLからスクリーンショットを取得する関数（簡易版）
スクレイピング不要で、ダミーデータから情報を取得
"""
import streamlit as st
from PIL import Image, ImageDraw, ImageFont


def create_placeholder_image(width: int, height: int, text: str = "プレースホルダー画像") -> Image.Image:
    """
    プレースホルダー画像を作成
    
    Args:
        width: 画像の幅
        height: 画像の高さ
        text: 表示するテキスト
    
    Returns:
        PIL Image object
    """
    img = Image.new('RGB', (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # テキストを中央に配置
    text_bbox = draw.textbbox((0, 0), text)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(position, text, fill=(150, 150, 150))
    
    return img


@st.cache_data(ttl=3600)
def capture_lp_screenshot(url: str, width: int = 1200, height: int = 3000) -> Image.Image:
    """
    URLからスクリーンショットを取得（簡易版）
    
    実際のスクリーンショットは取得せず、プレースホルダー画像を返す
    
    Args:
        url: キャプチャするURL
        width: スクリーンショットの幅
        height: スクリーンショットの高さ
    
    Returns:
        PIL Image object
    """
    return create_placeholder_image(width, height, f"LP: {url}")


@st.cache_data(ttl=3600)
def extract_swipe_lp_images(url: str):
    """
    スワイプLPから各ページの画像を抽出する（簡易版）
    
    実際のスクレイピングは行わず、ダミーデータから推測されるページ数分の
    プレースホルダー画像を返す
    
    Args:
        url: スワイプLPのURL
    
    Returns:
        画像情報のリスト（辞書形式: {'type': 'image', 'url': '...', 'page_num': N}）
    """
    # ダミーデータから推測されるページ数（デフォルト: 10ページ）
    # 実際のアプリケーションでは、ダミーデータから最大ページ数を取得
    default_page_count = 10
    
    images = []
    for i in range(1, default_page_count + 1):
        images.append({
            'type': 'image',
            'url': f'{url}/page{i}.jpg',  # ダミーURL
            'page_num': i
        })
    
    return images

