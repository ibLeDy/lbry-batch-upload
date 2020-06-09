# LBRY Batch Upload - WIP

Automate uploading entire folders to [lbry.tv] using [selenium] and [pyautogui].

Made mostly to practice Selenium, it is designed for music albums, still rough around
the edges and neither well thought nor complete.

## User Requirements

- Fill/replace values in [settings.json] before running the script
- Create `.env` file with your lbry credentials (PASSWORD, EMAIL)
- Provide an absolute folder path
- Have a thumbnail url available
- Song titles must match the format `{number} - {title}.{format}`
- Folder structure as follows

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

> Files should be in a folder which is named after the album, which should be located
> inside another folder that is named after the artist.

### TODO

- [ ] Better explanation of usage and capabilities
- [ ] Add configuration guide to `README.md` with all valid values for `settings.json`
- [ ] Add example credentials file or move them to `settings.json`
- [ ] Validate `settings.json` before uploading any file
- [ ] Warn about naming issues before uploading any file (mainly punctuation)
- [ ] Keep the upload page on sight when uploading the last file
- [ ] Prepend artist, album and title info to description string
- [ ] Better way of setting a description than a string in `settings.json`
- [ ] Follow prefered selector order (`id > name > links text > css > xpath`)
- [ ] PageObject pattern
- [ ] Implement waits
- [ ] Type hints
- [ ] Unit tests

[lbry.tv]: https://lbry.tv/
[selenium]: https://github.com/SeleniumHQ/selenium
[pyautogui]: https://github.com/asweigart/pyautogui
[settings.json]: settings.json
