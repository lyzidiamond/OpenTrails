[![Build Status](https://travis-ci.org/codeforamerica/PLATS.png)](https://travis-ci.org/codeforamerica/PLATS)

OpenTrails Converter and Validator
=====

Description
-----------

These in-development tools will allow park agencies and other trail stewards to upload and transformer their existing shapefile data describing trail systems—including trail segments, trailheads, and the areas they traverse—into [OpenTrails](http://codeforamerica.org/specifications/trails)-compliant GeoJSON and CSV files.

Current Status
--------------

The converter tool currently transformers shapefiles containing trail segment data, proudcing:
* trail_segments.geojson
* named_trails.csv
* stewards.csv

Future functionality will provide a similar transformation for shapefiles describing trailheads (points) and areas (polygons).


Install
-------

PLATS is a [Python Flask application](https://github.com/codeforamerica/howto/blob/master/Python-Virtualenv.md),
and depends on [Amazon S3](http://aws.amazon.com/s3/) for storage of uploads.

* Amazon Web Services configuration comes from the `DATASTORE` environmental
variable, given in this form:

    `s3n://<AWS key>:<AWS secret>@<S3 bucket name>`

* Set up a [virtualenv](https://pypi.python.org/pypi/virtualenv)

```
pip install virtualenv
virtualenv venv-plats
source venv-plats/bin/activate
```

* Install the required libraries 

```
$ pip install -r requirements.txt
```



Contributing
------------

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request


License and Copyright
---------------------

Copyright 2014 Code for America, MIT License
