# -*- coding: utf-8 -*-
#-*- coding:utf-8 -*-
from PyQt5.QtWidgets import (QApplication,QMainWindow,QDockWidget,QWidget,QFrame,QLabel,
						QLineEdit,QTextEdit,QPushButton,QDialog,QSlider,QMessageBox,
						QInputDialog,QFileDialog,QFontDialog,QColorDialog,QToolBar,
						QMenuBar,QStatusBar,QGroupBox,QGridLayout,QHBoxLayout,QVBoxLayout,
						QFormLayout,QListWidget,QScrollBar,QDesktopWidget,QProgressBar,
						QShortcut,QMenu,QAction)
from PyQt5.QtGui import (QFont,QIcon,QPixmap,QColor,QTextCursor,QPalette,QKeySequence,QCursor)
from PyQt5.QtCore import (Qt,QFile,QTimer,QDateTime,QThread,pyqtSignal,QBasicTimer,QObject,
						QCoreApplication,QModelIndex,QPoint)
# from PyQt5.QtMultimedia import QAudioInput,QAudioOutput,QAudioDeviceInfo
import subprocess as sub
import win32clipboard as cb
import msvcrt,os,sys,time,re,win32api,win32con,locale
from res import res
from random import randint
# from eth import eth
# from xlwt_style import style
from ui_WiFiViewer import ui_WiFiViewer
from threads_WiFiViewer import WorkThread_WiFiViewer

