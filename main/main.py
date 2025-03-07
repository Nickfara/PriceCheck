# import interface
import os

from log import log

dir = os.listdir('data/prices')

for i in dir:
    log(i)
