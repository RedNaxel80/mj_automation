import wx
import wx.xrc
from PyQt6.QtCore import QStandardPaths
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QFileDialog, QLabel
import sys

import ui_qt
import ui_wx


class UIType:
	QT = 0
	WX = 1


UI_TYPE = UIType.QT


class UI:
	def __init__(self, connector):
		self.connector = connector
		self.ui = UI_TYPE
		self.start(self.connector)

	def start(self, connector):
		if self.ui == UIType.QT:
			self.start_qt(connector)
		elif self.ui == UIType.WX:
			self.start_wx(connector)

	def start_qt(self, connector):
		# self.ui_qt.start()  # # maybe there's a way to start this within the QT UI class
		# app = QApplication([])
		# demo = FileDialogDemo(connector)
		# app.exec()

		app = QApplication(sys.argv)
		ex = ui_qt.SimpleApp(connector)
		sys.exit(app.exec())

	def start_wx(self, connector):
		# self.ui_wx.start()  # maybe there's a way to start this within the WX UI class
		app = wx.App(False)
		frame = ui_wx.MyFrame2(connector)
		frame.Show(True)
		app.MainLoop()
