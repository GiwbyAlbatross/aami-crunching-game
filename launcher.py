#!/usr/bin/env python
" launcher that installs and runs the aami crunching game "

# only standard library imports
import os
#import tkinter # maybe use a GUI?

VERSIONS = { # download URLs of various versions of the game
    "v1.2.2":"https://github.com/GiwbyAlbatross/aami-crunching-game/raw/refs/heads/main/releases/release-12-010525_BETA.tar.gz",
    "v1.1.0":"https://giwbyalbatross.github.io/downloads/aami-crunching/release-11-250325.tar.gz", # current release version
    "v1.0.2":"https://github.com/GiwbyAlbatross/aami-crunching-game/raw/refs/heads/main/releases/release-10-190225_BETA.tar.gz",
}

def choose_version() -> str:
    " choose which version to use, make a GUI version eventually "
    print("Select version by number")
    versionsbynumber = {}
    for i, version in enumerate(VERSIONS.keys()):
        print(f"({i}) {version}")
        versionsbynumber[i] = version
    return versionsbynumber[int(input("Use version: "))]

versionURL = VERSIONS[choose_version()]

# to be continued
