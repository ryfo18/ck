#!/usr/bin/python

import render
from bs4 import BeautifulSoup
from urllib import urlencode,urlopen
import json
import requests
import re

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

def get_kitty_details(id):
  url = "http://api.cryptokitties.co/kitties/" + str(id)
  response = urllib.urlopen(url)
  data = json.loads(response.read())
  return data

def create_attributes():
  html = requests.get("http://www.kittyexplorer.com/").content
  soup = BeautifulSoup(html, "html.parser")
  print soup.h3.text
  total_cats = int(re.search('\d+', soup.h3.text).group(0))
  buttons = soup.find_all("button", class_="btn-primary")
  cat_attrs=dict()
  for button in buttons:
    attr = button.text.strip().split()
    pct = float(attr[1]) / total_cats * 100
    cat_attrs[attr[0]] = pct

  print cat_attrs
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
      price = self.get_price(kitties_soup[i])
      kitties.append(Kitty(id, price))
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

class Kitty:
  """ A kitty class to describe a kitten """
  unique = 100
  def __init__(self, id, price=None):
    self.id = int(id)
    print self.id
    self.data = get_kitty_details(self.id)
    self.fancy = self.data["is_fancy"]
    self.set_price()
    self.set_gen()
    if self.gen != 0:
      self.set_parents()
    self.set_attributes()
    self.set_unique()

  def set_gen(self):
    self.gen = int(self.data["generation"])

  def set_parents(self):
    self.parents=[]
    self.parents.append(Parent(self.data["sire"]["id"]))
    self.parents.append(Parent(self.data["matron"]["id"]))

  def set_price(self):
    if bool(self.data["auction"]):
      self.price = self.data["auction"]["current_price"]

  def set_attributes(self):
    """ Attributes are from KittyExplorer """
    attrs_soup = self.ke_soup.find_all("button", class_="btn-primary")
    self.attrs = []
    if len(attrs_soup) > 0: # hack b/c some kitty explorer pages are empty
      for i in range(0, len(attrs_soup)):
        self.attrs.append(attrs_soup[i].text)
        if self.attrs[i] == "is fancy":
          self.num_attributes = i + 1
          self.fancy = True
          break

  def set_unique(self):
    if not self.fancy and len(self.attrs) > 0:
      for attr in self.attrs:
        pct = int(re.sub('%', '', attr.split()[1]))
        if pct < self.unique:
          self.unique = pct

  def print_details(self):
    print "ID: " + str(self.id)
    print "Gen: " + str(self.gen)
    print "Price: " + str(self.price)
    print "Attrs:" 
    print self.attrs
    for parent in self.parents:
      print parent.attrs

class Parent(Kitty):
  def __init__(self, id):
    self.id = int(id)
    self.data = get_kitty_details(self.id)
    self.fancy = self.data["is_fancy"]
    self.set_gen()
    self.set_attributes()
    self.set_unique()
