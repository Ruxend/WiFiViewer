# -*- coding: utf-8 -*-
#-*- coding:utf-8 -*-
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import (QTextCursor,QColor,QPalette)
from PyQt5.QtCore import (QThread,pyqtSignal)
from random import randint
import subprocess as sub
import os,time,webbrowser,re
from urllib import parse
from ui_WiFiViewer import ui_WiFiViewer

class WorkThread_WiFiViewer(QThread):
	# 使用信号和UI主线程通讯，参数是发送信号时附带参数的数据类型，可以是str、int、list等
	finishSignal = pyqtSignal()
	signal_name = pyqtSignal(str, str)
	signal_key = pyqtSignal(str, str)
	signal_err = pyqtSignal(str)
	signal_conn_succ = pyqtSignal(str)
	signal_conn_fail = pyqtSignal(str)
	signal_net_del = pyqtSignal(str)
	signal_else = pyqtSignal(str)
	# signal_1 = pyqtSignal(str)
	# signal_2 = pyqtSignal(str)
	def __init__(self, command, parent=None):
		super().__init__(parent)
		self.cmd = command

	def run(self, msg_in=""):
		try:
			proc = sub.Popen(self.cmd.decode("gbk"),
							shell=True,
							stdin=sub.PIPE,
							stdout=sub.PIPE,
							stderr=sub.PIPE,
							)
			stdout_value , stderr_value = proc.communicate(input=msg_in)
			stdout_value = stdout_value.decode("gbk", "ignore")
			stderr_value = stderr_value.decode("gbk", "ignore")
			if "组策略配置文件" in stdout_value:
				self.signal_name.emit(stdout_value, stderr_value)
			elif "配置文件信息" in stdout_value:
				self.signal_key.emit(stdout_value, stderr_value)
			elif "已成功完成连接请求" in stdout_value:
				self.signal_conn_succ.emit(stdout_value)
			elif "指定的网络无法用于连接" in stdout_value:
				self.signal_conn_fail.emit(stdout_value)
			elif "已从接口“WLAN”中删除配置文件" in stdout_value:
				self.signal_net_del.emit(stdout_value)
			else:
				print(stdout_value)
				self.signal_else.emit(stdout_value)
			return
		except Exception as e:
			self.signal_err.emit(f"{e}")
		# except ValueError as err:
		# 	# log("ValueError: %s" % err)
		# 	# print(err)
		# 	self.signal_1.emit(err)
		# 	return
		# except IOError as err:
		# 	# log("IOError: %s" % err)
		# 	self.signal_2.emit(err)
			return
		self.finishSignal.emit()  		# 发射程序结束输出

# cmd = "netsh wlan show profiles name=\"锦轩宾馆\" key=clear".encode("gbk")
# cmd = "netsh wlan connect name=\"1807-1\"".encode("gbk")
# cmd = f"netsh wlan delete profile name=\"1807-1\"".encode("gbk")
# WorkThread_WiFiViewer(cmd).run()