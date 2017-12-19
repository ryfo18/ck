#!/usr/bin/python

#import render
from bs4 import BeautifulSoup
from urllib import urlencode,urlopen
import json
import requests
import re
import render

cat_attrs = 0

# loads a cryptokitties page
def get_ck_soup(url, tag=None, selenium=False):
  if not selenium:
    r = render.Render(url)
    html = unicode(r.frame.toHtml())
    return BeautifulSoup(html, "html.parser")
  else:
    return BeautifulSoup(render.selenium_render(url, tag), "html.parser")

# load a kittyexplorer page
def get_ke_soup(id):
  url = 'https://www.kittyexplorer.com/kitties/' + str(id)
  html = requests.get(url).content
  return BeautifulSoup(html, "html.parser")

def get_attributes_dict():
  """ Attributes obtained from kittyexplorer.com. This function uses a global
  variable to store them for performance """
  global cat_attrs
  if cat_attrs == 0:
    html = requests.get("http://www.kittyexplorer.com/").content
    soup = BeautifulSoup(html, "html.parser")
    total_cats = int(re.search('\d+', soup.h3.text).group(0))
    buttons = soup.find_all("button", class_="btn-primary")
    cat_attrs=dict()
    for button in buttons:
      attr = button.text.strip().split()
      pct = float(attr[1]) / total_cats * 100
      cat_attrs[attr[0]] = pct

  return cat_attrs

class Marketplace:

  num_kitties_per_page = 12
  def __init__(self, gens=[], attrs=[], cooldown=[], page=1, selenium=True):
    self.gens = gens
    self.attrs = attrs
    self.cooldown = cooldown
    self.page = str(page)
    self.selenium = selenium
    self.base_url = 'https://www.cryptokitties.co/marketplace/sale/' + self.page + '?'
    self.set_soup()
    self.set_num_pages()

  def set_soup(self):
    search = {'orderBy' : 'current_price', 'orderDirection' : 'asc', 
        'search' : '', 'sorting' : 'cheap'}
    if self.attrs is not None:
      search['search'] += ','.join(self.attrs) + ' '
    if self.gens is not None:
      search['search'] += 'gen:' + ','.join(map(str, self.gens)) + ' '
    if self.cooldown is not None:
      search['search'] += 'cooldown:' + ','.join(self.cooldown)
    url = self.base_url + urlencode(search).replace('+', '%20')
    self.soup = get_ck_soup(url, 'KittiesFilter', self.selenium)

  def set_num_pages(self):
#    num_results = self.soup.find("div", class_="KittiesFilter-header").span[0].text.replace(',', '')
    num_results = self.soup.find("div", class_="KittiesFilter-header").span.text
    self.num_results = re.search('\d+,?\d*', num_results).group(0)
    self.num_results = int(self.num_results.replace(',', ''))
    print 'Found ' + str(self.num_results) + ' kitties'
    self.num_pages = int(self.num_results / self.num_kitties_per_page) + 1

  def get_kitty_list(self):
    kitties_soup = self.soup.find_all("div", class_="KittyCard-wrapper")
    kitties = []
    for i in range(0, len(kitties_soup)):
      id = self.get_id(kitties_soup[i])
      #price = self.get_price(kitties_soup[i])
      #kitties.append(Kitty(id, price))
      kitties.append(Kitty(id))
    return kitties

  def get_id(self, soup):
      id = soup.find("div", class_="KittyCard-subname").text
      id = int(re.search('\d+', id).group(0))
      return id

  def get_price(self, soup):
    price = soup.find_all("span", class_="KittyStatus-note")[0].text
    if price == "Free":
      price = 0.0
    else:
      price = float(re.search('\d+\.?\d*', price).group(0))
    return price

class Cat:
  """" Base class for all cats will initialize basic parameters """
  unique = 100
  def __init__(self, id):
    self.id = int(id)
    self.attrs_dict = get_attributes_dict()
    self.attrs_list = None
    self.data = self.get_kitty_details(self.id)
    self.fancy = self.data["is_fancy"]
    self.set_gen()
    self.set_attributes()
    self.set_unique()

  def get_kitty_details(self, id):
    """ gets the information from the cryptokitties API """
    url = "http://api.cryptokitties.co/kitties/" + str(id)
    response = urlopen(url)
    data = json.loads(response.read())
    return data

  def set_gen(self):
    self.gen = int(self.data["generation"])

  def set_attributes(self):
    self.attrs = []
    if self.fancy is True:
      self.attrs.append({"type" : "fancy", "desc" : self.data["fancy_type"], "pct" : self.attrs_dict[self.data["fancy_type"]]})
    else:
      for attr in self.data["cattributes"]:
        self.attrs.append({"type" : attr["type"], "desc" : attr["description"], "pct" : self.attrs_dict[attr["description"]]})

  def set_unique(self):
    for attr in self.attrs:
      if attr["pct"] < self.unique:
        self.unique = attr["pct"]

  def get_attrs_list(self):
    """ returns a list of attributes sorted by rarity """
    if self.attrs_list is None:
      self.attrs_list = []
      temp_dict = dict()
      for attr in self.attrs:
        temp_dict.update({attr["desc"] : attr["pct"]})
      for key, value in sorted(temp_dict.iteritems(), key=lambda (k,v): (v,k)):
        self.attrs_list.append("%s %.2f" % (key, value))
    return self.attrs_list


class Kitty(Cat):
  """ A kitty class to describe a kitten """
  def __init__(self, id):
    Cat.__init__(self, id)
    print self.id
    self.set_price()
    if self.gen != 0:
      self.set_parents()

  def set_parents(self):
    self.parents=[]
    self.parents.append(Cat(self.data["sire"]["id"]))
    self.parents.append(Cat(self.data["matron"]["id"]))

  def set_price(self):
    self.price = None
    if bool(self.data["auction"]):
      self.price = float(self.data["auction"]["current_price"]) * 1e-18

  def print_details(self):
    print "ID: " + str(self.id)
    print "Gen: " + str(self.gen)
    print "Price: " + str(self.price)
    print "Attrs:" 
    print list(self.get_attrs_list())
    for parent in self.parents:
      print parent.get_attrs_list()