class myWidget_WiFiViewer(QMainWindow, ui_WiFiViewer):
	signal_child_3 = pyqtSignal()
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setupUi(self)
		self.btn_1_clicked()
		self.list.clicked.connect(self.list_clicked) 		# 连接槽
		self.list.doubleClicked.connect(self.list_doubleclicked) 	# 连接槽
		self.btn_1.clicked.connect(self.btn_1_clicked) 		# 连接槽
		self.btn_2.clicked.connect(self.btn_2_clicked) 		# 连接槽
		# self.btn_confirm.clicked.connect(self.confirm)			# 连接槽
		# QShortcut(QKeySequence("Return"), self, self.confirm)
		self.btn_quit.clicked.connect(self.close)					# 连接槽
		QShortcut(QKeySequence("Escape"), self, self.close)

	def btn_1_clicked(self):
		command = "netsh wlan show profiles".encode("gbk")
		try:
			self.work_start(cmd=command)
		except Exception as e:
			QMessageBox.information(self, "Exception", f"{e}")

	def btn_2_clicked(self):
		aString = self.entry_2.text()
		# set_clipboard(aString)
		try:
			cb.OpenClipboard()
			cb.EmptyClipboard()
			cb.SetClipboardData(cb.CF_UNICODETEXT, aString)
		finally:
			cb.CloseClipboard()
		self.statusbar.showMessage(f"状态: 已复制到剪切板!", 15000)
		msg = QMessageBox.information(self, "Infomation", "已复制到剪切板!", QMessageBox.Ok)
		if msg == QMessageBox.Ok:
			self.statusbar.showMessage("", 1000)

	def list_clicked(self, QModelIndex):
		self.entry_2.clear()
		ssid = self.wifilist[QModelIndex.row()]	# Method_1
		# ssid = self.list.selectionModel().selectedIndexes()[0].date()	# Methon_2
		self.entry_1.setText(ssid)
		command = f"netsh wlan show profiles name=\"{ssid}\" key=clear".encode("gbk")
		try:
			self.work_start(cmd=command)
		except Exception as e:
			QMessageBox.warning(self, "Exception", f"{e}")

	def list_doubleclicked(self):
		wifiname = self.entry_1.text()
		command = f"netsh wlan connect name=\"{wifiname}\"".encode("gbk")
		try:
			self.work_start(cmd=command)
		except Exception as e:
			QMessageBox.warning(self, "Exception", f"{e}")

	def list_selection_forget(self):
		name = self.entry_1.text()
		command = f"netsh wlan delete profile name=\"{name}\"".encode("gbk")
		try:
			self.work_start(cmd=command)
		except Exception as e:
			QMessageBox.warning(self, "Exception", f"{e}")

	# def confirm(self):
	# 	self.entry_1_value = self.entry_1.text()
	# 	if self.entry_1_value=="":
	# 		self.list.append("----------Oops！Please Input All Necessary Parameters！----------\n")
	# 		self.refresh_color()
	# 		self.statusbar.showMessage("请输入必要参数!", 1000)
	# 	else:
	# 		try:
	# 			self.work_start()
	# 		except Exception as e:
	# 			QMessageBox.infomation(self, "Quit", e)

	def work_start(self, cmd):
		self.statusbar.showMessage("状态: 请稍等,正在处理...", 3600000)
		self.thread = WorkThread_WiFiViewer(command=cmd)
		# 将线程th的信号finishSignal和UI主线程中的槽函数button_finish进行连接
		self.thread.finishSignal.connect(self.work_finish)
		self.thread.signal_name.connect(self.signal_name_call)
		self.thread.signal_key.connect(self.signal_key_call)
		self.thread.signal_conn_succ.connect(self.signal_conn_succ_call)
		self.thread.signal_conn_fail.connect(self.signal_conn_fail_call)
		self.thread.signal_net_del.connect(self.signal_net_del_call)
		self.thread.signal_err.connect(self.signal_err_call)
		# self.thread.signal_1.connect(self.signal_1_call)
		# self.thread.signal_2.connect(self.signal_2_call)
		self.thread.start()  				# 启动线程

	def signal_name_call(self, stdout_value, stderr_value):
		# wifilist = re.findall(r"[:](.*?)[\r\n]", stdout_value)
		wifilist = re.findall(r"(?<=: )(.*?)(?=\n)", stdout_value)
		self.wifilist = [s.strip() for s in wifilist if s.strip("\r") != ""]
		self.slm.setStringList(self.wifilist)	# 绑定数据源
		self.statusbar.showMessage(f"状态: 列表刷新成功!", 5000)

	def signal_key_call(self, stdout_value, stderr_value):
		if "关键内容" in stdout_value:
			# self.entry_2.setText(re.search(r"关键内容(.*)[\r]", stdout_value).group().split(":")[1][1:-1])#.split("\r")[0])
			self.entry_2.setText(re.search(r"(?<=关键内容            : )(.*?)(?=\n)", stdout_value).group().strip("\r\n"))
		else:
			self.entry_2.setText("无密码")
		self.work_finish()

	def signal_conn_succ_call(self, stdout_value):
		self.statusbar.showMessage(f"状态: 处理完成, 连接成功!", 5000)
		QMessageBox.information(self, "Information", f"处理完成, 连接成功!\n{stdout_value}", QMessageBox.Ok, QMessageBox.Ok)
		self.statusbar.showMessage("")

	def signal_conn_fail_call(self, stdout_value):
		self.statusbar.showMessage(f"状态: 处理完成, 连接失败!", 5000)
		QMessageBox.warning(self, "Warning", f"发生异常, 连接失败!\nException详情: {stdout_value}", QMessageBox.Ok, QMessageBox.Ok)
		self.statusbar.showMessage("")

	def signal_net_del_call(self, stdout_value):
		self.statusbar.showMessage(f"状态: 已删除该网络配置文件!", 5000)
		QMessageBox.information(self, "Information", f"处理完成, 执行成功!\n{stdout_value}", QMessageBox.Ok, QMessageBox.Ok)
		self.statusbar.showMessage("")

	def signal_err_call(self, err):
		self.statusbar.showMessage(f"状态: 发生异常, 获取失败!", 5000)
		QMessageBox.warning(self, "Exception", f"发生异常, 获取失败!\nException详情: {err}", QMessageBox.Ok, QMessageBox.Ok)
		self.statusbar.showMessage("")

	# def signal_1_call(self):
	# 	self.entry_1.setText(text_1)

	# def signal_2_call(self):
	# 	self.entry_2.setText(text_2)

	def work_finish(self):
		self.statusbar.showMessage(f"状态: 处理完成, 执行成功!", 5000)

	# 每一个QObject对象或其子对象都有一个QObject.timerEvent方法
	# 为了响应定时器的超时事件，需要重写进度条的timerEvent方法
	def closeEvent(self, event):
		"""重写该方法使用sys.exit(0) 时就会只要关闭了主窗口，所有关联的子窗口也会全部关闭"""
		reply = QMessageBox.question(self, "Quit", "Do you want to quit ?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		if reply == QMessageBox.Yes:
			event.accept()
			self.signal_child_3.emit()
		else:
			event.ignore()

if __name__ == "__main__":
	QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)	# 适应高分辨率屏幕
	app = QApplication(sys.argv)
	window = myWidget_WiFiViewer()
	window.show()
	sys.exit(app.exec())
