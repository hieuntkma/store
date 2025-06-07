import os
import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

SAVE_DIR = "Product_Image"

# Xác định category từ URL
CATEGORY_MAPPING = {
    "rau-cu": "Rau củ",
    "hoa-qua": "Hoa quả",
    "hai-san": "Hải sản",
    "cac-loai-hat": "Các loại hạt",
    "thuc-pham-tuoi-song": "Thực phẩm tươi sống"
}

def slugify(text):
    return re.sub(r'\W+', '_', text.strip()).lower()

def get_category_from_url(url):
    for slug, name in CATEGORY_MAPPING.items():
        if slug in url:
            return name
    return "Không rõ"

def download_image(url, save_path):
    try:
        if url.startswith("//"):
            url = "https:" + url
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"  ✅ Lưu ảnh: {save_path}")
    except Exception as e:
        print(f"  ❌ Lỗi tải ảnh: {e}")

def crawl_product(product_url):
    handle = urlparse(product_url).path.strip('/').split('/')[-1]
    json_url = f"https://coolorganic.myharavan.com/products/{handle}.js"

    res = requests.get(json_url, headers=HEADERS)
    if res.status_code != 200:
        print(f"❌ Không lấy được JSON từ: {json_url}")
        return

    try:
        data = res.json()
    except json.JSONDecodeError:
        print(f"❌ JSON lỗi tại: {json_url}")
        return

    # Lấy thông tin
    title = data.get("title", handle)
    slug = slugify(title)
    description_html = data.get("description", "")
    # description = BeautifulSoup(description_html, "html.parser").get_text(strip=True)

    original_price = data.get("compare_at_price", 0) // 100
    sale_price = data.get("price", 0) // 100
    images = data.get("images", [])

    category = get_category_from_url(product_url)

    # Tạo thư mục lưu
    folder_path = os.path.join(SAVE_DIR, slug)
    os.makedirs(folder_path, exist_ok=True)

    # Lưu ảnh
    for idx, img_url in enumerate(images):
        save_path = os.path.join(folder_path, f"{slug}_{idx+1}.png")
        download_image(img_url, save_path)

    # Lưu file JSON
    info = {
        "title": title,
        "original_price": original_price,
        "sale_price": sale_price,
        "description": description_html,
        "category": category
    }

    with open(os.path.join(folder_path, f"{slug}.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=4)
    print(f"📦 Đã xử lý xong: {title}")

def run():
    with open("san_pham.txt", "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f"🔎 Tổng số sản phẩm: {len(urls)}\n")

    for url in urls:
        crawl_product(url)

if __name__ == "__main__":
    run()
