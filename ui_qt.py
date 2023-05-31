from PyQt6.QtCore import QStandardPaths
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QFileDialog, QLabel
import sys


class SimpleApp(QWidget):
    def __init__(self, connector):
        super().__init__()
        self.initUI()
        self.connector = connector

    def initUI(self):
        layout = QVBoxLayout()

        self.inputField = QLineEdit()
        self.inputField.returnPressed.connect(self.on_submit)  # Add this line
        layout.addWidget(self.inputField)

        btn = QPushButton("Send", self)
        btn.clicked.connect(self.on_submit)
        layout.addWidget(btn)

        self.setLayout(layout)
        self.setWindowTitle("Midjourney Automation UI")
        self.show()

    def on_submit(self):
        self.process_prompt(self.inputField.text())
        self.inputField.clear()

    def process_prompt(self, input):
        print(f"\nProcessing: {input}", end="")
        self.connector.send_prompt_to_bot(input)


class FileDialogDemo(QWidget):
    def __init__(self, connector):
        super().__init__()
        self.setWindowTitle("Midjourney Automation UI")
        self.file_path = ''
        self.connector = connector

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel()
        layout.addWidget(self.label)

        self.label.setText(f'Selected File: {self.file_path}')
        self.btn_select = QPushButton("Select File")
        self.btn_select.clicked.connect(self.select_file)
        layout.addWidget(self.btn_select)

        self.btn_submit = QPushButton("Submit")
        self.btn_submit.clicked.connect(self.submit_file)
        layout.addWidget(self.btn_submit)
        self.show()

    def select_file(self):
        file_dialog = QFileDialog()
        self.file_path, _ = file_dialog.getOpenFileName(self, "Select File", QStandardPaths.writableLocation(QStandardPaths.StandardLocation.HomeLocation))
        self.label.setText(f'Selected File: {self.file_path}')

    def submit_file(self):
        if self.file_path:
            # call your file processing function here
            self.connector.send_file_to_bot(self.file_path)
            print(f'File submitted: {self.file_path}')
        else:
            print('No file selected.')

