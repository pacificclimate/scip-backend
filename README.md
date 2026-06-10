# scip-backend
This application accesses a PostGIS database containing information on predefined areas a user might care about (watersheds, basins, and salmon conservation units) and metadata about salmon populations. Its role is to provide data to the [SCIP frontend](https://github.com/pacificclimate/scip-frontend).

## Installation for development

The SCIP backend uses [Poetry](https://python-poetry.org/) to manage virtual environments and package installation. Once you have Poetry installed and this repository cloned, you can use Poetry to set up and manage the virtual environment:

This project now targets Python 3.12 or newer.

```bash
$ git clone http://github.com/pacificclimate/scip-backend
$ cd scip-backend
$ poetry install
```

This is a [Flask](https://flask.palletsprojects.com/en/2.3.x/) application; it is configured by setting environment variables for Flask to read:

```bash
$ export FLASK_APP=scip.wsgi:app #what app to run
$ export DB="postgresql://user:password@server:port/database" #where to get data
$ export FLASK_DEBUG=1 #print error messages
```

And now you should be able to run it:
```
$ poetry run flask run
```

## Releasing

Creating a versioned release involves:

1. Incrementing `__version__` in `pyproject.toml`
2. Summarize the changes from the last release in `NEWS.md`
3. Commit these changes, then tag the release:

  ```bash
git add setup.py NEWS.md
git commit -m"Bump to version x.x.x"
git tag -a -m"x.x.x" x.x.x
git push --follow-tags
  ```