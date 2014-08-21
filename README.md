youtube-dl - download videos from youtube.com or other video platforms

# SYNOPSIS
**youtube-dl** [OPTIONS] URL [URL...]

# INSTALLATION

To install it right away for all UNIX users (Linux, OS X, etc.), type:

    sudo curl https://yt-dl.org/latest/youtube-dl -o /usr/local/bin/youtube-dl
    sudo chmod a+x /usr/local/bin/youtube-dl

If you do not have curl, you can alternatively use a recent wget:

    sudo wget https://yt-dl.org/downloads/latest/youtube-dl -O /usr/local/bin/youtube-dl
    sudo chmod a+x /usr/local/bin/youtube-dl

Windows users can [download a .exe file](https://yt-dl.org/latest/youtube-dl.exe) and place it in their home directory or any other location on their [PATH](http://en.wikipedia.org/wiki/PATH_%28variable%29).

OS X users can install **youtube-dl** with [Homebrew](http://brew.sh/).

    brew install youtube-dl

You can also use pip:

    sudo pip install youtube-dl

Alternatively, refer to the developer instructions below for how to check out and work with the git repository. For further options, including PGP signatures, see https://rg3.github.io/youtube-dl/download.html .

# DESCRIPTION
**youtube-dl** is a small command-line program to download videos from
YouTube.com and a few more sites. It requires the Python interpreter, version
2.6, 2.7, or 3.3+, and it is not platform specific. It should work on
your Unix box, on Windows or on Mac OS X. It is released to the public domain,
which means you can modify it, redistribute it or use it however you like.

# OPTIONS
    -h, --help                       print this help text and exit
    --version                        print program version and exit
    -U, --update                     update this program to latest version. Make
                                     sure that you have sufficient permissions
                                     (run with sudo if needed)
    -i, --ignore-errors              continue on download errors, for example to
                                     skip unavailable videos in a playlist
    --abort-on-error                 Abort downloading of further videos (in the
                                     playlist or the command line) if an error
                                     occurs
    --dump-user-agent                display the current browser identification
    --list-extractors                List all supported extractors and the URLs
                                     they would handle
    --extractor-descriptions         Output descriptions of all supported
                                     extractors
    --proxy URL                      Use the specified HTTP/HTTPS proxy. Pass in
                                     an empty string (--proxy "") for direct
                                     connection
    --socket-timeout None            Time to wait before giving up, in seconds
    --default-search PREFIX          Use this prefix for unqualified URLs. For
                                     example "gvsearch2:" downloads two videos
                                     from google videos for  youtube-dl "large
                                     apple". Use the value "auto" to let
                                     youtube-dl guess ("auto_warning" to emit a
                                     warning when guessing). "error" just throws
                                     an error. The default value "fixup_error"
                                     repairs broken URLs, but emits an error if
                                     this is not possible instead of searching.
    --ignore-config                  Do not read configuration files. When given
                                     in the global configuration file /etc
                                     /youtube-dl.conf: do not read the user
                                     configuration in ~/.config/youtube-dl.conf
                                     (%APPDATA%/youtube-dl/config.txt on
                                     Windows)

## Video Selection:
    --playlist-start NUMBER          playlist video to start at (default is 1)
    --playlist-end NUMBER            playlist video to end at (default is last)
    --match-title REGEX              download only matching titles (regex or
                                     caseless sub-string)
    --reject-title REGEX             skip download for matching titles (regex or
                                     caseless sub-string)
    --max-downloads NUMBER           Abort after downloading NUMBER files
    --min-filesize SIZE              Do not download any videos smaller than
                                     SIZE (e.g. 50k or 44.6m)
    --max-filesize SIZE              Do not download any videos larger than SIZE
                                     (e.g. 50k or 44.6m)
    --date DATE                      download only videos uploaded in this date
    --datebefore DATE                download only videos uploaded on or before
                                     this date (i.e. inclusive)
    --dateafter DATE                 download only videos uploaded on or after
                                     this date (i.e. inclusive)
    --min-views COUNT                Do not download any videos with less than
                                     COUNT views
    --max-views COUNT                Do not download any videos with more than
                                     COUNT views
    --no-playlist                    download only the currently playing video
    --age-limit YEARS                download only videos suitable for the given
                                     age
    --download-archive FILE          Download only videos not listed in the
                                     archive file. Record the IDs of all
                                     downloaded videos in it.
    --include-ads                    Download advertisements as well
                                     (experimental)
    --youtube-include-dash-manifest  Try to download the DASH manifest on
                                     YouTube videos (experimental)

## Download Options:
    -r, --rate-limit LIMIT           maximum download rate in bytes per second
                                     (e.g. 50K or 4.2M)
    -R, --retries RETRIES            number of retries (default is 10)
    --buffer-size SIZE               size of download buffer (e.g. 1024 or 16K)
                                     (default is 1024)
    --no-resize-buffer               do not automatically adjust the buffer
                                     size. By default, the buffer size is
                                     automatically resized from an initial value
                                     of SIZE.

## Filesystem Options:
    -a, --batch-file FILE            file containing URLs to download ('-' for
                                     stdin)
    --id                             use only video ID in file name
    -A, --auto-number                number downloaded files starting from 00000
    -o, --output TEMPLATE            output filename template. Use %(title)s to
                                     get the title, %(uploader)s for the
                                     uploader name, %(uploader_id)s for the
                                     uploader nickname if different,
                                     %(autonumber)s to get an automatically
                                     incremented number, %(ext)s for the
                                     filename extension, %(format)s for the
                                     format description (like "22 - 1280x720" or
                                     "HD"), %(format_id)s for the unique id of
                                     the format (like YouTube's itags: "137"),
                                     %(upload_date)s for the upload date
                                     (YYYYMMDD), %(extractor)s for the provider
                                     (youtube, metacafe, etc), %(id)s for the
                                     video id, %(playlist)s for the playlist the
                                     video is in, %(playlist_index)s for the
                                     position in the playlist and %% for a
                                     literal percent. %(height)s and %(width)s
                                     for the width and height of the video
                                     format. %(resolution)s for a textual
                                     description of the resolution of the video
                                     format. Use - to output to stdout. Can also
                                     be used to download to a different
                                     directory, for example with -o '/my/downloa
                                     ds/%(uploader)s/%(title)s-%(id)s.%(ext)s' .
    --autonumber-size NUMBER         Specifies the number of digits in
                                     %(autonumber)s when it is present in output
                                     filename template or --auto-number option
                                     is given
    --restrict-filenames             Restrict filenames to only ASCII
                                     characters, and avoid "&" and spaces in
                                     filenames
    -t, --title                      [deprecated] use title in file name
                                     (default)
    -l, --literal                    [deprecated] alias of --title
    -w, --no-overwrites              do not overwrite files
    -c, --continue                   force resume of partially downloaded files.
                                     By default, youtube-dl will resume
                                     downloads if possible.
    --no-continue                    do not resume partially downloaded files
                                     (restart from beginning)
    --no-part                        do not use .part files
    --no-mtime                       do not use the Last-modified header to set
                                     the file modification time
    --write-description              write video description to a .description
                                     file
    --write-info-json                write video metadata to a .info.json file
    --write-annotations              write video annotations to a .annotation
                                     file
    --write-thumbnail                write thumbnail image to disk
    --load-info FILE                 json file containing the video information
                                     (created with the "--write-json" option)
    --cookies FILE                   file to read cookies from and dump cookie
                                     jar in
    --cache-dir DIR                  Location in the filesystem where youtube-dl
                                     can store some downloaded information
                                     permanently. By default $XDG_CACHE_HOME
                                     /youtube-dl or ~/.cache/youtube-dl . At the
                                     moment, only YouTube player files (for
                                     videos with obfuscated signatures) are
                                     cached, but that may change.
    --no-cache-dir                   Disable filesystem caching
    --rm-cache-dir                   Delete all filesystem cache files

## Verbosity / Simulation Options:
    -q, --quiet                      activates quiet mode
    --no-warnings                    Ignore warnings
    -s, --simulate                   do not download the video and do not write
                                     anything to disk
    --skip-download                  do not download the video
    -g, --get-url                    simulate, quiet but print URL
    -e, --get-title                  simulate, quiet but print title
    --get-id                         simulate, quiet but print id
    --get-thumbnail                  simulate, quiet but print thumbnail URL
    --get-description                simulate, quiet but print video description
    --get-duration                   simulate, quiet but print video length
    --get-filename                   simulate, quiet but print output filename
    --get-format                     simulate, quiet but print output format
    -j, --dump-json                  simulate, quiet but print JSON information.
                                     See --output for a description of available
                                     keys.
    --newline                        output progress bar as new lines
    --no-progress                    do not print progress bar
    --console-title                  display progress in console titlebar
    -v, --verbose                    print various debugging information
    --dump-intermediate-pages        print downloaded pages to debug problems
                                     (very verbose)
    --write-pages                    Write downloaded intermediary pages to
                                     files in the current directory to debug
                                     problems
    --print-traffic                  Display sent and read HTTP traffic

## Workarounds:
    --encoding ENCODING              Force the specified encoding (experimental)
    --no-check-certificate           Suppress HTTPS certificate validation.
    --prefer-insecure                Use an unencrypted connection to retrieve
                                     information about the video. (Currently
                                     supported only for YouTube)
    --user-agent UA                  specify a custom user agent
    --referer REF                    specify a custom referer, use if the video
                                     access is restricted to one domain
    --add-header FIELD:VALUE         specify a custom HTTP header and its value,
                                     separated by a colon ':'. You can use this
                                     option multiple times
    --bidi-workaround                Work around terminals that lack
                                     bidirectional text support. Requires bidiv
                                     or fribidi executable in PATH

## Video Format Options:
    -f, --format FORMAT              video format code, specify the order of
                                     preference using slashes: "-f 22/17/18".
                                     "-f mp4" and "-f flv" are also supported.
                                     You can also use the special names "best",
                                     "bestvideo", "bestaudio", "worst",
                                     "worstvideo" and "worstaudio". By default,
                                     youtube-dl will pick the best quality.
    --all-formats                    download all available video formats
    --prefer-free-formats            prefer free video formats unless a specific
                                     one is requested
    --max-quality FORMAT             highest quality format to download
    -F, --list-formats               list all available formats

## Subtitle Options:
    --write-sub                      write subtitle file
    --write-auto-sub                 write automatic subtitle file (youtube
                                     only)
    --all-subs                       downloads all the available subtitles of
                                     the video
    --list-subs                      lists all available subtitles for the video
    --sub-format FORMAT              subtitle format (default=srt) ([sbv/vtt]
                                     youtube only)
    --sub-lang LANGS                 languages of the subtitles to download
                                     (optional) separated by commas, use IETF
                                     language tags like 'en,pt'

## Authentication Options:
    -u, --username USERNAME          account username
    -p, --password PASSWORD          account password
    -n, --netrc                      use .netrc authentication data
    --video-password PASSWORD        video password (vimeo, smotri)

## Post-processing Options:
    -x, --extract-audio              convert video files to audio-only files
                                     (requires ffmpeg or avconv and ffprobe or
                                     avprobe)
    --audio-format FORMAT            "best", "aac", "vorbis", "mp3", "m4a",
                                     "opus", or "wav"; best by default
    --audio-quality QUALITY          ffmpeg/avconv audio quality specification,
                                     insert a value between 0 (better) and 9
                                     (worse) for VBR or a specific bitrate like
                                     128K (default 5)
    --recode-video FORMAT            Encode the video to another format if
                                     necessary (currently supported:
                                     mp4|flv|ogg|webm|mkv)
    -k, --keep-video                 keeps the video file on disk after the
                                     post-processing; the video is erased by
                                     default
    --no-post-overwrites             do not overwrite post-processed files; the
                                     post-processed files are overwritten by
                                     default
    --embed-subs                     embed subtitles in the video (only for mp4
                                     videos)
    --embed-thumbnail                embed thumbnail in the audio as cover art
    --add-metadata                   write metadata to the video file
    --xattrs                         write metadata to the video file's xattrs
                                     (using dublin core and xdg standards)
    --prefer-avconv                  Prefer avconv over ffmpeg for running the
                                     postprocessors (default)
    --prefer-ffmpeg                  Prefer ffmpeg over avconv for running the
                                     postprocessors

# CONFIGURATION

You can configure youtube-dl by placing default arguments (such as `--extract-audio --no-mtime` to always extract the audio and not copy the mtime) into `/etc/youtube-dl.conf` and/or `~/.config/youtube-dl/config`. On Windows, the configuration file locations are `%APPDATA%\youtube-dl\config.txt` and `C:\Users\<Yourname>\youtube-dl.conf`.

# OUTPUT TEMPLATE

The `-o` option allows users to indicate a template for the output file names. The basic usage is not to set any template arguments when downloading a single file, like in `youtube-dl -o funny_video.flv "http://some/video"`. However, it may contain special sequences that will be replaced when downloading each video. The special sequences have the format `%(NAME)s`. To clarify, that is a percent symbol followed by a name in parenthesis, followed by a lowercase S. Allowed names are:

 - `id`: The sequence will be replaced by the video identifier.
 - `url`: The sequence will be replaced by the video URL.
 - `uploader`: The sequence will be replaced by the nickname of the person who uploaded the video.
 - `upload_date`: The sequence will be replaced by the upload date in YYYYMMDD format.
 - `title`: The sequence will be replaced by the video title.
 - `ext`: The sequence will be replaced by the appropriate extension (like flv or mp4).
 - `epoch`: The sequence will be replaced by the Unix epoch when creating the file.
 - `autonumber`: The sequence will be replaced by a five-digit number that will be increased with each download, starting at zero.
 - `playlist`: The name or the id of the playlist that contains the video.
 - `playlist_index`: The index of the video in the playlist, a five-digit number.

The current default template is `%(title)s-%(id)s.%(ext)s`.

In some cases, you don't want special characters such as 中, spaces, or &, such as when transferring the downloaded filename to a Windows system or the filename through an 8bit-unsafe channel. In these cases, add the `--restrict-filenames` flag to get a shorter title:

    $ youtube-dl --get-filename -o "%(title)s.%(ext)s" BaW_jenozKc
    youtube-dl test video ''_ä↭𝕐.mp4    # All kinds of weird characters
    $ youtube-dl --get-filename -o "%(title)s.%(ext)s" BaW_jenozKc --restrict-filenames
    youtube-dl_test_video_.mp4          # A simple file name

# VIDEO SELECTION

Videos can be filtered by their upload date using the options `--date`, `--datebefore` or `--dateafter`, they accept dates in two formats:

 - Absolute dates: Dates in the format `YYYYMMDD`.
 - Relative dates: Dates in the format `(now|today)[+-][0-9](day|week|month|year)(s)?`
 
Examples:

    # Download only the videos uploaded in the last 6 months
    $ youtube-dl --dateafter now-6months

    # Download only the videos uploaded on January 1, 1970
    $ youtube-dl --date 19700101

    $ # will only download the videos uploaded in the 200x decade
    $ youtube-dl --dateafter 20000101 --datebefore 20091231

# FAQ

### Can you please put the -b option back?

Most people asking this question are not aware that youtube-dl now defaults to downloading the highest available quality as reported by YouTube, which will be 1080p or 720p in some cases, so you no longer need the `-b` option. For some specific videos, maybe YouTube does not report them to be available in a specific high quality format you're interested in. In that case, simply request it with the `-f` option and youtube-dl will try to download it.

### I get HTTP error 402 when trying to download a video. What's this?

Apparently YouTube requires you to pass a CAPTCHA test if you download too much. We're [considering to provide a way to let you solve the CAPTCHA](https://github.com/rg3/youtube-dl/issues/154), but at the moment, your best course of action is pointing a webbrowser to the youtube URL, solving the CAPTCHA, and restart youtube-dl.

### I have downloaded a video but how can I play it?

Once the video is fully downloaded, use any video player, such as [vlc](http://www.videolan.org) or [mplayer](http://www.mplayerhq.hu/).

### The links provided by youtube-dl -g are not working anymore

The URLs youtube-dl outputs require the downloader to have the correct cookies. Use the `--cookies` option to write the required cookies into a file, and advise your downloader to read cookies from that file. Some sites also require a common user agent to be used, use `--dump-user-agent` to see the one in use by youtube-dl.

### ERROR: no fmt_url_map or conn information found in video info

youtube has switched to a new video info format in July 2011 which is not supported by old versions of youtube-dl. You can update youtube-dl with `sudo youtube-dl --update`.

### ERROR: unable to download video ###

youtube requires an additional signature since September 2012 which is not supported by old versions of youtube-dl. You can update youtube-dl with `sudo youtube-dl --update`.

### SyntaxError: Non-ASCII character ###

The error

    File "youtube-dl", line 2
    SyntaxError: Non-ASCII character '\x93' ...

means you're using an outdated version of Python. Please update to Python 2.6, 2.7 or 3.3+.

### What is this binary file? Where has the code gone?

Since June 2012 (#342) youtube-dl is packed as an executable zipfile, simply unzip it (might need renaming to `youtube-dl.zip` first on some systems) or clone the git repository, as laid out above. If you modify the code, you can run it by executing the `__main__.py` file. To recompile the executable, run `make youtube-dl`.

### The exe throws a *Runtime error from Visual C++*

To run the exe you need to first install the [Microsoft Visual C++ 2008 Redistributable Package](http://www.microsoft.com/en-us/download/details.aspx?id=29).

# CONTRIBUTING
You are welcome to [report a bug](CONTRIBUTING.md#bugs) or [contribute code](CONTRIBUTING.md#developer-instructions).


# COPYRIGHT

youtube-dl is released into the public domain by the copyright holders.

This README file was originally written by Daniel Bolton (<https://github.com/dbbolton>) and is likewise released into the public domain.
