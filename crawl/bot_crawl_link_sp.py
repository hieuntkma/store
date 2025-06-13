import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://coolorganic.myharavan.com"
COLLECTION_URL = f"{BASE_URL}/collections/all"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_all_product_links():
    page = 1
    product_links = []

    while True:
        url = f"{COLLECTION_URL}?page={page}"
        print(f"📄 Đang lấy trang: {url}")
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Cập nhật selector theo đúng HTML thực tế
        cards = soup.select('a.image_link[href]')
        if not cards:
            print("⛔ Không tìm thấy thêm sản phẩm, dừng lại.")
            break

        for a_tag in cards:
            product_url = urljoin(BASE_URL, a_tag['href'])
            if product_url not in product_links:
                product_links.append(product_url)

        page += 1

    return product_links

if __name__ == "__main__":
    links = get_all_product_links()
    print(f"\n🔗 Tổng số sản phẩm: {len(links)}")
    for link in links:
        print(link)
