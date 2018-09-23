# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


LONG_DESCRIPTION = (
    open('README.rst').read() +
    '\n' +
    open('CHANGES.rst').read() +
    '\n')

setup(
    name='plone.app.iterate',
    version='3.3.9',
    description='check-out/check-in staging for Plone',
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Framework :: Plone :: 5.1',
        'Framework :: Plone :: 5.2',
        'Framework :: Zope2',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='check-out check-in staging',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://pypi.python.org/pypi/plone.app.iterate',
    license='GPL version 2',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['plone', 'plone.app'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Acquisition',
        'DateTime',
        'plone.locking',
        'plone.memoize',
        'Products.CMFCore',
        'Products.CMFEditions',
        'Products.CMFPlacefulWorkflow',
        'Products.DCWorkflow',
        'Products.GenericSetup>=1.8.2',
        'Products.statusmessages',
        'setuptools',
        'zope.annotation',
        'zope.component',
        'zope.event',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.schema',
        'zope.viewlet',
    ],
    extras_require={
        'archetypes': [
            'Products.Archetypes',
        ],
        'test': [
            'plone.app.testing',
            'plone.app.contenttypes',
            'plone.app.robotframework',
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
