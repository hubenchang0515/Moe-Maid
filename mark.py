from markdown.extensions import Extension
from markdown.util import etree
from markdown.postprocessors import Postprocessor
from markdown.preprocessors import Preprocessor

# 特殊字符转换
converts = {
	"<" : "&lt;",
	">" : "&gt;"
}

# 加载js
js_files = (
	"https://cdnjs.cloudflare.com/ajax/libs/SyntaxHighlighter/3.0.83/scripts/shCore.js",
	"https://cdnjs.cloudflare.com/ajax/libs/SyntaxHighlighter/3.0.83/scripts/shBrushPlain.js",
	"https://cdnjs.cloudflare.com/ajax/libs/SyntaxHighlighter/3.0.83/scripts/shBrushCpp.min.js",
	"https://cdnjs.cloudflare.com/ajax/libs/SyntaxHighlighter/3.0.83/scripts/shBrushCSharp.min.js",
	"https://cdnjs.cloudflare.com/ajax/libs/SyntaxHighlighter/3.0.83/scripts/shBrushJava.min.js",
	"https://cdnjs.cloudflare.com/ajax/libs/SyntaxHighlighter/3.0.83/scripts/shBrushPython.min.js",
	"https://cdnjs.cloudflare.com/ajax/libs/SyntaxHighlighter/3.0.83/scripts/shBrushCss.min.js",
	"https://cdnjs.cloudflare.com/ajax/libs/SyntaxHighlighter/3.0.83/scripts/shBrushJScript.min.js",
	"https://cdnjs.cloudflare.com/ajax/libs/SyntaxHighlighter/3.0.83/scripts/shBrushPhp.min.js",
	
)

# 加载css
css_files = (
	"https://cdnjs.cloudflare.com/ajax/libs/SyntaxHighlighter/3.0.83/styles/shCore.min.css",
	"https://cdnjs.cloudflare.com/ajax/libs/SyntaxHighlighter/3.0.83/styles/shCoreEclipse.min.css",
	"https://cdnjs.cloudflare.com/ajax/libs/SyntaxHighlighter/3.0.83/styles/shThemeEclipse.min.css",
)

# 预处理器
class CodePreprocessor(Preprocessor):
	def run(self, lines): # lines里保存了每一行原始数据
		output = []       # 返回值
		in_code = False
		for line in lines:
			for key in converts :
				line = line.replace(key, converts[key])
				
			if line[:3]=='```':
				if in_code:
					line = "</pre>"
					in_code = False
				else:
					line = "<pre class='brush: %s;'>" % line[3:].strip()
					in_code = True
			
			# 这里有个bug
			# 通常情况下html标签包起来的内容，例如
			# <span>
			# #Hello
			# </span> 
			# markdown不进行渲染
			# 即#Hello不会被渲染成<h1>Hello</h1>
			# 但是当<span>上一行的内容被markdown渲染了的时候
			# 即使上一行有两个空格结尾，也会发生bug
			# 导致<span>内部的内容也被markdown渲染
			# 为了保证代码内容不变，避免代码内容被markdown渲染
			# 强制增加空行，躲开这个bug
			# 而空行会被markdown忽了
			# 故不影响其他行的渲染
			elif not in_code :
				line = line + "\n"
			
			output.append(line)
		return output

# 后处理器
class CodePostprocessor(Postprocessor):
	def run(self, text):
		return text

	
# 扩展类	
class CodeExtension(Extension):
	def __init__(self, configs={}):
		self.config = configs

	def extendMarkdown(self, md, md_globals):
		# 注册
		md.registerExtension(self)

		# 设置预处理器
		md.preprocessors.add('codepreprocessor',         # 给预处理器取个名字
							CodePreprocessor(md),        # 预处理器对象
							"<normalize_whitespace")     # 不知道是干嘛的

		# 设置后处理器
		md.postprocessors.add('codepostprocessor', CodePostprocessor(md), ">unescape")
	

# 将markdown渲染成html，强制使用UTF8编码
def mark2html(md_text) :
	myext = CodeExtension()
	return markdown.markdown(md_text, extensions=[myext]).encode("utf-8").decode("utf-8")
		
if __name__ == "__main__" :
	import sys
	import os
	if len(sys.argv) < 2 or len(sys.argv) > 3 :
		script = os.path.basename(sys.argv[0])
		print("Usage : %s <input> [output]" % script)
		print("        %s readme.md readme.html" % script)
		print("        %s mark.md" % script)
		quit(1)

		
	import markdown
	fp = open(sys.argv[1], encoding="utf-8")
	html = mark2html(fp.read())
	if len(sys.argv) == 2 :
		print(html)
	else :
		out = open(sys.argv[2], "w", encoding="utf-8")
		out.write("<html>\n<head>\n<meta charset='utf-8'/>\n")
		for css in css_files :
			out.write("<link href='%s' rel='stylesheet'/>\n" % css)
		for js in js_files :
			out.write("<script src='%s'></script>\n" % js)
		out.write("<script>SyntaxHighlighter.all()</script>\n")
		out.write("</head>\n<body>\n")
		out.write(html)
		out.write("\n</body>\n</html>")