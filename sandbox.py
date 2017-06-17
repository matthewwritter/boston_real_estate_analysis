#!/usr/bin/env python2
# -*- coding: utf-8 -*-
""" Outputs pickle file of data
@author: matthewwritter

See documentation here: https://www.census.gov/data-tools/demo/codebook/ahs/ahsdict.html?s_appName=ahsdict&s_searchvalue=ras&s_year=2011&s_topic=64179F8D1BC221FC18DE17F591A06B65,ECBD2265722B9673E3748D6C3C801F2D,C87D77E6C8E6B324B39533C5BE9E8041

Takes Enigma URL
"""

import json
import urllib
import pickle
import random
import pandas as pd

with open('secretkey.txt','r') as f:
    SECRETKEY = f.read()

def test_connection():
    """ No arguments

    :return: Nothing, just prints
    """
    url1 = "https://api.enigma.io/v2/data/{}/us.gov.census.ahs.2011.thomimp?conjunction=and"
    response1 = urllib.urlopen(url1.format(SECRETKEY))
    data1 = json.loads(response1.read())

    print data1.keys()
    for key in ['info', 'success']:
        print "\n\n== {} == \n{}".format(key, data1[key])
    print type(data1['result'])
    print data1['result'][0]  # Check out the first row of actual data


def is_number(x):
    try:
        float(str(x))
        return True
    except ValueError:
        return False


def download_data(url_base, max_downloads=1, num_pages=5):

    with open('api_pages_downloaded.txt', 'r') as f:
        already_used = [int(x) for x in f.read().split('\n') if x]

    # This is designed to prevent the same page from being downloaded again
    with open('datalist.pkl', 'r') as f:
        datalist = pickle.load(f)

    for i in [x for x in
              random.sample(set(range(num_pages)) - set(already_used),
                            max_downloads)]:
        with open('api_pages_downloaded.txt', 'r') as f:
            if str(i) in f.read().split('\n'):
                print "Page {} already in datalist".format(i)
                continue
        url = url_base.format(secretkey=SECRETKEY,pagenum=i)
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        datalist.append(data)
        with open('datalist.pkl', 'w') as f:
            pickle.dump(datalist, f)
        with open('api_pages_downloaded.txt', 'a') as f:
            f.writelines('{}\n'.format(i))
    return datalist


def clean_data(
        datalist,
        column_names,
):
    l = []
    for x in datalist:
        if 'result' in x.keys():
            l.extend(x['result'])
    raw_df = pd.DataFrame(l).astype(str)
    for col in ['rad','ras']:
        try:
            raw_df.loc[:, col] = raw_df.loc[:, col].str.replace("'",
                                                                "").astype(int)
        except ValueError:
            pass
    raw_df = raw_df.rename(columns=column_names)
    return raw_df

if __name__ == '__main__':
    url_base = \
    "https://api.enigma.io/v2/data/{secretkey}/df.co?page={pagenum}"
    datalist = download_data(
        url_base=url_base,
        max_downloads=3,
        num_pages=295,
    )

    df = clean_data(datalist, {'rad': 'improvement_cost', 'rah': 'done_by_self',
                               'ras': 'improvement_type_id'})
    print(df.head().to_string())
    df.improvement_cost[lambda x: x < 1e4].hist(bins=30)
    print("Example contribution")
