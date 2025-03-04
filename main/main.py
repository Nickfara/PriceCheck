# import interface
import os

from log import log

dir = os.listdir('doc')

for i in dir:
    log(i)
