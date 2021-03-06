# -*- coding: utf-8 -*-
"""
Created on Fri May  4 10:00:42 2018

@author: jhoar
"""

import unittest
import pathlib
import uuid
import FileCache
import inspect
import shutil
import os
import stat

import FileCache

class FileCacheTest(unittest.TestCase):

    def setUp(self):
        self.home = pathlib.Path.home()

    def test_initEmpty(self):
        path = self.home / getUid()
        S = FileCache.StorageArea(str(path))
        self.assertTrue(S.storagePath.exists())
        shutil.rmtree(str(path))

    def test_initNotEmpty(self):
        # Setup
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        S1.addContext(ctxt)

        # Test
        S2 = FileCache.StorageArea(str(path))
        k = ctxt in S2.contexts
        self.assertTrue(k)
        shutil.rmtree(str(path))

    def test_addContext(self):
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        S1.addContext(ctxt)
        cDir = S1.storagePath / ctxt
        self.assertTrue(cDir.exists())
        shutil.rmtree(str(path))

    def test_addContextDup(self):
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        S1.addContext(ctxt)
        S1.addContext(ctxt)
        shutil.rmtree(str(path))

    def test_addContextDirExist(self):
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        dupDir = path / ctxt
        dupDir.mkdir()
        S1.addContext(ctxt, True)
        shutil.rmtree(str(path))

    def test_addContextNotWritable(self):
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        os.chmod(str(path), 0o0077)
        ctxt = getUid()
        S1.addContext(ctxt)
        os.chmod(str(path), 0o0777)
        shutil.rmtree(str(path))

    def test_delContext(self):
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        S1.addContext(ctxt)
        S1.deleteContext(ctxt)
        shutil.rmtree(str(path))

    def test_delContextNoExist(self):
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        S1.addContext(ctxt)
        S1.deleteContext('foo')
        shutil.rmtree(str(path))

    def test_delContextNotWritable(self):
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        S1.addContext(ctxt)
        S1.writable = False
        S1.deleteContext(ctxt)
        shutil.rmtree(str(path))

    def test_listContexts(self):
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        S1.addContext(ctxt)
        S1.listContexts()
        shutil.rmtree(str(path))

    def test_purge(self):
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        C1 = S1.addContext(ctxt)
        C1.addFile("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")
        C1.getFile("foo.pdf")
        C1.purge()
        shutil.rmtree(str(path))

    def test_purgeNotWritable(self):
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        C1 = S1.addContext(ctxt)
        C1.addFile("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")
        C1.getFile("foo.pdf")
        S1.writable = False
        C1.purge()
        shutil.rmtree(str(path))

    def test_addFile(self):
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        C1 = S1.addContext(ctxt)
        C1.addFile("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")
        shutil.rmtree(str(path))

    def test_addFileNotWritable(self):
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        C1 = S1.addContext(ctxt)
        S1.writable = False
        C1.addFile("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")
        shutil.rmtree(str(path))

    def test_getFile(self):
        print('test_getFile')
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        C1 = S1.addContext(ctxt)
        C1.addFile("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")
        C1.getFile("foo.pdf")
        shutil.rmtree(str(path))

    def test_getFileNotWritable(self):
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        C1 = S1.addContext(ctxt)
        C1.addFile("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")
        S1.writable = False
        C1.getFile("foo.pdf")
        shutil.rmtree(str(path))

    def test_getFileNotExists(self):
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        C1 = S1.addContext(ctxt)
        C1.addFile("http://vospace.esac.esa.int/vospace/sh/blah","foo.pdf")
        C1.getFile("foo.pdf")
        shutil.rmtree(str(path))

    def test_deleteFile(self):
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        C1 = S1.addContext(ctxt)
        C1.addFile("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")
        C1.getFile("foo.pdf")
        C1.deleteFile("foo.pdf")
        shutil.rmtree(str(path))

    def test_deleteFileNoExist(self):
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        C1 = S1.addContext(ctxt)
        C1.addFile("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")
        C1.getFile("foo.pdf")
        C1.deleteFile("foo1.pdf")
        shutil.rmtree(str(path))

    def test_deleteFileNotWritable(self):
        area = getUid()
        path = self.home / area
        S1 = FileCache.StorageArea(str(path))
        ctxt = getUid()
        C1 = S1.addContext(ctxt)
        C1.addFile("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")
        C1.getFile("foo.pdf")
        S1.writable = False
        C1.deleteFile("foo.pdf")
        shutil.rmtree(str(path))

    def test_testSimpleCache(self):
        S = FileCache.SimpleCache()
        S.load("http://vospace.esac.esa.int/vospace/sh/4807f490cec42f15d1574442881ccb1f1275bd?dl=1")
        S.get("foo.pdf")
        shutil.rmtree(str(self.home / 'EuclidCache'))

    def test_test1(self):
        S = FileCache.StorageArea(str(self.home / 'EuclidCache'))
        testContext = getUid()
        C = S.addContext(testContext)
        C.addFile("http://vospace.esac.esa.int/vospace/sh/eb9834b594e8da89111147899d15c26dd5ecf9?dl=1","foo.pdf")
        C.getFile("foo.pdf")
        C.export("export.json")
        C.deleteFile("foo.pdf")
        S.deleteContext(testContext)
        shutil.rmtree(str(self.home / 'EuclidCache'))

    def test_test2(self):
        nextContext = getUid()
        S = FileCache.StorageArea(str(self.home / 'EuclidCache'))
        C = S.addContext(nextContext)
        C.load("export.json")
        C.refresh()
        shutil.rmtree(str(self.home / 'EuclidCache'))

    def test_test3(self):
        next2Context = getUid()
        S = FileCache.StorageArea(str(self.home / 'EuclidCache'))
        C = S.addContext(next2Context)
        C.load("http://vospace.esac.esa.int/vospace/sh/4807f490cec42f15d1574442881ccb1f1275bd?dl=1")
        C.refresh()
        shutil.rmtree(str(self.home / 'EuclidCache'))

    def test_test4(self):
        next3Context = getUid()
        S = FileCache.StorageArea(str(self.home / 'EuclidCache'))
        C = S.addContext(next3Context) # TODO Should check for existing dirs
        C.addFile("http://vospace.esac.esa.int/vospace/sh/66ee2fc9964193fcc2984e35a25bdee14057f9?dl=1","ick906030_prev.fits")
        C.export("export1.json")
        C.addFile("http://vospace.esac.esa.int/vospace/sp/e09e212133c2c61093431c4eb13ed16e7e31bb36?dl=2","1525190698647O-result.vot")
        C.export("export2.json")
        S.deleteContext(next3Context) # TODO Check for context
        shutil.rmtree(str(self.home / 'EuclidCache'))

    def test_test5(self):
        S = FileCache.StorageArea(str(self.home / 'EuclidCache'))
        S.listContexts()
        shutil.rmtree(str(self.home / 'EuclidCache'))


'''
      self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)
'''

def getUid():
    return str(uuid.uuid4())[:8]

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase( FileCacheTest )
    unittest.TextTestRunner(verbosity=2).run(suite)
