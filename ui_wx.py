import wx
import wx.xrc
import os
import subprocess
import platform
import config
import sys


# -*- coding: utf-8 -*-


class MainWindow(wx.Frame):
    def __init__(self, parent, connector):
        self.connector = connector
        self.prompts_file_name = ""  # this is the path to the file to be processed
        self.download_path = config.DOWNLOAD_FOLDER

        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"Mj automator", pos=wx.DefaultPosition,
                          size=wx.Size(500, 430), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL,
                          name=u"Midjourney Automation")

        self.SetSizeHints(wx.Size(300, 430), wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.label_prompt_input = wx.StaticText(self, wx.ID_ANY, u"Write the prompt:", wx.DefaultPosition,
                                                wx.DefaultSize, 0)
        self.label_prompt_input.Wrap(-1)

        self.label_prompt_input.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))

        bSizer1.Add(self.label_prompt_input, 0, wx.ALL, 5)

        self.input_prompt = wx.TextCtrl(self, wx.ID_ANY, u"prompt...", wx.DefaultPosition, wx.Size(-1, 100),
                                        wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)
        bSizer1.Add(self.input_prompt, 0, wx.ALL | wx.EXPAND, 5)

        self.button_submit_prompt = wx.Button(self, wx.ID_ANY, u"Process", wx.DefaultPosition, wx.DefaultSize, 0)
        self.button_submit_prompt.Enable(False)

        bSizer1.Add(self.button_submit_prompt, 0, wx.ALL, 5)

        self.separator = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(-1, 10), wx.LI_HORIZONTAL)
        self.separator.SetMinSize(wx.Size(-1, 10))

        bSizer1.Add(self.separator, 0, wx.EXPAND | wx.ALL, 5)

        self.label_file_import = wx.StaticText(self, wx.ID_ANY, u"or select a text file with prepared prompts:",
                                               wx.DefaultPosition, wx.DefaultSize, 0)
        self.label_file_import.Wrap(-1)

        self.label_file_import.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))

        bSizer1.Add(self.label_file_import, 0, wx.ALL, 5)

        bSizer4 = wx.BoxSizer(wx.VERTICAL)

        bSizer6 = wx.BoxSizer(wx.HORIZONTAL)

        self.button_browse = wx.Button(self, wx.ID_ANY, u"Browse", wx.DefaultPosition, wx.DefaultSize, 0)

        self.button_browse.SetBitmapFocus(wx.NullBitmap)
        bSizer6.Add(self.button_browse, 0, wx.ALL, 5)

        self.m_filePicker2 = wx.FilePickerCtrl(self, wx.ID_ANY, u"/Volumes/Data/Desktop/untitled2.txt",
                                               u"Select a file", u"TXT files (*.txt)|*.txt|CSV files (*.csv)|*.csv",
                                               wx.DefaultPosition, wx.DefaultSize, wx.FLP_FILE_MUST_EXIST | wx.FLP_OPEN)
        self.m_filePicker2.Enable(False)
        self.m_filePicker2.Hide()

        bSizer6.Add(self.m_filePicker2, 0, wx.ALL, 5)

        self.button_file_import = wx.Button(self, wx.ID_ANY, u"Import and process", wx.DefaultPosition, wx.DefaultSize,
                                            0)
        self.button_file_import.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNTEXT))
        self.button_file_import.Enable(False)

        bSizer6.Add(self.button_file_import, 0, wx.ALL, 5)

        bSizer4.Add(bSizer6, 1, wx.EXPAND, 5)

        self.separator1 = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(-1, 10), wx.LI_HORIZONTAL)
        self.separator1.SetMinSize(wx.Size(-1, 10))
        self.separator1.SetMaxSize(wx.Size(-1, 10))

        bSizer4.Add(self.separator1, 0, wx.EXPAND | wx.ALL, 5)

        self.label_download_location = wx.StaticText(self, wx.ID_ANY,
                                                     u"Your files will be downloaded to this location: ",
                                                     wx.DefaultPosition, wx.DefaultSize, 0)
        self.label_download_location.Wrap(-1)

        self.label_download_location.SetForegroundColour(wx.Colour(108, 108, 108))

        bSizer4.Add(self.label_download_location, 0, wx.ALL, 5)

        self.input_download_location = wx.TextCtrl(self, wx.ID_ANY, u"/Volumes/Data/Dropbox/midjourney/test",
                                                   wx.DefaultPosition, wx.DefaultSize, 0)
        self.input_download_location.Enable(False)

        bSizer4.Add(self.input_download_location, 0, wx.ALL | wx.EXPAND, 5)

        bSizer8 = wx.BoxSizer(wx.HORIZONTAL)

        self.button_open_folder = wx.Button(self, wx.ID_ANY, u"Open this folder", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer8.Add(self.button_open_folder, 0, wx.ALL, 5)

        self.button_change_folder = wx.Button(self, wx.ID_ANY, u"Change location", wx.DefaultPosition, wx.DefaultSize,
                                              0)
        bSizer8.Add(self.button_change_folder, 0, wx.ALL, 5)

        bSizer4.Add(bSizer8, 1, wx.EXPAND, 5)

        bSizer1.Add(bSizer4, 1, wx.EXPAND, 5)

        bSizer1.Add((0, 10), 1, wx.EXPAND, 5)

        self.SetSizer(bSizer1)
        self.Layout()
        self.statusbar = self.CreateStatusBar(2, wx.STB_DEFAULT_STYLE | wx.STB_SIZEGRIP, wx.ID_ANY)
        self.menubar = wx.MenuBar(0)
        self.SetMenuBar(self.menubar)

        self.Centre(wx.BOTH)

        # Connect Events
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.input_prompt.Bind(wx.EVT_KILL_FOCUS, self.OnLoseFocus)
        self.input_prompt.Bind(wx.EVT_SET_FOCUS, self.OnFocus)
        self.input_prompt.Bind(wx.EVT_TEXT, self.ProcessTextEventFromInput)
        self.input_prompt.Bind(wx.EVT_TEXT_ENTER, self.PromptGotEnterKey)
        self.button_submit_prompt.Bind(wx.EVT_BUTTON, self.SendPrompt)
        self.button_browse.Bind(wx.EVT_BUTTON, self.BrowseForFile)
        self.button_file_import.Bind(wx.EVT_BUTTON, self.ImportPromptFile)
        self.button_open_folder.Bind(wx.EVT_BUTTON, self.OpenDownloadsFolder)
        self.button_change_folder.Bind(wx.EVT_BUTTON, self.ChangeDownloadsFolder)

        self.separator.SetFocus()
        self.statusbar.SetFieldsCount(2)
        self.statusbar.SetStatusWidths([-1, -2])

        # Set messages in the additional sections
        self.statusbar.SetStatusText("Bot: status", 0)
        self.statusbar.SetStatusText(f"Jobs queued: 0, running: 0, done: 0", 1)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.UpdateStatus, self.timer)
        self.timer.Start(1000)

    def __del__(self):
        pass

    def OnClose(self, event):
        self.connector.bot.stop()
        self.Destroy()

    def IsBotRunning(self):
        if self.connector.bot.status in (self.connector.bot.Status.READY, self.connector.bot.Status.PROCESSING):
            return True
        else:
            return False

    def UpdateStatus(self, event):
        if self.connector.bot:
            self.statusbar.SetStatusText(f"Bot: {self.connector.bot.status}", 0)
            self.statusbar.SetStatusText(f"Jobs queued: {self.connector.bot.job_manager.get_queue_count() or 0}, "
                                         f"running: {self.connector.bot.job_manager.running_jobs or 0}, "
                                         f"done: {self.connector.bot.job_manager.completed_jobs or 0}", 1)
        else:
            self.statusbar.SetStatusText(f"Bot: {self.connector.bot.Status.ERROR}", 0)
            self.statusbar.SetStatusText(f"Jobs queued: -, "
                                         f"running: -, "
                                         f"done: -", 1)
        event.Skip()

    def ProcessTextEventFromInput(self, event):
        if not self.IsBotRunning():
            return
        prompt = self.input_prompt.GetValue()
        if prompt != "prompt..." and prompt != "":
            self.SendPromptEnable(event)
        else:
            self.SendPromptDisable(event)
        event.Skip()

    def SendPromptEnable(self, event):
        self.button_submit_prompt.Enable()
        event.Skip()

    def SendPromptDisable(self, event):
        self.button_submit_prompt.Disable()
        event.Skip()

    def PromptGotEnterKey(self, event):
        self.SendPrompt(event)

    def SendPrompt(self, event):
        if not self.IsBotRunning():
            return

        prompt = self.input_prompt.GetValue()
        if prompt == "prompt..." or prompt == "":
            return

        self.connector.send_prompt_to_bot(prompt)
        self.input_prompt.Clear()
        # self.input_prompt.SetValue("prompt...")
        self.button_submit_prompt.Disable()

    def ImportPromptFile(self, event):
        if not self.prompts_file_name or not self.IsBotRunning():
            return

        self.connector.send_file_to_bot(self.prompts_file_name)
        self.prompts_file_name = ""
        event.Skip()

    def OnFocus(self, event):
        if self.input_prompt.GetValue() == "prompt...":
            self.input_prompt.Clear()
        event.Skip()

    def OnLoseFocus(self, event):
        if self.input_prompt.GetValue() == "":
            self.input_prompt.SetValue("prompt...")
        event.Skip()

    def BrowseForFile(self, event):
        with wx.FileDialog(self, "Open file", wildcard="TXT files (*.txt)|*.txt|CSV files (*.csv)|*.csv",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # Proceed loading the file chosen by the user
            self.prompts_file_name = fileDialog.GetPath()
            self.button_file_import.Enable()
            # self.file_path.SetValue(pathname)
        event.Skip()

    def OpenDownloadsFolder(self, event):
        dir_path = os.path.dirname(self.download_path + "/")
        subprocess.Popen(["open", dir_path])

        # determine the system type and run the appropriate command
        if platform.system() == 'Windows':
            os.startfile(dir_path)
        elif platform.system() == 'Darwin':
            subprocess.Popen(['open', dir_path])
        else:
            try:
                subprocess.Popen(['xdg-open', dir_path])
            except OSError:
                pass  # xdg-open didn't work, no other idea for Linux, just do nothing
        event.Skip()

    def ChangeDownloadsFolder(self, event):
        dialog = wx.DirDialog(None, "Choose downloads folder:", defaultPath=self.download_path,
                              style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            self.input_download_location.SetValue(dialog.GetPath())
            # send this to settings manager to change actual folder
        dialog.Destroy()


def start(connector):
    app = wx.App(False)
    frame = MainWindow(None, connector)
    frame.Show(True)
    app.MainLoop()
