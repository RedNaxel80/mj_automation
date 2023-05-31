import wx
import wx.xrc


# -*- coding: utf-8 -*-

###########################################################################
# Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b)
# http://www.wxformbuilder.org/
#
# PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

class MyFrame2(wx.Frame):

    def __init__(self, connector, parent=None):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"Midjourney Automation UI", pos=wx.DefaultPosition,
                          size=wx.Size(500, 300), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        fgSizer2 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer2.SetFlexibleDirection(wx.BOTH)
        fgSizer2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button(self, wx.ID_OK)
        m_sdbSizer1.AddButton(self.m_sdbSizer1OK)
        self.m_sdbSizer1Cancel = wx.Button(self, wx.ID_CANCEL)
        m_sdbSizer1.AddButton(self.m_sdbSizer1Cancel)
        m_sdbSizer1.Realize()

        fgSizer2.Add(m_sdbSizer1, 1, wx.EXPAND, 5)

        self.SetSizer(fgSizer2)
        self.Layout()

        self.Centre(wx.BOTH)

    def __del__(self):
        pass

    # Virtual event handlers, override them in your derived class
    def call_this_function(self, event):
        event.Skip()

    def start(self):
        app = wx.App(False)
        frame = MyFrame2(None)
        frame.Show(True)
        app.MainLoop()
