#
# Copyright (c) 2018 Red Hat, Inc.
#
# This file is part of gluster-plus-one-scale project which is a
# subproject of GlusterFS ( www.gluster.org)
#
# This file is licensed to you under your choice of the GNU Lesser
# General Public License, version 3 or any later version (LGPLv3 or
# later), or the GNU General Public License, version 2 (GPLv2), in all
# cases as published by the Free Software Foundation.

from setuptools import setup


setup(
    name="gluster-plus-one-scale",
    version="0.1",
    packages=["glusterhealth", "glusterhealth.reports"],
    include_package_data=True,
    install_requires=["glustercli"],
    entry_points={
        "console_scripts": [
            "gluster-health-report = glusterhealth.main:main"
        ]
    },
    platforms="linux",
    zip_safe=False,
    author="Gluster Developers",
    author_email="gluster-devel@gluster.org",
    description="Gluster Plus One scale API's and Script",
    license="GPLv2",
    keywords="gluster, tool, health",
    url="https://github.com/gluster/gluster-plus-one-scale",
    long_description="""
    Gluster Plus One Scale
    """,
    classifiers=[
        "Development Status :: Beta",
        "Topic :: Utilities",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
    ],
)
