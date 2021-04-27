"""
HubGrep request cache is modular, so we need to implement interfaces for each cache vendor that we want to allow.
The output is wrapped by CachedResponse for normalization, and a CachedSession is responsible for resolving requests.
"""
