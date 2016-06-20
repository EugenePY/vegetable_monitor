import argparse
from datetime import datetime
from datetime import timedelta
from database import CloudantDB
import logging
from crawler.weather_crawler import weather_crawler
from crawler.weather_crawler import price_crawler


__version__ = '1.0'

logger = logging.getLogger('Weather Crawler')


def main(cmdline=None):
    # initial the database
    logger.info('Start the Crawler Program.\n Start')
    db = CloudantDB(name='gossiping_test')
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description='''
        A crawler for the web version of PTT,
the largest online community in Taiwan.
        Input: board name and page indices (or articla ID)
        Output: BOARD_NAME-START_INDEX-END_INDEX.json (or BOARD_NAME-ID.json)
    ''')
    parser.add_argument('-i', metavar=('[start date]', '[end date]'),
                        type=str, nargs=2,
                        help='Start and End date', required=True)
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + __version__)

    if cmdline:
        args = parser.parse_args(cmdline)
    else:
        args = parser.parse_args()

    # check the datetime format
    def time_range(start, diff_day, n_steps):
        temp = []
        for i in range(n_steps):
            temp.extend([start + timedelta(days=diff_day*i)])
        return temp

    # check the time-format is correct
    current = datetime.strptime(args.i[0], '%Y/%m/%d')
    end = datetime.strptime(args.i[1], '%Y/%m/%d')
    status = True
    while status:
        while current <= end:
            date = current.strftime('%Y/%m/%d')
            data = {'date': date}
            data.update(weather_crawler(date)[date])
            data.update(price_crawler(date)[date])
            db.store(data)
            current += timedelta(days=1)

        logger.info('Crawler is Done')

if __name__ == '__main__':
    pass
    # main(['-i', '2016/02/01', '2016/05/05'])
