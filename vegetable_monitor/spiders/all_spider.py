# coding: utf-8
from __future__ import absolute_import
import requests
import re
from bs4 import BeautifulSoup
import json

# Image Process
from StringIO import StringIO

# Datetime object
from datetime import datetime
from datetime import date
from datetime import timedelta
from datetime import tzinfo
# Scrapy
from scrapy.spiders import SitemapSpider
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from vegetable_monitor.items import VegetableMonitorItem


def get_viewstate():
    url = "http://210.69.71.171/veg/VegProdDayTransInfo.aspx"
    req = requests.get(url)
    data = req.text
    bs = BeautifulSoup(data, "html.parser")
    # print bs.find('input', {'id': '__EVENTTARGET'})
    return bs.find("input", {"id": "__VIEWSTATE"}).attrs['value'], \
        bs.find("input", {"id": "__EVENTVALIDATION"}).attrs['value']


def time_range(start, diff_day, n_steps):
    temp = []
    for i in range(n_steps):
        temp.extend([start + timedelta(days=diff_day*i)])
    return temp


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


class VegetableSpider_new(Spider):
    name = "price"

    def __init__(self, date_):
        # Helper
        def date_trans(date_):
            year = int(date_.split('/')[0]) - 1911
            return '/'.join([str(year)] + date_.split('/')[1:])
        today = date_
        date_string = date_trans(today.strftime('%Y/%m/%d')).split('/')
        self.meta_data = [
            "104 台北二",
            "109 台北一",
            "241 三重市",
            "260 宜蘭市",
            "338 桃園縣",
            "400 台中市",
            "420 豐原區",
            "512 永靖鄉",
            "514 溪湖鎮",
            "540 南投市",
            "648 西螺鎮",
            "800 高雄市",
            "830 鳳山區",
            "900 屏東市",
            "930 台東市",
            "950 花蓮市"]
        self.start_urls = [["http://210.69.71.171/v-asp/v102r.asp",
                            {"myy": date_string[0],
                             "mmm": date_string[1],
                             "mdd": date_string[2],
                             "mkno": market.split(' ')[0]}]
                           for market in self.meta_data]

    def make_requests_from_url(self, url):
        return FormRequest(url[0], formdata=url[1])

    def parse(self, response):
        item = VegetableMonitorItem()
        url = self.start_urls[0][1]
        soup = BeautifulSoup(response.body, 'lxml')
        try:
            table = soup.findAll('table')
            # for each web page there are three tables
            data = get_tables(table)
        except:
            data = {}

        def date_trans(x):
            a = x.split('/')
            y = int(a[0]) + 1911
            return '/'.join([str(y)] + a[1:])

        data = {'date': date_trans('/'.join([url['myy'], url['mmm'],
                                             url['mdd']])), 'data': data}
        if data:
            item['data'] = data
            yield item


class SattelliteSpider(Spider):
    name = "sattellite"
    allowed_domains = ['http://www.cwb.gov.tw/V7/observe/satellite/Data']

    def __init__(self, date_):
        today = date_
        # create the time list for download the images yeasterday
        dat_list = [today]
        while dat_list[-1].day < (dat_list[-1] + timedelta(days=1)).day:
            dat_list.extend([dat_list[-1] + timedelta(minutes=10)])

        self.start_urls = [
            "http://www.cwb.gov.tw/V7/observe/satellite/Data/s3o/s3o-%s.jpg" %
            datetime.strftime(image_time, "%Y-%m-%d-%H-%M")
            for image_time in dat_list]

    def parse(self, response):
        item = VegetableMonitorItem()
        item['date'] = date(self.today.year,
                            self.today.month,
                            self.today.day).strftime('%Y/%m/%d')
        item['image'] = StringIO(response.body)
        yield item


class WeatherSpider(Spider):

    name = "weather"
    start_urls = ["http://pblap.atm.ncu.edu.tw/plotOBS_track.asp"]

    def __init__(self, date):
        today = date
        zipcode = datetime.strftime(today, "%Y/%m/%d")
        self.formdata = {'zipcode': zipcode,
                         'syr': zipcode.split('/')[0],
                         'smo': zipcode.split('/')[1],
                         'sdy': '{:02d}'.format(today.day), 'B1': 'PLOT'}
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
    "ctl00$contentPlaceHolder$txtProduct": "全部產品",
    "ctl00$contentPlaceHolder$hfldProductNo": "ALL",
    "ctl00$contentPlaceHolder$hfldProductType": "A",
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


class Taiwan(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=8)

    def dst(self, dt):
        return timedelta(hours=0)


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

if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess()
    TODAY = datetime.utcnow() + timedelta(hours=8)
    ACTIVATE_TIME = datetime(
            TODAY.year, TODAY.month, TODAY.day, 23) + timedelta()
    for i in time_range(TODAY, 1, 20):
        process.crawl(VegetableSpider_new, i)
        process.crawl(WeatherSpider, i)
    process.start()
