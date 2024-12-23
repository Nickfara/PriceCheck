#import interface
import os

dir = os.listdir('doc')
for i in dir:
    print(i)

with open('doc/Интерфиш.xls', "rb") as f:
    peek = f.read()