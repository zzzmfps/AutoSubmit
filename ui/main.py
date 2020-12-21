import sys
import time
import os
from threading import Thread

from PySide2.QtCore import QDate
from PySide2.QtGui import QCloseEvent
from PySide2.QtWidgets import QFileDialog
from util.data import JsonUtil, ValidateUtil
from util.request import RequestUtil

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
        sys.exit(self.app.exec_())

    def set_handlers(self) -> None:
        # main panel
        self.win.date.dateChanged.connect(self.__handle_date)
        self.win.btn_select.clicked.connect(self.__handle_select)
        self.win.btn_start.clicked.connect(self.__handle_start)
        # file
        self.win.create_txt.triggered.connect(self.__handle_create_txt)
        self.win.convert.triggered.connect(self.__handle_convert_json)
        self.win.quit.triggered.connect(self.close)
        # config
        self.win.common.triggered.connect(self.__handle_common)
        self.win.name.triggered.connect(self.__handle_name)
        self.win.rank.triggered.connect(self.__handle_rank)
        self.win.url.triggered.connect(self.__handle_url)
        # help
        self.win.about.triggered.connect(self.__handle_about)
        self.win.about_qt.triggered.connect(self.__handle_about_qt)

    def set_init_values(self) -> None:
        local_time = time.localtime(time.time())
        date = QDate(local_time.tm_year, local_time.tm_mon, local_time.tm_mday)
        self.win.date.setDate(date)

    # events
    def closeEvent(self, event: QCloseEvent) -> None:
        if self.is_running:
            self.quit = QuitWindow()
            self.quit.force_quit.connect(self.app.quit)
            self.quit.run()
        else:
            self.app.quit()
        event.ignore()

    # handlers
    def __handle_date(self, new_date: QDate) -> None:
        if self.win.date.editingFinished:
            self.__add_log('local', f'Date changed to {new_date.toPython()}')

    def __handle_select(self) -> None:
        self.__add_log('local', 'Selecting json file...')
        json_path, _ = QFileDialog.getOpenFileName(self, 'Load Json', './', '*.json')
        if not json_path:
            self.__add_log('local', 'Selection cancelled')
        else:
            self.__check_selected(json_path)

    def __handle_start(self) -> None:
        self.__add_log('local', 'Start to exec submit task')
        self.is_running = True
        self.win.btn_select.setDisabled(True)
        self.win.btn_start.setDisabled(True)
        self.win.progress_bar.setValue(0)
        Thread(target=self.__exec_submit, daemon=True).start()

    def __handle_submit_log(self, log: str) -> None:
        level = 'ERRO' if log.startswith(' ! ') else 'INFO'
        self.__add_log('network', log.lstrip(' !'), level)

    def __handle_update_percent(self, perc: int) -> None:
        self.win.progress_bar.setValue(perc)

    def __handle_create_txt(self) -> None:
        self.create_txt = CreateWindow()
        self.create_txt.saved_success.connect(self.__handle_saved)
        self.create_txt.require_jump.connect(self.__handle_jump)
        self.create_txt.run()

    def __handle_saved(self, txt_path: str) -> None:
        self.__add_log('local', f'Saved data into [{txt_path}]')

    def __handle_jump(self, txt_path: str) -> None:
        self.__handle_convert_json(txt_path)

    def __handle_convert_json(self, txt_path: str = '') -> None:
        self.convert_json = ConvertWindow(txt_path)
        self.convert_json.converted.connect(self.__handle_converted)
        self.convert_json.run()

    def __handle_converted(self, json_path: str) -> None:
        self.__add_log('local', f'Converted and saved data into [{json_path}]')
        self.__check_selected(json_path)

    def __handle_common(self) -> None:
        self.common = CommonWindow()
        self.common.conf_status.connect(self.__handle_load_conf)
        self.common.run()

    def __handle_load_conf(self, status: bool, conf_path: str, add_msg: str) -> None:
        if not status:
            self.__add_log('local', f'Initialized new config [{conf_path}]: {add_msg}', 'WARN')
        elif not add_msg:
            self.__add_log('local', f'Config [{conf_path}] is loaded')
        else:
            self.__add_log('local', f'Saved config into [{conf_path}]: {add_msg}')

    def __handle_name(self) -> None:
        os.system('notepad.exe assets/json/bank_map.json')

    def __handle_rank(self) -> None:
        # 1 AAA, 2 AA+, 3 AA, 4 AA-, 5 A+, 6 A, 7 A-, 8 BBB+
        os.system('notepad.exe assets/json/bank_rank.json')

    def __handle_url(self) -> None:
        os.system('notepad.exe assets/json/url.json')

    def __handle_about(self) -> None:
        self.about = AboutWindow()
        self.about.run()

    def __handle_about_qt(self) -> None:
        self.about_qt = AboutQtWindow()
        self.about_qt.run()

    # helpers
    def __add_log(self, target: str, log: str, level: str = 'INFO') -> None:
        color = {'INFO': 'green', 'WARN': 'orange', 'ERRO': 'red'}
        level = f'<span style="color: {color[level]};">{level}</span>'
        formatted = f'[{time.ctime(time.time())}] {level} -> {log}'
        if target.lower() == 'local':
            self.win.log_local.append(formatted)
        elif target.lower() == 'network':
            self.win.log_network.append(formatted)

    def __check_selected(self, json_path: str) -> None:
        is_valid, msg = ValidateUtil.validate_json(json_path)
        if is_valid:
            self.__add_log('local', f'Selected [{json_path}] is parsed as: {msg}')
            self.win.addr.setText(json_path)
            self.win.btn_start.setEnabled(True)
        else:
            self.__add_log('local', f'Selected [{json_path}] is invalid: {msg}', 'ERRO')
            self.win.addr.clear()
            self.win.btn_start.setDisabled(True)

    def __exec_submit(self) -> None:
        ''' return None\n
        Exec the entire process of submission, including load data, login,
        submit, print logs and recover the state of related widgets.
        '''
        def finish_or_recover(success: bool):
            self.win.btn_start.setEnabled(True)
            self.win.btn_select.setEnabled(True)
            self.is_running = False
            if success:
                self.__add_log('local', 'Submit task completed')
            else:
                self.__add_log('local', 'Submit task failed', 'ERRO')

        req = RequestUtil(True)
        req.new_log.connect(self.__handle_submit_log)
        req.cur_percent.connect(self.__handle_update_percent)
        data = JsonUtil.load(self.win.addr.text())
        offset = self.win.date.date().daysTo(QDate.currentDate())
        if offset < 0:
            self.__add_log('local', 'Cannot submit offers from future', 'ERRO')
            finish_or_recover(False)
            return
        notice_date = 1000 * (int(time.time()) - 86400 * offset)
        try:
            req.login()
            failed = req.add_offers(data, notice_date)
            time.sleep(0.5)  # ensure order of logs
        except Exception as ex:
            success = False
            self.__add_log('network', ex.__str__(), 'ERRO')
        else:
            success = True
            if not failed:
                self.__add_log('network', '* All Succeeded *')
            else:
                self.__add_log('network', f'* Totally {len(failed)} fail(s):', 'WARN')
                for fail in failed:
                    self.__add_log('network', str(fail), 'WARN')
        finish_or_recover(success)


if __name__ == '__main__':
    pass
