# coding: utf-8
from __future__ import absolute_import
import requests
import re
from bs4 import BeautifulSoup
from parser.loggin import logger
import json
import mechanize
import urllib


def data_parser(str):
    FORMAT = r'[0-9]+[,][0-9]+'
    a = re.match(FORMAT, str)
    if a:
        return a.group(0)
    else:
        return None


def from_str2float(str):
    FORMAT = r'[0-9]+[,][0-9]+'
    a = re.compile(FORMAT)

    try:
        sign, number = str.split()

        # parsing the sign
        if u"-" == sign:
            sign = -1
        if u"+" == sign:
            sign = 1

        val = sign * float(number)
    except:
        try:
            val = float(str)
        except:
            find = a.match(str)
            if find:
                val = float(find.group(0).replace(',', '.'))
            else:
                val = str

    return val


def get_tables(table_list):
    data = []

    for table in table_list:
        rows = table.findAll('tr')
        for row in rows:
            temp = []
            for i in row.findAll('td'):
                e = i.text
                temp.append(from_str2float(e.strip()))

            data.append(temp)

    return data


def get_viewstate():
        url = "http://210.69.71.171/veg/VegProdDayTransInfo.aspx"
        req = requests.get(url)
        data = req.text
        bs = BeautifulSoup(data, 'lxml')
        # print bs.find('input', {'id': '__EVENTTARGET'})
        return bs.find("input", {"id": "__VIEWSTATE"}).attrs['value'], \
            bs.find("input", {"id": "__EVENTVALIDATION"}).attrs['value']


def price_crawler(date):
    url = "http://210.69.71.171/veg/VegProdDayTransInfo.aspx"

    def get_viewstate():
        url = "http://210.69.71.171/veg/VegProdDayTransInfo.aspx"
        req = requests.get(url)
        data = req.text
        bs = BeautifulSoup(data, "lxml")
        # print bs.find('input', {'id': '__EVENTTARGET'})
        return bs.find("input", {"id": "__VIEWSTATE"}).attrs['value'], \
            bs.find("input", {"id": "__EVENTVALIDATION"}).attrs['value']

    # the request has been encrysped
    temp = get_viewstate()
    # trans from the ”民國“ into YYYY form.
    def date_trans(date):
        year = int(date.split('/')[0]) - 1911
        return '/'.join([str(year)] + date.split('/')[1:])
    # fooling the requested server
    trans = date_trans(date)
    data = {
    "ctl00$ScriptManager_Master": "ctl00$contentPlaceHolder$updatePanelMain|ctl00$contentPlaceHolder$btnQuery",
    "ctl00$ucLogin$txtMemberID": "",
    "ctl00$ucLogin$txtPassword": "",
    "ctl00$ucLogin$txtValCode": "",
    "ctl00$contentPlaceHolder$ucSolarLunar$radlSolarLunar": "S",
    "ctl00$contentPlaceHolder$txtSTransDate": trans,
    "ctl00$contentPlaceHolder$txtETransDate": trans,
    "ctl00$contentPlaceHolder$txtMarket": "全部市場",
    "ctl00$contentPlaceHolder$hfldMarketNo": "ALL",
    "ctl00$contentPlaceHolder$txtProduct": "FE 冬瓜",
    "ctl00$contentPlaceHolder$hfldProductNo": "FE",
    "ctl00$contentPlaceHolder$hfldProductType": "B",
    "__EVENTTARGET": "",
    "__EVENTARGUMENT": "",
    "__VIEWSTATE": temp[0],
    "__EVENTVALIDATION": temp[1],
    "__ASYNCPOST": "true",
    "ctl00$contentPlaceHolder$btnQuery": "查詢"}

    data = urllib.urlencode(data)
    req = mechanize.Request(url, data=data)
    # add request header
    req.add_header('Referer', url)
    req.add_header('Accept', ' application/json, text/javascript, */*')
    req.add_header('Content-Type',
                   'application/x-www-form-urlencoded; charset=UTF-8')
    req.add_header('X-Requested-With', 'XMLHttpRequest')
    req.add_header("User-Agent",
                   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36")
    xml = mechanize.urlopen(req)
    print xml.code
    soup = BeautifulSoup(xml.read(), 'lxml')

    # data = soup.findAll('td', {"align": "right"})
    tables = soup.find('div', {'id': 'ctl00_contentPlaceHolder_panel'})
    try:
        table = tables.findAll('table')
        # for each web page there are three tables
        data = get_tables(table[1:])
    except:
        data = 'NA'
    data = {date:{'market data': data}}
    return data


def weather_crawler(date):
    """ usuage: python weather_crawler -s [start_date end_date] -n \
    [start_date today]
    """

    backend = 'http://pblap.atm.ncu.edu.tw/plotOBS_track.asp'
    headers = {'User-Agent':
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) ' +
               'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/' +
               '50.0.2661.75 Safari/537.36'}
    trans = date.split('/')
    data = {'zipcode': date, 'syr': trans[0], 'smo': trans[1], 'sdy': trans[2],
            'B1': 'PLOT',
            }

    resp = requests.get(backend, allow_redirects=False, headers=headers,
                        data=data)
    resp.encoding = 'utf-8'
    if resp.status_code != 200:
        logger.debug('Status Code %i', resp.status_code)
    # the format of the input is YYYY/MM/DD
    Data = [json.loads(dataSets[11:]) for dataSets in
            re.findall(r'"dataSets":\[\{.+?\}\]', resp.text)]
    data = {date:{'weather':{}}}
    for feature in Data:
        if feature[0]['id'].encode('utf-8') == u"":
            feature[0]['id'] = 'Specific Hummidity'.encode('utf-8')
        data[date]['weather'].update({feature[0]['id']: feature[0]['data']})

    return data


def price_parser(soup):
    pass


if __name__ == "__main__":
    from datetime import date
    from datetime import timedelta
    import cPickle as pk
    # a = date(2016, 4, 22)
    # print a
    # print a.strftime('%Y/%m/%d')
    # da = '2016/04/22'

    def time_range(start, diff_day, n_steps):
        temp = []
        for i in range(n_steps):
            temp.extend([start + timedelta(days=diff_day*i)])
        return temp
    date = date(2016, 1, 1)
    a = time_range(date, 1, 150)
    data = {}
    for i in a:
        print i
        date = i.strftime('%Y/%m/%d')
        data.update(weather_crawler(date))
        data[date].update(price_crawler(date)[date])

    pk.dump(data, open('./test.pk', 'wb'))
