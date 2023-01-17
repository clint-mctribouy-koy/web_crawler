## BOSTON REALTY WEB SCRAPER
- This is a web crawler i created to scrape real estate lisitings data from Boston Realty Advisors
- There are two spiders in the __web_crawler/bostonrealtyadvisorsscraper/spiders/bostonrealtyadvisorsscraper.py__ file. One to scrape data from a single listings page and the other that includes pagination to quickly scrape data from multiple pages. 
- The stack used to create this were **Scrapy** and **Selenium**
- The json output for the data crawled by both spiders can be found in the __web_crawler/bracrawler_listings.json__ and __web_crawler/bradvisory_single_listing.json__ files respectively.
- Using precise **XPath** and **CSS** selectors to extract data.
