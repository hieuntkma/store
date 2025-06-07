import json

# Đường dẫn tới file
original_file = "info_product.json"
categorized_file = "info_product_categorized.json"
output_file = "info_product_categorized_with_html_desc.json"

# Đọc file gốc (chứa description HTML)
with open(original_file, "r", encoding="utf-8") as f:
    original_data = json.load(f)

# Đọc file đã phân loại (mô tả đã bị rút gọn)
with open(categorized_file, "r", encoding="utf-8") as f:
    categorized_data = json.load(f)

# Tạo dict ánh xạ title -> description từ file gốc
desc_lookup = {item["title"]: item["description"] for item in original_data}

# Thay thế description trong dữ liệu phân loại
for item in categorized_data:
    title = item.get("title")
    if title in desc_lookup:
        item["description"] = desc_lookup[title]

# Ghi kết quả ra file mới
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(categorized_data, f, ensure_ascii=False, indent=4)

print("Đã cập nhật mô tả và lưu tại:", output_file)
