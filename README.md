# Case Scraper
Code repo for scraping criminal cases from websites. Design doc can be found at https://docs.google.com/document/d/1572dcR6u2lWWdua-O1tvze7mPz6TO3cTnF7L9-bkqsQ/edit?usp=sharing

To scrape data from court websites, I have built the scrapers by using Python Request, BeautifulSoup4, ScraperAPI, Scrapy Splash, 2Captcha and Pytest for unit test.
I have deployed this scrapers to AWS Lambda to serve the api. You can find more details from the doc I shared above.

Python Request

BeautifulSoup4

Scrapy Splash(to get the html from javascript websites instead of Selenium)

ScraperAPI(Rotating Proxy)

2Captcha(to bypass the Google Captcha)

Pytest

This project are including well-structured and well-tested scrapers for 14 websites.