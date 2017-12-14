#!/usr/bin/python

import render
from bs4 import BeautifulSoup
from urllib import urlencode
import requests
import re

# loads a cryptokitties page
def get_ck_soup(url, selenium=False):
  if not selenium:
    r = render.Render(url)
    html = unicode(r.frame.toHtml())
    return BeautifulSoup(html, "html.parser")
  else:
    return BeautifulSoup(render.selenium_render(url), "html.parser")

# load a kittyexplorer page
def get_ke_soup(id):
  url = 'https://www.kittyexplorer.com/kitties/' + str(id)
  html = requests.get(url).content
  return BeautifulSoup(html, "html.parser")


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
    if len(self.attrs) > 0:
      search['search'] += ','.join(self.attrs) + ' '
    if len(self.gens) > 0:
      search['search'] += 'gen:' + ','.join(map(str, self.gens))
    if len(self.cooldown) > 0:
      search['search'] += 'cooldown:' + ','.join(self.cooldown)
    url = self.base_url + urlencode(search).replace('+', '%20')
    self.soup = get_ck_soup(url, self.selenium)

  def set_num_pages(self):
#    num_results = self.soup.find("div", class_="KittiesFilter-header").span[0].text.replace(',', '')
    num_results = self.soup.find("div", class_="KittiesFilter-header").span.text
    self.num_results = int(re.search('\d+', num_results).group(0))
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
  base_ck_url = "https://www.cryptokitties.co/kitty/"
  num_attributes = 8
  unique = 100
  def __init__(self, id, price=None):
    self.id = int(id)
    print self.id
    self.price = price
    self.ck_url = self.base_ck_url + str(self.id)
    self.ck_soup = get_ck_soup(self.ck_url, selenium=True)
    self.ke_soup = get_ke_soup(id)
    self.set_gen()
    self.set_parents()
    self.fancy = False
    self.set_attributes()
    self.set_unique()

  def set_gen(self):
    gen = self.ck_soup.find("a", class_="KittyHeader-details-generation").text
    self.gen = int(re.search('\d+', gen).group(0))

  def set_parents(self):
    self.parents=[]
    parent_soup = self.ck_soup.find_all("div", class_="KittyCard-subname")
    for i in range(0,2): # parents should be first two results
      id = re.search('\d+', parent_soup[i].text).group(0)
      self.parents.append(Parent(id))

  def set_attributes(self):
    """ Attributes are from KittyExplorer """
    attrs_soup = self.ke_soup.find_all("button", class_="btn-primary")
    if len(attrs_soup) > 0: # hack b/c some kitty explorer pages are empty
      self.attrs = []
      for i in range(0, self.num_attributes):
        print i
        self.attrs.append(attrs_soup[i].text)
        if self.attrs[i] == "is fancy":
          self.num_attributes = i + 1
          self.fancy = True
          break

  def set_unique(self):
    if not self.fancy:
      for attr in self.attrs:
        pct = int(re.sub('%', '', attr.split()[1]))
        if pct < self.unique:
          self.unique = pct

class Parent(Kitty):
  def __init__(self, id):
    self.id = int(id)
    self.fancy = False
    self.ke_soup = get_ke_soup(id)
    self.set_gen()
    self.set_attributes()
    self.set_unique()

  def set_gen(self):
    gen = self.ke_soup.find("div", class_="col-md-9").h3.text
    self.gen = int(gen.split()[-1])