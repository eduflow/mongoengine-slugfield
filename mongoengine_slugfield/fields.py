import re

from mongoengine.errors import ValidationError
from mongoengine.fields import StringField
from mongoengine import signals
from slugify import Slugify


__all__ = ('SlugField')


def create_slug_signal(sender, document):
    for fieldname, field in document._fields.iteritems():
        if isinstance(field, SlugField):
            if document.pk and not getattr(field, 'always_update'):
                continue

            document._data[fieldname] = field._generate_slug(
                document,
                getattr(document, field.populate_from or fieldname)
            )


class SlugField(StringField):

    """A field that that produces a slug from the inputs and auto-
    increments the slug if the value already exists."""

    def __init__(self, *args, **kwargs):
        self.populate_from = kwargs.pop('populate_from', None)
        self.always_update = kwargs.pop('always_update', False)
        self.allow_unicode = kwargs.pop('allow_unicode', True)
        self.queryset_manager = kwargs.pop('queryset_manager', 'objects')
        kwargs['unique'] = True

        slugify_kwargs = kwargs.pop('slugify_kwargs', {})
        self.slugify_kwargs = slugify_kwargs
        # Always use lowercase slugs
        slugify_kwargs['to_lower'] = True
        if self.allow_unicode:
            self._slugify = Slugify(translate=None, **slugify_kwargs)
        else:
            self._slugify = Slugify(**slugify_kwargs)

        super(SlugField, self).__init__(*args, **kwargs)

    def _generate_slug(self, instance, value):
        count = 1
        slug = slug_attempt = self._slugify(value)
        cls = instance.__class__
        while getattr(cls, self.queryset_manager)(**{self.db_field: slug_attempt}).count() > 0:
            slug_attempt = '%s-%s' % (slug, count)
            count += 1
        return slug_attempt

    def __get__(self, instance, owner):
        # mongoengine calls this after document initialization
        if not hasattr(self, 'owner'):
            self.owner = owner
            signals.pre_save.connect(create_slug_signal, sender=owner)

        return super(SlugField, self).__get__(instance, owner)
