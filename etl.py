__author__ = 'eliashussen'

import pandas as p
import requests as r
from StringIO import StringIO
import datetime


def get_quotes(url):
    # ud = u.urlopen('http://ichart.yahoo.com/table.csv?s=GOOG&a=0&b=2&c=2015&d=17&e=3&f=2015')

    d = r.get('http://ichart.yahoo.com/table.csv?s=GOOG&a=0&b=2&c=2015&d=17&e=3&f=2015')

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

def construct_search_url_yh(start_date, end_date=datetime.date.today()):
    url_dict = {}
    date_list = [end_date - datetime.timedelta(days=x) for x in range(1, (end_date - start_date).days + 1)]

    for d in date_list:

        g_url = "http://finance.yahoo.com/q/h?s=AAPL&t={0}".format(
            str(d.date()))

        url_dict[str(d.date())] = g_url

    return url_dict