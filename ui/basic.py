from typing import Union

from PySide2.QtCore import QFile
from PySide2.QtGui import Qt
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QDialog, QMainWindow, QWidget


class WidgetUtil:
    ''' A utility class contains common methods used by Qt-related classes.
    '''
    @staticmethod
    def load_window(ui_path: str) -> Union[QWidget, QDialog, QMainWindow]:
        qfile = QFile(ui_path)
        qfile.open(QFile.ReadOnly)
        qfile.close()
        return QUiLoader().load(qfile)


class BasicWidget(QWidget):
    ''' Define basic behaviour of widgets.
    '''
    def __init__(self) -> None:
        super().__init__()
        self.win = None
        self.ui_path = ''

    def run(self) -> None:
        if self.win is None: self.win = WidgetUtil.load_window(self.ui_path)
        self.set_attributes()
        if not self.win.isVisible(): self.win.show()
        self.set_init_values()
        self.set_handlers()

    def set_attributes(self) -> None:
        pass

    def set_init_values(self) -> None:
        pass

    def set_handlers(self) -> None:
        pass


class BasicDialog(QDialog):
    ''' Define basic behaviour of dialogs.
    '''
    def __init__(self) -> None:
        super().__init__()
        self.win = None
        self.ui_path = ''

    def run(self) -> None:
        if self.win is None: self.win = WidgetUtil.load_window(self.ui_path)
        self.set_attributes()
        if not self.win.isVisible(): self.win.show()
        self.set_handlers()

    def set_attributes(self) -> None:
        self.win.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)

    def set_handlers(self) -> None:
        pass


class BasicWindow(QMainWindow):
    ''' Define basic behaviour of windows. Should be unique.
    '''
    def __init__(self) -> None:
        self.app = QApplication([])
        super().__init__()
        self.win = None
        self.ui_path = ''
        self.is_running = False

    def run(self) -> None:
        if self.win is None: self.win = WidgetUtil.load_window(self.ui_path)
        self.set_attributes()
        if not self.win.isVisible(): self.win.show()
        self.set_init_values()
        self.set_handlers()

    def set_attributes(self) -> None:
        pass

    def set_init_values(self) -> None:
        pass

    def set_handlers(self) -> None:
        pass


if __name__ == '__main__':
    pass
