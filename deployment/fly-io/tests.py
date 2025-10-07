import undetected_chromedriver as uc
from time import sleep
import sys
from selenium import webdriver

print(sys.version_info)

driver = uc.Chrome()
str1 = driver.capabilities["browserVersion"]
str2 = driver.capabilities["chrome"]["chromedriverVersion"].split(" ")[0]
print(str1)
print(str2)
print(str1[0:2])
print(str2[0:2])
assert str1[0:2] == str2[0:2], f"version mismatch: {str1}, {str2}"

driver.get("https://check.torproject.org/")
sleep(5)
scraped_page = driver.page_source
driver.quit()
print(scraped_page)
