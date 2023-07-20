import ctypes,sys,os,time
class res():
	author, myappid = "Author:Loryhx", "Version 1.0.0.0" # 这里可以设置任意文本
	ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid) 	# 同步更改任务栏图标
	#生成资源文件目录访问路径
	def path(base_path):
		# if getattr(sys, "frozen", True): # 是否Bundle Resource
		# 	dir_path = os.path.join(os.path.expandvars("%WINDIR%\\Temp"), "onefile_wifivewer")
		# 	# dir_path = sys.executable
		# 	# dir_path = sys._MEIPASS
		# else:
		# 	# dir_path = os.path.dirname(__file__)
		# 	# dir_path = os.path.dirname(sys.argv[0])
		# 	dir_path = os.path.abspath(".")
		dir_path = os.path.abspath(".")
		return os.path.join(dir_path, base_path)

# 	def path(relative_path):
# 		if hasattr(sys, "frozen"):
# 			base_path = sys.executable
# 			return os.path.join(base_path, relative_path) # 使用打包后的exe目录
# 		return os.path.join(os.path.dirname(__file__), relative_path)		   # 没打包前的py目录


# print(os.path.dirname(sys.executable))
# print(res.path("res\\win.ico"))