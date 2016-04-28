import re
import sys
import requests
import argparse
import time
import os

from bs4 import BeautifulSoup
from flask import Flask
from database import CloudantDB
from crawler.crawler import getLastPage, parse

__version__ = '1.0'
VERIFY = True
if sys.version_info[0] < 3:
    VERIFY = False
    requests.packages.urllib3.disable_warnings()

app = Flask(__name__)
port = int(os.getenv('VCAP_APP_PORT', 8080))


def main(cmdline=None):
    # initial the database
    db = CloudantDB(name='gossiping_test')
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description='''
        A crawler for the web version of PTT,
the largest online community in Taiwan.
        Input: board name and page indices (or articla ID)
        Output: BOARD_NAME-START_INDEX-END_INDEX.json (or BOARD_NAME-ID.json)
    ''')
    parser.add_argument('-b', metavar='BOARD_NAME',
                        help='Board name', required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-i', metavar=('START_INDEX', 'END_INDEX'), type=int,
                       nargs=2, help="Start and end index")
    group.add_argument('-a', metavar='ARTICLE_ID', help="Article ID")
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + __version__)

    if cmdline:
        args = parser.parse_args(cmdline)
    else:
        args = parser.parse_args()
    board = args.b
    PTT_URL = 'https://www.ptt.cc'
    if args.i:
        start = args.i[0]
        if args.i[1] == -1:
            end = getLastPage(board)
        else:
            end = args.i[1]
        index = start
        for i in range(end-start+1):
            index = start + i
            print('Processing index:', str(index))
            resp = requests.get(
                url=PTT_URL + '/bbs/' + board + '/index' + str(index) + '.html',
                cookies={'over18': '1'}, verify=VERIFY
            )
            if resp.status_code != 200:
                print('invalid url:', resp.url)
                continue
            soup = BeautifulSoup(resp.text)
            divs = soup.find_all("div", "r-ent")
            for div in divs:
                try:
                    href = div.find('a')['href']
                    link = PTT_URL + href
                    article_id = re.sub('\.html', '', href.split('/')[-1])
                    if div == divs[-1] and i == end-start:
                        # last div of last page
                        db.store(parse(link, article_id, board))
                    else:
                        db.store(parse(link, article_id, board))
                except:
                    pass
            time.sleep(0.5)
    else:  # args.a
        article_id = args.a
        link = PTT_URL + '/bbs/' + board + '/' + article_id + '.html'
        db.store(parse(link, article_id, board))


@app.route('/')
def status():
    return 'The crawler is done parsing.'

if __name__ == '__main__':
    main(['-b', 'Gossiping', '-i', '1', '3'])
    app.run(host='0.0.0.0', port=port)
