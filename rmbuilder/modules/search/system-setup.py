#!/usr/bin/env python3

import sys
import os
import argparse

HERE = os.path.abspath(os.path.dirname(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
READIES = os.path.join(ROOT, "deps/readies")
sys.path.insert(0, READIES)
import paella

#----------------------------------------------------------------------------------------------

class RediSearchSetup(paella.Setup):
    def __init__(self, nop=False):
        paella.Setup.__init__(self, nop)

    def common_first(self):
        self.install_downloaders()
        self.pip_install("wheel")
        self.pip_install("setuptools --upgrade")

        self.run("%s/bin/enable-utf8" % READIES)
        self.install("git rsync")

    def debian_compat(self):
        self.install("libatomic1")
        self.run("%s/bin/getgcc" % READIES)

        if self.platform.is_arm() and self.dist == 'ubuntu' and self.os_version[0] < 20:
            self.install("python-gevent")
        self.install("python-dev")

    def redhat_compat(self):
        self.install("redhat-lsb-core")
        self.install("libatomic")

        self.run("%s/bin/getgcc --modern" % READIES)

        # fix setuptools
        self.pip_install("-IU --force-reinstall setuptools")

        if self.platform.is_arm():
            self.install("python-gevent")
        self.install("python2-devel")

    def archlinux(self):
        self.install("gcc-libs")

    def fedora(self):
        self.install("libatomic")
        self.run("%s/bin/getgcc" % READIES)

    def macos(self):
        self.install_gnu_utils()
        self.install("pkg-config")

        # for now depending on redis from brew, it's version6 with TLS.
        self.run("{PYTHON} {READIES}/bin/getredis -v 6 --force".format(PYTHON=self.python, READIES=READIES))

    def common_last(self):
        self.run("{PYTHON} {READIES}/bin/getcmake".format(PYTHON=self.python, READIES=READIES))
        # self.run("{PYTHON} {READIES}/bin/getrmpytools --reinstall".format(PYTHON=self.python, READIES=READIES))
        if self.dist != "arch":
            self.install("lcov")
        else:
            self.install("lcov-git", aur=True)
        self.pip_install("pudb awscli")

        if int(sh("{PYTHON} -c 'import gevent' 2> /dev/null; echo $?".format(PYTHON=self.python))) != 0:
            self.pip_install("gevent")

        # self.pip_install("-r %s/tests/pytests/requirements.txt" % ROOT)

#----------------------------------------------------------------------------------------------

parser = argparse.ArgumentParser(description='Set up system for build.')
parser.add_argument('-n', '--nop', action="store_true", help='no operation')
args = parser.parse_args()

RediSearchSetup(nop = args.nop).setup()
