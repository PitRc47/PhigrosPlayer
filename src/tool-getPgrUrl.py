import json
import random
import urllib.parse
import urllib.request
import urllib3
import typing
from uuid import uuid4
from time import time
from hashlib import md5
from string import ascii_lowercase, digits

import requests

urllib3.disable_warnings()

def get_download_info(appid: int, apkid: typing.Optional[int] = None):
    UID = uuid4()
    API = "https://api.taptapdada.com"
    USER_AGENT = "okhttp/3.12.1" # 必须要有, 否则频繁请求会风控
    VN_CODE = "281001004"
    X_UA = f"V=1&PN=TapTap&VN_CODE={VN_CODE}&LOC=CN&LANG=zh_CN&CH=default&UID={UID}"
    quoted_X_UA = urllib.parse.quote(X_UA)
    
    try:
        apkid_result = requests.get(
            f"{API}/app/v2/detail-by-id/{appid}?X-UA={quoted_X_UA}",
            headers = {"User-Agent": USER_AGENT},
            verify = False
        ).json()
    except json.decoder.JSONDecodeError:
        raise Exception("TapTap API 风控")
    
    apkid = apkid_result["data"]["download"]["apk_id"] if apkid is None else apkid

    nonce = "".join(random.sample(ascii_lowercase + digits, 5))
    t = int(time())
    sign = md5(f"X-UA={X_UA}&end_point=d1&id={apkid}&node={UID}&nonce={nonce}&time={t}PeCkE6Fu0B10Vm9BKfPfANwCUAn5POcs".encode()).hexdigest()

    return json.load(urllib.request.urlopen(urllib.request.Request(
        f"{API}/apk/v1/detail?X-UA={quoted_X_UA}",
        data = f"sign={sign}&node={UID}&time={t}&id={apkid}&nonce={nonce}&end_point=d1".encode(),
        headers = {"Content-Type": "application/x-www-form-urlencoded", "User-Agent": USER_AGENT}
    )))

PHIGROS_APPID = 165287

if __name__ == "__main__":
    from sys import argv
    
    if "--appid" in argv:
        PHIGROS_APPID = int(argv[argv.index("--appid") + 1])
        
    # print("tip: 请不要多次运行, 以免触发 TapTap 的风控机制\n")
    result = get_download_info(PHIGROS_APPID)
    print(f"版本: {result["data"]["apk"]["version_name"]}")
    print(f"下载地址: {result["data"]["apk"]["download"]}")
