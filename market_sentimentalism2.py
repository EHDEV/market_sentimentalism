from flask import Flask
from flask import render_template
from alchemyapi import AlchemyAPI
import json
from bs4 import BeautifulSoup
import requests
import re
import numpy as np
import etl
import datetime


app = Flask(__name__)

# url_for('static', filename='style.css')

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('test_test.html', name=name)

@app.route('/post/<int:post_id>/')
def post(post_id):
    if post_id == 12:
        return '12 is returned'
    else:
        return 'post is not 12'

def sentiment_alchemy(url):

    alchemyapi = AlchemyAPI()

    response = alchemyapi.sentiment('url', url)
    response['usage'] = None

    if response['status'] == 'OK':
        print('## Response Object ##')
        print(json.dumps(response, indent=4))

        print('')
        print('## Author ##')
        print('author: ', response.get('author', ''))
        print('')
    else:
        print('Error in author extraction call: ', response['statusInfo'])

    response = alchemyapi.keywords('url', url)
    del(response['usage'])

    if response['status'] == 'OK':
        print('## Response Object ##')
        print(json.dumps(response, indent=4))

        print('')
        print('## Keywords ##')
        for keyword in response['keywords']:
            print('text: ', keyword['text'].encode('utf-8'))
            print('relevance: ', keyword['relevance'])
            print('sentiment: ', keyword.get('sentiment', {}).get('type', ''))
            if 'score' in keyword.get('sentiment', {}):
                print('sentiment score: ' + keyword['sentiment']['score'])
            print('')
        else:
            print('Error in keyword extaction call: ', response.get('statusInfo', ''))


def news_scrape_goog(nurl):
    links = []
    rss = requests.get(nurl)

    soup = BeautifulSoup(rss.text)

    for l in soup.find_all('a', href=True):
        # print(l)
        li = l['href']

            #print k['href']

        t = re.search('url=.+', str(k))
        if t:
            t = t.group()
            t = re.search('.+?\&amp', t)
            t = t.group()
            t = t.replace('&amp', '').replace('url=', '')
            print t
            print k.contents[0]

        else:
            continue
            mtch = re.search("\*.+", l.text)
        try:
            url = mtch.group()
            links += [url[1:]]
        except AttributeError:
            print("Regex Error, " + str(l))
            continue

    print (links)

    return links


def news_scrape(rurl):

    links = []
    rss = requests.get(rurl)

    soup = BeautifulSoup(rss.text)

    for l in soup.find_all('a'):
        # print(l)
        lhr = l['href']
        mtch = re.search("\*http://.+?\"", lhr)

        try:
            url = mtch.group()
            links += [url[1:-1]]

        except AttributeError:
            mtch =re.search('http:\/\/finance.yahoo.com\/news.+\.html', lhr)
            try:
                url = mtch.group()
                links += [url]
            except AttributeError:
                continue

            print("Regex Error, " + str(l))
            continue

    print (links)

    return links

def aggregate_news_sentiment(news_urls):
    alchemyapi = AlchemyAPI()

    agg_sentiment = 0.0
    sscores = []

    for link in news_urls:

        print ("Processing, " + link)
        response = alchemyapi.sentiment('url', link)
        print(json.dumps(response))
        del(response['usage'])

        if response['status'] == 'OK' and response.get('docSentiment', {}).get('type', '') != 'neutral':

            sscores += [float(response.get('docSentiment', {}).get('score'))]

    agg_sentiment = np.sum(sscores)

    print (agg_sentiment)

    return agg_sentiment

@app.route('/sentiment/<ticker>/')
def get_sentiment(ticker=None):

    score_dict = {}

    # url = "http://www.cnbc.com/id/102595050?__source=yahoo%7cfinance%7cheadline%7cheadline%7cstory&par=yahoo&doc=102595050"
    #
    # rss_feed_aapl = "http://finance.yahoo.com/q/h?s=AAPL&t=2015-03-27"
    # rss_feed_nasdaq = "feeds.finance.yahoo.com/rss/headline?s=^IXIC"
    # rss_feed_goog = "feeds.finance.yahoo.com/rss/headline?s=goog"
    # rss_feed_sandp = "feeds.finance.yahoo.com/rss/headline?s=^gspc"
    # rss_feed_dow = "feeds.finance.yahoo.com/rss/headline?s=^DJI"

    # sentiment_alchemy(url)

    urls_dict = etl.construct_search_url_yh(datetime.datetime(2015, 04, 01), datetime.datetime(2015, 04, 11))

    for dl in urls_dict:

        articles = news_scrape(urls_dict[dl])

        score_dict[dl] = {'articles': articles}

        score_dict[dl]['score'] = aggregate_news_sentiment(articles)

    if ticker:
        print 'ticker is ', ticker

    # aapl_news_urls = news_scrape(rss_feed_aapl)
    #
    # appl_score = aggregate_news_sentiment(aapl_news_urls)
    # goog_score = aggregate_news_sentiment(aapl_news_urls)
    # nasdaq_score = aggregate_news_sentiment(aapl_news_urls)
    # sandp_score = aggregate_news_sentiment(aapl_news_urls)
    # dow_score = aggregate_news_sentiment(aapl_news_urls)

    return render_template('json.html', dictionary=json.dumps(score_dict, ensure_ascii=False))

@app.route('/test/')
def test():

    score_dict = {}

    url = 'http://ichart.yahoo.com/table.csv?s=GOOG&a=0&b=1&c=2000&d=0&e=31&f=2010'

    gurl = 'https://www.google.com/finance/company_news?q=NASDAQ%3AAAPL&startdate=2015-3-01&enddate=2015-3-01'

    urls_dict = etl.construct_search_url_goog(datetime.datetime(2015, 04, 01), datetime.datetime(2015, 04, 02))

    for dl in urls_dict:

        articles = news_scrape_goog(urls_dict[dl])

        score_dict[dl] = {'articles': articles}

        score_dict[dl]['score'] = aggregate_news_sentiment(articles)

    # d = etl.get_quotes(url)

    return render_template('json.html', dictionary=score_dict)





if __name__ == '__main__':
    app.run()
