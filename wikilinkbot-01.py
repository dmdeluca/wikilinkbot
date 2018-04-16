
#This code is not open-source. It is copyrighted by David DeLuca.

from selenium import webdriver

from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException

import time
import urllib
import math
import re
import string
import datetime

list_of_pages = []

def link_is_valid(url):
    must_have = ['wikipedia']
    must_not_have = ['#']
    for each_must in must_have:
        if url.find(each_must) == -1:
            return 0
    for each_must_not in must_not_have:
        if url.find(each_must_not) != -1:
            return 0
    return 1

class page:
    def __init__(self,title_,url_):
        #initialize every page object with a topic and a url
        self.title = title_
        self.url = url_
        self.outgoing_links = []
        self.incoming_links = []
    def add_out_link(self,page_):
        if page_ not in self.outgoing_links:
            self.outgoing_links.append(page_)
    def add_in_link(self,page_):
        if page_ not in self.incoming_links:
            self.incoming_links.append(page_)
    def print_links(self,in_or_out,with_links=1):
        if in_or_out == 'in':
            print_list = self.incoming_links
            list_title = "Incoming Links"
        else:
            print_list = self.outgoing_links
            list_title = "Outgoing Links"        
        #print a list of all outgoing links on page
        list_count = len(print_list)
        print(list_title,"(",list_count,") :")
        for c, each_page in enumerate(print_list,1):
            if with_links:
                print('\t',str(c)+".\t",each_page.title," - (",each_page.url,")")
            else:
                print('\t',str(c)+".\t",each_page.title)
    def print_count(self):
        print("Page Title:",self.title)
        print("\t"+self.title,"<--",len(self.incoming_links),"articles.")
        print("\t"+self.title,"-->",len(self.outgoing_links),"articles.")
    def adds(self,in_or_out,links):
        if in_or_out == 'in':
            for c,each_link in enumerate(links,1):
                print("Reading incoming links on additional page: "+str(round(c/len(links)*100,2))+"%\t","Incoming links catalogued:",len(self.incoming_links),end = "\r")
                this_link_title = each_link.get_attribute("title")
                this_link_url = each_link.get_attribute("href")
                if link_is_valid(this_link_url):
                    new_linked_page_object = page(this_link_title,this_link_url)
                    self.add_in_link(new_linked_page_object)
                    list_of_pages.append(new_linked_page_object)
        elif in_or_out == 'out':
            for c,each_link in enumerate(links,1):
                print("Reading outgoing links: "+str(round(c/len(links)*100,2))+"%\t","Outgoing links catalogued:",len(self.outgoing_links),end = "\r")
                this_link_title = each_link.get_attribute("title")
                this_link_url = each_link.get_attribute("href")
                if link_is_valid(this_link_url):
                    known_page = find_page_by_url(this_link_url)
                    if known_page != -1:
                        self.add_out_link(known_page)
                    else:
                        new_linked_page_object = page(this_link_title,this_link_url)
                        self.add_out_link(new_linked_page_object)
                        new_linked_page_object.add_in_link(self)
                        list_of_pages.append(new_linked_page_object)

def do_chrome():
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2, "profile.managed_default_content_settings.images":2}
    chrome_options.add_experimental_option("prefs",prefs)
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.implicitly_wait(10)
    print("\nOpened Chrome browser.")
    return driver

def open_what_links_to_wiki_page_for(search_term,driver):
    driver.get("https://"+language_select+".wikipedia.org/w/index.php?title=Special:WhatLinksHere/"+search_term+"&namespace=0&limit=10000&hideredirs=1")
    print("Opened links page for "+search_term+".")

def find_page_by_url(url_):
    for each_page in list_of_pages:
        if each_page.url == url_:
            #print(url_,"already in pages list")
            return each_page
    return -1

def fast_count(keyword,driver_,language_select):

    driver_.get("https://"+language_select+".wikipedia.org/wiki/"+keyword)
    page_title = driver_.find_element_by_css_selector("h1").text
    page_url = driver_.current_url

    print("Opened wikipedia page for "+page_title+".")

    links = driver_.find_elements_by_css_selector("#mw-content-text > div > p > a")
    outgoing_links_number = len(links)

    incoming_links_number = 0

    open_what_links_to_wiki_page_for(page_title,driver_)
    links = driver_.find_elements_by_css_selector("#mw-whatlinkshere-list > li > a")
    incoming_links_number += len(links)

    while len(links) == 5000:
        driver_.get("https://"+language_select+".wikipedia.org/w/index.php?title=Special:WhatLinksHere/"+page_title+"&namespace=0&limit=5000&hideredirs=1&from=25829421&back=0")
        links = driver_.find_elements_by_css_selector("#mw-whatlinkshere-list > li > a")
        incoming_links_number += len(links)

    print("\nPage Title:",page_title)
    print("\t"+page_title,"<--",incoming_links_number,"articles.")
    print("\t"+page_title,"-->",outgoing_links_number,"articles.")

