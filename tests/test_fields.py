# -*- coding: utf-8 -*-
import pytest

from mongoengine import BooleanField, Document, queryset_manager, StringField
from mongoengine.errors import NotUniqueError, ValidationError
from mongoengine_slugfield.fields import SlugField


def test_auto_slug_creation(conn):
    """Ensure that slugs are automatically created and kept unique.
    """

    # Four scenarios:
    # (1) No match is found, this is a brand new slug
    # (2) A matching document is found, but it's this one
    # (3) A matching document is found but without any number
    # (4) A matching document is found with an incrementing value

    class Article(Document):
        title = StringField()
        slug = SlugField()

    first_doc = Article()
    first_doc.slug = 'My document title'
    first_doc.save()
    first_doc.reload()
    assert first_doc.slug == 'my-document-title'

    # Shouldn't be increasing the count if the document instance
    # is already counted.
    first_doc.slug = 'my-document-title'
    first_doc.save()
    assert first_doc.slug == 'my-document-title'

    second_doc = Article()
    second_doc.slug = 'My document title'
    second_doc.save()
    assert second_doc.slug == 'my-document-title-1'

    third_doc = Article()
    third_doc.slug = 'My document title'
    third_doc.save()
    assert third_doc.slug == 'my-document-title-2'


def test_auto_slug_nonalphachars(conn):
    class Article(Document):
        title = StringField()
        slug = SlugField()

    article = Article()
    article.slug = " Here's a nice headline, enjoy it?/"
    article.save()
    assert article.slug == 'heres-a-nice-headline-enjoy-it'


def test_SlugField_populate_from(auto_slug_document):
    document = auto_slug_document()
    document.name = 'Auto Slug Document'
    document.save()
    assert document.slug == 'auto-slug-document'


def test_SlugField_generate_next_slug(auto_slug_document):
    document = auto_slug_document()
    document.name = 'Auto Slug Document'
    document.save()
    assert document.slug == 'auto-slug-document'

    document = auto_slug_document()
    document.name = 'Auto Slug Document'
    document.save()
    assert document.slug == 'auto-slug-document-1'

    document = auto_slug_document()
    document.name = 'Auto Slug Document'
    document.save()
    assert document.slug == 'auto-slug-document-2'


def test_SlugField_doesnt_change_after_saving(auto_slug_document):
    document = auto_slug_document()
    document.name = 'Auto Slug Document'
    document.save()
    assert document.slug == 'auto-slug-document'

    document.save()
    assert document.slug == 'auto-slug-document'

    document = auto_slug_document.objects.first()
    document.save()
    assert document.slug == 'auto-slug-document'


def test_multiple_autoslug_fields(conn):
    class FooDocument(Document):
        name = StringField()
        name1 = StringField()
        slug = SlugField(populate_from='name')
        slug1 = SlugField(populate_from='name1')

    document = FooDocument()
    document.name = 'Auto Slug Document'
    document.name1 = 'Auto Slug Document'
    document.save()

    assert document.slug == 'auto-slug-document'
    assert document.slug1 == 'auto-slug-document'

    document = FooDocument.objects.first()
    assert document.slug == 'auto-slug-document'
    assert document.slug1 == 'auto-slug-document'


def test_always_update_autoslug_field_must_change(conn):
    class AutoUpdateDocument(Document):
        name = StringField()
        slug = SlugField(populate_from='name', always_update=True)

    document = AutoUpdateDocument()
    document.name = 'Auto Slug Document'
    document.save()
    assert document.slug == 'auto-slug-document'

    document.name = 'I Can Haz New Slug'
    document.save()
    assert document.slug == 'i-can-haz-new-slug'


def test_unicode_slugify(conn):
    class PageWithUnicodeSlug(Document):
        title = StringField()
        slug = SlugField(populate_from='title')

    document = PageWithUnicodeSlug(title='Мобильные технологии в образовании')
    document.save()

    assert document.slug == 'мобильные-технологии-в-образовании'


def test_no_unicode_slugify(conn):
    class PageWithUnicodeSlug(Document):
        title = StringField()
        slug = SlugField(populate_from='title', allow_unicode=False)

    document = PageWithUnicodeSlug(title='Мобильные технологии в образовании')
    document.save()

    assert document.slug == 'mobilnye-tekhnologii-v-obrazovanii'


def test_slugify(conn):
    class Page(Document):
        title = StringField()
        slug = SlugField(populate_from='title')
    page = Page(title='Я ♥ борщ').save()
    assert page.slug == '\u044f-\u0431\u043e\u0440\u0449'
    # >>> print page.slug
    # я-борщ


def test_allow_unicode(conn):
    '''Test that setting `allow_unicode` to `False` will transliterate unicode
    characters to ascii'''
    class Page(Document):
        title = StringField()
        slug = SlugField(populate_from='title', allow_unicode=False)
    page = Page(title='Я ♥ борщ').save()
    assert page.slug == 'ia-borshch'


def test_slugify_kwargs(conn):
    '''Test than parameters can be passed directly to `awesome-slugify`'s
    `Slugify()`-class with `slugify_kwargs`'''
    custom_slugify_args = {'pretranslate': {'я': 'i', '♥': 'love'}}
    class Page(Document):
        title = StringField()
        slug = SlugField(populate_from='title', allow_unicode=False, slugify_kwargs=custom_slugify_args)
    page = Page(title='Я ♥ борщ').save()
    assert page.title == '\u042f \u2665 \u0431\u043e\u0440\u0449'
    assert page.slug == 'i-love-borshch'


def test_custom_queryset(conn):
    """Test that it's possible to use a custom queryset the document having
    the SlugField
    """

    # Four scenarios:
    # (1) No match is found, this is a brand new slug
    # (2) A matching document is found, but it's this one
    # (3) A matching document is found but without any number
    # (4) A matching document is found with an incrementing value

    class Page(Document):
        title = StringField()
        slug = SlugField(populate_from='title')
        is_draft = BooleanField(default=True)

        @queryset_manager
        def objects(doc_cls, queryset):
            # By default -- never show drafts courses
            return queryset.filter(is_draft=False)

        @queryset_manager
        def draft_objects(doc_cls, queryset):
            return queryset.filter(is_draft=True)

        @queryset_manager
        def all_objects(doc_cls, queryset):
            # Use `Page.all_objects()` to access all pages (drafts and non-drafts)
            return queryset

    page1 = Page(title='Front page').save()
    with pytest.raises(NotUniqueError):
        page2 = Page(title='Front page').save()

    class Page(Document):
        title = StringField()
        slug = SlugField(populate_from='title', queryset_manager='all_objects')
        is_draft = BooleanField(default=True)

        @queryset_manager
        def objects(doc_cls, queryset):
            # By default -- never show drafts courses
            return queryset.filter(is_draft=False)

        @queryset_manager
        def draft_objects(doc_cls, queryset):
            return queryset.filter(is_draft=True)

        @queryset_manager
        def all_objects(doc_cls, queryset):
            # Use `Page.all_objects()` to access all pages (drafts and non-drafts)
            return queryset

    page3 = Page(title='About page').save()
    page4 = Page(title='About page').save()
    assert page4.slug == 'about-page-1'
