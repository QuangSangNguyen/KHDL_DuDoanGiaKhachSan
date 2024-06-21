from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.edge.service import Service
import csv
from unidecode import unidecode
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


def unicode_list(list):
    for i in range(len(list)):
        list[i] = unidecode(list[i])
    return list

def create_csv():
    with open ('hotel_raw.csv', 'w', encoding='utf8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Address', 'Price', 'Size', 'Distance to beach', "Distance to airport"] + Facilities)
        
def find_hotel():
    global Facilities
    driver.get('https://www.booking.com/searchresults.vi.html?ss=%C4%90%C3%A0+N%E1%BA%B5ng&ssne=%C4%90%C3%A0+N%E1%BA%B5ng&ssne_untouched=%C4%90%C3%A0+N%E1%BA%B5ng&label=gog235jc-1DCAEoggI46AdIKlgDaPQBiAEBmAEquAEXyAEM2AED6AEB-AECiAIBqAIDuAK6yKiyBsACAdICJDU3YzI1ZGVhLWU0YWUtNDY4Ni04MDliLTQ4NTgxYzBiZGM4N9gCBOACAQ&sid=b038fb4aee9b3344a70240f8ddde6474&aid=397594&lang=vi&sb=1&src_elem=sb&src=index&dest_id=-3712125&dest_type=city&checkin=2024-07-03&checkout=2024-07-05&group_adults=2&no_rooms=1&group_children=0')
    for i in range(50):
        # Cuộn trang xuống cuối
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            # Chờ cho đến khi nút bấm xuất hiện
            load_page = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.a83ed08757.c21c56c305.bf0537ecb5.f671049264.deab83296e.af7297d90d')))
            load_page.click()
        except TimeoutException:
            # Nếu sau 10 giây mà nút bấm vẫn không xuất hiện, tiếp tục cuộn trang
            continue

    soup = BeautifulSoup(driver.page_source, 'lxml')
    wait = WebDriverWait(driver, 10)

    hotels = soup.find_all('div', class_='c82435a4b8 a178069f51 a6ae3c2b40 a18aeea94d d794b7a0f7 f53e278e95 c6710787a4')
    for hotel in hotels:
        # Lấy tên, giá và link của từng hotel
        name = hotel.find('div', class_='f6431b446c a15b38c233').text
        price = hotel.find('span', class_='f6431b446c fbfd7c1165 e84eb96b1f').text
        more_infor = hotel.find('a', class_='a78ca197d0')['href']

        driver.execute_script(f"window.open('{more_infor}', 'new_window')")
        driver.switch_to.window(driver.window_handles[1])

        sub_soup = BeautifulSoup(driver.page_source, 'lxml')

        address = sub_soup.find('span', class_='hp_address_subtitle js-hp_address_subtitle jq_tooltip').text.strip()

        try:
            size = sub_soup.find('div', class_='hprt-facilities-facility', attrs={"data-name-en": "room size"}).get_text().split()[0]
        except:
            size = 0

        facilities_res = [0] * len(Facilities)
        try:
            facilities_crawl = list(sub_soup.find_all('div', class_='c1f85371f5 c56ea7427a'))
            facilities_list = [facility.text.strip() for facility in facilities_crawl][:len(facilities_crawl)//2]
            Facilities = [facility.strip() for facility in Facilities]

            facilities_list = unicode_list(facilities_list)
            Facilities = unicode_list(Facilities)
            
            pool = unidecode('2 ho boi')
            pool2 = unidecode('Ho boi trong nha')
            if pool in facilities_list or pool2 in facilities_list:
                facilities_list[facilities_list.index(pool)] = "Ho boi ngoai troi"

            for facility in facilities_list:
                if facility in Facilities:
                    facilities_res[Facilities.index(facility)] = 1
        except:
            pass
        
        # Tìm tất cả thẻ div có cùng CSS Selector
        divs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.c807d72881.c3b290dbba.be7182ad14.e10711a42e')))
        # Tìm khoảng cách tới biển gần nhất
        try:
            div_child = divs[4].find_elements(By.CSS_SELECTOR, '.a8b57ad3ff.d50c412d31.fb9a5438f9.c7a5a1307a')
            min_beach = []
            for i in range(len(div_child)):
                print(div_child[i].get_attribute('innerHTML'))
                min_beach.append(div_child[i].find_element(By.CSS_SELECTOR, '.a53cbfa6de.f45d8e4c32.c875b9e968').text)
            for i in range(len(min_beach)):
                if 'km' in min_beach[i]:
                    min_beach[i] = float(min_beach[i].replace('km', '').replace(',', '.')) * 1000
                else:
                    min_beach[i] = float(min_beach[i].replace('m', '').replace(',', '.'))
            min_beach = min(min_beach) / 1000 
        except:
            min_beach = 0
            
        try:
            div_child2 = divs[6].find_elements(By.CSS_SELECTOR, '.a8b57ad3ff.d50c412d31.fb9a5438f9.c7a5a1307a')
            airport = div_child2[0].find_element(By.CSS_SELECTOR, '.a53cbfa6de.f45d8e4c32.c875b9e968').text
            
            if 'km' in airport:
                airport = float(airport.replace('km', '').replace(',', '.')) 
            else:
                airport = float(airport.replace('m', '').replace(',', '.')) / 1000
        except:
            airport = 0
            
        # Tìm khoảng cách tới sân bay Đà Nẵng
        with open ('KHDL_DuDoanGiaKhachSan/raw data/hotel_raw.csv', 'a', encoding='utf8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([name, address, price, size, min_beach, airport] + facilities_res)
    driver.quit()  
    
# Địa chỉ tới file msedgedriver.exe
driver = webdriver.Edge(service=Service(r"D:\\msedgedriver.exe"))

Facilities = [
'Hồ bơi ngoài trời',
'Xe đưa đón sân bay',
'Phòng không hút thuốc',
'Giáp biển',
'WiFi miễn phí',
'Phòng gia đình',
'Quầy bar',
'Bữa sáng tuyệt hảo'
]

create_csv()
find_hotel()