from scrapy.crawler import CrawlerProcess

from scrapy.utils.project import get_project_settings
from vegetable_monitor.spiders import weather_crawler

import datetime
import logging
import time
# timezone correctness

FORMAT = '%(asctime)-15s - [%(name)s] - [%(levelname)s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger('VegetableMonitor')


class Taiwan(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(hours=8)

    def dst(self, dt):
        return datetime.timedelta(0)


def main():
    Done = False

    TODAY = datetime.datetime.now(Taiwan())
    ACTIVATE_TIME = datetime.datetime(
            TODAY.year, TODAY.month, TODAY.day, 1, tzinfo=Taiwan())

    while not Done:
        logger.info('Crawler is running')
        current = datetime.datetime.now(Taiwan())
        logger.info("Time delta before Crawler activate: %s",
                    str(ACTIVATE_TIME-current))
        time.sleep(3)
        if current >= ACTIVATE_TIME:  # perform the crawler at 1:00 am every
            logger.info('Crawler is activated')
            time.sleep(10)
            settings = get_project_settings()
            process = CrawlerProcess(settings)
            process.crawl(weather_crawler.SattelliteSpider)
            process.crawl(weather_crawler.VegetableSpider_new)
            process.crawl(weather_crawler.WeatherSpider)
            process.start()
            Done = True

if __name__ == "__main__":
    main()
