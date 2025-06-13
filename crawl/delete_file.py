import os
import shutil

PRODUCT_DIR = "Product_Image"

def delete_empty_cool_organic_folders():
    for folder in os.listdir(PRODUCT_DIR):
        full_path = os.path.join(PRODUCT_DIR, folder)

        if os.path.isdir(full_path) and folder.endswith("_cool_organic"):
            if not os.listdir(full_path):  # kiểm tra thư mục trống
                shutil.rmtree(full_path)
                print(f"🗑️ Đã xóa thư mục trống: {folder}")
            else:
                print(f"⚠️ Bỏ qua: {folder} (không trống)")

if __name__ == "__main__":
    delete_empty_cool_organic_folders()