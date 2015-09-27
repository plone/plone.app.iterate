from setuptools import setup, find_packages

version = '3.1.3'

setup(name='plone.app.iterate',
      version=version,
      description="check-out/check-in staging for Plone",
      long_description=open("README.rst").read() + "\n" + open("CHANGES.rst").read(),
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Plone :: 5.0",
          "Framework :: Zope2",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
      ],
      keywords='check-out check-in staging',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.app.iterate',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
          test=[
              'plone.app.testing',
              'plone.app.contenttypes'
          ]
      ),
      install_requires=[
          'setuptools',
          'plone.locking',
          'plone.memoize',
          'zope.annotation',
          'zope.component',
          'zope.event',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.lifecycleevent',
          'zope.schema',
          'zope.viewlet',
          'Acquisition',
          'DateTime',
          'Products.Archetypes',
          'Products.CMFCore',
          'Products.CMFEditions',
          'Products.CMFPlacefulWorkflow',
          'Products.DCWorkflow',
          'Products.statusmessages',
          'ZODB3',
          'Zope2',
      ],
      entry_points='''
          [z3c.autoinclude.plugin]
          target = plone
      ''',
      )
