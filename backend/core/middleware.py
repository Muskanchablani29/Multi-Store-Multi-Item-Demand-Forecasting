class NoBFCacheMiddleware:
    """
    Sets Cache-Control: no-store on every API response.
    This opts the page out of the browser Back-Forward Cache (bfcache),
    which prevents Chrome from suspending in-flight XHR requests
    (ERR_NETWORK_IO_SUSPENDED) when the user navigates back/forward
    while a long-running request (e.g. ML training) is still in progress.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith('/api/'):
            response['Cache-Control'] = 'no-store'
        return response
