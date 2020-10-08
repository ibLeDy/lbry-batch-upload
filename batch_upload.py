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


class Config:
    def __init__(self, path):
        self.parse_config(path)

    def _parse_user_fields(self, user_config):
        self.email = user_config['email']
        self.password = user_config['password']

    def _parse_files_fields(self, files_config):
        self.folder_path = files_config['folder_path']
        self.audio_format = files_config['audio_format']  # FIXME: check dot
        self.thumbnail_format = files_config['thumbnail_format']  # FIXME: check dot
        self.excluded = files_config['excluded']
        self.album_name = os.path.split(self.folder_path)[-1]
        self.thumbnail_name = f'{self.album_name}{self.thumbnail_format}'

    def _parse_upload_fields(self, upload_config):
        self.description = upload_config['description']
        self.tags = upload_config['tags']
        self.channel = upload_config['channel']
        self.deposit = upload_config['deposit']
        self.price = upload_config['price']
        self.language = upload_config['language']
        self.license_type = upload_config['license_type']
        self.license_notice = upload_config['license_notice']

    def parse_config(self, path):
        with open(path, 'r') as f:
            config = toml.load(f)

        self._parse_user_fields(config['user'])
        self._parse_files_fields(config['files'])
        self._parse_upload_fields(config['upload'])


class BasePage:
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config

    def _banner(self):
        return self.driver.find_element_by_css_selector('button.nag__button')

    def close_banners(self):
        try:
            self._banner().click()
            self._banner().click()
        except NoSuchElementException:
            pass

    def scroll_page_to_top(self):
        self.driver.execute_script('window.scrollTo(0, 0)')


