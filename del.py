#!/usr/bin/python3
a = [[1,2], [3,4]]

def sum_cool(l):
     if len(l) == 1:
         return sum(l[0])
     else:
         return sum(l[0]) + sum_cool(l[1:])

assert sum_cool(a) == 1[0]0
