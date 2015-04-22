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
from facebook_etl import *
from flask import request


app = Flask(__name__)

# url_for('static', filename='style.css')



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
    del (response['usage'])

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

        # print k['href']

        t = re.search('url=.+', str(l))
        if t:
            t = t.group()
            t = re.search('.+?\&amp', t)
            t = t.group()
            t = t.replace('&amp', '').replace('url=', '')
            print t

        else:
            mtch = re.search("\*.+", l.text)
            continue
        try:
            url = mtch.group()
            links += [url[1:]]
        except AttributeError:
            print("Regex Error, " + str(l))
            continue

    print (links)

    return links

@app.route('/sentiment/<ticker>/')
def get_sentiment(ticker=None):
    score_dict = {}

    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)

    if not start_date:
        start_date = datetime.datetime(2015, 04, 01)
    else:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')

    if not end_date:
        end_date = start_date + datetime.timedelta(days=1)

    else:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    urls_dict = etl.construct_search_url_yh(start_date, end_date)

    for dl in urls_dict:
        articles = etl.news_scrape(urls_dict[dl])

        score_dict[dl] = {'articles': articles}

        score_dict[dl]['score'] = etl.aggregate_news_sentiment(articles)

    file_path = path.join(path.dirname(__file__), 'data/sentiment_scores_daily_train.json')

    with open(file_path, 'w+') as file:
        json.dump(score_dict, file)

    if ticker:
        print 'ticker is ', ticker

    return render_template('highcharts1.html', dictionary=json.dumps(score_dict, ensure_ascii=False))


# @app.route('/test/')
# def test():
#     score_dict = {}
#
#     url = 'http://ichart.yahoo.com/table.csv?s=GOOG&a=0&b=1&c=2000&d=0&e=31&f=2010'
#
#     gurl = 'https://www.google.com/finance/company_news?q=NASDAQ%3AAAPL&startdate=2015-3-01&enddate=2015-3-01'
#
#     urls_dict = etl.construct_search_url_goog(datetime.datetime(2015, 04, 01), datetime.datetime(2015, 04, 02))
#
#     for dl in urls_dict:
#         articles = news_scrape_goog(urls_dict[dl])
#
#         score_dict[dl] = {'articles': articles}
#
#         score_dict[dl]['score'] = etl.aggregate_news_sentiment(articles)
#
#     # d = etl.get_quotes(url)
#
#     return render_template('json.html', dictionary=score_dict)


@app.route('/fb/<id_or_name>/')
def fb(id_or_name):
    access_token = request.args.get('access_token', None)

    if not access_token:
        d = {'Error': 'No Access Token provided'}
    else:
        d = get_fb_page(id_or_name, access_token)

    # data = json.dumps(d)

    return render_template("default.html", data=json.dumps(d))


@app.route('/tweets/<search_term>/')
def tw(search_term='AAPL', date=str(datetime.date.today())):
    twits_bydate = {}

    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)

    if not start_date:
        start_date = datetime.datetime(2015, 04, 01)
    else:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')

    if not end_date:
        end_date = start_date + datetime.timedelta(days=1)
    else:
        end_date = datetime.datetime.strftime(end_date, '%Y-%m-%d')

    d = etl.construct_search_url_tw(start_date, end_date, search_term)

    for dt in d:
        twits_bydate[dt] = etl.collect_historical_tweets(d[dt])


    return render_template('default.html', data=json.dumps(twits_bydate, ensure_ascii=True))


@app.route('/test/')
def test():
    d = etl.prepare_data_for_modeling()
    return d

if __name__ == '__main__':
    app.run()
