#! /usr/bin/env python3

# 这个脚本的功能是将图片生成字符画
# 使用方法：script.py <input> [output] [width]
# 将<input>指定的图形文件转换成字符画，保存到output指定的文件中
# 如果没有[output]参数，则将字符画打印出来
# 如果图片的宽度大于[width]像素，则自动缩放到宽度为[width]
# 如果没有[width]参数，则采用默认值50



import os
import sys
from PIL import Image

if __name__ == "__main__" :
	# 参数检查
	if len(sys.argv) < 2 or len(sys.argv) > 4 :
		script = os.path.basename(sys.argv[0])
		print("Usage : %s <input> [output] [width]" % script)
		print("        %s cat.png cat.txt" % script)
		print("        %s ping.jpg" % script)
		quit(1)
	
	# 打开输出文件
	fp = None
	if len(sys.argv) >= 3 :
		fp = open(sys.argv[2],"w")
		
	base = "@#&$%*o!;."
	img = Image.open(sys.argv[1])
	gray = img.convert("L")
	
	# 缩放到宽度为50，太大了不方便显示
	width = 50
	if len(sys.argv) == 4 :
		width = int(sys.argv[3])
	if gray.size[0] > width :
		resize_coefficient = width / gray.size[0]
		gray = gray.resize((width, round(resize_coefficient * gray.size[1])))

	# 将像素转换成字符
	for y in range(0, gray.size[1]) :
		for x in range(0, gray.size[0]) :
			index = round(gray.getpixel((x,y)) / 255 * len(base) - 1) # 归一化
			if len(sys.argv) >= 3 :
				fp.write(base[index])
				fp.write(base[index])
			else :
				print(base[index], end="")
				print(base[index], end="")
		if len(sys.argv) >= 3 :
			fp.write("\n")
		else :
			print("")
	
	# 不close了，让GC自动回收资源
