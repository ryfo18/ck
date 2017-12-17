#!/usr/bin/python

import urllib
import json

url = "https://api.cryptokitties.co/kitties/238021"
response = urllib.urlopen(url)
data = json.loads(response.read())
print data
