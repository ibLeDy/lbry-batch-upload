import os
import time
import json

import pyautogui
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException


class PageObject:
    def __init__(self, driver):
        self.driver = driver

    def __banner(self):
        return self.driver.find_element_by_css_selector('button.nag__button')

    def close_banners(self):
        try:
            self.__banner().click()
            self.__banner().click()
        except NoSuchElementException:
            print('No banner found')


class LoginPage(PageObject):
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

    def login(self, email, password):
        self.__email_field().send_keys(email)
        self.__signin_button().click()
        time.sleep(0.5)
        self.__password_field().send_keys(password)
        self.__continue_button().click()


# def close_success_popup():
#     # FIXME: waiting for fill_and_publish to be separated
#     try:
#         driver.find_element_by_css_selector('[aria-label="Close"]').click()
#     except NoSuchElementException:
#         print('No success popup found')


# def detect_popup(func):
#     def func_wrapper(*args):
#         try:
#             func(*args)
#         except ElementClickInterceptedException:
#             driver.find_element_by_css_selector('[aria-label="Close"]').click()
#             func(*args)
#     return func_wrapper


# def detect_popup(driver):
#     def popup_decorator(func):
#         def func_wrapper(*args):
#             try:
#                 func(*args)
#             except ElementClickInterceptedException:
#                 print('Popup detected, trying to close it and continue')
#                 driver.find_element_by_css_selector('[aria-label="Close"]').click()
#                 func(*args)
#         return func_wrapper
#     return popup_decorator


class UploadPage(PageObject):
    def __init__(self, driver, settings):
        self.settings = settings
        super().__init__(driver)

    def __file_button(self):
        return self.driver.find_element_by_css_selector('[aria-label="Choose File"]')

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
        return self.driver.find_element_by_css_selector('#channel')

    def __claim_url(self):
        return self.driver.find_element_by_css_selector('#content_name')

    def __deposit(self):
        return self.driver.find_element_by_css_selector('#content_bid')

    def __price_button(self):
        return self.driver.find_element_by_css_selector('#content_cost')

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
        return self.driver.find_element_by_css_selector('[aria-label="Publish"]')

    def __publish_next_button(self):  # FIXME: replace with load_page
        return self.driver.find_element_by_link_text('Publish')

    def load_page(self):
        self.driver.get('https://lbry.tv/$/publish')

    def choose_file(self, song_name):
        self.__file_button().click()

        time.sleep(1)
        file_path = f'{self.settings["folder_path"]}/{song_name}'
        for folder in file_path.lstrip(os.sep).split(os.sep):
            pyautogui.hotkey('divide')
            pyautogui.write(folder)

        time.sleep(0.5)  # FIXME: slow computers might need more time
        pyautogui.press('enter')
        time.sleep(1)

    # @detect_popup
    def fill_title(self, upload_title):
        self.__title().send_keys(upload_title)

    # @detect_popup
    def fill_description(self):
        self.__description().send_keys(self.settings['description'])

    # @detect_popup
    def fill_thumbnail_url(self):
        self.__thumbnail_button().click()
        self.__thumbnail().send_keys(self.settings['thumbnail_url'])

    # @detect_popup
    def fill_tags(self):
        self.__tags().send_keys(','.join(self.settings['tags']), Keys.ENTER)

    # @detect_popup
    def select_channel(self):
        Select(self.__channel_list()).select_by_value(self.settings['channel'])

    # @detect_popup
    def fill_claim_name(self, claim_name):
        claim = self.__claim_url()
        claim.clear()
        claim.send_keys(claim_name)

    # @detect_popup
    def fill_deposit(self):
        content_bid = self.__deposit()
        content_bid.clear()
        content_bid.send_keys(self.settings['deposit'])

    # @detect_popup
    def fill_price(self):
        self.__price_button().click()
        price = self.__price()
        price.clear()
        price.send_keys(self.settings['price'])

    # @detect_popup
    def open_additional_options(self):
        self.__options_button().click()

    # @detect_popup
    def select_language(self):
        Select(self.__language_list()).select_by_value(self.settings['language'])

    # @detect_popup
    def select_license(self):
        Select(self.__license_list()).select_by_value(self.settings['license']['type'])

    # @detect_popup
    def fill_license(self):
        copyright_notice = self.__copyright_notice()
        copyright_notice.clear()
        copyright_notice.send_keys(self.settings['license']['notice'])

    # @detect_popup
    def publish(self):
        self.__publish_button().click()

    def upload_song(self, song_data, first_song=False):
        self.choose_file(song_data['song_name'])
        self.fill_title(song_data['upload_title'])
        self.fill_description()
        self.fill_thumbnail_url()
        self.fill_tags()
        self.select_channel()
        self.fill_claim_name(song_data['claim_name'])

        if self.settings['deposit'] is not None:
            self.fill_deposit()

        # if self.settings['price'] is not None:  # FIXME: label is obstructing so can't click
        #     self.fill_price()

        if first_song:
            self.open_additional_options()

        self.select_language()

        if self.settings['license']['type'] is not None:
            self.select_license()
            self.fill_license()  # TODO: only fill if license == "copyright"

        self.publish()

    def continue_publishing(self):
        self.__publish_next_button().click()


def get_upload_settings():
    with open('upload_settings.json', 'r') as fp:
        return json.load(fp)


def get_song_names(folder_path, audio_format, excluded):
    song_names = []
    for file in os.listdir(folder_path):
        if os.path.splitext(file)[-1] == audio_format:
            if file not in excluded:
                song_names.append(file)

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


def get_song_data(song_name, folder_path):
    path_head, album = os.path.split(folder_path)
    _, artist = os.path.split(path_head)
    upload_title = f'{os.path.splitext(song_name)[0]} - {album} - {artist}'
    sanitized_claim_name = get_sanitized_claim_name(song_name)
    claim_name = os.path.splitext(sanitized_claim_name)[0].replace(' ', '-')

    return {
        'album': album,
        'artist': artist,
        'song_name': song_name,
        'upload_title': upload_title,
        'claim_name': claim_name,
    }


if __name__ == '__main__':
    upload_settings = get_upload_settings()

    driver = webdriver.Chrome()
    driver.implicitly_wait(10)

    login_page = LoginPage(driver)
    login_page.load_page()
    login_page.login(upload_settings['email'], upload_settings['password'])
    login_page.close_banners()

    upload_page = UploadPage(driver, upload_settings)
    upload_page.load_page()

    songs = get_song_names(
        upload_settings['folder_path'],
        upload_settings['audio_format'],
        upload_settings['excluded'],
    )
    song_count = len(songs)

    while len(songs) > 0:
        # From last to first so they are ordered on the feed
        song_name = songs.pop()
        song_data = get_song_data(song_name, upload_settings['folder_path'])

        # Click "Additional Options" only on the first publish
        if len(songs) + 1 == song_count:
            upload_page.upload_song(song_data, first_song=True)
        else:
            upload_page.upload_song(song_data)

        print('[PUBLISHED]', song_name)
        time.sleep(0.5)

        # Keep the upload page on sight when uploading the last file
        if not len(songs) == 0:
            upload_page.continue_publishing()
