import os

import sqlite3
import time
import sys
import urllib.parse
import json
from dateutil import parser
import datetime
from bs4 import BeautifulSoup
import requests
from oauth import authorize_creds

# connect ke sqlite
NAME_DB = "database.db"
conn = sqlite3.connect(NAME_DB)

SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


#  service_account_file.json is the private key that you created for your service account.

# Update link article sudah di index
def update(link_article):
    conn.execute("UPDATE tbl_article set indexing = 1 WHERE link ='" + link_article + "'")
    conn.commit()


# untuk run index
def indexing(jsonFile):
    i = 1
    while i <= 200:
        http = authorize_creds(jsonFile)
        a = i
        cursor = conn.execute("SELECT link FROM tbl_article WHERE indexing = 0 ORDER BY RANDOM() LIMIT 1")
        cursor_count = conn.execute("SELECT COUNT(*) FROM tbl_article WHERE indexing = 0")
        result = cursor_count.fetchall()
        if result[0][0] == 0:
            print("data kosong")
            sys.exit()
        else:
            for row in cursor:
                url = row[0]
                content = """{
                        \"url\": \"""" + url + """\",
                        \"type\": \"URL_UPDATED\"
                        }"""
                response, content = http.request(ENDPOINT, method="POST", body=content)
                status = response['status']
                if status == '429':
                    print("limit request")
                    return
                else:
                    update(url)
                    check_link(url, http)
                    print(url)
                    # print(response)
                    print("Status = " + response['status'])
                    print("File Json = " + jsonFile)
                    print("====================================")
                    # print(content)
                    time.sleep(3)
        i += 1


# check link dan tgl indexing
def check_link(url, http):
    url_convert = urllib.parse.quote(url, safe='')
    response, content = http.request(
        "https://indexing.googleapis.com/v3/urlNotifications/metadata?url=" + url_convert + "",
        method="GET")
    response_object = json.loads(content)
    date = parser.parse(response_object['latestUpdate']['notifyTime']).date()
    link = response_object['url']
    result = datetime.datetime.strftime(date, '%d-%m-%Y')
    update_date(result, link)


# insert tanngal indexing
def update_date(date, link):
    conn.execute("UPDATE tbl_article set date = '" + date + "' WHERE link ='" + link + "'")
    conn.commit()


# script dapat link sitemap

# untuk scrap link dari sitemap
def sitemap(base_url):
    r = requests.get("" + base_url + "sitemap.xml")
    xml = r.text

    soup = BeautifulSoup(xml, 'html.parser')
    singlesitemapTags = soup.find_all("url")
    sitemapTags = soup.find_all("sitemap")
    jmlh = len(sitemapTags)
    print(jmlh)
    print("The number of sitemaps are {0}".format(len(sitemapTags)))
    if jmlh == 0:
        print("Single data ")
        for sitemap2 in singlesitemapTags:
            link2 = sitemap2.findNext("loc").text
            # print(link2)
            insert(link2)
    else:
        for sitemap in sitemapTags:
            link = sitemap.findNext("loc").text
            # print(link)
            url = requests.get(link)
            data = url.text
            soup2 = BeautifulSoup(data, 'html.parser')
            sitemapTags2 = soup2.find_all("url")
            print("The number of sitemaps2 are {0}".format(len(sitemapTags2)))
            for sitemap2 in sitemapTags2:
                link2 = sitemap2.findNext("loc").text
                # print(link2)
                insert(link2)


# insert data link dari scrap sitemap
def insert(link_article):
    conn.execute("INSERT OR IGNORE INTO tbl_article (link) VALUES ('" + link_article + "')")
    conn.commit()


# run sitemap
def run_sitemap():
    blog_file = os.path.join(THIS_FOLDER, 'site.txt')
    with open(blog_file) as f:
        blog = f.read().split('\n')
        size = len(blog)
    i = 0
    while i < size:
        print(blog[i])
        sitemap(blog[i])
        i += 1


def run_indexing():
    # blog_file = os.path.join(THIS_FOLDER, 'list-json.txt')
    # with open(blog_file) as f:
    #     json_file = f.read().split('\n')
    #     size = len(json_file)
    # i = 0
    # while i < size:
    #     indexing(json_file[i])
    #     i += 1
    for x in os.listdir("credential"):
        if x.endswith(".json"):
        # Prints only text file present in My Folder
            indexing("credential/" + x)


if __name__ == '__main__':
    cursor_count = conn.execute("SELECT COUNT(*) FROM tbl_article WHERE indexing = 0")
    result = cursor_count.fetchall()
    print(result[0][0])
    if result[0][0] < 200:
        run_sitemap()
        run_indexing()
        sys.exit()
    else:
        run_indexing()
        sys.exit()
