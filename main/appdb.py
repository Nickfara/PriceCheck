'''
Запрос приложений с сайта APPDB
'''

import requests
import json
import time

s = requests.session()


id = '4114d4145a3ab635ae8f77bbd87fcac242a9cedc'
uoi = '68dc41f45f8d29c37444c15144a2e7076036097c'


list_uoi_link = f'https://api.dbservices.to/v1.7/search_index/?lang=en&lt={id}&st=&name=&developer_name=&type=&compatibility=ios&source_name=&start=0&length=1000&brand=appdb'
list_uoi = s.get(list_uoi_link).json()

data_uoi = [i['universal_object_identifier'] for i in list_uoi['data']]

print(data_uoi)


download_ticket = s.get(f'https://api.dbservices.to/v1.7/universal_gateway/?lang=en&lt={id}&st=&universal_object_identifier={data_uoi[110]}&brand=appdb').json()['data']['download_ticket']
print(download_ticket)
redirection_ticket = s.get(f'https://api.dbservices.to/v1.7/process_redirect/?lang=en&lt={id}&st=&t={download_ticket}&brand=appdb').json()['data']['redirection_ticket']
print(redirection_ticket)
s.post(f'https://www.google-analytics.com/g/collect?v=2&tid=G-F3EV3Q5E1R&gtm=45je5411v9104549773za200&_p=1743698488832&gcd=13l3l3l3l1l1&npa=0&dma=0&tag_exp=102788824~102803279~102813109~102887800~102926062~102975949~103016951&cid=1038880555.1743691954&ul=ru&sr=1920x1080&uaa=x86&uab=64&uafvl=Not%2520A(Brand%3B8.0.0.0%7CChromium%3B132.0.6834.955%7CYaBrowser%3B25.2.4.955%7CYowser%3B2.5&uamb=0&uam=&uap=Windows&uapv=19.0.0&uaw=0&are=1&frm=0&pscdl=noapi&_eu=AEA&dl=https%3A%2F%2Fappdb.to%2Fdetails%2F2fcc254e1b9b57f32e6c6fcd5dcb1635688ec295&dr=https%3A%2F%2Fappdb.to%2Fredirect%{download_ticket}&sid=1743691953&sct=1&seg=1&dt=Survivalcraft%202%20-%20appdb&_s=3&tfd=63906')
time.sleep(16)
link = s.get(f'https://api.dbservices.to/v1.7/process_redirect/?lang=en&lt=4114d4145a3ab635ae8f77bbd87fcac242a9cedc&st=&rt=SnhQSkl3aWkxMzJZQTJWd3dzMzlPNzFzRUlIelc0ZlRXVCs3cjkxbkd5Ly9oQzYyM2xwb0MwZ3JhUWtaWkJmNlpadzNVSEtKOVZ4L1dEaERvSVhlaHFuYld5NkQ0SzdIYld4U0I2ZG9uRlVPaHBjQVQ5Y2lObEg1eGJacm0wWEpWTWJ5SnU4VzJ6S0NYdzZmdXRCUTRVd2h0WW9iQ083ZHA5RktFUXRCVmNtcTlEbXBkdUdZOWJCaHp6U1AwZFJI&brand=appdb').json()["data"]["link"]
print(link)

download_link = s.get(f'https://s3cdn.dbservices.to/ipas/{uoi}.ipa?verify={link}').json()['data']['link']

ss = s.get(download_link).json()

print(ss)
