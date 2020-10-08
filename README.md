# WIP - LBRY Batch Upload

Automate uploading entire folders to [lbry.tv] using [selenium] and [pyautogui].

Made mostly to practice Selenium, it is designed for music albums, still rough around
the edges and neither well thought nor complete.

## User Requirements

- Fill [config.toml] before running the script
- Provided folder path must be an absolute one
- Song titles must match the format `{number} - {title}.{format}`
- If there's a thumbnail named after the album, it will be used
- Folder structure as follows

> Files should be in a folder which is named after the album, inside a
> folder that is named after the artist.

```bash
.
└── Red Hot Chili Peppers
    └── Californication
        ├── 01 - Around the World.flac
        ├── 02 - Parallel Universe.flac
        ├── 03 - Scar Tissue.flac
        ├── 04 - Otherside.flac
        ├── 05 - Get on Top.flac
        ├── 06 - Californication.flac
        ├── 07 - Easily.flac
        ├── 08 - Porcelain.flac
        ├── 09 - Emit Remmus.flac
        ├── 10 - I Like Dirt.flac
        ├── 11 - This Velvet Glove.flac
        ├── 12 - Savior.flac
        ├── 13 - Purple Stain.flac
        ├── 14 - Right on Time.flac
        ├── 15 - Road Trippin.flac
        ├── album_info.txt
        └── Californication.jpg
```

## Usage

- Create a virtual enviroment and activate it

  ```text
  python3 -m virtualenv .venv && source .venv/bin/activate
  ```

- Install the requirements

  ```sh
  pip install -r requirements.txt
  ```

- Fill [config.toml]

- Run the script

  ```sh
  python lbry_batch_upload.py
  ```

### Changelog

- October 8, 2020:
  - Fix outdated selectors
  - Account for lbry's new upload confirmation popup
  - Use thumbnail file inside the album folder instead of a url
  - Delete `thumbnail_url` from upload section in config
  - Add `thumbnail_format` to files section in config
  - Don't use `-` separator between song number and name

- September 14, 2020:
  - Basic validation for `language` and `license_type`

- September 10, 2020:
  - Closing the success popup is more reliable
  - Selecting files is more reliable
  - Fix outdated selectors
  - Use ASCII in claim name

- July 24, 2020:
  - Changelog is now in reverse chronological order

- June 17, 2020:
  - Use toml instead of json for config file: `config.json -> config.toml`
  - Define constants to catch basic config errors
  - Replace `None` checks with existence ones

- June 16, 2020:
  - Rename settings file: `upload_settings.json -> config.json`
  - Handle closing success upload popup with a custom decorator
  - Add missing decorator to some functions
  - Rename base class for pages `PageObject -> BasePage`
  - Separate clicking and filling info so we can resume when a popup was detected
  - Add sleep before uploading next file so they get uploaded in order

- June 13, 2020:
  - Handle `price` option, only LBC atm

- June 12, 2020:
  - Change webdriver yo improve speed: `Firefox -> Chrome`
  - Change settings file name: `settings.json -> upload_settings.json`
  - Move credentials from `.env` to `upload_settings.json`
  - Remove `python-dotenv` requirement
  - Implement PageObject pattern
  - Remove `price` from settings until i manage to circunvent an obstructing label
  - Bump wait time before and after file selection to 1s

### TODO

- [x] Implement PageObject pattern
- [x] Keep the upload page on sight when uploading the last file
- [x] Better explanation of usage and capabilities _(not good enough)_
- [x] Handle price option _(only for LBC)_
- [x] Add example credentials file or move them to `config.toml` _(they got moved)_
- [x] Validate `config.toml` before uploading any file _(parsing and key existence)_
- [x] Better way of setting a description _(toml supports multi-line strings)_
- [ ] Add configuration guide to `README.md` with all valid values for `config.toml`
- [ ] Check that all value types are correct in `config.toml`
- [ ] Warn about naming issues before uploading any file (mainly punctuation)
- [ ] Prepend artist, album and title info to description string
- [ ] Follow prefered selector order (`id > name > links text > css > xpath`)
- [ ] Prevent or react to "failed to fetch" error on login
- [ ] Add argument to enable dark mode on the webpage
- [ ] Implement custom error messages
- [ ] Implement waits
- [ ] Type hints
- [ ] Unit tests

[lbry.tv]: https://lbry.tv
[selenium]: https://github.com/SeleniumHQ/selenium
[pyautogui]: https://github.com/asweigart/pyautogui
[config.toml]: config.toml
