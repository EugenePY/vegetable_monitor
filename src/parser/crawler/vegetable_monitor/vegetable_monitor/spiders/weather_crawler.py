# coding: utf-8
from __future__ import absolute_import
import requests
import re
from bs4 import BeautifulSoup
import json
import mechanize
import urllib

# Scrapy

from scrapy.spiders import Spider
from scrapy.http import FormRequest
from vegetable_monitor.items import VegetableMonitorItem

# from vegetable_monitor.items import VegetableMonitorItem
def get_viewstate():
        url = "http://210.69.71.171/veg/VegProdDayTransInfo.aspx"
        req = requests.get(url)
        data = req.text
        bs = BeautifulSoup(data, "html.parser")
        # print bs.find('input', {'id': '__EVENTTARGET'})
        return bs.find("input", {"id": "__VIEWSTATE"}).attrs['value'], \
            bs.find("input", {"id": "__EVENTVALIDATION"}).attrs['value']


class VegetableSpider(Spider):
    name = 'price'
    allowed_domains = ['http://210.69.71.171/veg/']
    start_urls = ["http://210.69.71.171/veg/VegProdDayTransInfo.aspx"]

    # the request has been encrysped
    # fooling the requested server

    def __init__(self):
        Spider.__init__(self)

        self.temp = get_viewstate()
        self.formdata = {
            "ctl00$ScriptManager_Master":
            "ctl00$contentPlaceHolder$updatePanelMain|ctl00$contentPlaceHolder$btnQuery",
            "ctl00$ucLogin$txtMemberID": "",
            "ctl00$ucLogin$txtPassword": "",
            "ctl00$ucLogin$txtValCode": "",
            "ctl00$contentPlaceHolder$ucSolarLunar$radlSolarLunar": "S",
            "ctl00$contentPlaceHolder$txtSTransDate": "105/04/22",
            "ctl00$contentPlaceHolder$txtETransDate": "105/04/22",
            "ctl00$contentPlaceHolder$txtMarket": "全部市場",
            "ctl00$contentPlaceHolder$hfldMarketNo": "ALL",
            "ctl00$contentPlaceHolder$txtProduct": "FE 冬瓜",
            "ctl00$contentPlaceHolder$hfldProductNo": "FE",
            "ctl00$contentPlaceHolder$hfldProductType": "B",
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": self.temp[0],
            "__EVENTVALIDATION": self.temp[1],
            "__ASYNCPOST": "true",
            "ctl00$contentPlaceHolder$btnQuery": "查詢"}

        self.headers = {'Referer': self.start_urls,
                        'Accept': ' application/json, text/javascript, */*',
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'X-Requested-With': 'XMLHttpRequest',
                        'User-Agent':
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36"
                        }

    def make_requests_from_url(self, url):
        return FormRequest(url, headers=self.headers, formdata=self.formdata)

    def parse(self, response):
        item = VegetableMonitorItem()
        item['data'] = response.body
        yield item


class WeatherSpider(Spider):

    name = "weather"
    allowed_domains = ["pblap.atm.ncu.edu.tw/plotOBS_track.asp"]
    start_urls = ["http://pblap.atm.ncu.edu.tw/plotOBS_track.asp"]

    def __init__(self):
        Spider.__init__(self)
        self.formdata = {'zipcode': '2016/03/19', 'syr': '2016', 'smo': '03',
                         'sdy': '19', 'B1': 'PLOT'}
        self.headers = {'User-Agent':
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) ' +
                        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/' +
                        '50.0.2661.75 Safari/537.36'}

    def make_requests_from_url(self, url):
        return FormRequest(url, headers=self.headers, formdata=self.formdata)

    def parse(self, response):
        item = VegetableMonitorItem()
        Data = [json.loads(dataSets[11:]) for dataSets in
                re.findall(r'"dataSets":\[\{.+?\}\]', response.body)]
        data = {"date": self.formdata['zipcode']}
        for feature in Data:
            if feature[0]['id'].encode('utf-8') == u"":
                feature[0]['id'] = 'Specific Hummidity'.encode('utf-8')
            data.update({feature[0]['id']: feature[0]['data']})
        item['data'] = data
        yield item


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
        body = table.find('tbody')
        rows = body.findAll('tr')
        for row in rows:
            temp = []
            for i in row.findAll('td'):
                e = i.text
                temp.append(from_str2float(e.strip()))

            data.append(temp)

    return data


