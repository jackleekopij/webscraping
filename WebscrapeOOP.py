
import re, urlparse

from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from pymongo import MongoClient


McKinseyURL = 'http://www.mckinsey.com/careers/search-jobs'

class McKinseyJobScrape(object):
    def __init__(self, url):
        self.url = url
        self.driver = webdriver.Chrome()
        self.success = True

    def get_landing_page(self):
        self.driver.get(McKinseyURL)
        #self.driver.find_element_by_xpath('//*[@id="career-search-container"]/section[2]/search-results/section[2]/div/button').click()
        sleep(3)
        self.driver.find_element_by_xpath('//*[@id="career-search-container"]/section[1]/searchbar/section[3]/div/div/div[2]/dl/dt/a').click()
        sleep(1)
        self.driver.find_element_by_xpath('//*[@id="career-search-container"]/section[1]/searchbar/section[3]/div/div/div[2]/dl/dd/div/ul/li[1]/ul/li[2]/a').click()
        sleep(3)
        '''Set the driver to continuously click 'load more' until jobs aren't left. When exception thrown 
           i.e. can't find element then set success flag to False'''

        # while self.success:
        for _ in range(3):
            try:
                self.driver.find_element_by_xpath('//*[@id="career-search-container"]/section[2]/search-results/section[2]/div/button').click()
                sleep(1)
            except:
                self.success = False

        return self.driver.page_source

    def parse_response_from_driver(self):
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        self.job_url_list = [job_url.get("href") for job_url in soup.find_all('a',class_= 'job-listing-link -arrow')]
        return self.job_url_list

    def get_job_information(self):
        job_qualifications = []
        for job_url in self.job_url_list:
            job_description = self.driver.get(job_url.replace("./search-jobs/", "http://www.mckinsey.com/careers/search-jobs/"))
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            job_qualifications.append({str(soup.find('h1', class_='headline')):str(soup.find('div', class_='narrow'))})
            for ul_tag in soup.find('div', class_='narrow').find_all("ul"):
                for li_tag in ul_tag.find_all('li'):
                    print "li tags {0}".format(li_tag)

            print type(job_qualifications[0])
        return job_qualifications


class MongoDB(object):
    # def __init__(self):

    def set_url_to_iterable(self,list_of_objects):
        url_list = []
        for index, element in enumerate(list_of_objects):
            key = "url {0}".format(index)
            url_list.append({key: str(element)})
        print url_list
        return url_list


    def connect_to_database(self, url_object):
        client = MongoClient()
        db = client.Jobs_urls
        result = db.mckinseyUrls.insert_many(url_object)
        return result



# The below condition is used for modularising python scripts.
# This allows you to have .py files run as stand alone applications or to be
# imported and not run as the main method.
if __name__ == '__main__':
    McKinsey = McKinseyJobScrape("Mckinsey jobs URL")
    McKinsey.get_landing_page()

    url_response =  McKinsey.parse_response_from_driver()

    print McKinsey.get_job_information()

    # test_mongo = MongoDB()
    # url_object = test_mongo.set_url_to_iterable(url_response)
    # print test_mongo.connect_to_database(url_object)
