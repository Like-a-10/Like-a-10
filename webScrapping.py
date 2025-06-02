import requests
from bs4 import BeautifulSoup

web=requests.get("https://www.tutorialsfreak.com/")

soup=BeautifulSoup(web.content ,"html.parser",from_encoding='utf-8')
# print(soup.prettify().encode('ascii','ignore').decode())
lines=soup.find_all("p")
for l in lines:
    print(l.text)