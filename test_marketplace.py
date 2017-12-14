#!/usr/bin/python
import kitty

gens = [1,2,3]
attrs = ['whixtensions']
cooldown = ['swift','snappy','brisk']
x = kitty.Marketplace(gens, attrs, cooldown, selenium=True)
kitties = x.get_kitty_list()
for kitty in kitties:
  print kitty.id
  print kitty.gen
  print kitty.attrs
  for parent in kitty.parents:
    print parent.id
    print parent.gen
    print parent.attrs
