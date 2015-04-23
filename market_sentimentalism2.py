from flask import Flask
from flask import render_template
import etl
from facebook_etl import *
from flask import request
import model


app = Flask(__name__)

# url_for('static', filename='style.css')


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

    return render_template('highcharts2.html', dictionary=json.dumps(score_dict, ensure_ascii=False))

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
    res = model.linear_reg(d)

    return render_template('default.html', data=json.dumps(res))

if __name__ == '__main__':
    app.run()
