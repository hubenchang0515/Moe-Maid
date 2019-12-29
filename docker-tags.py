#! /usr/bin/env python3
# Python >= 3.6 for f-string
import json
import os
import ssl
import sys
from urllib import request

ssl._create_default_https_context = ssl._create_unverified_context

if len(sys.argv) not in (2, 3):
    print(f"Usage : {os.path.basename(__file__)} <repo> [tag]")
    print(f"        {os.path.basename(__file__)} nginx")
    print(f"        {os.path.basename(__file__)} mysql 5.6")
    quit(1)

url = f"https://registry.hub.docker.com/v1/repositories/{sys.argv[1]}/tags"
try:
    res = request.urlopen(url, timeout=3)
    tags = json.loads(res.read().decode("utf-8"))

    tags = [
        tag["name"] for tag in tags if len(sys.argv) == 2 or sys.argv[2] in tag["name"]
    ]
    for tag in tags:
        print(f"{sys.argv[1]}:{tag}")
    print()
    print(f"total {len(tags)} tags")
except Exception as e:
    print(e)
