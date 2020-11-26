import time

from PySide2.QtCore import QDate
from PySide2.QtWidgets import QFileDialog
from util.data import ValidateUtil

from ui.basic import BasicWindow
from ui.config import CommonWindow
from ui.file import ConvertWindow, CreateWindow, QuitWindow
from ui.help import AboutQtWindow, AboutWindow


class MainWindow(BasicWindow):
    ''' Define behaviour of main window.
    '''
    def __init__(self) -> None:
        super().__init__('assets/ui/main.ui')

    def run(self) -> None:
        super().run()
        self.app.exec_()

    def set_init_values(self) -> None:
        local_time = time.localtime(time.time())
        date = QDate(local_time.tm_year, local_time.tm_mon, local_time.tm_mday)
        self.win.date.setDate(date)

    def set_handlers(self) -> None:
        self.win.date.dateChanged.connect(self.__handle_date)
        self.win.btn_choose.clicked.connect(self.__handle_choose)
        self.win.btn_start.clicked.connect(self.__handle_start)
        self.win.btn_cancel.clicked.connect(self.__handle_cancel)
        self.win.create_txt.triggered.connect(self.__handle_create_txt)
        self.win.convert.triggered.connect(self.__handle_convert_json)
        self.win.quit.triggered.connect(self.__handle_quit)
        self.win.common.triggered.connect(self.__handle_common)
        self.win.about.triggered.connect(self.__handle_about)
        self.win.about_qt.triggered.connect(self.__handle_about_qt)

    # handlers
    def __handle_date(self, new_date: QDate) -> None:
        if self.win.date.editingFinished:
            self.__add_log('local', f'Date changed to {new_date.toPython()}')

    def __handle_choose(self) -> None:
        self.__add_log('local', 'Selecting json file...')
        json_path, _ = QFileDialog.getOpenFileName(self, 'Load Json', './', '*.json')
        if not json_path:
            self.__add_log('local', 'Selecting cancelled')
            return
        is_valid, msg = ValidateUtil.validate_json(json_path)
        if is_valid:
            self.__add_log('local', f'Selected [{json_path}] is parsed as: {msg}')
            self.win.addr.setText(json_path)
            self.win.btn_start.setEnabled(True)
        else:
            self.__add_log('local', f'Selected [{json_path}] is invalid: {msg}', 'ERRO')
            self.win.addr.clear()
            self.win.btn_start.setDisabled(True)

    def __handle_start(self) -> None:
        self.is_running = True
        self.win.btn_choose.setDisabled(True)
        self.win.btn_start.setDisabled(True)
        self.win.btn_cancel.setEnabled(True)

    def __handle_cancel(self) -> None:
        self.is_running = False
        self.win.btn_cancel.setDisabled(True)
        self.win.btn_choose.setEnabled(True)
        self.win.btn_start.setEnabled(True)

    def __handle_create_txt(self) -> None:
        self.create_txt = CreateWindow()
        self.create_txt.require_jump.connect(self.__handle_jump)
        self.create_txt.run()

    def __handle_jump(self, txt_path: str) -> None:
        self.__handle_convert_json(txt_path)

    def __handle_convert_json(self, txt_path: str = '') -> None:
        self.convert_json = ConvertWindow(txt_path)
        self.convert_json.converted.connect(self.__handle_converted)
        self.convert_json.run()

    def __handle_converted(self, json_path: str) -> None:
        self.win.addr.setText(json_path)

    def __handle_quit(self) -> None:
        if self.is_running:
            self.quit = QuitWindow()
            self.quit.force_quit.connect(self.app.quit)
            self.quit.run()
        else:
            self.app.quit()

    def __handle_common(self) -> None:
        self.common = CommonWindow()
        self.common.run()

    def __handle_about(self) -> None:
        self.about = AboutWindow()
        self.about.run()

    def __handle_about_qt(self) -> None:
        self.about_qt = AboutQtWindow()
        self.about_qt.run()

    # helpers
    def __add_log(self, target: str, log: str, level: str = 'INFO') -> None:
        formatted = f'[{time.ctime(time.time())}] {level} -> {log}'
        if target.lower() == 'local':
            self.win.log_local.append(formatted)
        elif target.lower() == 'network':
            self.win.log_network.append(formatted)


if __name__ == '__main__':
    pass
