from setuptools import find_packages
from setuptools import setup


LONG_DESCRIPTION = open("README.rst").read() + "\n" + open("CHANGES.rst").read() + "\n"

setup(
    name="plone.app.iterate",
    version="5.0.2.dev0",
    description="check-out/check-in staging for Plone",
    long_description=LONG_DESCRIPTION,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "Framework :: Zope2",
        "Framework :: Zope :: 4",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="check-out check-in staging",
    author="Plone Foundation",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://pypi.org/project/plone.app.iterate",
    license="GPL version 2",
    packages=find_packages(),
    namespace_packages=["plone", "plone.app"],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "Acquisition",
        "DateTime",
        "plone.locking",
        "plone.memoize",
        "Products.CMFCore",
        "Products.CMFEditions",
        "Products.CMFPlacefulWorkflow",
        "Products.DCWorkflow",
        "Products.GenericSetup>=1.8.2",
        "Products.statusmessages",
        "setuptools",
        "zope.annotation",
        "zope.component",
        "zope.event",
        "zope.i18nmessageid",
        "zope.interface",
        "zope.lifecycleevent",
        "zope.schema",
        "zope.viewlet",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            "plone.app.contenttypes",
            "plone.app.robotframework",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
