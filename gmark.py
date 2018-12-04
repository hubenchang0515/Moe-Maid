#! /usr/bin/env python3

# 通过GitHub的API渲染Makedown
# https://api.github.com/markdown
# 注意结尾不要带/

import sys
import os
import requests
import json
script = os.path.basename(sys.argv[0])

if __name__ != "__main__" :
	pass
else :


	if len(sys.argv) < 2 or len(sys.argv) > 3 :
			print("Usage : %s <input> [output]" % script)
			print("        %s readme.md readme.html" % script)
			print("        %s mark.md" % script)
			quit(1)
	fp = open(sys.argv[1], encoding="utf-8")
	md = fp.read()
	#Zheaders = {'Content-Type': 'text/x-markdown'}
	payload = {"text" : md, "mode" : "markdown"}
	response = requests.post("https://api.github.com/markdown", data=json.dumps(payload))
	output = response.text.encode("utf-8").decode("utf-8")
	if len(sys.argv) == 2 :
		print(output)
	else :
		outfile = open(sys.argv[2], "w", encoding="utf-8")
		outfile.write(output)