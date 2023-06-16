from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QTextEdit, QPushButton, QFrame, QFileDialog, QStatusBar, QLineEdit, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, QSize
import config


class MainWindow(QMainWindow):
    def __init__(self, connector, parent=None):
        super(MainWindow, self).__init__(parent)
        # super().__init__(parent)
        self.connector = connector
        print(connector)
        self.connector = connector
        self.prompts_file_name = ""
        self.download_path = config.DOWNLOAD_FOLDER
        self.setWindowTitle("Mj automator")
        self.setFixedSize(500, 430)

        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        layout = QVBoxLayout(centralWidget)

        self.label_prompt_input = QLabel("Write the prompt:", self)
        layout.addWidget(self.label_prompt_input)

        self.input_prompt = QTextEdit("prompt...", self)
        self.input_prompt.setFixedHeight(100)
        layout.addWidget(self.input_prompt)

        self.button_submit_prompt = QPushButton("Process", self)
        self.button_submit_prompt.setEnabled(False)
        layout.addWidget(self.button_submit_prompt)

        self.separator = QFrame(self)
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setFixedHeight(10)
        layout.addWidget(self.separator)

        self.label_file_import = QLabel("or select a text file with prepared prompts:", self)
        layout.addWidget(self.label_file_import)

        browse_layout = QHBoxLayout()
        self.button_browse = QPushButton("Browse", self)
        browse_layout.addWidget(self.button_browse)
        self.m_filePicker2 = QFileDialog(self)
        self.m_filePicker2.setEnabled(False)
        self.m_filePicker2.hide()

        self.button_file_import = QPushButton("Import and process", self)
        self.button_file_import.setEnabled(False)
        browse_layout.addWidget(self.button_file_import)
        layout.addLayout(browse_layout)

        self.separator1 = QFrame(self)
        self.separator1.setFrameShape(QFrame.Shape.HLine)
        self.separator1.setFixedSize(QSize(10, 10))
        layout.addWidget(self.separator1)

        self.label_download_location = QLabel("Your files will be downloaded to this location: ", self)
        layout.addWidget(self.label_download_location)

        self.input_download_location = QLineEdit(config.DOWNLOAD_FOLDER, self)
        self.input_download_location.setEnabled(False)
        layout.addWidget(self.input_download_location)

        folder_layout = QHBoxLayout()
        self.button_open_folder = QPushButton("Open this folder", self)
        folder_layout.addWidget(self.button_open_folder)
        self.button_change_folder = QPushButton("Change location", self)
        folder_layout.addWidget(self.button_change_folder)
        layout.addLayout(folder_layout)

        layout.addSpacing(10)

        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Bot: status   Jobs queued: 0, running: 0, done: 0")

        # Connect Events
        self.input_prompt.textChanged.connect(self.ProcessTextEventFromInput)
        self.button_submit_prompt.clicked.connect(self.SendPrompt)
        self.button_browse.clicked.connect(self.BrowseForFile)
        self.button_file_import.clicked.connect(self.ImportPromptFile)
        self.button_open_folder.clicked.connect(self.OpenDownloadsFolder)
        self.button_change_folder.clicked.connect(self.ChangeDownloadsFolder)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.UpdateStatus)
        self.timer.start(1000)

    def ProcessTextEventFromInput(self):
        pass

    def SendPrompt(self):
        pass

    def BrowseForFile(self):
        pass

    def ImportPromptFile(self):
        pass

    def OpenDownloadsFolder(self):
        pass

    def ChangeDownloadsFolder(self):
        pass

    def UpdateStatus(self):
        pass


def start(connector):
    app = QApplication([])
    window = MainWindow(connector)
    window.show()
    app.exec()

# def select_file(self):
#     file_dialog = QFileDialog()
#     self.file_path, _ = file_dialog.getOpenFileName(self, "Select File", QStandardPaths.writableLocation(QStandardPaths.StandardLocation.HomeLocation))
#     self.label.setText(f'Selected File: {self.file_path}')
#
# def submit_file(self):
#     if self.file_path:
#         # call your file processing function here
#         self.connector.send_file_to_bot(self.file_path)
#         print(f'File submitted: {self.file_path}')
#     else:
#         print('No file selected.')
#
