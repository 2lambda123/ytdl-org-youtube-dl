#!/bin/sh

# IMPORTANT: the following assumptions are made
# * you did --set-upstream
# * the gh-pages branch is named so locally
# * the git config user.signingkey is properly set

# You will need
# pip install coverage nose rsa

set -e

if [ -z "$1" ]; then echo "ERROR: specify version number like this: $0 1994.09.06"; exit 1; fi
version="$1"
if [ ! -z "`git tag | grep "$version"`" ]; then echo 'ERROR: version already present'; exit 1; fi
if [ ! -z "`git status --porcelain | grep -v CHANGELOG`" ]; then echo 'ERROR: the working directory is not clean; commit or stash changes'; exit 1; fi
if [ ! -f "updates_key.pem" ]; then echo 'ERROR: updates_key.pem missing'; exit 1; fi

echo "\n### First of all, testing..."
make clean
nosetests --with-coverage --cover-package=youtube_dl --cover-html test || exit 1

echo "\n### Changing version in version.py..."
sed -i~ "s/__version__ = '.*'/__version__ = '$version'/" youtube_dl/version.py

echo "\n### Committing CHANGELOG README.md and youtube_dl/version.py..."
make README.md
git add CHANGELOG README.md youtube_dl/version.py
git commit -m "release $version"

echo "\n### Now tagging, signing and pushing..."
git tag -s -m "Release $version" "$version"
git show "$version"
read -p "Is it good, can I push? (y/n) " -n 1
if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi
echo
git push

echo "\n### OK, now it is time to build the binaries..."
REV=$(git rev-parse HEAD)
make youtube-dl youtube-dl.tar.gz
wget "http://jeromelaheurte.net:8142/download/rg3/youtube-dl/youtube-dl.exe?rev=$REV" -O youtube-dl.exe || \
	wget "http://jeromelaheurte.net:8142/build/rg3/youtube-dl/youtube-dl.exe?rev=$REV" -O youtube-dl.exe
mkdir -p "update_staging/$version"
mv youtube-dl youtube-dl.exe "update_staging/$version"
mv youtube-dl.tar.gz "update_staging/$version/youtube-dl-$version.tar.gz"
git checkout HEAD -- youtube-dl youtube-dl.exe

echo "\n### Signing and uploading the new binaries to youtube-dl.org..."
for f in update_staging/$version/*; do gpg --detach-sig "$f"; done
scp -r "update_staging/$version" ytdl@youtube-dl.org:html/downloads/
rm -r update_staging

echo "\n### Now switching to gh-pages..."
MASTER=$(git rev-parse --abbrev-ref HEAD)
git checkout gh-pages
git checkout "$MASTER" -- devscripts/gh-pages/
git reset devscripts/gh-pages/
devscripts/gh-pages/add-version.py $version
devscripts/gh-pages/sign-versions.py < updates_key.pem
devscripts/gh-pages/generate-download.py
devscripts/gh-pages/update-copyright.py
rm -r test_coverage
mv cover test_coverage
git add *.html *.html.in update test_coverage
git commit -m "release $version"
git show HEAD
read -p "Is it good, can I push? (y/n) " -n 1
if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi
echo
git push

echo "\n### DONE!"
git checkout $MASTER
