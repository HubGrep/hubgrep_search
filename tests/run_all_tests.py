import unittest
import logging

def run(zappa_cli):
    loader = unittest.TestLoader()
    tests = loader.discover('.')
    test_runner = unittest.runner.TextTestRunner()
    result = test_runner.run(tests)

    if result.failures or result.errors:
        logging.error('one or more failures or errors, stopped deployment')
        exit(1)
