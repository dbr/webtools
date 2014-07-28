Potentially a collection of Django apps to do misc stuff

[![Requirements Status](https://requires.io/github/dbr/webtools/requirements.png?branch=master)](https://requires.io/github/dbr/webtools/requirements/?branch=master)

[![Build Status](https://travis-ci.org/dbr/webtools.png?branch=master)](https://travis-ci.org/dbr/webtools)

# Installation

*Only tested on OS X 10.7, with Python 2.7.5 (installed via Homebrew)*

1. Setup python requirements

 Using virtualenvwrapper:

        mkvirutalenv webtools
        workon webtools
        pip install -r requirements.txt


2. Install required commands

 The `ytdl` application requires `youtube-dl`, which is easily
 installed via [Homebrew][homebrew] on OS X:

        brew install youtube-dl

 Simlarly the `run.sh` script uses `tmux` to run the server and task
 queue in the background:

        brew install tmux

3. Check the settings in `webtools/settings.py`

4. Initialise the database.

   The default configuration uses sqlite3 - which while not terribly
   fast with around 10,000 videos over 35 channels, it's usable and
   simple to maintain.

        workon webtools
        python manage.py syncdb

5. To launch:

        ./run.sh


# Applications

## `ytdl`

You can add a bunch of Youtube or Vimeo channels, then click a button
to download them (using [`youtube-dl`][youtube-dl]).

Multiple downloads will be queued up (using the [python-rq][python-rq] task
queue), and it keeps track of the state of videos (new, downloaded,
ignored)

So you can quickly see what new videos have been released on various
channels, click the "download" button on the interesting ones, and end
up with a folder of `.mp4` files to watch later (or, transfer onto an
iPad to something like AVPlayerHD etc etc).

Very little noise (no Youtube comments, no annotations, no pre-roll
and overlayed-banner ads), no buffering.


Some probably-outdated screenshots:

* [List of all channels](http://i.imgur.com/1v5WVW8.png)
* [Viewing a channel](http://i.imgur.com/1RPHbuM.png)


Random notes:

* Currently will always download the highest quality video possible,
  and the files are potentially quite large (some 30-40 minute videos
  are ~1GB). The `--max-quality` flag to `youtube-dl` might be worth
  using
* When adding a Vimeo user, only the first "3 pages" (about 60 videos)
  will be listed currently, due to using the
  ["simple API"](http://developer.vimeo.com/apis/simple). This
  restriction could be removed by registering for an API key and using
  the full API (which requires OAuth)
* The web interface does what I needed and no more. It's not the
  fanciest thing ever, but functional.


[youtube-dl]: http://rg3.github.io/youtube-dl/
[python-rq]: http://python-rq.org/
[homebrew]: http://brew.sh/
