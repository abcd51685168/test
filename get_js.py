__author__ = 'lunac'
from bs4 import BeautifulSoup
src_path = "/root/m.html"
with open(src_path) as f:
    soup = BeautifulSoup(f)

scripts = soup.find_all('script', {'type': 'text/javascript'}) + soup.find_all('script', {'type': False})


script_text = "\n".join([script.get_text().strip() for script in scripts if script.get_text().strip()])

if script_text:
    print(script_text)
else:
    print False
# print script_text
