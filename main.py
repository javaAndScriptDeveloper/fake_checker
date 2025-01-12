# Application initialization
import sys

from PyQt5.QtWidgets import QApplication

from singletons import manager
from ui.view import AppDemo

app = QApplication(sys.argv)
demo = AppDemo(manager)
demo.show()
sys.exit(app.exec_())