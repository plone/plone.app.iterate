from setuptools import setup, find_packages
import os

version = '1.2.4'

setup(name='plone.app.iterate',
      version=version,
      description="check-out/check-in staging for Plone",
      long_description=\
          open(os.path.join("plone", "app", "iterate", "README.txt")).read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Kapil Thangavelu',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.app.iterate',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages = ['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
        test=[
            'Products.PloneTestCase',
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
          'zope.schema',
          'zope.viewlet',
          'Products.Archetypes',
          'Products.CMFCore',
          'Products.CMFEditions',
          'Products.CMFPlacefulWorkflow',
          'Products.DCWorkflow',
          'Products.statusmessages',
          'ZODB3',
          # 'Acquisition',
          # 'DateTime',
          # 'Zope2',
      ],
      )
