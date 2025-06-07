import os
import json

ROOT_DIR = "Product_Image"
OUTPUT_FILE = "info_product.json"

def collect_product_info():
    result = []

    for folder in os.listdir(ROOT_DIR):
        folder_path = os.path.join(ROOT_DIR, folder)
        if os.path.isdir(folder_path):
            json_file = os.path.join(folder_path, f"{folder}.json")
            if os.path.exists(json_file):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        result.append(data)
                        print(f"✅ Đã thêm: {folder}")
                except Exception as e:
                    print(f"❌ Lỗi đọc file {json_file}: {e}")
            else:
                print(f"⚠️ Không tìm thấy {folder}.json")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print(f"\n📁 Đã lưu tất cả vào {OUTPUT_FILE}")

if __name__ == "__main__":
    collect_product_info()