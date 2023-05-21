import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox

class SimpleApp(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize the window
        self.initUI()

    def initUI(self):
        # Create a QVBoxLayout
        layout = QVBoxLayout()

        # Create a QLabel
        self.label = QLabel('Enter your name:')
        layout.addWidget(self.label)

        # Create a QLineEdit
        self.line_edit = QLineEdit()
        self.line_edit.returnPressed.connect(self.show_message)  # Connect the returnPressed signal
        layout.addWidget(self.line_edit)

        # Create a QPushButton
        self.button = QPushButton('Submit')
        self.button.clicked.connect(self.show_message)
        layout.addWidget(self.button)

        # Set the layout
        self.setLayout(layout)

        # Set the window properties
        self.setGeometry(300, 300, 200, 150)
        self.setWindowTitle('Simple PyQt6 App')
        self.show()

    def show_message(self):
        # Show a message box when the button is clicked
        QMessageBox.information(self, 'Message', f'Hello, {self.line_edit.text()}!')


def main():
    app = QApplication(sys.argv)

    ex = SimpleApp()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
