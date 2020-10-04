from selenium import webdriver
import time
import re
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

df = pd.read_csv("artists.csv", usecols=['slug']).drop_duplicates()
slug_list = df['slug'].to_list()

driver = webdriver.Chrome()

slugs = []
joined_dates = []
products = []
print_avail = []
is_new = []

for slug in slug_list[6:10]:
	# Get to the artist's page
	print(slug)
	driver.get(f'https://www.artfinder.com/{slug}/sort-artist_order/page-1/#/')
	time.sleep(1)
	# Close the pop up for discount
	try:
		close_pop_up = driver.find_element_by_xpath('//div[@class="af-register-modal--b"]//a[@class="close"]')
		close_pop_up.click()
		time.sleep(1)
	except:
		pass

	# Scroll till the end
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
	# WebDriverWait(driver, 10).until(
	# 	EC.presence_of_element_located((By.XPATH,
	# 		'//div[@class="text-right margin margin-l margin-bottom"]')))
	time.sleep(7)
	# Find two elements
	joined_artfinder = driver.find_element_by_xpath('//p[@class="af-small-text margin margin-none"]').text.split(": ")[1]

	# Find number of pages
	try:
		num_page = driver.find_element_by_xpath('//ul[@class="af-pagination margin margin-s margin-top"]').text.split("\n")[-1]
	except:
		num_page = 1

	# Iterate through the pages
	for page in range(1,int(num_page)+1):
		# No need to get driver for the already loaded first page 
		if page != 1:
			driver.get(f'https://www.artfinder.com/{slug}/sort-artist_order/page-{page}/#/')
			# WebDriverWait(driver, 10).until(
			# 	EC.visibility_of_all_elements_located((By.XPATH,
			# 		'//div[@style="display: flex; margin-left: -10px;"]')))
			time.sleep(7)
			# Scroll thill the bottom
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
			# WebDriverWait(driver, 10).until(
			# 	EC.visibility_of_all_elements_located((By.XPATH,
			# 		'//div[@style="display: flex; margin-left: -10px;"]')))		
			time.sleep(7)
		
		# Scrape the product names
		product_names = driver.find_element_by_xpath('//div[@class="af-place-container margin margin-s margin-bottom"]')
		product_names = product_names.find_elements_by_xpath('//a[@class="af-place fit-in"]')
		print(len(product_names))
		for product in product_names:
			product = product.get_attribute('href')
			if product[-8:] == "/prints/":
				prod = product.split('/quick-view/')[-1].split('/')[0]
			else:
				prod = product.split("/")[-1]
			# print(prod)
			products.append(prod)

		# Scrape other elements
		others = driver.find_elements_by_xpath('//div[@class="af-place-container margin margin-s margin-bottom"]')
		for other in others:
			if re.findall("Prints available", other.text) == []:
				print_avail.append("NA")
			else:
				avail = other.text.split(" ")[-1]
				print_avail.append(avail)

			new = other.text
			if new[-3:] == "New":
				is_new.append("New")
			else:
				is_new.append("NA")

			slugs.append(slug)
			joined_dates.append(joined_artfinder)

# Create dictionary of the values
product_df = {'slug': slugs, 'joined_dates': joined_dates, 
				'products': products,'print_avail': print_avail, 'is_new': is_new}

# convert dictionary to df and export as .csv
df = pd.DataFrame.from_dict(product_df, orient='index')
df_final = df.transpose()
df_final.to_csv('product_df.csv', index=False, header=True, encoding='utf-8')

driver.quit()







