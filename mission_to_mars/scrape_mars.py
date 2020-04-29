from bs4 import BeautifulSoup
from splinter import Browser
import requests
import pandas as pd
import pymongo
import time


# Create connection variable
conn = 'mongodb://localhost:27017'

# Pass connection to the pymongo instance.
client = pymongo.MongoClient(conn)

# Connect to a database or create one if it doesn't exist.
db = client.mars_db

# Drops collection if exists
db.planet.drop()


# set the url for the html page to be scraped
#web_url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'


def scrape():

    # set the path to te chromedriver
    executable_path = ({"executable_path": "./chromedriver"})

    # instantiate Browser based on path
    browser = Browser("chrome", **executable_path, headless=False)

    # set the url for the html page to be scraped
    web_url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'

    # Start Browsing the page
    browser.visit(web_url)

    # set sleep for 5 seconds to
    time.sleep(5)

    # identify teh parser engine to use
    soup = BeautifulSoup(browser.html, "html.parser")

    # initiatlize a paragrpah list to hold temp results that we will iterate over
    paragraph = []
    paragraph = soup.find_all("div", class_="article_teaser_body")

    # Get the news summary we are interested in
    news_summary = paragraph[0].text

    links = soup.find_all("div", class_="content_title")
    headline = []

    try:
        for link in links:
            anchor = link.find('a')
            # print(anchor)
            if anchor != None:
                headline.extend(anchor)
    except TypeError:
        pass

    # Get The NEws headline we are inetrested in
    news_headline = headline[0]

    # First Scrape - Complete!

    # Start the next scrape
    new_web_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'

    # Open Browser window
    browser.visit(new_web_url)

    time.sleep(5)

    # set the Parser engine to use
    soup = BeautifulSoup(browser.html, "html.parser")

    # Get the featured img url for our Dictionary
    hdr = soup.find('div', class_='carousel_container')
    feature_img = hdr.find('article')
    img_background = feature_img['style']
    img_id = img_background[53:61]
    feature_image_url = f'https://www.jpl.nasa.gov/spaceimages/images/largesize/{img_id}_hires.jpg'

    # traverse the image tree
    img = soup.find('a', class_='button fancybox')['data-fancybox-href']

    img_url = 'https://www.jpl.nasa.gov' + img

    mars_weather_url = 'https://twitter.com/marswxreport?lang=en'

    browser.visit(mars_weather_url)

    # set the sleep to 6 seconds
    time.sleep(6)

    soup = BeautifulSoup(browser.html, "html.parser")

    tweet_div = soup.find_all(
        'div', class_='css-901oao r-hkyrab r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0')

    # Get the Mars Weather details that we need for the dictionary
    mars_weather = tweet_div[0].text

    mars_facts_url = 'https://space-facts.com/mars/'

    tables = pd.read_html(mars_facts_url)

    df = tables[0]

    df = df.rename(columns={0: 'Metric', 1: 'Value'})
    df.set_index('Metric', inplace=True)

    # Get the table variable with the html we need for our Dictionary
    html_table = df.to_html()
    html_table.replace('\n', '')

    hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    browser.visit(hemisphere_url)

    time.sleep(6)

    soup = BeautifulSoup(browser.html, "html.parser")

    hemisphere_image_urls = []
    base_url = 'https://astrogeology.usgs.gov'
    products = soup.find_all('div', class_='description')
    for product in products:
        title = product.h3.text
        targ = product.a['href']
        browser.visit(base_url + targ)
        soup = BeautifulSoup(browser.html, "html.parser")
        time.sleep(5)
        sample_div = soup.find('div', class_='downloads')
        anchor = sample_div.ul.li.a['href']

        hemisphere = {}

        hemisphere['title'] = title
        hemisphere['img_url'] = anchor

        # Append all the Hemisphere elements we need for our
        hemisphere_image_urls.append(hemisphere)

    # Now create a collection
    mars_data_dict = {
        'news_title': news_headline,
        'news_p': news_summary,
        "featured_image_url": feature_image_url,
        'mars_weather': mars_weather,
        'facts_table': html_table,
        'hemisphere_images': hemisphere_image_urls
    }

    # insert the collection into the database
    db.planet.insert_many([

        mars_data_dict
    ]
    )
    # clean-up by making sure to close the Chrome Browser
    browser.quit()
