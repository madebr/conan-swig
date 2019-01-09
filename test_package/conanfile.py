#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from conans import ConanFile
import os


class TestPackageConan(ConanFile):

    def test(self):
        self.run("swig -version")
        self.run("swig -swiglib") # TODO we should generate some code for testing...
