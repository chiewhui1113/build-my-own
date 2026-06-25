# Let's Build A Web Server — Learning Summary

My notes from working through Ruslan Spivak's "Let's Build A Web Server" (LSBAWS) tutorial,
rebuilding an HTTP server from sockets up to a concurrent, framework-compatible server.

**Difficulty:** ⭐⭐ — fun, with visual components (drawings) and easy to grasp. Good for beginners.

## Part 1 — A bare-bones socket server (`part1/webserver1.py`)

Key things I learned:

- A **socket** is one endpoint of a network connection. `AF_INET` = IPv4, `SOCK_STREAM` = TCP.
- The server lifecycle is: create socket → `setsockopt(SO_REUSEADDR)` (reuse the port right away
  instead of waiting through TIME_WAIT) → `bind()` to an address → `listen()` → loop on `accept()`.
- `accept()` **blocks** until a client connects, then returns a new connection socket.
- I read the request with `recv(1024)` and write back a hardcoded raw HTTP response
  (`HTTP/1.1 200 OK` + body), then `close()` the connection.

Takeaway: HTTP is just text sent over a TCP socket

## Part 2 — A WSGI server (`part2/webserver2.py`)

Turned the toy server into one that can actually run real Python web frameworks 
by implementing the **WSGI** interface.

Key things I learned:

- **WSGI** is the contract between a web server and a Python app. The server calls
  `application(environ, start_response)` and gets back an iterable that becomes the response body.
- I parse the request line into method / path / version (`GET /hello HTTP/1.1`).
- `get_environ()` builds the `environ` dict (CGI vars like `REQUEST_METHOD`, `PATH_INFO`,
  plus `wsgi.*` keys) that the app reads.
- `start_response(status, headers)` is the callback the app uses to set the status and headers;
  the server stashes them and adds its own (`Date`, `Server`).
- `finish_response()` stitches status + headers + body into a raw HTTP response and sends it.

Same framework code runs unchanged because they all speak WSGI. 

## Part 3 — Concurrency (`part3/webserver3a.py` → `3g.py`)

The progression:

- **3a** — Iterative server: handles one request at a time.
- **3b** — Adds `sleep(60)` to *prove* the problem: while one client is being served,
  everyone else is blocked.
- **3c** — Concurrent server using `os.fork()`: parent keeps `accept()`ing, each child handles
  one request. Parent and child each close their **duplicate** copy of the socket descriptors.
- **3d** — Shows what goes wrong if the parent doesn't close its copy of the client connection.
- **3e** — **Zombie processes**: finished children that the parent never reaped. Introduces a
  `SIGCHLD` handler (`grim_reaper`) calling `os.wait()`.
- **3f** — `accept()` gets interrupted by the `SIGCHLD` signal and raises `EINTR`; fix is to
  catch it and restart the `accept()` call.
- **3g** — Final version: reaps *all* pending children in a loop with
  `os.waitpid(-1, os.WNOHANG)`, because signals can coalesce and one handler call may need to
  clean up several children.

`client3.py` is a test client that forks many connections at once to stress the server.

Key things I learned:

- `fork()` duplicates the process; both copies share open file descriptors, so each side must
  close the ones it doesn't need.
- Child processes must be **reaped** or they become zombies.
- Signals can interrupt blocking system calls (`EINTR`) and can be merged, so handlers must be
  written defensively.

## Quick reference

| Part | File(s) | Concept |
|------|---------|---------|
| 1 | `webserver1.py` | Raw sockets + minimal HTTP |
| 2 | `webserver2.py`, `*app.py` | WSGI server for real frameworks |
| 3 | `webserver3a–g.py`, `client3.py` | Concurrency via `fork()`, reaping, signals |

Source tutorial: [Ruslan Spivak, *Let's Build A Web Server* (Parts 1–3)](https://ruslanspivak.com/lsbaws-part1/)
