import scrapy
from bostonrealtyadvisorsscraper.items import BostonrealtyadvisorsscraperItem

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import time
from urllib.parse import urljoin

from bostonrealtyadvisorsscraper.settings import SELENIUM_DRIVER_EXECUTABLE_PATH


class BostonRealtySpider(scrapy.Spider):
    name = 'search_boston_realty'
    custom_settings = {
        'FEEDS': {'data/%(name)s_%(time)s.jsonl': {'format': 'jsonlines'}}
        }

    def start_requests(self):
        property_listing = ['842304-lease']
        for listing in property_listing:
            listing_url = f"https://buildout.com/plugins/5339d012fdb9c122b1ab2f0ed59a55ac0327fd5f/bradvisors.com/inventory/{listing}?pluginId=0&iframe=true&embedded=true&cacheSearch=true&propertyId={listing}"
            yield scrapy.Request(url=listing_url, callback=self.parse_listing, meta={'listing': listing, 'listing_url': listing_url })

    def parse_listing(self, response):
        item = {}
        item['url'] = response.meta['listing_url']

        """
        LOCATION
        """
        map_container = response.css('div.js-map-container.map-container.w-100')
        item['location'] = [{
            'address': response.css('h2.plugin-header-address::text').get().replace('|', ','),
            'building_name': map_container.attrib['data-address'],
            'latitude': map_container.attrib['data-latitude'],
            'longitude': map_container.attrib['data-longitude']
        }
        ]
        """
        BROCHURE DOCUMENTS
        """
        item['brochure_docs'] = []
        brochure_blocks = response.css('div.js-folder-table')
        for block in brochure_blocks:
            brochure = {}
            try:
                base_url = 'https://buildout.com'
                brochure['brochure_doc_link(s)'] = [urljoin(base_url, element) for element in block.css('a.js-doc-link::attr(href)').getall()]

                [element.replace('\r', '') for element in response.css('div.section p::text').getall()]
            except Exception as e:
                print('ERROR: There was error trying to get brochure link', e)
                brochure['brochure_link(s)'] = ''

        item['brochure_docs'].append(brochure)
        """
        PROPERTY DETAILS TABLE
        """
        item['property_details'] = []
        table_row = response.css('div.summary-table-split-item.pr-sm-3 dd::text').getall()
        property_table = {
            'price': table_row[0],
            'size': table_row[1],
            'property_type': table_row[2],
            'building_size': table_row[3],
        }

        item['property_details'].append(property_table)

        """
        SPACES INFORMATION
        """
        item['spaces'] = []
        space_table_row = response.css('div#spaces table.table.mb-0 td::text').getall()
        try:
            spaces_table = {
                'title': response.css('div.card-body h5::text').get(),
                'space_available': space_table_row[0],
                'lease_rate': space_table_row[2],
                'availability': space_table_row[3],
                'sublease': space_table_row[1],
            }
        except Exception as e:
            print('ERROR: There was error trying to get spaces information', e)
            spaces_table = {}

        item['spaces'].append(spaces_table)

        """
        BROKER INFORMATION
        """
        item['broker_info'] = []
        broker_info_block = response.css('div.row.no-gutters')
        for broker in broker_info_block:
            brokers = {}

            # name
            try:
                brokers['name'] = broker.css('div.col-9.pl-3 strong::text').get() or broker.css('div.col-9.pl-3 strong a::text').get()
            except Exception as e:
                print('ERROR: There was error trying to get broker name', e)
                brokers['name'] = ''

            # email
            try:
                brokers['email'] = broker.css('div.broker-email a::attr(href)').get().replace('mailto:', '')
            except Exception as e:
                print('ERROR: There was error trying to get broker email', e)
                brokers['email'] = ''

            # telephone
            try:
                brokers['telephone'] = broker.css('div.broker-phone a::attr(href)').get()
            except Exception as e:
                print('ERROR: There was error trying to get broker telephone number', e)
                brokers['telephone'] = ''

            # mobile
            try:
                mobile = broker.css('div.broker-cell a::attr(href)').get()
                if mobile is not None:
                    brokers.update({'mobile': mobile})
                else:
                    yield None
            except Exception as e:
                print('ERROR: Error trying to look for mobile number', e)

            item['broker_info'].append(brokers)

            """
            DESCRIPTION
            """
            item['description'] = [element.replace('\r', '') for element in response.css('div.section p::text').getall()]


        yield item


class BostonRealtyListingsSpider(scrapy.Spider):
    name = 'listing_crawler'

    custom_settings = {
        'FEEDS': {'data/%(name)s_%(time)s.jsonl': {'format': 'jsonlines'}}
        }

    def start_requests(self):
        url = 'https://buildout.com/plugins/5339d012fdb9c122b1ab2f0ed59a55ac0327fd5f/bradvisors.com/inventory/?pluginId=0&iframe=true&embedded=true&cacheSearch=true&initialPropertyUses=1'
        yield scrapy.Request(url=url, callback=self.parse_listings)


    async def parse_listings(self, response):
        url = 'https://buildout.com/plugins/5339d012fdb9c122b1ab2f0ed59a55ac0327fd5f/bradvisors.com/inventory/?pluginId=0&iframe=true&embedded=true&cacheSearch=true&initialPropertyUses=1'
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        desired_capabilities = options.to_capabilities()
        driver = webdriver.Chrome(SELENIUM_DRIVER_EXECUTABLE_PATH, desired_capabilities=desired_capabilities)


        driver.get(url)
        try:
            for x in range(0,5):
                wait = WebDriverWait(driver, 30)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "result-list-item")))
                wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "js-paginate-btn.paginate-button.clickable")))
                    # next_page_buttons = driver.find_elements(By.CLASS_NAME,'js-paginate-btn.paginate-button.clickable')
                    # next_page_buttons[x].click()

                driver.execute_script(f'document.querySelectorAll("div.js-paginate-btn.paginate-button.clickable")[{x}].click()')
                driver.set_page_load_timeout(10)
                time.sleep(1)

                listings = driver.find_elements(By.CLASS_NAME, "result-list-item")

                if listings is not None:
                    for listing in listings:
                        listing_item = BostonrealtyadvisorsscraperItem()

                        listing_info = listing.find_elements(By.CSS_SELECTOR,'div.list-item-attribute')
                        listing_item['property_title'] = listing.find_element(By.CSS_SELECTOR, 'h5.ellipsis.plugin-primary-color.list-item-title').text
                        listing_item['transaction_type'] = listing.find_element(By.CSS_SELECTOR,'div.list-item-banner').text.replace('\n', '').lstrip().rstrip()
                        listing_item['building_address'] = listing_info[0].text.replace('|', ',')
                        if listing_item['transaction_type'] == "FOR SALE":
                            listing_item['price'] = listing_info[1].text
                            listing_item['size'] = listing_info[2].text
                        elif listing_item['transaction_type'] == "FOR LEASE" or "FOR SUBLEASE":
                            listing_item['price'] = listing_info[2].text
                            listing_item['size'] = listing_info[1].text

                        yield listing_item

                continue
        except Exception as error:
            print('ERROR: ', error)
            driver.close()










