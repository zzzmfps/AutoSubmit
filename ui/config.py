from ui.basic import BasicWidget


class CommonWindow(BasicWidget):
    ''' Define behaviour of config->common window.
    '''
    def __init__(self) -> None:
        super().__init__('assets/ui/common.ui')


if __name__ == "__main__":
    pass
