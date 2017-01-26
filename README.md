mongoengine-slugfield
=====================

`mongoengine-slugfield` is a fork of [bennylope/mongoengine-extras] that
only seeks to implement `SlugField` (similar to `AutoSlugField` in the
original packaage) and uses the [dimka665/awesome-slugify]-package
to slugify.

The raison d'être for this package is two-fold:

1. The original `AutoSlugField` doesn't work for string that are fully unicode,
   e.g. `Мобильные технологии в образовании`  
   -- Using `AutoSlugField` on the above string will create an "empty" slug, causing an error.
2. This package meant to only contain `SlugField` -- no other fields.
  

[dimka665/awesome-slugify]: https://github.com/dimka665/awesome-slugify

Installing
----------

Using pip:

    pip install 'git+git@github.com:peergradeio/mongoengine-slugfield.git#egg=mongoengine-slugfield'


Or download the source, and run

    python setup.py install

Dependencies
------------

mongoengine-slugfield requires MongoEngine (which requires pymongo).

Tests
-----

The tests can by run with `python setup.py test`. Tests require a MongoDB 
database running on the standard port.

Authors
-------

### mongoengine-slugfield package

* Malthe Jørgensen (@malthejorgensen <https://github.com/malthejorgensen>)

### mongoengine-extras package

* Ben Lopatin (@bennylope <https://github.com/bennylope>)
* Esteban Feldman (@eka <https://github.com/eka>)

Inspiration
-----------
* https://www.pydanny.com/awesome-slugify-human-readable-url-slugs-from-any-string.html
* https://github.com/mozilla/unicode-slugify

License
-------

Public domain
