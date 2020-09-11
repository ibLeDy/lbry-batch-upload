import os
import time

import toml
import unidecode
import pyautogui
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException


with open('config.toml', 'r') as f:
    config = toml.load(f)

EMAIL = config['user']['email']
PASSWORD = config['user']['password']
FOLDER_PATH = config['files']['folder_path']
AUDIO_FORMAT = config['files']['audio_format']
EXCLUDED = config['files']['excluded']
DESCRIPTION = config['upload']['description']
THUMBNAIL_URL = config['upload']['thumbnail_url']
TAGS = config['upload']['tags']
CHANNEL = config['upload']['channel']
DEPOSIT = config['upload']['deposit']
PRICE = config['upload']['price']
LANGUAGE = config['upload']['language']
LICENSE_TYPE = config['upload']['license_type']
LICENSE_NOTICE = config['upload']['license_notice']


class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def __banner(self):
        return self.driver.find_element_by_css_selector('button.nag__button')

    def close_banners(self):
        try:
            self.__banner().click()
            self.__banner().click()
        except NoSuchElementException:
            pass

    def scroll_page_to_top(self):
        self.driver.execute_script('window.scrollTo(0, 0)')


class LoginPage(BasePage):
    def __email_field(self):
        return self.driver.find_element_by_css_selector('#username')

    def __password_field(self):
        return self.driver.find_element_by_css_selector('#password')

    def __signin_button(self):
        return self.driver.find_element_by_css_selector('[aria-label="Sign In"]')

    def __continue_button(self):
        return self.driver.find_element_by_css_selector('[aria-label="Continue"]')

    def load_page(self):
        self.driver.get('https://lbry.tv/$/signin')

    def login(self):
        self.__email_field().send_keys(EMAIL)
        self.__signin_button().click()
        time.sleep(0.5)
        self.__password_field().send_keys(PASSWORD)
        self.__continue_button().click()


