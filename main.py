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
    if cursor.rowcount == 1:
        print(record['title'])
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


def get_dezeen_images(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    article = soup.find('article')
    images = article.findAll('figure')
    img = []
    for image in images:
        try:
            img.append(str(image['data-lightboximage']))
        except:
            pass

    if img:
        image_url = img[0]
        image_urls = img[1:]

        return image_url, image_urls
    else:
        return None, None


def get_dezeen(url, category):
    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')
    soup = soup.find("ul", {"class": "main-story-list"})
    articles = soup.findAll('article')

    for article in articles:
        link = article.find('a', href=True)['href']
        title = article.find('h3').text
        summary = article.find('p').text.replace(". More", ".")
        published = article.find('time')['datetime']
        published = datetime.strptime(published, "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M:%S")

        first_image, images = get_dezeen_images(link)
        if first_image and images:
            images = ";".join(images)

            text = title + " " + summary
            text = process_text(text)
            record = {
                'link': link,
                'category': category,
                'title': title,
                'published': published,
                'authors': article.find('footer').find('a').text,
                'first_image': first_image,
                'images': images,
                'summary': summary,
                'search_text': text
            }
            store_in_db(record)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    load_dotenv()

    # designboom
    url = 'https://www.designboom.com/feed/'
    feed = get_feed(url)
    process(feed.entries)

    # dezeen (architecture)
    url = "https://www.dezeen.com/architecture/"
    get_dezeen(url, 'architecture')

    url = "https://www.dezeen.com/interiors/"
    get_dezeen(url, 'interiors')

    url = "https://www.dezeen.com/design/"
    get_dezeen(url, 'design')

    url = "https://www.dezeen.com/lookbooks/"
    get_dezeen(url, 'interiors')
