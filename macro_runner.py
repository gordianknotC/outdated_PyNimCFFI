# -*- coding: utf-8 -*-
import sys, importlib, os
sys.path.append(os.path.join(__file__, '../../python_macro'))
from karnickel import install_hook
importer = install_hook()
#import example.test

def execute(*args):
    basepath = os.path.abspath(os.path.curdir)
    for arg in args:
        repath = os.path.relpath( arg, os.path.abspath(os.path.curdir))
        repath = repath.replace( '\\','.')[:-3]
        importlib.import_module(repath)

if __name__ == '__main__':
    arg = r'nimlang.py'
    if len(sys.argv) == 1: execute( arg )
    else:                  execute( *sys.argv[1:] )


