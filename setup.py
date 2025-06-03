from pathlib import Path
from setuptools import find_packages
from setuptools import setup


version = "6.2.0"

long_description = (
    f"{Path('README.rst').read_text()}\n{Path('CHANGES.rst').read_text()}"
)

setup(
    name="plone.app.iterate",
    version=version,
    description="check-out/check-in staging for Plone",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # Get more strings from
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 5",
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
        "plone.app.relationfield",
        "plone.indexer",
        "plone.locking",
        "plone.memoize",
        "Products.CMFEditions",
        "Products.CMFPlacefulWorkflow",
        "Products.DCWorkflow",
        "Products.GenericSetup>=1.8.2",
        "Products.statusmessages",
        "setuptools",
        "Zope",
        "plone.app.layout",
        "plone.base",
        "plone.dexterity",
        "plone.registry",
        "z3c.relationfield",
        "zc.relation",
        "zope.intid",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            "plone.app.contenttypes[test]",
            "plone.testing",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
