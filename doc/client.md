# NAME
Client -- HTTP client

# LIBRARY
Neubot Runtime

# SYNOPSIS
```python
from neubot_runtime.http_client import HttpClient

class MyClient(HttpClient):
    def connection_ready(self, stream):
        # Use stream and message to send a request

    def got_response(self, stream, request, response):
        # Process the whole response

```

# DESCRIPTION
The HTTP Client class allows you to send and receive HTTP Request.

To do this you have to override in your own class principally two methods, `connection_ready()` and `got_response()`.

The first method is invoked when the connection is ready, it takes one argument, `stream`, which is a stream object from [http_client_stream](/client_stream).

The second method is invoked when the response headers and body are received, it takes three arguments: `stream`, in the same way of the previous method; `request`, the HTTP request made by the client; `response`, i.e. the HTTP response received by the client.

# HISTORY
The `HTTP Client` class appeared in Neubot Runtime 0.5.0.