class LoginPage(BasePage):
    def _email_field(self):
        return self.driver.find_element_by_css_selector('#username')

    def _password_field(self):
        return self.driver.find_element_by_css_selector('#password')

    def _signin_button(self):
        return self.driver.find_element_by_css_selector('[aria-label="Log In"]')

    def _continue_button(self):
        return self.driver.find_element_by_css_selector('[aria-label="Continue"]')

    def load_page(self):
        self.driver.get('https://lbry.tv/$/signin')

    def login(self):
        self._email_field().send_keys(self.config.email)
        self._signin_button().click()
        time.sleep(0.5)
        self._password_field().send_keys(self.config.password)
        self._continue_button().click()


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
    def _file_button(self):
        return self.driver.find_element_by_xpath(
            '//*[@id="app"]/div/div[1]/main/div/section[1]/'
            'div[2]/fieldset-section[2]/input-submit/button'
        )

    def _title(self):
        return self.driver.find_element_by_css_selector('#content_title')

    def _description(self):
        return self.driver.find_element_by_css_selector('#content_description')

    def _thumbnail_button(self):
        return self.driver.find_element_by_xpath(
            '//*[@id="app"]/div/div[1]/main/div/div/section[2]/'
            'div/div/fieldset-section/input-submit/button'
        )

    def _thumbnail_upload_button(self):
        return self.driver.find_element_by_xpath(
            '/html/body/div[4]/div/div/div/button[1]'
        )

    def _tags(self):
        return self.driver.find_element_by_css_selector('.tag__input')

    def _channel_list(self):
        return self.driver.find_element_by_css_selector('#ID_FF_SELECT_CHANNEL')

    def _claim_url(self):
        return self.driver.find_element_by_css_selector('#content_name')

    def _deposit(self):
        return self.driver.find_element_by_css_selector('#content_bid')

    def _price_button(self):
        return self.driver.find_element_by_css_selector('label[for="content_cost"]')

    def _price(self):
        return self.driver.find_element_by_css_selector('#content_cost_amount_amount')

    def _options_button(self):
        return self.driver.find_element_by_css_selector(
            '[aria-label="Additional Options"]'
        )

    def _language_list(self):
        return self.driver.find_element_by_css_selector('#content_language')

    def _license_list(self):
        return self.driver.find_element_by_css_selector('#license')

    def _copyright_notice(self):
        return self.driver.find_element_by_css_selector('#copyright-notice')

    def _publish_button(self):
        return self.driver.find_element_by_css_selector('[aria-label="Upload"]')

    def _skip_preview_checkbox(self):
        return self.driver.find_element_by_xpath(
            '/html/body/div[4]/div/div/form/section/div[3]/div[2]/label'
        )

    def _upload_button(self):
        return self.driver.find_element_by_xpath(
            '/html/body/div[4]/div/div/form/section/div[3]/div[1]/button[1]'
        )

    def _publish_next_button(self):
        return self.driver.find_element_by_css_selector('a[href="/$/upload"]')

    def load_page(self):
        self.driver.get('https://lbry.tv/$/publish')

    def choose_file(self, song_name):  # NOTE: designed for nautilus
        self._file_button().click()
        pyperclip.copy(os.path.join(self.config.folder_path, song_name))
        time.sleep(1)
        pyautogui.hotkey('divide')
        pyautogui.press('backspace')
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(1)

    def fill_title(self, upload_title):
        self._title().send_keys(upload_title)

    def fill_description(self):
        self._description().send_keys(self.config.description)

    def choose_thumbnail(self, thumbnail_name):  # NOTE: designed for nautilus
        path = os.path.join(self.config.folder_path, thumbnail_name)
        if os.path.isfile(path):
            self._thumbnail_button().click()
            pyperclip.copy(path)
            time.sleep(1)
            pyautogui.hotkey('divide')
            pyautogui.press('backspace')
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(1)
            self._thumbnail_upload_button().click()

    def fill_tags(self):
        self._tags().send_keys(','.join(self.config.tags), Keys.ENTER)

    def select_channel(self):
        Select(self._channel_list()).select_by_value(self.config.channel)

    def fill_claim_name(self, claim_name):
        claim = self._claim_url()
        claim.clear()
        claim.send_keys(claim_name)

    def fill_deposit(self):
        content_bid = self._deposit()
        content_bid.clear()
        content_bid.send_keys(str(self.config.deposit))

    def select_price(self):
        self._price_button().click()

    def fill_price(self):
        price = self._price()
        price.clear()
        price.send_keys(str(self.config.price))

    def open_additional_options(self):
        self._options_button().click()

    def select_language(self):
        language_list_element = self._language_list()
        available_languages = [
            element.get_attribute('value')
            for element in language_list_element.find_elements_by_tag_name('option')
        ]
        if self.config.language not in available_languages:
            raise ValueError(
                'Language {!r} is not a valid option -> {}'.format(
                    self.config.language, available_languages
                )
            )
        Select(language_list_element).select_by_value(self.config.language)

    def select_license(self):
        license_list_element = self._license_list()
        available_licenses = [
            element.get_attribute('value')
            for element in license_list_element.find_elements_by_tag_name('option')
        ]
        if self.config.license_type not in available_licenses:
            raise ValueError(
                'License {!r} is not a valid option -> {}'.format(
                    self.config.license_type, available_licenses
                )
            )
        Select(license_list_element).select_by_value(self.config.license_type)

    def fill_license(self):
        copyright_notice = self._copyright_notice()
        copyright_notice.clear()
        copyright_notice.send_keys(self.config.license_notice)

    def publish(self):
        self._publish_button().click()

    def confirm_upload(self):
        self._skip_preview_checkbox().click()
        self._upload_button().click()

    @close_success_popup
    def continue_publishing(self):
        self._publish_next_button().click()

    @close_success_popup
    def upload_song(self, song_data, first_song):
        self.choose_file(song_data['song_name'])
        self.fill_title(song_data['upload_title'])
        self.fill_description()
        self.choose_thumbnail(self.config.thumbnail_name)
        self.fill_tags()
        self.select_channel()
        self.fill_claim_name(song_data['claim_name'])

        if self.config.deposit:
            self.fill_deposit()

        if self.config.price:
            self.select_price()
            self.fill_price()

        if first_song:
            self.open_additional_options()

        self.select_language()

        self.select_license()
        # FIXME: do not hardcode values
        # TODO: handle `license_type == 'other'`
        if self.config.license_type == 'copyright':
            self.fill_license()

        self.publish()
        if first_song:
            self.confirm_upload()
        time.sleep(5)  # NOTE: so they finish uploading in order


def get_song_names(folder_path, audio_format, excluded):  # TODO: revisit conditions
    song_names = []
    for file in os.listdir(folder_path):
        if os.path.splitext(file)[-1] == audio_format:
            if file not in excluded:
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


def get_song_data(folder_path, song_name):  # TODO: move to `upload_page`
    path_head, album = os.path.split(folder_path)
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
    driver.implicitly_wait(5)

    config = Config('config.toml')

    login_page = LoginPage(driver, config)
    login_page.load_page()
    login_page.login()
    login_page.close_banners()

    upload_page = UploadPage(driver, config)
    upload_page.load_page()

    songs = get_song_names(config.folder_path, config.audio_format, config.excluded)
    song_count = len(songs)

    while len(songs) > 0:
        # From last to first so they are ordered on the feed
        song_name = songs.pop()
        song_data = get_song_data(config.folder_path, song_name)

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
