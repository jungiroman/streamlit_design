from dotenv import load_dotenv
import os
import feedparser
from lxml import html
import requests
import pandas as pd
from bs4 import BeautifulSoup
from textblob import TextBlob
import nltk
from gensim.parsing.preprocessing import remove_stopwords
import re
import mysql.connector
from datetime import datetime
nltk.download('wordnet')


def get_feed(url):
    feed = requests.get(url).content
    feed = feedparser.parse(feed)
    return feed


def process_text(text):
    text = text.lower()
    text = re.sub(r'[.,"\'-?:!;’‘]', '', text)
    #text = text.replace(''', '')
    text = remove_stopwords(text)
    text = " ".join([word.lemmatize() for word in TextBlob(text).words])
    return text


def get_images(url):
    response = requests.get(url)
    root = html.fromstring(response.content)
    image_url = root.xpath("//img/@src")[0]
    image_urls = root.xpath("//div[@class='page-content']//img/@data-src")
    if not str(image_url).startswith('https'):
        image_url = image_urls[0]
        image_urls = image_urls[1:]
    return image_url, image_urls


def store_in_db(record):
    db = mysql.connector.connect(
        host=os.environ.get('host'),
        database=os.environ.get('database'),
        user=os.environ.get('user'),
        password=os.environ.get('password')
    )

    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS articles (link VARCHAR(255) PRIMARY KEY, category VARCHAR(255), title VARCHAR(1024), published TIMESTAMP, authors VARCHAR(1024), first_image VARCHAR(1024), images VARCHAR(65535), summary VARCHAR(1024), search_text VARCHAR(2048))")
    sql = "INSERT IGNORE INTO articles (link, category, title, published, authors, first_image, images, summary, search_text) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (record['link'], record['category'], record['title'], record['published'], record['authors'], record['first_image'], record['images'], record['summary'], record['search_text'])
    cursor.execute(sql, values)
    print(str(cursor.rowcount))
    db.commit()


def process(articles):
    for article in articles:
        link = article['link']
        category = link.split('/')[3]
        title = article['title']
        published = article['published']
        published = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d %H:%M:%S")
        authors = (x['name'] for x in article['authors'])
        authors = ";".join(authors)
        first_image, images = get_images(link)
        images = ";".join(images)
        summary = article.summary.replace('<img src="https://www.designboom.com/feed/" /><br />', '')
        summary = summary.replace('<img src="" /><br />', '')
        soup = BeautifulSoup(summary, 'html.parser')
        summary = soup.p.get_text()
        text = title + " " + summary
        text = process_text(text)
        record = {
            'link': link,
            'category': category,
            'title': title,
            'published': published,
            'authors': authors,
            'first_image': str(first_image),
            'images': images,
            'summary': summary,
            'search_text': text
        }
        store_in_db(record)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    load_dotenv()
    #db_user = os.environ.get('secretUser')
    #db_pw = os.environ.get('secretKey')
    url = 'https://www.designboom.com/feed/'
    feed = get_feed(url)
    process(feed.entries)
