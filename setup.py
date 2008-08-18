from setuptools import setup, find_packages
import os

version = '1.1.5'

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
      url='http://svn.plone.org/svn/plone/plone.app.iterate',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages = ['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          "plone.locking",
      ],
      )
