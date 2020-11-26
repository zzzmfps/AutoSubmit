from PySide2.QtCore import Signal

from ui.basic import BasicDialog, BasicWidget


class CreateWindow(BasicWidget):
    ''' Define behaviour of file->create window.
    '''
    def __init__(self) -> None:
        super().__init__()
        self.ui_path = 'assets/ui/create.ui'

    def set_handlers(self) -> None:
        self.win.content.textChanged.connect(self.__handle_text_changed)

    def __handle_text_changed(self) -> None:
        pass


class JumpWindow(BasicDialog):
    ''' Define behaviour of file->quit window.
    '''
    force_quit = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.ui_path = 'assets/ui/quit.ui'


class ConvertWindow(BasicWidget):
    ''' Define behaviour of file->convert window.
    '''
    def __init__(self) -> None:
        super().__init__()
        self.ui_path = 'assets/ui/convert.ui'


class QuitWindow(BasicDialog):
    ''' Define behaviour of file->quit window.
    '''
    force_quit = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.ui_path = 'assets/ui/quit.ui'

    def set_handlers(self) -> None:
        self.win.btn_quit.clicked.connect(self.__handle_quit)
        self.win.btn_cancel.clicked.connect(self.win.close)

    def __handle_quit(self) -> None:
        self.force_quit.emit()


if __name__ == "__main__":
    pass
