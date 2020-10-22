import time
from typing import List, Tuple

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from jsonio import JsonUtil


class BondChain:
    ''' Auto submit table data to bondchain.io
    '''
    def __init__(self, conf: str, user: str):
        self.conf = JsonUtil.load(conf)
        self.user = JsonUtil.load(user)
        self.driver = webdriver.Edge(self.conf['driver'])

    def login(self):
        ''' @return None\n
        Simulate login procedure
        '''
        self.driver.get(self.conf['page']['login'])
        # input username
        self.driver.find_element_by_name('loginName').send_keys(self.user['username'])
        # input password
        self.driver.find_element_by_name('loginPassword').send_keys(self.user['password'])
        # click submit button
        self.driver.find_element_by_css_selector(self.conf['elem']['btn_login']).click()
        # wait for change of router
        time.sleep(3)

    def add_offer(self, payload: List[str]) -> bool:
        ''' @return bool - whether the offer is successfully submitted\n
        Add an offer
        '''
        try:
            self.__try_add_offer(payload)
        except TimeoutException:  # no id, no such a rank, or something else
            btn_cancel = (By.XPATH, self.conf['elem']['btn_cancel'])
            self.driver.find_element_by_xpath(btn_cancel[1]).click()
            return False
        return True

    def done(self):
        ''' @return None\n
        Close browser and end driver
        '''
        self.driver.quit()

    def __try_add_offer(self, payload: List[str]):
        ''' @return None. Will raise TimeoutException\n
        Add an offer. Use explicit method waiting for webpage loading
        '''
        if self.driver.current_url != self.conf['page']['add_offer']:
            self.driver.get(self.conf['page']['add_offer'])
        # wait for addOffer button
        btn_addoffer = (By.XPATH, self.conf['elem']['btn_addoffer'])
        self.__wait_for_visible(btn_addoffer, 3, 0.5)
        self.driver.find_element_by_xpath(btn_addoffer[1]).click()
        # wait for institute input field
        txt_institute = (By.XPATH, self.conf['elem']['txt_institute'])
        self.__wait_for_visible(txt_institute, 3, 0.5)
        self.driver.find_element_by_xpath(txt_institute[1]).send_keys(payload[0])
        # wait for institute select field
        slt_institute = (By.XPATH, self.conf['elem']['slt_institute'])
        self.__wait_for_visible(slt_institute, 3, 0.5)
        slt_ul = self.driver.find_element_by_xpath(slt_institute[1])
        for opt in slt_ul.find_elements_by_tag_name('li'):
            span = opt.find_element_by_tag_name('span')
            if span.text == payload[0]:
                opt.click()
                break
        # input interest ratios
        for i in range(1, 6):
            if not payload[i]: continue
            # input i-th interest ratio
            txt_interesti = (By.XPATH, self.conf['elem']['txt_interest0'] % (i + 1))
            self.driver.find_element_by_xpath(txt_interesti[1]).send_keys(payload[i])
        # click confirm button
        btn_confirm = (By.XPATH, self.conf['elem']['btn_confirm'])
        self.driver.find_element_by_xpath(btn_confirm[1]).click()
        # check whether offer is submitted
        self.__wait_for_not_visible(btn_confirm, 1, 0.2)

    def __wait_for_visible(self, element: Tuple[str, str], timeout: float, frequency: float):
        ''' @return None. Will raise `TimeoutException` when times out\n
        Force driver to wait until a certain element is present and visible
        '''
        WebDriverWait(self.driver, timeout, frequency).until(EC.visibility_of_element_located(element))

    def __wait_for_not_visible(self, element: Tuple[str, str], timeout: float, frequency: float):
        ''' @return None. Will raise `TimeoutException` when times out\n
        Force driver to wait until a certain element is present but not visible
        '''
        WebDriverWait(self.driver, timeout, frequency).until_not(EC.visibility_of_element_located(element))
