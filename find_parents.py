#!/usr/bin/python

import argparse
import kitty

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Find bargain kitties")
  parser.add_argument('--gens', dest='gens', nargs='*', type=int)
  parser.add_argument('--attrs', dest='attrs', nargs='*')
  parser.add_argument('--cooldown', dest='cooldown', nargs='*')
  parser.add_argument('--max_cost', type=float)
  args = parser.parse_args()
  
  x = kitty.Marketplace(args.gens, args.attrs, args.cooldown, selenium=True)
  num_pages = x.num_pages
  attrs = dict()
  for i in range (1, num_pages + 1):
    x = kitty.Marketplace(args.gens, args.attrs, args.cooldown, i, selenium=True)
    kitties = x.get_kitty_list()
    for cat in kitties:
      for parent in cat.parents:
        for attr in parent.attrs:
          if attr in attrs:
            attrs[attr] += 1
          else:
            attrs[attr] = 1
    for key, value in sorted(attrs.iteritems(), key=lambda (k,v): (v,k)):
      print "%s: %d" % (key, value)
