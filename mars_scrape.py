# Dependencies
import time
import pandas as pd
import requests as req
from splinter import Browser
from bs4 import BeautifulSoup as bs
import twitterscraper

from twitterscraper import query_tweets_from_user as qtfu


def init_browser():
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()


    #Mars News------------------------------------------


    # Visit url for NASA Mars News -- Latest News
    news_url = "https://mars.nasa.gov/news/"
    browser.visit(news_url)
    html = browser.html

    # Parse HTML with Beautiful Soup  
    soup = bs(html, "html.parser")

    # Get article title and paragraph text
    article = soup.find("div", class_='list_text')
    news_title = article.find("div", class_="content_title").text
    news_p = article.find("div", class_ ="article_teaser_body").text


    ### JPL Mars Space Images-----------------------------


    # Visit url for JPL Featured Space Image
    image_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(image_url)

    # Go to 'FULL IMAGE'
    browser.click_link_by_partial_text('FULL IMAGE')
    time.sleep(5)

    # Go to 'more info'
    browser.click_link_by_partial_text('more info')

    # Parse HTML with Beautiful Soup
    html = browser.html
    image_soup = bs(html, "html.parser")

    # Get featured image
    feat_img_url = image_soup.find('figure', class_='lede').a['href']
    featured_image_url = f'https://www.jpl.nasa.gov{feat_img_url}'


    #Mars Weather ---------------------------------------------


    tweets = qtfu(user='MarsWxReport', limit=10)
    tweets_df=pd.DataFrame(t.__dict__ for t in tweets)
    mars_weather=tweets_df.loc[0,'text']



    #Mars Facts ------------------------------------------------

    # Visit Mars Facts webpage
    facts_url = "https://space-facts.com/mars/"
    browser.visit(facts_url)
    html = browser.html

    # Use Pandas to scrape the table containing facts about Mars
    tables = pd.read_html(facts_url)
    df = tables[0]

    # Rename columns
    df.columns = ['Description','Value']

    # Reset Index to be description
    df = df.set_index('Description')

    # Use Pandas to convert the data to a HTML table string
    html_table = df.to_html(table_id="html_tbl_css",justify='left',index=False)
    data = df.to_dict(orient='records') 

    #Save html to folder and show as html table string
    mars_df = df.to_html(classes = 'table table-striped')


    #Mars Hemisphere ---------------------------------------------------


    # Visit USGS webpage for Mars hemispehere images
    hemispheres_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemispheres_url)
    hemispheres_html = browser.html

    # Parse HTML with Beautiful Soup
    hemispheres_soup = bs(hemispheres_html, "html.parser")

    # Mars hemispheres products data
    all_mars_hemispheres = hemispheres_soup.find('div', class_='collapsible results')
    mars_hemispheres = all_mars_hemispheres.find_all('div', class_='item')

    hemisphere_image_urls = []

    # Iterate through each hemisphere data
    for i in mars_hemispheres:
        # Collect Title
        hemisphere = i.find('div', class_="description")
        title = hemisphere.h3.text
    
        # Collect image link by browsing to hemisphere page
        hemisphere_link = hemisphere.a["href"]    
        browser.visit("https://astrogeology.usgs.gov/" + hemisphere_link)
    
        image_html = browser.html
        image_soup = bs(image_html, 'html.parser')
    
        image_link = image_soup.find('div', class_='downloads')
        image_url = image_link.find('li').a['href']

        # Create Dictionary to store title and url info
        image_dict = {}
        image_dict['title'] = title
        image_dict['img_url'] = image_url
    
        hemisphere_image_urls.append(image_dict)

    
    #Store the Data -------------------------------------------
    #clear data from prior scrapes
    mars_data = {}

    #store the current data
    mars_data = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_image_url": featured_image_url,
        "mars_weather": mars_weather,
        "mars_facts": mars_df,
        "hemisphere_image_urls": hemisphere_image_urls
    }


    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data

if __name__ == '__main__':
    scrape()

 








