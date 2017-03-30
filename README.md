mongoengine-slugfield
=====================

`mongoengine-slugfield` is a fork of [bennylope/mongoengine-extras] that
only seeks to implement `SlugField` (similar to `AutoSlugField` in the
original package) and uses the [dimka665/awesome-slugify]-package
to slugify.

The raison d'être for this package is two-fold:

1. The original `AutoSlugField` doesn't work for strings that are fully unicode,
   e.g. `Мобильные технологии в образовании`
   – Using `AutoSlugField` on the above string will create an "empty" slug, causing an error.
2. This package is meant to only contain `SlugField` – no other fields.

Note that this package will slugify to slugs _with_ unicode chars by default, e.g.:

    u'ættarsamfélagið'

will be slugified to:

    u'ættarsamfélagið'  # this package (mongoengine_slugfield)
    u'ttarsamfelagi'    # mongoengine_extras

[bennylope/mongoengine-extras]: https://github.com/bennylope/mongoengine-extras
[dimka665/awesome-slugify]: https://github.com/dimka665/awesome-slugify

Case-sensitivity
----------------
Currently `mongoengine-slugfield` will make all slugs lowercase, even though
this isn't the `awesome-slugify` default. This is because we use MongoDB's
`unique`-index to test for already existing slugs (duplicate slugs).

MongoDB only supports case-insensitive `unique`-indexes since 3.4.0, and
therefore we always use lowercase to ensure uniqueness.

See: <http://stackoverflow.com/questions/33736192/mongo-unique-index-case-insensitive>

Installing
----------

Using pip:

    pip install 'git+git://github.com/peergradeio/mongoengine-slugfield.git@master#egg=mongoengine-slugfield'

"Hands on" developers can do a git clone into their virtualenv like this:

    pip install -e 'git+git@github.com:peergradeio/mongoengine-slugfield.git#egg=mongoengine-slugfield'

Usage
-----
Import `SlugField` from this package

    >>> from mongoengine_slugfield import SlugField

and then use as you would a normal MongoEngine field.
The `populate_from`-parameter determines which field to create the slug from:

    >>> class Page(Document):
    ...     title = StringField()
    ...     slug = SlugField(populate_from='title')
    >>> page = Page(title=u'Я ♥ борщ').save()
    >>> page.slug
    u'я-борщ''

setting `allow_unicode` to `False` will transliterate unicode characters to ascii  
(`allow_unicode` is `True` by default)

    >> class Page(Document):
    ..     title = StringField()
    ..     slug = SlugField(populate_from='title', allow_unicode=False)
    >> page = Page(title=u'Я ♥ борщ').save()
    >> page.slug
    u'ia-borshch'

you can pass parameters directly to `awesome-slugify`'s `Slugify()`-class
with `slugify_kwargs`

    >>> from __future__ import unicode_literals
    >>> custom_slugify_args = {'pretranslate': {u'я': u'i', u'♥': u'love'}}
    >>> class Page(Document):
    ...     title = StringField()
    ...     slug = SlugField(populate_from='title', allow_unicode=True, slugify_kwargs=custom_slugify_args)
    >>> page = Page(title=u'Я ♥ борщ').save()
    >>> page.slug
    u'i-love-borshch'


lastly if you use a custom queryset for `objects`, you can make `SlugField` use
a different attribute to look up duplicates:

    >>> class Page(Document):
    ...     title = StringField()
    ...     slug = SlugField(populate_from='title', queryset_manager='all_objects')
    ...     is_draft = BooleanField(default=True)
    ...
    ...     @queryset_manager
    ...     def objects(doc_cls, queryset):
    ...         # By default -- never show drafts courses
    ...         return queryset.filter(draft=False)
    ...
    ...     @queryset_manager
    ...     def draft_objects(doc_cls, queryset):
    ...         return queryset.filter(draft=True)
    ...
    ...     @queryset_manager
    ...     def all_objects(doc_cls, queryset):
    ...         # Use `Page.all_objects()` to access all pages (drafts and non-drafts)
    ...         return queryset
    ...
    >>> page1 = Page(title=u'Front page').save()
    >>> page2 = Page(title=u'Front page').save()
    >>> page2.slug
    u'front-page-1'

Dependencies
------------
Tested with following versions:

* awesome-slugify 1.6.5
* mongoengine 0.11.0
* blinker 1.4

mongoengine-slugfield requires MongoEngine (which requires pymongo).

Tests
-----
To run the tests first install `pytest` (tested with version 3.0.6)

    pip install pytest

And then run the tests with

    py.test

Tests require a MongoDB database running on the standard port.

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
