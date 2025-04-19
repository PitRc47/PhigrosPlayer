from urllib.request import Request, urlopen
from sys import argv

with open(argv[1], "wb") as f:
    req = Request(argv[2])
    f.write(urlopen(req).read())