import os
import json
import re

# Đọc file phân loại
with open("info_product_categorized_with_html_desc.json", "r", encoding="utf-8") as f:
    categorized_data = json.load(f)

# Tạo mapping: slug của title -> category
title_to_category = {
    re.sub(r'\W+', '_', item['title'].strip()).lower(): item['category']
    for item in categorized_data
}

# Duyệt thư mục chứa ảnh và json
image_dir = "Product_Image"
for folder in os.listdir(image_dir):
    folder_path = os.path.join(image_dir, folder)
    json_path = os.path.join(folder_path, f"{folder}.json")

    if os.path.isdir(folder_path) and os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        slug = re.sub(r'\W+', '_', data.get("title", "").strip()).lower()
        if slug in title_to_category:
            data["category"] = title_to_category[slug]
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"✅ Đã cập nhật category cho: {folder}")
        else:
            print(f"⚠️ Không tìm thấy category cho: {folder}")