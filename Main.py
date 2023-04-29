import threading
import time

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QSystemTrayIcon, QMenu, QAction, \
    QMessageBox
import sys

from AdministratorControlPanel import AdministratorControlPanel
from RATConnection import RATClient, RATServer
from RATFunction.Echo import Echo
from RATFunction.RATFunction import Side
from RATFunction.RATFunctionRegistry import RATFunctionRegistry

function_classes = [Echo]

class SystemSelectionDialog(QWidget):
    def __init__(self):
        super().__init__()

        # create a vertical layout for the dialog
        self.layout = QVBoxLayout()

        # add a label to the layout
        self.label = QLabel("Which system will you be running?")
        self.layout.addWidget(self.label)

        # add two buttons to the layout
        self.admin_button = QPushButton("Administrator")
        self.admin_button.clicked.connect(self.select_administrator)
        self.layout.addWidget(self.admin_button)

        self.remote_button = QPushButton("Remote System")
        self.remote_button.clicked.connect(self.select_remote_system)
        self.layout.addWidget(self.remote_button)

        # set the layout for the dialog
        self.setLayout(self.layout)

        # set the window title and size
        self.setWindowTitle("System Selection")
        self.setFixedSize(300, 150)

    def select_administrator(self):
        print("User selected: Administrator")
        self.widget = AdministratorControlPanel(function_classes)
        self.widget.show()
        # self.close()

    def select_remote_system(self):

        self.remote_button.hide()
        self.admin_button.hide()
        self.label.setText("Running as Remote System")
        self.repaint()
        threading.Thread(target=self.run_remote_system, daemon=True).start()

    def run_remote_system(self):
        server = RATServer()
        server.listen(8888)

        registry = RATFunctionRegistry()
        for function_class in function_classes:
            registry.add_function(function_class(Side.REMOTE_SIDE, server.packet_queue))

        server.packet_callback = registry.route_packet

        server.listen_for_packets()








if __name__ == "__main__":

    # create an instance of the dialog and show it
    app = QApplication(sys.argv)
    dialog = SystemSelectionDialog()
    dialog.show()

    # start the application event loop
    sys.exit(app.exec_())
