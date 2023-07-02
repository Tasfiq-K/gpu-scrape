from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re
import time
import random
import pandas as pd

url = "https://www.techpowerup.com/gpu-specs/"

columns = ['gpu_name', 'gpu_chip', 'released_date', 'bus', 'mem_size(GB)', 'mem_type', 'mem_bus(bit)', 
           'mem_clock(MHz)', 'gpu_clock(MHz)', 'shaders', 'TMUs', 'ROPs']

def get_price(driver, url):
    contents = {}
    driver.get(url)
    time.sleep(random.randint(1, 10))

    try:
        price = driver.find_element(By.XPATH, "//dd[contains(text(),'USD')]").text.split(' ')[0]
        contents['price($)'] = float(price.replace(',', ''))
    except NoSuchElementException:
        contents['price($)'] = 0.0

    return contents
    

def scrape_details(row):

    contents = {}

    contents['gpu_name'] = row[0].text
    contents['gpu_chip'] = row[1].text
    contents['released_date'] = row[2].text
    contents['bus'] = row[3].text
    contents['mem_size(GB)'] = int(row[4].text.split(', ')[0].split(' ')[0])
    contents['mem_type'] = row[4].text.split(', ')[1]
    contents['mem_bus(bit)'] = int(row[4].text.split(', ')[2].split(' ')[0])
    contents['mem_clock(MHz)'] = int(row[6].text.split(' ')[0])
    contents['gpu_clock(MHz)'] = int(row[5].text.split(' ')[0])
    contents['shaders'] = int(row[7].text.split(' / ')[0])
    contents['TMUs'] = int(row[7].text.split(' / ')[1])
    contents['ROPs'] = int(row[7].text.split(' / ')[2])

    return contents


data = []
price = []

def main():
    # initializing the driver and firefox profile
    webdriver_path = "C:\Program Files (x86)\geckodriver.exe"
    options = Options()
    options.set_preference('profile', webdriver_path)
    driver = Firefox(options=options)
    driver.get(url)
    time.sleep(5)

    table = driver.find_elements(By.TAG_NAME, 'tbody')[-1].find_elements(By.TAG_NAME, 'td')

    hrefs = [link.get_attribute('href') for link in driver.find_elements(By.CSS_SELECTOR, "td[class^='vendor-'] > a")]

    for row in range(0, len(table) // 8):
        new_row = table[row * 8 : (row + 1) * 8]


        tic = time.perf_counter()
        data.append(scrape_details(new_row))
        toc = time.perf_counter()

        print(f"Completed {row + 1} batch, Took about {(toc - tic) // 60} Mins, {(toc - tic) % 60} Sec(s)")
    
    print("--" * 80)

    for idx, link in enumerate(hrefs):
        tic = time.perf_counter()
        price.append(get_price(driver, link))
        toc = time.perf_counter()
        print(f"Completed link {idx + 1}, Took about {(toc - tic) // 60} Mins, {(toc - tic) % 60} Sec(s)")


    
    df = pd.DataFrame(data=data, columns=columns)
    df.to_csv('gpu_data.csv', index=False)

    df_price = pd.DataFrame(data=price, columns=['price($)'])
    df_price.to_csv('gpu_price.csv', index=False)

    driver.close()

    return



if __name__ == "__main__":
    tic = time.perf_counter()
    main()
    toc = time.perf_counter()
    print(f"Total time took to scrape: {(toc - tic) // 60} Mins, {(toc - tic) % 60} Sec(s)")