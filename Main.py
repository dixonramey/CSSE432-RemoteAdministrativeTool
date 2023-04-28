from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
import sys
import socket


class SystemSelectionDialog(QWidget):
    def __init__(self):
        super().__init__()

        # create a vertical layout for the dialog
        layout = QVBoxLayout()

        # add a label to the layout
        label = QLabel("Which system will you be running?")
        layout.addWidget(label)

        # add two buttons to the layout
        admin_button = QPushButton("Administrator")
        admin_button.clicked.connect(self.select_administrator)
        layout.addWidget(admin_button)

        remote_button = QPushButton("Remote System")
        remote_button.clicked.connect(self.select_remote_system)
        layout.addWidget(remote_button)

        # set the layout for the dialog
        self.setLayout(layout)

        # set the window title and size
        self.setWindowTitle("System Selection")
        self.setFixedSize(300, 150)

    def select_administrator(self):
        print("User selected: Administrator")
        self.close()

    def select_remote_system(self):
        print("User selected: Remote System")
        self.close()


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # create an instance of the dialog and show it
    app = QApplication(sys.argv)
    dialog = SystemSelectionDialog()
    dialog.show()

    # start the application event loop
    sys.exit(app.exec_())
