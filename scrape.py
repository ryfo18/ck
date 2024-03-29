#!/usr/bin/python

import argparse
import kitty

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Find bargain kitties")
  parser.add_argument('--gens', dest='gens', nargs='*', type=int)
  parser.add_argument('--attrs', dest='attrs', nargs='*')
  parser.add_argument('--cooldown', dest='cooldown', nargs='*')
  parser.add_argument('--thresh', dest='thresh', type=int)
  parser.add_argument('--max_cost', type=float)
  args = parser.parse_args()
  
  thresh = args.thresh
  x = kitty.Marketplace(args.gens, args.attrs, args.cooldown, selenium=True)
  num_pages = x.num_pages
  for i in range (1, num_pages + 1):
    x = kitty.Marketplace(args.gens, args.attrs, args.cooldown, i, selenium=True)
    kitties = x.get_kitty_list()
    for cat in kitties:
      if cat.unique < thresh:
        cat.print_details()
      else:
        for parent in cat.parents:
          if parent.unique < thresh:
            cat.print_details()
