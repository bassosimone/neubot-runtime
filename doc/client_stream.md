# NAME
Client Stream -- HTTP client

# LIBRARY
Neubot Runtime

# SYNOPSIS
```python
from .http_stream import HttpStream

class HttpClientStream(HttpStream):
    def send_request(self, request):
        # Sends a request

```

# DESCRIPTION
The main method of the HTTP Client Stream class is `send_request`.

It takes one argument, `request`, that is the HTTP request which will be sent by the client.

# HISTORY
The `HTTP Client Stream` class appeared in Neubot Runtime 0.5.0.
