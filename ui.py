from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit
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

