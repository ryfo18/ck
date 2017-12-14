#!/usr/bin/python

import re,copy
from bs4 import BeautifulSoup,Comment
import argparse
import render

def get_kitty_list(soup):
  kitties_soup = soup.find_all("div", class_="KittyCard-wrapper")
  for i in range(0, len(kitties_soup)):
    id = kitties_soup[i].find("div", class_="KittyCard-subname").text
    id = int(re.search('\d+', id).group(0))
    print id
    price = kitties_soup[i].find_all("span", class_="KittyStatus-note")[0].text
    if price == "Free":
      price = 0.0
    else:
      price = float(re.search('\d+\.?\d*', price).group(0))
    print price

def get_id(soup):
  id = soup.find("div", class_="KittyHeader-details").span.string
  id = re.search('\d+', id).group(0)
  return id

def get_gen(soup):
  gen = soup.find("a", class_="KittyHeader-details-generation").text
  gen = re.search('\d+', gen).group(0)
  print gen

def get_key_attributes(id, thresh):
  url = 'https://www.kittyexplorer.com/kitties/' + id
  html = requests.get(url).content
  soup = BeautifulSoup(html, "html.parser")
  attrs = soup.find_all("button", class_="btn-primary")
  key_attrs = []
  for i in range(0,8):
    attr = attrs[i].text.split()
    pct = int(re.sub('%', '', attr[1]))
    if pct < thresh:
      key_attrs.append(attrs[i].text)
  return key_attrs

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Find bargain kitties")
  parser.add_argument('--gen', dest='gen', nargs='*', type=int)
  parser.add_argument('--attrs', dest='attrs', nargs='*')
  parser.add_argument('--cooldown', dest='cooldown', nargs='*')
  parser.add_argument('--thresh', type=int)
  parser.add_argument('--max_cost', type=float)
  args = parser.parse_args()
  soup = get_search_soup(args.gen, args.attrs, args.cooldown, 1)
#  print soup.prettify().encode('UTF-8')
  num_pages = get_num_pages(soup)
  print num_pages
  get_kitty_list(soup)

  '''
  url = 'https://www.cryptokitties.co/kitty/115599'
  r = Render(url)
  html = unicode(r.frame.toHtml())

  #print result.toUtf8()
  soup = BeautifulSoup(html, "html.parser")
  comments=soup.findAll(text=lambda text:isinstance(text, Comment))

  for comment in comments:
    comment.extract()

  #for script in soup(["script", "style"]):
  #  script.extract()

  #print soup.prettify().encode('UTF-8')
  #print soup.prettify()

  id = get_id(soup)
  get = get_gen(soup)
  parents = get_parents(soup)

  stats = []
  stats.append(get_key_attributes(id, 1))
  for parent in parents:
    stats.append(get_key_attributes(parent, 1))

  for stat in stats:
    print len(stat)
    '''
