from setuptools import setup, find_packages
import sys, os

version = '1.0b2'

setup(name='plone.app.iterate',
      version=version,
      description="check-out/check-in staging for Plone",
      long_description="""\
plone.app.iterate is a check-out/check-in staging solution for Plone, 
initially released as a Zope 2 product called "iterate". It uses CMFEditions,
CMFDiffTool and other Plone 3 features.
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Kapil Thangavelu',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/plone/plone.app.iterate',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
