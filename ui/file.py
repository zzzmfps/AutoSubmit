from PySide2.QtCore import Signal
from PySide2.QtWidgets import QFileDialog
from util.data import JsonUtil, ValidateUtil

from ui.basic import BasicDialog, BasicWidget


class CreateWindow(BasicWidget):
    ''' Define behaviour of file->create window.
    '''
    class JumpWindow(BasicDialog):
        ''' Define behaviour of file->create->jump window.
        '''
        ask_jump = Signal(bool)

        def __init__(self) -> None:
            super().__init__('assets/ui/jump_to_convert.ui')

        def set_handlers(self) -> None:
            self.win.btn_jump.clicked.connect(self.__handle_jump)
            self.win.btn_cancel.clicked.connect(self.__handle_cancel)

        # handlers
        def __handle_jump(self) -> None:
            self.__handle_decide_jump(True)

        def __handle_cancel(self) -> None:
            self.__handle_decide_jump(False)

        def __handle_decide_jump(self, do_jump: bool) -> None:
            self.ask_jump.emit(do_jump)
            self.win.close()

    saved_success = Signal(str)
    require_jump = Signal(str)

    def __init__(self) -> None:
        super().__init__('assets/ui/create.ui')

    def set_handlers(self) -> None:
        self.win.content.textChanged.connect(self.__handle_text_changed)
        self.win.btn_save.clicked.connect(self.__handle_save)
        self.win.btn_cancel.clicked.connect(self.win.close)

    # handlers
    def __handle_text_changed(self) -> None:
        self.lines = [x for x in self.win.content.toPlainText().split('\n') if x]
        is_valid, msg = ValidateUtil.validate_txt(content=self.lines)
        self.win.status.setText(msg)
        self.win.btn_save.setEnabled(is_valid)

    def __handle_save(self) -> None:
        self.txt_path, _ = QFileDialog.getSaveFileName(self, 'Save txt', './', '*.txt')
        with open(self.txt_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.lines))
        self.saved_success.emit(self.txt_path)
        self.jump = self.JumpWindow()
        self.jump.ask_jump.connect(self.__handle_jump)
        self.jump.run()
        self.win.close()

    def __handle_jump(self, do_jump: bool) -> None:
        if do_jump: self.require_jump.emit(self.txt_path)


class ConvertWindow(BasicWidget):
    ''' Define behaviour of file->convert window.
    '''
    converted = Signal(str)

    def __init__(self, txt_path: str = '') -> None:
        super().__init__('assets/ui/convert.ui')
        if txt_path:
            self.txt_path = txt_path
            self.win.addr.setText(txt_path)
            self.win.table.setEnabled(True)

    def set_handlers(self) -> None:
        self.win.btn_select.clicked.connect(self.__handle_select)
        self.win.table.cellChanged.connect(self.__handle_cell_changed)
        self.win.btn_convert.clicked.connect(self.__handle_convert)
        self.win.btn_cancel.clicked.connect(self.win.close)

    # handlers
    def __handle_select(self) -> None:
        self.txt_path, _ = QFileDialog.getOpenFileName(self, 'Load txt', './', '*.txt')
        is_valid, msg = ValidateUtil.validate_txt(txt_path=self.txt_path)
        self.win.addr.setText((self.txt_path if is_valid else msg))
        self.win.table.setEnabled(is_valid)
        if not is_valid: self.win.btn_convert.setDisabled(True)

    def __handle_cell_changed(self) -> None:
        self.win.btn_convert.setEnabled(True)

    def __handle_convert(self) -> None:
        division = [[int(self.win.table.item(i, j).text()) for j in range(5)] for i in range(4)]
        json_path, _ = QFileDialog.getSaveFileName(self, 'Save json', './', '*.json')
        try:
            JsonUtil.convert(self.txt_path, json_path, division)
        except Exception as ex:
            self.win.addr.setText(f'Convert failed: {ex.__str__()}')
            self.win.btn_convert.setDisabled(True)
        else:
            self.converted.emit(json_path)
            self.win.close()


class QuitWindow(BasicDialog):
    ''' Define behaviour of file->quit window.
    '''
    force_quit = Signal()

    def __init__(self) -> None:
        super().__init__('assets/ui/quit.ui')

    def set_handlers(self) -> None:
        self.win.btn_quit.clicked.connect(self.force_quit.emit)
        self.win.btn_cancel.clicked.connect(self.win.close)


if __name__ == '__main__':
    pass
