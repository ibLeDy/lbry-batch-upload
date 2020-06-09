import os
import time
import json

import pyautogui
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException


def get_settings():
    with open('settings.json', 'r') as fp:
        settings = json.load(fp)

    return settings


def get_files(path, format):
    songs = []
    for file in os.listdir(settings['folder_path']):
        if os.path.splitext(file)[-1] == settings['audio_format']:
            if file not in settings['excluded']:
                songs.append(file)

    songs.sort(reverse=True)
    return songs


def get_file_data(file):
    path_head, album = os.path.split(settings['folder_path'])
    _, artist = os.path.split(path_head)
    title = f'{os.path.splitext(file)[0]} - {album} - {artist}'

    # Clean name for claim url
    sanitized_name = []
    for char in os.path.splitext(file)[0]:
        if char.isalpha():
            sanitized_name.append(char)
        elif char == ' ':
            if sanitized_name and sanitized_name[-1] != char:
                sanitized_name.append(char)

    claim_name = ''.join(sanitized_name).lower().split(' - ', 1)[-1]
    claim_name_url = os.path.splitext(claim_name)[0].replace(' ', '-')

    song_data = {
        'album': album,
        'artist': artist,
        'file': file,
        'title': title,
        'claim_name_url': claim_name_url,
    }
    return song_data


def launch_webdriver():
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    return driver


def get_rid_of_bottom_banners(driver):  # NOTE: usually there are only two
    try:
        driver.find_element_by_css_selector('button.nag__button').click()
        time.sleep(0.5)
        driver.find_element_by_css_selector('button.nag__button').click()
    except NoSuchElementException:
        pass


def get_rid_of_success_popup(driver):
    try:
        driver.find_element_by_css_selector('[aria-label="Close"]').click()
    except NoSuchElementException:
        pass


def sign_in(driver):
    driver.find_element_by_css_selector('#username').send_keys(os.getenv('EMAIL'))
    driver.find_element_by_css_selector('[aria-label="Sign In"]').click()
    time.sleep(0.5)
    driver.find_element_by_css_selector('#password').send_keys(os.getenv('PASSWORD'))
    driver.find_element_by_css_selector('[aria-label="Continue"]').click()


def fill_and_publish(driver, settings, song_data, first_upload):
    # Choose file
    driver.find_element_by_css_selector('[aria-label="Choose File"]').click()

    file_path = f'{settings["folder_path"]}/{song_data["file"]}'
    for folder in file_path.lstrip(os.sep).split(os.sep):
        pyautogui.hotkey('divide')
        pyautogui.write(folder)

    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(0.5)

    # Fill title and description
    driver.find_element_by_css_selector('#content_title').send_keys(song_data['title'])
    driver.find_element_by_css_selector('#content_description').send_keys(
        settings['description']
    )

    # Fill thumbnail url
    driver.find_element_by_css_selector('[aria-label="Enter a thumbnail URL"]').click()
    driver.find_element_by_css_selector('#content_thumbnail').send_keys(
        settings['thumbnail_url']
    )

    # Enter tags
    driver.find_element_by_css_selector('.tag__input').send_keys(
        ', '.join(settings['tags']), Keys.ENTER
    )

    # Select channel
    Select(driver.find_element_by_css_selector('#channel')).select_by_value(
        settings['channel']
    )

    # Set url and deposit
    content_name = driver.find_element_by_css_selector('#content_name')
    content_name.clear()
    content_name.send_keys(song_data['claim_name_url'])

    deposit = settings['deposit']
    if deposit is not None:
        content_bid = driver.find_element_by_css_selector('#content_bid')
        content_bid.clear()
        content_bid.send_keys(deposit)

    # # Set price  # FIXME: label is obstructing so can't click
    # amount = settings['price']
    # if amount is not None:
    #     driver.find_element_by_css_selector('#content_cost').click()
    #     content_cost = driver.find_element_by_css_selector(
    #         '#content_cost_amount_amount'
    #     )
    #     content_cost.clear()
    #     content_cost.send_keys(amount)

    # Select language and license
    if first_upload:
        driver.find_element_by_css_selector('[aria-label="Additional Options"]').click()

    Select(driver.find_element_by_css_selector('#content_language')).select_by_value(
        settings['language']
    )

    if settings['license']['type'] is not None:
        Select(driver.find_element_by_css_selector('#license')).select_by_value(
            settings['license']['type']
        )
        copyright_notice = driver.find_element_by_css_selector('#copyright-notice')
        copyright_notice.clear()
        copyright_notice.send_keys(settings['license']['notice'])

    # Publish
    driver.find_element_by_css_selector('[aria-label="Publish"]').click()


def upload_song(driver, song, first_upload):
    song_data = get_file_data(song)
    fill_and_publish(driver, settings, song_data, first_upload)
    next_publish(driver, song)


def next_publish(driver, last_song):
    print('[UPLOADED]', last_song)
    driver.find_element_by_link_text('Publish').click()


if __name__ == '__main__':
    load_dotenv()
    driver = launch_webdriver()
    driver.get('https://lbry.tv/$/signin')

    sign_in(driver)
    get_rid_of_bottom_banners(driver)
    driver.get('https://lbry.tv/$/publish')

    settings = get_settings()
    songs = get_files(settings['folder_path'], settings['audio_format'])

    first_upload = True
    for song in songs:
        try:
            upload_song(driver, song, first_upload)
        except ElementClickInterceptedException:
            get_rid_of_success_popup(driver)
            upload_song(driver, song, first_upload)

        first_upload = False
