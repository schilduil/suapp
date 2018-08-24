# SchildUil Application (suapp)

SuApp is a framework for building flexible, extendible database based applications in Python3.

*In a stage that is still far from useful.*

It has 3 main components:

* *The data part*: (ab/u)sing PonyORM
* *The application flow*: how the user and data navigates from window to window.
* *The target*: the user interface (flexible, see below).

The original intention was to make the (G)UI part tkinter, but it can support several 'targets'. The most worked out target at the moment is localweb:

* *localweb*: launches a webserver on localhost:8385 and a browser pointing to it. Uses bootstrap.
* *tk*: launches a tkinter application.
* *test*: command line to make testing of the non-target parts of SuApp easier.
