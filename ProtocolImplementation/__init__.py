"""
Python implementation of a custom protocol to send and receive files (binary data) over the network.

Protocol specification described in the README.md file.

This is an application-layer protocol, carried by a TCP connection, that aims to turn a simple socket stream into a
reliable way to transfer long files by sending start, end and control bytes, as well as defining and handling different
types of error.
"""