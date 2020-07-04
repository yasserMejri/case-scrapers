""" Module containing InitializedSession class. """
import requests

class InitializedSession(requests.Session):
    """ A pre-initialized session. 
    
    This is a specialized subclass of Requests.Session
    which performs initialization when instantiated
    with some values.
    """
    def __init__(self,
                headers = {},
                initial_url=False):

        # Initialize the base class
        requests.Session.__init__(self)
        
        # If we've set a user agent string (the default)
        # update the headers to contain it.
        if 'User-Agent' not in headers:
            headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
        elif headers['User-Agent'] == False:
            del headers['User-Agent']
        self.headers.update(headers)
        # If we need to hit a page first in order to get
        # some session cookies first this is where we do it.
        # This might add an ASPSESSIONID cookie to the session.
        if initial_url:
            self.get(initial_url)