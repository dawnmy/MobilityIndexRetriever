#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
File: retrieve_mobility_index.py
Created Date: March 27th 2020
Author: ZL Deng <dawnmsg(at)gmail.com>
---------------------------------------
Last Modified: 27th March 2020 5:26:29 pm
'''

import sys
import time
import json
import click
import requests
import pandas as pd
from os import path

from china_cities import cities
from pypinyin import lazy_pinyin
from datetime import datetime, timedelta
from os.path import dirname, abspath, realpath, join


city_cn2en_dict = {}
for city in cities.get_cities():
    city_cn2en_dict[city.name_cn] = (city.province, city.name_en)


df = pd.read_csv(join(dirname(dirname(abspath(__file__))),
                      'data/china_areacode_baidu_wien.txt'),
                 sep='\t', index_col=0)

citycode_dict = pd.Series(df.CODE_CITY.values, index=df.NAME_CITY_EN).to_dict()

base_url = "http://huiyan.baidu.com/migration"


@click.command()
@click.option('-a', '--app', type=click.Choice(('intercity', 'intracity', 'history')), default='intercity')
@click.option('--city', type=str, default='Hubei Wuhan',
              help='The "province city" for which to extract data (must be quoted: e.g. "Hubei Wuhan")')
@click.option('-m', '--move', type=click.Choice(('in', 'out')), default='in',
              help='Data for move in, out of the city (for intercity and history)')
@click.option('-d', '--date', type=str, default='2020-03-01',
              help='Date in format of "2020-03-01" or range "2020-03-01:2020-03-26" for intercity')
@click.option('-o', '--output', type=str, help='The output file name')
def retrieve_mobility(app, city, move, date, output):
    """ Retrieve the mobility data from Baidu Huiyan

    Arguments:

        app {str} -- The application to call: `intercity` (flows from a given city to top 100 cities or flows to 
a given city from top 100 cities for given date range), `intracity` (within a city) or 
`history` (all flow from or to a given city in history).

        city {str} -- The city where the flows to or from, in the format of "Province City" e.g. "Hubei Wuhan"

        move {str} -- move in (to) or out (from)

        date {str} -- date or date range (only for intercity), e.g. "2020-03-01" or "2020-03-01:2020-03-07" 

        output {str} -- The output file name

    """

    (input_province, input_city) = city.rsplit(" ", 1)

    out_fh = open(output, 'w') if output else sys.stdout

    if app == 'intercity':
        header = '\t'.join(['{}'] * 8).format('Date', 'Province_CN', 'City_CN',
                                              'From_Province', 'From_City',
                                              'To_Province', 'To_City', 'Index')
        out_fh.write(header + '\n')

        date_list = daterange2datelist(date) if ':' in date else [date]
        for date in date_list:
            print('{} {} move {} on {}'.format(app, city, move, date))
            url = get_url(app, city, move, date)
            print('Retrieving {}'.format(url))
            try:
                r = requests.get(url=url)
            except:
                print('Unknown error occurs when visiting the url.')
                sys.exit(1)
            text = r.text

            data = json.loads(web2json(text))['data']['list']
            for item in data:
                output_province_cn = item['province_name']
                output_city_cn = item['city_name']
                try:
                    (output_province,
                     output_city) = city_cn2en_dict[output_city_cn]
                except KeyError:
                    output_province = ''.join(lazy_pinyin(
                        output_province_cn)).capitalize()
                    output_city = ''.join(lazy_pinyin(
                        output_city_cn)).capitalize()
                index = item['value']
                if move == 'in':
                    from_province = output_province
                    from_city = output_city
                    to_province = input_province
                    to_city = input_city
                else:
                    from_province = input_province
                    from_city = input_city
                    to_province = output_province
                    to_city = output_city
                out_fh.write('\t'.join(['{}'] * 8).format(date, output_province_cn, output_city_cn,
                                                          from_province, from_city,
                                                          to_province, to_city, index) + '\n')

    else:
        if ':' in date:
            print('Date range parameter is only valid for intercity data')
            sys.exit(1)
        else:

            url = get_url(app, city, move, date)
            print('Retrieving {}'.format(url))

            try:
                r = requests.get(url=url)
            except:
                print('Unknown error occurs when visiting the url.')
                sys.exit(1)
            text = r.text

            data = json.loads(web2json(text))['data']['list']

            if app == 'intracity':
                province_str = 'Within_Province'
                city_str = 'Within_City'
            else:
                if move == 'in':
                    province_str = 'To_Province'
                    city_str = 'To_City'
                else:
                    province_str = 'From_Province'
                    city_str = 'From_City'
            header = '\t'.join(['{}'] * 4).format('Date',
                                                  province_str, city_str, 'Index')
            out_fh.write(header + '\n')

            for date, value in data.items():
                out_fh.write('\t'.join(['{}'] * 4).format(date,
                                                          input_province, input_city, value) + '\n')

    out_fh.close()


def str2date(date_str):
    """ Convert a "%Y-%m-%d" date str into datetime object

    Arguments:
        date_str {str} -- A string represents a date in the format of "2020-03-01"

    Return:
        date {datetime}
    """
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def daterange2datelist(date_range_str):
    """ Convert a date range str into a list of date strs

    Arguments:
        date_range_str {str} -- A string represents a date range in the format of "2020-03-01:2020-03-07"

    Return:
        date_list {list} --- A list of date strs

    """

    start_date_str, end_date_str = date_range_str.split(":")

    start_date = str2date(start_date_str)
    end_date = str2date(end_date_str)

    delta = end_date - start_date

    date_list = []
    for i in range(delta.days + 1):
        date = start_date + timedelta(days=i)
        date_list.append(date.strftime("%Y-%m-%d"))
    return date_list


def web2json(web_content):
    text = web_content.encode('utf-8').decode('unicode_escape')

    json_data = text.split('(')[1].rstrip(')')

    return json_data


def get_url(app, city, move, date):
    """ Get the url of data upon request parameters

    Arguments:

        app {str} -- The application to call: `intercity` (flows from a given city to top 100 cities or flows to 
                       a given city from top 100 cities for given date range), `intracity` (within a city) or 
                       `history` (all flow from or to a given city in history).

        city {str} -- The city where the flows to or from, in the format of "Province City" e.g. "Hubei Wuhan"
        move {str} -- Move in (to) or out (from)
        date {str} -- Date, e.g. "2020-03-01"

    Return:
        url {str} -- A url to retrieve the specified data

    """

    datetime_str = date + ' 00:00:00'

    datatime_list = time.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    timestamp = time.mktime(datatime_list)

    try:
        citycode = citycode_dict[city]
    except KeyError:
        print('The city name "{}" is not valid in the database. Please read the help message with `--help`.'.format(city))
        sys.exit(1)
    date = date.replace('-', '')

    if app == 'intercity':
        app = 'cityrank.jsonp'
        date_str = '&date={}'.format(date)
        type_str = '&type=move_{}'.format(move)

    elif app == 'intracity':
        app = 'internalflowhistory.jsonp'
        type_str = ''
        date_str = '&date={}'.format(date)

    else:
        app = 'historycurve.jsonp'
        type_str = '&type=move_{}'.format(move)
        date_str = ''

    url = '{0}/{1}?dt=city&id={2}{3}{4}&callback=jsonp_{5}000_0000000'.format(
        base_url, app, citycode, type_str, date_str, int(timestamp))
    return url


if __name__ == '__main__':
    retrieve_mobility()
