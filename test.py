#!/usr/bin/python
 
import kitty

x = kitty.Kitty(175607)
print x.id
print x.attrs
print x.unique
for parent in x.parents:
  print parent.id
  print parent.attrs
  print parent.unique
