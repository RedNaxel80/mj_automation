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


UI_TYPE = UIType.WX


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
		ui_qt.start(connector)

	def start_wx(self, connector):
		ui_wx.start(connector)
