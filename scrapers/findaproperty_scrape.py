#!/usr/bin/python

# Brutally scrape a property website
# 1) make first query
# 2) while there's still another page in the results get all the info for each property

import urllib
import urllib2
import cookielib
import re
import time
from BeautifulSoup import BeautifulSoup
import httplib2

cj = cookielib.CookieJar()
loc = "N12"
bedrooms = 0
minprice = ""
maxprice = ""
data = urllib.urlencode([("loc",loc),
                         ("bedrooms", bedrooms),
                         ("minprice", minprice),
                         ("maxprice", maxprice),
                         ("f",""),
                         ("res", 0),
                         ("salerent",0),
                         ("edid",0),
                         ("ResultsHeaderControl:ResultsViewModeControl:p",30)])
# we'll want to rotate the header for stealth at some stage
headers = {'user-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
#req = urllib2.Request(url="http://findaproperty.co.uk/searchresults.aspx?" + data, headers=headers)
#opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
#page = opener.open(req)
h = httplib2.Http()
resp, page = h.request("http://findaproperty.co.uk/searchresults.aspx?" + data, method="GET", headers=headers)
# TODO: eventually we'll loop around postcodes, then this'll be a continue, rather than an assert
assert resp.status == 200
soup = BeautifulSoup(page)


divs = soup.findAll("div", {"class" : "search_results_table"})

# regexp to get the following ids from a url
#edid=00&salerent=0&pid=489315&agentid=06678
property_ids_re = re.compile('.*edid=(\\d+)&salerent=(\\d+)&pid=(\\d+)&agentid=(\\d+)')

for div in divs:
    div_soup= BeautifulSoup(str(div))
    hrefs = div_soup.findAll("a")
    # First href has the property desc as it's contents
    property_desc = hrefs[0].contents[0].strip()
    print property_desc
    # second href has property id and agent id.  Inside it has an image of the property
    # TODO get the image
    ids_href = hrefs[1]
    match = property_ids_re.match(ids_href['href'])
    # TODO what does match return on no matches?  0 or None?
    (edid, salerent, pid, agentid) = match.groups()
    # get the image
    ids_href_soup = BeautifulSoup(str(ids_href))
    property_image = ids_href_soup.findAll("img")[0]
    img_url = property_image['src']
    print img_url
    # third href has the agent desc.  We have the agent id above
    agent_href = hrefs[2]
    print agent_href.contents[0]
    # TODO
    # get extra details about the property by hitting a url like
    # http://www.findaproperty.com/displayprop.aspx?edid=00&salerent=0&pid=489315&agentid=06678
    data = urllib.urlencode([("edid", edid),("salerent", salerent),("pid", pid),("agentid", agentid)])
# If we can't get httplib2, we have to use this
#    req = urllib2.Request(url="http://findaproperty.co.uk/displayprop.aspx?" + data, headers=headers)
#    page = opener.open(req)
# TODO: handle error responses
    resp, page = h.request("http://findaproperty.co.uk/displayprop.aspx?" + data, method="GET", headers=headers)
    if resp.status != 200:
        print "ERROR: we couldn't fetch http://findaproperty.co.uk/displayprop.aspx?" + data
        continue
    soup = BeautifulSoup(page)

    # get some details from the page, currently in no particular
    tmp_soup = BeautifulSoup(str(soup.findAll("div", {"class" : "agenttext"})[0]))
    agenttext = tmp_soup.findAll("b")[0].contents[0]
    print agenttext

    # get the status of this property
    statuses = soup.findAll(attrs={'class' : re.compile("^status.*")})
    if len(statuses) == 1:
        status = statuses[0].contents[0]
    else:
        status = ""
    print status

    time.sleep(5)

# now we get the next results button, if it exists.
# it'll look like http://www.findaproperty.com/searchresults.aspx?so=0&vw=0&res=1&sp=2&p=30
# next one being http://www.findaproperty.com/searchresults.aspx?so=0&vw=0&res=1&sp=3&p=30
results_nav_paging = soup.findAll("div", {"class" :"results_nav_paging"})[0]
results_nav_soup = BeautifulSoup(str(results_nav_paging))
results_hrefs = results_nav_soup.findAll("a")
if results_hrefs[-1].contents[0] == 'Next':
    print results_hrefs[-1]['href']


# Update the number of results returned per page
# params:
# opener - the opener object we're using to scrape this site
# soup - the soup of a results page
# returns:
# page - the page that was returned by this call
def update_results_per_page(opener, soup, base_url="http://findaproperty.co.uk/",results=30):
    # Update the settings for paging
    rsform = soup.findAll("form", {"name" : "rsform"})[0]
    action = rsform['action']
    viewstate = soup.findAll("input", {"name" : "__VIEWSTATE"})[0]

    # do we need all these?  Certainly the first three
    # two names?  include both.  Later we'll only need to search for a limited time period
#<select name="RefineSearchControl:sh" id="RefineSearchControl_sh" name="sh">
#<option value="0">Anytime</option>
#<option value="1440">Last 24 hours</option>
#<option value="4320">Last 3 days</option>
#<option value="10080">Last week</option>
#<option value="43200">Last month</option>
    data = urllib.urlencode([("__EVENTTARGET","ResultsHeaderControl:ResultsViewModeControl:so"),
                             ("__EVENTARGUMENT",""),
                             ("ResultsHeaderControl:ResultsViewModeControl:p",30),
                             ("RefineSearchControl:sh",0),
                             ("sh",0),
                             ("ResultsHeaderControl:ResultsViewModeControl:so",0),
                             ("sp",0),
                             ("RefineSearchControl:abeds",0),
                             ("RefineSearchControl:vw",0),
                             ("RefineSearchControl:edid",0),
                             ("RefineSearchControl:salerent",0),
                             ("RefineSearchControl:res",0),
                             ("RefineSearchControl:regionid",0),
                             ("RefineSearchControl:countyid",0),
                             ("RefineSearchControl:areaid",0),
                             ("RefineSearchControl:al",""),
                             ("RefineSearchControl:tl",""),
                             ("RefineSearchControl:zl",""),
                             ("RefineSearchControl:ll",""),
                             ("RefineSearchControl:ts",0)])

    req = urllib2.Request(url="http://findaproperty.co.uk/" + action)
    settings_page = opener.open(req, data=data)