def close_success_popup(func):
    def wrapper(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
        except ElementClickInterceptedException:
            self.driver.find_element_by_css_selector('[aria-label="Close"]').click()
            self.scroll_page_to_top()
            func(self, *args, **kwargs)

    return wrapper


class UploadPage(BasePage):
    def __file_button(self):
        return self.driver.find_element_by_css_selector('[aria-label="Browse"]')

    def __title(self):
        return self.driver.find_element_by_css_selector('#content_title')

    def __description(self):
        return self.driver.find_element_by_css_selector('#content_description')

    def __thumbnail_button(self):
        return self.driver.find_element_by_css_selector(
            '[aria-label="Enter a thumbnail URL"]'
        )

    def __thumbnail(self):
        return self.driver.find_element_by_css_selector('#content_thumbnail')

    def __tags(self):
        return self.driver.find_element_by_css_selector('.tag__input')

    def __channel_list(self):
        return self.driver.find_element_by_css_selector('#ID_FF_SELECT_CHANNEL')

    def __claim_url(self):
        return self.driver.find_element_by_css_selector('#content_name')

    def __deposit(self):
        return self.driver.find_element_by_css_selector('#content_bid')

    def __price_button(self):
        return self.driver.find_element_by_css_selector('label[for="content_cost"]')

    def __price(self):
        return self.driver.find_element_by_css_selector('#content_cost_amount_amount')

    def __options_button(self):
        return self.driver.find_element_by_css_selector(
            '[aria-label="Additional Options"]'
        )

    def __language_list(self):
        return self.driver.find_element_by_css_selector('#content_language')

    def __license_list(self):
        return self.driver.find_element_by_css_selector('#license')

    def __copyright_notice(self):
        return self.driver.find_element_by_css_selector('#copyright-notice')

    def __publish_button(self):
        return self.driver.find_element_by_css_selector('[aria-label="Upload"]')

    def __publish_next_button(self):
        return self.driver.find_element_by_css_selector('a[href="/$/upload"]')

    def load_page(self):
        self.driver.get('https://lbry.tv/$/publish')

    def choose_file(self, song_name):  # NOTE: designed for nautilus
        self.__file_button().click()
        pyperclip.copy(os.path.join(FOLDER_PATH, song_name))
        time.sleep(1)
        pyautogui.hotkey('divide')
        pyautogui.press('backspace')
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(1)

    def fill_title(self, upload_title):
        self.__title().send_keys(upload_title)

    def fill_description(self):
        self.__description().send_keys(DESCRIPTION)

    def select_thumbnail_url(self):
        self.__thumbnail_button().click()

    def fill_thumbnail_url(self):
        self.__thumbnail().send_keys(THUMBNAIL_URL)

    def fill_tags(self):
        self.__tags().send_keys(','.join(TAGS), Keys.ENTER)

    def select_channel(self):
        Select(self.__channel_list()).select_by_value(CHANNEL)

    def fill_claim_name(self, claim_name):
        claim = self.__claim_url()
        claim.clear()
        claim.send_keys(claim_name)

    def fill_deposit(self):
        content_bid = self.__deposit()
        content_bid.clear()
        content_bid.send_keys(str(DEPOSIT))

    def select_price(self):
        self.__price_button().click()

    def fill_price(self):
        price = self.__price()
        price.clear()
        price.send_keys(str(PRICE))

    def open_additional_options(self):
        self.__options_button().click()

    def select_language(self):
        Select(self.__language_list()).select_by_value(LANGUAGE)

    def select_license(self):
        Select(self.__license_list()).select_by_value(LICENSE_TYPE)

    def fill_license(self):
        copyright_notice = self.__copyright_notice()
        copyright_notice.clear()
        copyright_notice.send_keys(LICENSE_NOTICE)

    def publish(self):
        self.__publish_button().click()

    @close_success_popup
    def continue_publishing(self):
        self.__publish_next_button().click()

    @close_success_popup
    def upload_song(self, song_data, first_song):
        self.choose_file(song_data['song_name'])
        self.fill_title(song_data['upload_title'])
        self.fill_description()
        self.select_thumbnail_url()
        self.fill_thumbnail_url()
        self.fill_tags()
        self.select_channel()
        self.fill_claim_name(song_data['claim_name'])

        if DEPOSIT:
            self.fill_deposit()

        if PRICE:
            self.select_price()
            self.fill_price()

        if first_song:
            self.open_additional_options()

        self.select_language()

        if LICENSE_TYPE:  # TODO: handle `LICENSE_TYPE != "copyright"`
            self.select_license()
            self.fill_license()

        self.publish()
        time.sleep(5)  # NOTE: so they finish uploading in order


def get_song_names():  # TODO: revisit conditions
    song_names = []
    for file in os.listdir(FOLDER_PATH):
        if os.path.splitext(file)[-1] == AUDIO_FORMAT:
            if file not in EXCLUDED:
                song_names.append(file)

    song_names.sort()
    return song_names


def get_sanitized_claim_name(song_name):
    sanitized_name = ''
    for char in os.path.splitext(song_name)[0]:
        if char.isalpha():
            sanitized_name += char
        elif char == ' ':
            if sanitized_name and sanitized_name[-1] != char:
                sanitized_name += char

    return sanitized_name.lower().split(' - ', 1)[-1]


def get_song_data(song_name):  # TODO: move to `upload_page`
    path_head, album = os.path.split(FOLDER_PATH)
    _, artist = os.path.split(path_head)
    # FIXME: `upload_title` can contain multiple `-`
    upload_title = f'{os.path.splitext(song_name)[0]} - {album} - {artist}'
    claim_name = unidecode.unidecode(
        os.path.splitext(get_sanitized_claim_name(song_name))[0].replace(' ', '-')
    )

    return {
        'album': album,
        'artist': artist,
        'song_name': song_name,
        'upload_title': upload_title,
        'claim_name': claim_name,
    }


if __name__ == '__main__':
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)

    login_page = LoginPage(driver)
    login_page.load_page()
    login_page.login()
    login_page.close_banners()

    upload_page = UploadPage(driver)
    upload_page.load_page()

    songs = get_song_names()
    song_count = len(songs)

    while len(songs) > 0:
        # From last to first so they are ordered on the feed
        song_name = songs.pop()
        song_data = get_song_data(song_name)

        # Click "Additional Options" only on the first publish
        first_song = False
        if len(songs) + 1 == song_count:
            first_song = True

        upload_page.upload_song(song_data, first_song=first_song)

        # Inform the user, useful for excluding songs if the script crashes
        print('[PUBLISHED]', song_name)

        # Keep the upload page on sight when uploading the last file
        if not len(songs) == 0:
            upload_page.continue_publishing()
