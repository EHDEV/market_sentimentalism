__author__ = 'eliashussen'

import pandas as p
import requests as r
from StringIO import StringIO
import datetime
from bs4 import BeautifulSoup
import re
from alchemyapi import AlchemyAPI
import json
import numpy as np
from flask import request
from os import path
import csv
from collections import defaultdict


def get_quotes(start_date='2015-04-01', end_date='2015-04-21', ticker='AAPL'):
    # ud = u.urlopen('http://ichart.yahoo.com/table.csv?s=GOOG&a=0&b=2&c=2015&d=17&e=3&f=2015')

    d = r.get('http://ichart.yahoo.com/table.csv?s=AAPL&a=01&b=04&c=2015&d=21&e=04&f=2015')

    dat = d.content

    csd = str(dat).strip("b'").encode('utf-8')

    # lines = csd.split('\\n')

    data = StringIO(csd)

    df = p.read_csv(data, sep=',')

    df = df.set_index('Date')

    return df.to_json()


def construct_search_url_goog(start_date, end_date):
    url_dict = {}
    date_list = [end_date - datetime.timedelta(days=x) for x in range(1, (end_date - start_date).days + 1)]

    for d in date_list:
        g_url = 'https://www.google.com/finance/company_news?q=NASDAQ%3AAAPL&startdate={0}&enddate={0}'.format(
            str(d.date()))

        url_dict[str(d.date())] = g_url

    return url_dict


def construct_search_url_yh(start_date, end_date=datetime.date.today(), ticker='AAPL'):
    url_dict = {}
    date_list = [end_date.date() - datetime.timedelta(days=x) for x in range(1, (end_date - start_date).days + 1)]

    for d in date_list:
        g_url = "http://finance.yahoo.com/q/h?s={0}&t={1}".format(
            ticker, str(d))

        url_dict[str(d)] = g_url

    return url_dict


def construct_search_url_tw(search_term, start_date, end_date=datetime.date.today()):
    url_dict = {}
    date_list = [end_date - datetime.timedelta(days=x) for x in range(1, (end_date - start_date).days + 1)]

    end_date = start_date + datetime.timedelta(days=1)

    for i, d in enumerate(date_list):
        g_url = "https://twitter.com/search?q={0}%20from%3Ayahoofinance%20since%3A{1}%20until%3A{2}&src=typd".format(
            search_term, start_date, end_date)
        start_date = end_date
        end_date = start_date + datetime.timedelta(days=1)

        url_dict[str(d)] = g_url

    return url_dict


def collect_historical_tweets(url):
    req = r.get(url)
    beatw = BeautifulSoup(req.text)
    twits_list = []

    for pa in beatw.find_all('p'):
        # print pa.get('class', None)
        if pa.get('class', [''])[0] == "js-tweet-text":
            twits_list += [str(pa)]

    return twits_list


def aggregate_news_sentiment(news_urls):
    alchemyapi = AlchemyAPI()

    agg_sentiment = 0.0
    sscores = []

    for link in news_urls:

        print ("Processing, " + link)
        response = alchemyapi.sentiment('url', link)
        del (response['usage'])

        if response['status'] == 'OK' and response.get('docSentiment', {}).get('type', '') != 'neutral':
            sscores += [float(response.get('docSentiment', {}).get('score'))]

    agg_sentiment = np.sum(sscores)

    print (agg_sentiment)

    return agg_sentiment


def news_scrape(rurl):
    links = []
    rss = r.get(rurl)

    soup = BeautifulSoup(rss.text)

    for l in soup.find_all('a'):
        # print(l)
        lhr = l['href']
        mtch = re.search("\*http://.+?\"", lhr)

        try:
            url = mtch.group()
            links += [url[1:-1]]

        except AttributeError:
            mtch = re.search('http:\/\/finance.yahoo.com\/news.+\.html', lhr)
            try:
                url = mtch.group()
                links += [url]
            except AttributeError:
                continue

            print("Regex Error, " + str(l))
            continue

    print (links)

    return links


def prepare_data_for_modeling():
    sent_formatted = {}

    try:
        file_path = path.join(path.dirname(__file__), 'data/goog_trends.csv')
        goog_df = p.read_csv(file_path)

    except IOError as e:
        print e.message

    try:
        file_path = path.join(path.dirname(__file__), 'data/sentiment_scores_daily_train.json')

        with open(file_path) as fp:
            sent_dict = json.load(fp)

    except IOError as e:
        print e.message
        exit()

    try:
        file_path = path.join(path.dirname(__file__), 'data/yahoo_quotes.csv')
        quotes_df = p.read_csv(file_path)

    except IOError as e:
        print e.message

    for dtk in sent_dict:
        sent_formatted[dtk] = sent_dict[dtk]['score']

    sent_df = p.DataFrame(sent_formatted, index=sent_formatted.keys())

    sent_df.columns = ['score']

    df_partial = p.merge(goog_df, sent_df, left_on='date', right_index=True, how='inner')

    df_fuller = p.merge(df_partial, quotes_df, left_on='date', right_on='Date', how='inner')

    del df_fuller['Date']

    # try:
    #     file_path = path.join(path.dirname(__file__), 'data/goog_trends.csv')
    #     quotes = p.read_csv(file_path)
    #
    # except IOError as e:
    #     print e.message

    return df_fuller

