from conans import ConanFile
import os


class TestPackageConan(ConanFile):    
    def test(self):
        testdir = os.path.dirname(os.path.realpath(__file__))
        self.run("swig -python -outcurrentdir %s" % os.path.join(testdir, "test.i"))
        assert "example.py" in os.listdir(".")
