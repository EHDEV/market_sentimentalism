__author__ = 'eliashussen'

from bs4 import BeautifulSoup
import requests
import re
from alchemyapi import AlchemyAPI
import json


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
