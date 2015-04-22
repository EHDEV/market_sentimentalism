__author__ = 'eliashussen'

from facepy import GraphAPI
import datetime
import json
from os import path

def get_fb_page(pageid, access_token):

    today = str(datetime.date.today())

    graph = GraphAPI(access_token)

    file_path = path.join(path.dirname(__file__), 'data/fb_page_response_' + today + '.json')

    data = graph.get('/v2.3/{0}/'.format(pageid))

    data['location']['longitude'] = float(data['location']['longitude'])
    data['location']['latitude'] = float(data['location']['latitude'])

    with open(file_path, 'w+') as file_name:
        json.dump(data, file_name)

    return data