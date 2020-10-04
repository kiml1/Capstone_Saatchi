from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import time
import re
import csv
import pandas as pd

# initialize Chrome in fullscreen because of popups
driver = webdriver.Chrome()
driver.maximize_window()

# Go to the page that we want to scrape. We need to go through all the hrefs
# let's get the hrefs first
href_df = pd.read_csv("../<pathhere>.csv",
                      usecols=['slugss'])
href_list = href_df['slugss'].to_list()
# loop all hrefs
for href in href_list:
    driver.get(f'https://www.artfinder.com/product/{href}')
    time.sleep(2)

    # Click review button to go to the shipping section
    close_pop_up = driver.find_element_by_xpath(
        '//div[@class="af-register-modal--b"]//a[@class="close"]')
    close_pop_up.click()
    time.sleep(2)

    wait_shipping = WebDriverWait(driver, 10)
    shipping_button = driver.find_element_by_xpath(
        '//div[@class="accordion-navigation"]//span[@class="toggler"]')
    shipping_button.click()
    time.sleep(3)

    # here we create a dictionary of things we want
    product_dict = {}

    product_dict['title'] = driver.find_elements_by_xpath(
        '//h1[@class="h2 af-underline-links"]')[0].text
    product_dict['type'] = driver.find_element_by_xpath(
        '//h2[@class="p af-underline-links margin margin-s"]/a').text

    try:
        product_dict['price'] = driver.find_elements_by_xpath(
            '//p[@class="h2 margin margin-m margin-bottom"]/span[@class="main-price js-price"]')[0].text
        product_dict['sold'] = "False"
    except:
        product_dict['price'] = driver.find_elements_by_xpath(
            '//p[@class="h2 margin margin-m margin-bottom"]/span[@class="linethrough"]')[0].text
        product_dict['sold'] = driver.find_elements_by_xpath(
            '//p[@class="h2 margin margin-m margin-bottom"]/span[@class="gray-text"]')[0].text

    bulletPoints_raw = driver.find_elements_by_xpath(
        '//ul[@class="af-underline-links"]/li/span')
    product_dict['bulletPoints'] = list(
        map(lambda x: x.text, bulletPoints_raw))

    # some links have an extra space in the p[@class]
    try:
        product_dict['shipping_price'] = driver.find_element_by_xpath(
            '//p[@class="clearfix af-bg-dots"]//span[@class="right af-bold"]/strong').text
    except:
        product_dict['shipping_price'] = driver.find_element_by_xpath(
            '//p[@class="clearfix af-bg-dots "]//span[@class="right af-bold"]/strong').text

    product_dict['description'] = driver.find_element_by_xpath(
        '//div[@id="product-description"]/p').text
    product_dict['materialsUsed'] = driver.find_elements_by_xpath(
        '//div[@id="product-description"]/p')[1].text.split(",")

    tags_raw = driver.find_elements_by_xpath(
        '//p[@class="af-line-height-l"]/a')
    product_dict['tags'] = list(
        filter(None, list(map(lambda x: x.text, tags_raw))))

    try:
        featured_raw = driver.find_element_by_xpath(
            '//div[@class="show-for-large-up margin margin-m margin-top"]//a')
        product_dict['featuredByEditors'] = list(
            map(lambda x: x.text, featured_raw))
    except:
        product_dict['featuredByEditors'] = "--NA--"

    # here, check if the product has print option
    time.sleep(2)
    try:
        otherOption = driver.find_element_by_xpath(
            '//div[@class="large-4 medium-12 columns af-offset-top "]/ul[@class="tabs af-red-tabs text-center"]')
        # if exists, click on it
        click_otherOption = driver.find_element_by_xpath(
            '//div[@class="large-4 medium-12 columns af-offset-top "]/ul[@class="tabs af-red-tabs text-center"]//a[@aria-selected="false"]')
        click_otherOption.click()
        # get what is the other option: Prints,... or anything else?
        product_dict['otherOption'] = driver.find_element_by_xpath(
            '//div[@class="large-4 medium-12 columns af-offset-top "]/ul[@class="tabs af-red-tabs text-center"]//a[@aria-selected="true"]').text

        try:
            # there could be many alternatives for the option selected
            alternatives_list = driver.find_element_by_xpath(
                '//label[@class="margin margin-none alternative-field"]')
            product_dict['otherOptionAlternatives'] = list(map(lambda x: x.text, driver.find_elements_by_xpath(
                '//label[@class="margin margin-none alternative-field"]//option')))
        except:
            product_dict['otherOptionAlternatives'] = [driver.find_element_by_xpath(
                '//div[@class="margin margin-none alternative-field"]/p').text]

    except:
        product_dict['otherOption'] = "--NA--"
        product_dict['otherOptionAlternatives'] = "--NA--"

    # write to csv
df = pd.DataFrame.from_dict(product_dict, orient='index')
df_final = df.transpose()
df_final.to_csv('products.csv', index=False, header=True, encoding='utf-8')

# close bot
time.sleep(1)
driver.close()
