import json
import random
import urllib.parse
import urllib.request
from uuid import uuid4
from time import time
from hashlib import md5
from string import ascii_lowercase, digits

def get_download_info(appid: int):
    uid = uuid4()
    X_UA = f"V=1&PN=TapTap&VN_CODE=206012000&LOC=CN&LANG=zh_CN&CH=default&UID={uid}"
    quoted_X_UA = urllib.parse.quote(X_UA)
    
    apkid_result = json.load(urllib.request.urlopen(urllib.request.Request(f"https://api.taptapdada.com/app/v2/detail-by-id/{appid}?X-UA={quoted_X_UA}")))
    apkid = apkid_result["data"]["download"]["apk_id"]

    nonce = "".join(random.sample(ascii_lowercase + digits, 5))
    t = int(time())
    sign = md5(f"X-UA={X_UA}&end_point=d1&id={apkid}&node={uid}&nonce={nonce}&time={t}PeCkE6Fu0B10Vm9BKfPfANwCUAn5POcs".encode()).hexdigest()

    return json.load(urllib.request.urlopen(urllib.request.Request(
        f"https://api.taptapdada.com/apk/v1/detail?X-UA={quoted_X_UA}",
        data = f"sign={sign}&node={uid}&time={t}&id={apkid}&nonce={nonce}&end_point=d1".encode()
    )))

PHIGROS_APPID = 165287

if __name__ == "__main__":
    from sys import stderr, argv
    
    if "--appid" in argv:
        PHIGROS_APPID = int(argv[argv.index("--appid") + 1])
        
    print("tip: 请不要多次运行, 以免触发 TapTap 的风控机制\n", file=stderr)
    result = get_download_info(PHIGROS_APPID)
    print(f"""Phigros版本: {result["data"]["apk"]["version_name"]}""", file=stderr)
    print(f"""下载地址: {result["data"]["apk"]["download"]}""", file=stderr)
    
    if "-c" in argv:
        print(result["data"]["apk"]["download"])