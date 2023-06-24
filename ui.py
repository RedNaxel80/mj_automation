# import ui_qt
# import ui_wx
import ui_flask


class UIType:
	QT = 0
	WX = 1
	FLASK = 2


UI_TYPE = UIType.FLASK


class UI:
	def __init__(self, connector, port=5000):
		self.port = port
		self.connector = connector
		self.ui = UI_TYPE
		self.start(self.connector)

	def start(self, connector):
		self.start_flask(connector, self.port)
		# if self.ui == UIType.QT:
		# 	self.start_qt(connector)
		# elif self.ui == UIType.WX:
		# 	self.start_wx(connector)
		# elif self.ui == UIType.FLASK:
		# 	self.start_flask(connector, self.port)

	# def start_qt(self, connector):
	# 	ui_qt.start(connector)
	#
	# def start_wx(self, connector):
	# 	ui_wx.start(connector)

	def start_flask(self, connector, port):
		ui_flask.start(connector, port)