def price_crawler():
    url = "http://210.69.71.171/veg/VegProdDayTransInfo.aspx"

    def get_viewstate():
        url = "http://210.69.71.171/veg/VegProdDayTransInfo.aspx"
        req = requests.get(url)
        data = req.text
        bs = BeautifulSoup(data, "html.parser")
        # print bs.find('input', {'id': '__EVENTTARGET'})
        return bs.find("input", {"id": "__VIEWSTATE"}).attrs['value'], \
            bs.find("input", {"id": "__EVENTVALIDATION"}).attrs['value']

    # the request has been encrysped
    temp = get_viewstate()
    # fooling the requested server
    data = {
    "ctl00$ScriptManager_Master": "ctl00$contentPlaceHolder$updatePanelMain|ctl00$contentPlaceHolder$btnQuery",
    "ctl00$ucLogin$txtMemberID": "",
    "ctl00$ucLogin$txtPassword": "",
    "ctl00$ucLogin$txtValCode": "",
    "ctl00$contentPlaceHolder$ucSolarLunar$radlSolarLunar": "S",
    "ctl00$contentPlaceHolder$txtSTransDate": "105/04/22",
    "ctl00$contentPlaceHolder$txtETransDate": "105/04/22",
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
    soup = BeautifulSoup(mechanize.urlopen(req).read())
    # data = soup.findAll('td', {"align": "right"})

    tables = soup.find('div', {'id': 'ctl00_contentPlaceHolder_panel'})
    table = tables.findAll('table')
    # for each web page there are three tables
    data = get_tables(table[1:])
    data = {'date': data[0][1][:9], 'market': None,
            'upper cap price ntd/kg': None,
            'mid cap price': None, 'lower cap price': None,
            'compare with last day(%)': None, 'volumn': None}
    return data


def expriments():
    url = "http://210.69.71.171/veg/VegProdDayTransInfo.aspx"

    def get_viewstate():
        url = "http://210.69.71.171/veg/VegProdDayTransInfo.aspx"
        req = requests.get(url)
        data = req.text
        bs = BeautifulSoup(data, "html.parser")
        # print bs.find('input', {'id': '__EVENTTARGET'})
        return bs.find("input", {"id": "__VIEWSTATE"}).attrs['value'], \
            bs.find("input", {"id": "__EVENTVALIDATION"}).attrs['value']

    # the request has been encrysped
    temp = get_viewstate()
    # fooling the requested server
    data = {
    "ctl00$ScriptManager_Master": "ctl00$contentPlaceHolder$updatePanelMain|ctl00$contentPlaceHolder$btnQuery",
    "ctl00$ucLogin$txtMemberID": "",
    "ctl00$ucLogin$txtPassword": "",
    "ctl00$ucLogin$txtValCode": "",
    "ctl00$contentPlaceHolder$ucSolarLunar$radlSolarLunar": "S",
    "ctl00$contentPlaceHolder$txtSTransDate": "105/04/22",
    "ctl00$contentPlaceHolder$txtETransDate": "105/04/22",
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
    headers = {'Referer': url,
               'Accept': ' application/json, text/javascript, */*',
               'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
               'X-Requested-With': 'XMLHttpRequest',
               'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36"
               }
    resp = requests.get(url , headers=headers, data=data)
    resp.encoding = 'utf-8'
    return data


def weather_crawler():
    ''' usuage: python weather_crawler -s [start_date end_date] -n \
    [start_date today]
    '''

    backend = 'http://pblap.atm.ncu.edu.tw/plotOBS_track.asp'
    headers = {'User-Agent':
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) ' +
               'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/' +
               '50.0.2661.75 Safari/537.36'}

    data = {'zipcode': '2016/03/19', 'syr': '2016', 'smo': '03', 'sdy': '19',
            'B1': 'PLOT',
            }

    resp = requests.get(backend, allow_redirects=False, headers=headers,
                        data=data)
    resp.encoding = 'utf-8'
    # the format of the input is YYYY/MM/DD
    Data = [json.loads(dataSets[11:]) for dataSets in
            re.findall(r'"dataSets":\[\{.+?\}\]', resp.text)]
    data = {"date": data['zipcode']}
    for feature in Data:
        if feature[0]['id'].encode('utf-8') == u"":
            feature[0]['id'] = 'Specific Hummidity'.encode('utf-8')
        data.update({feature[0]['id']: feature[0]['data']})

    return data


def price_parser(soup):
    pass
