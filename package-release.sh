#!/usr/bin/sh

tarfilelocation="releases/release-$1-$2_BETA.tar.gz"

echo "Removing unnessesary files (pycache, ._* files etc.)"

#mkdir ._* /tmp/unnessesary
#mv  src/__pycache__ /tmp/unnessesary

echo "Putting this release's files into a tar file located at $tarfilelocation"

tar cvzf $tarfilelocation src/ assets/ run.py > /tmp/aami-crunching-game_compile-tar.log
