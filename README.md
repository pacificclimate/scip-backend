# scip-backend
This application accesses a PostGIS database containing information on predefined areas a user might care about (watersheds, basins, etc) and the locations of various salmon populations. Its role is to provide data to the [SCIP frontend](https://github.com/pacificclimate/scip-frontend).

## Installation for development

The SCIP backend uses [Poetry](https://python-poetry.org/) to manage virtual environments and package installation. Once you have Poetry installed and this repository cloned, you can use Poetry to set up and manage the virtual environment:

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