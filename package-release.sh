#!/usr/bin/sh

# all this does is put the src and assets into a tar file that can be taken anywhere and unpakced then run

tarfilelocation="releases/release-$1-$2_BETA.tar.gz"

echo "Removing unnessesary files (pycache, ._* files etc.)"

mkdir /tmp/unnessesary
mv */._* src/__pycache__ /tmp/unnessesary

echo "Putting this release's files into a tar file located at $tarfilelocation"

tar cvzf $tarfilelocation src/ assets/ run.py > /tmp/aami-crunching-game_compile-tar.log