def simple_count(keyword,driver_,language_select):
    driver_.get("https://"+language_select+".wikipedia.org/wiki/"+keyword)
    page_title = driver_.find_element_by_css_selector("h1").text
    page_url = driver_.current_url

    links = driver_.find_elements_by_css_selector("#mw-content-text > div > p > a")

    outgoing_links_list = []
    incoming_links_list = []

    #add outgoing links to page object

    for c, each_link in enumerate(links,1):
        print("Reading outgoing links: "+str(round(c/len(links))),end = "\r")
        this_link_title = each_link.get_attribute("title")
        this_link_url = each_link.get_attribute("href")
        if link_is_valid(this_link_url) and this_link_url not in outgoing_links_list:
            outgoing_links_list.append(this_link_url)

    open_what_links_to_wiki_page_for(page_title,driver_)
    links = driver_.find_elements_by_css_selector("#mw-whatlinkshere-list > li > a")

    for each_link in links:
        print("Reading incoming links: "+str(round(c/len(links))),end = "\r")
        this_link_title = each_link.get_attribute("title")
        this_link_url = each_link.get_attribute("href")
        if link_is_valid(this_link_url):
            incoming_links_list.append(this_link_url)

    print("\nPage Title:",page_title)
    print(page_title,"<--",str(len(incoming_links_list))+" articles.")
    print(page_title,"-->",str(len(outgoing_links_list))+" articles.")

def harvest_links(keyword,driver_,language_select):
    
    driver_.get("https://"+language_select+".wikipedia.org/wiki/"+keyword)
    page_title = driver_.find_element_by_css_selector("h1").text
    page_url = driver_.current_url

    known_page = find_page_by_url(page_url)

    if known_page != -1:
        this_page = known_page
    else:
        this_page = page(page_title,page_url)
        list_of_pages.append(this_page)

    #get outgoing links
    links = driver_.find_elements_by_css_selector("#mw-content-text > div > p > a")

    #add outgoing links to page object
    this_page.adds('out',links)
    
    #get incoming links to page object
    open_what_links_to_wiki_page_for(page_title,driver_)
    links = driver_.find_elements_by_css_selector("#mw-whatlinkshere-list > li > a")
    this_page.adds('in',links)

    while len(links) == 5000:
        driver_.get("https://"+language_select+".wikipedia.org/w/index.php?title=Special:WhatLinksHere/"+page_title+"&namespace=0&limit=5000&hideredirs=1&from=25829421&back=0")
        links = driver_.find_elements_by_css_selector("#mw-whatlinkshere-list > li > a")
        this_page.adds('in',links)

    return this_page

user_input = ['']

print("Welcome to WikiLinkBot 1.0.\n\nFor the help menu, enter 'h'.")

while user_input[0] != 'quit':
    user_input = input('\nTo perform a WikiLinkBot search, type "full," "titles," or "count" and then the topic/title of the page you would like to examine: ').split(' - ')
    language_select = "en"
    if user_input[len(user_input)-1][0]== '+':
        language_select = user_input[len(user_input)-1][1:]
    if user_input[0] == 'count':
        my_driver = do_chrome()
        fast_count(user_input[1],my_driver,language_select) 
        my_driver.quit()
        print("( Language chosen:",language_select," )")
    elif user_input[0] == 'full':
        my_driver = do_chrome()
        p = harvest_links(user_input[1],my_driver,language_select)
        my_driver.quit()
        p.print_links('in')
        p.print_links('out')
        p.print_count()
        print("( Language chosen:",language_select," )")
    elif user_input[0] == 'titles':
        my_driver = do_chrome()
        p = harvest_links(user_input[1],my_driver,language_select)
        my_driver.quit()
        p.print_links('in',0)
        p.print_links('out',0)
        p.print_count()
        print("( Language chosen:",language_select," )")
    elif user_input[0] == 'h':
        print("\nHere is an example input:\n\ncount - dogs\n\nThis input will tell me to count the number of links connected to the page 'Dog', incoming and outgoing on Wikipedia.\n\nTo run the search in French, type: count - dogs - +fr\n\nFor Deutsch, type +de. For Italian, type +it.\n\nOther commands besides 'count' are 'full' and 'titles.'\n\tcount = give a quick count of articles\n\tfull = give an exhaustive list of linking articles by title, including URLs\n\ttitles = give the same exhaustive list, without URLs\n\nEnter 'q' to quit.\n\n")
    else:
        print("Invalid input. Try again. \n")
    print("\n")

print("\n\nBye now!\n\nCopyright 2018 David DeLuca\n\n")
