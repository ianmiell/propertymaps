#!/usr/bin/python

# Brutally scrape for a postcode
# 1) make first query
# 2) while there's still another page in the results get all the info for each property

import urllib
import urllib2
import re
import time
from BeautifulSoup import BeautifulSoup
import httplib2

postcode = "SE5 8"
data = urllib.urlencode([("q",postcode),
                         ("output", "js")])
h = httplib2.Http()
headers = {'user-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
resp, page = h.request("http://maps.google.co.uk/maps?" + data, method="GET", headers=headers)
# TODO: eventually we'll loop around postcodes and then 1-10, then this'll be a continue, rather than an assert
assert resp.status == 200

#center: {lat: 51.466331,lng: -0.084897}
latlong_re = re.compile('.*center: .lat: ([^,]*),lng: ([0-9\.-+]*)')

match = lat_re(page)
(lat,long) = match.groups()

print lat
print long

#property_ids_re = re.compile('.*edid=(\\d+)&salerent=(\\d+)&pid=(\\d+)&agentid=(\\d+)')

