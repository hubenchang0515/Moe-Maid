#! /usr/bin/env python3
# author: planc
# e-mail: hubenchang0515@outlook.com
# repo: https://github.com/hubenchang0515/Moe-Maid/blob/master/vscode-download.py

import argparse
import urllib.request
import urllib.parse
from pathlib import Path

os_options: list[str] = [
    "win32-x64-user",
    "win32-user",
    "win32-arm64-user",

    "win32-x64",
    "win32",
    "win32-arm64",

    "win32-x64-archive",
    "win32-archive",
    "win32-arm64-archive",

    "cli-win32-x64",
    "cli-x64",
    "cli-arm64-x64",

    "linux-deb-x64",
    "linux-deb-armhf",
    "linux-deb-arm64",

    "linux-rpm-x64",
    "linux-rpm-armhf",
    "linux-rpm-arm64",

    "linux-x64",
    "linux-armhf",
    "linux-arm64",

    "cli-alpine-x64",
    "cli-alpine-armhf",
    "cli-alpine-arm64",

    "darwin",
    "darwin-arm64",
    "darwin-universal",

    "cli-darwin-x64",
    "cli-darwin-arm64",
]

build_options: list[str] = [
    "stable",
    "insider"
]

class RedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self, cdn) -> None:
        super().__init__()
        self.__cdn = cdn

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        print(f"Redirect to {newurl}")
        parts = urllib.parse.urlparse(newurl)
        parts = parts._replace(netloc=self.__cdn)
        newurl = parts.geturl()
        print(f"Redirect to {newurl}")
        return urllib.request.Request(newurl)

if __name__ == "__main__":
    build_options:str = "\n\t".join(build_options)
    os_options:str = "\n\t".join(os_options)
    parser = argparse.ArgumentParser(description="Download VS Code with CDN", 
                                        epilog=f"build options:\n\t{build_options}\n\nos options:\n\t{os_options}\n",
                                        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--os", required=True, help="operating system")
    parser.add_argument("--build", required=False, help="build type, default 'stable'", default="stable")
    parser.add_argument("--cdn", required=False, help="CDN url, default 'vscode.cdn.azure.cn'", default="vscode.cdn.azure.cn")
    parser.add_argument("--proxy", required=False, help="proxy, default None")
    args = parser.parse_args()

    if args.proxy is None:
        proxies = None
    else:
        proxies = {
            "http": args.proxy,
            "https": args.proxy,
            "socks5": args.proxy,
        }

    proxy_handler = urllib.request.ProxyHandler(proxies=proxies)
    redirect_handler = RedirectHandler(args.cdn)
    opener = urllib.request.build_opener(proxy_handler, redirect_handler)

    params = urllib.parse.urlencode({'build': args.build, 'os': args.os})
    url:str = f"https://code.visualstudio.com/sha/download?{params}"
    print(f"Request {url}")
    
    with opener.open(url) as response:
        parts = urllib.parse.urlparse(response.geturl())
        path = Path(parts.path)
        total_bytes:int = int(response.getheader('Content-Length'))
        done_bytes:int = 0
        with open(path.name, mode="wb") as fp:
            while done_bytes < total_bytes:
                data = response.read(4*1024)
                if data is None:
                    break
                fp.write(data)
                done_bytes += len(data)
                print(f"Download {done_bytes}/{total_bytes} bytes", end="\r")
            print("\nDone.")
