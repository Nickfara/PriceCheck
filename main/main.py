# import interface
import os
from log import log


dir = os.listdir('doc')

for i in dir:
    log(i)

with open('doc/Интерфиш.xls', "rb") as f:
    peek = f.read()
