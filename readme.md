# `ytdl`

[![Build Status](https://travis-ci.org/dbr/webtools.png?branch=master)](https://travis-ci.org/dbr/webtools) [![Requirements Status](https://requires.io/github/dbr/webtools/requirements.png?branch=master)](https://requires.io/github/dbr/webtools/requirements/?branch=master)

A web interface where you can add any number of Youtube or Vimeo channels. Videos from these channels are then cleanly listed, and can be downloaded with a single click (using [`youtube-dl`][youtube-dl]).

Multiple downloads will be queued up (using the [python-rq][python-rq] task queue), and it keeps track of the state of videos (new, downloaded, ignored)

So you can quickly see what new videos have been released on various channels, click the "download" button on the interesting ones, and end up with a folder of `.mp4` files to watch later (or, transfer onto an iPad to something like AVPlayerHD etc etc).

Very little noise (no Youtube comments, no annotations, no pre-roll and overlayed-banner ads), no buffering.

Some probably-outdated screenshots:

* [List of all channels](http://i.imgur.com/1v5WVW8.png)
* [Viewing a channel](http://i.imgur.com/1RPHbuM.png)

## Installation

Docker is the preferred means of installation.

1. Adjust paths in `docker-compose.yml` as necessary.

    In the `app` container, `/data` contains the SQLite database and downloaded files. `/app` contains the code. In the `redis` container, there is a `/data` container used for the download queue data.

2. Start via `docker-compose`:

       docker-compose up --build --detatch

   This will run in the background (because `--detatch`)

3. Initialize database (only necessary on first run)

       docker-compose exec app python3 main.py dbinit

4. To stop:

      docker-compose down

## Running tests

Tests are run via docker-compose similarly to the main application.

    docker-compose -f docker-compose.test.yml up --build --exit-code-from test

## Random notes:

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
