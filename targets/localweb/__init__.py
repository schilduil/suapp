#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import http.server
from threading import Thread
import os.path
import webbrowser

import suapp.jandw
from logdecorator import *


html_template = """<html>
    <head>
        <title>%(title)s</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta charset="utf-8">

        <!-- Bootstrap -->
        <link href="/css/bootstrap/3.3.5/bootstrap.min.css" rel="stylesheet" media="screen">
        <link href="/css/site.css" rel="stylesheet" media="screen">
        <link href="/css/syntax.css" rel="stylesheet" media="screen">

        <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
        <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
        <!--[if lt IE 9]>
            <script src="/js/html5shiv/3.7.0/html5shiv.js"></script>
            <script src="/js/respond.js/1.3.0/respond.min.js"></script>
        <![endif]-->

    </head>
    <body>

%(body)s

        <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
        <!-- <script src="https://code.jquery.com/jquery.js"></script> -->
        <script src="/js/jquery/2.1.4/jquery.min.js"></script>
        <!-- Include all compiled plugins (below), or include individual files as needed -->
        <script src="/js/bootstrap/3.3.5/bootstrap.min.js"></script>

    </body>
</html>"""

#            <script src="/js/html5shiv/3.7.0/html5shiv.js"></script>
#            <script src="/js/respond.js/1.3.0/respond.min.js"></script>

#            <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
#            <script src="https://oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js"></script>


class LocalWebHandler(http.server.BaseHTTPRequestHandler):

    jeeves = None
    start = None

    @loguse
    def content_main(self, jeeves, drone, prefix = None):
        if not prefix:
            prefix = ""
        dataobject = None
        if drone:
            if drone.dataobject:
                dataobject = drone.dataobject
        if not dataobject:
            dataobject = {}
        if not 'name' in dataobject:
            dataobject['name'] = 'SuApp'
        name = dataobject['name']
        output = []
        tables = None
        if 'tables' in dataobject:
            logging.getLogger(__name__).debug(": Application[%r].inflow() : Setting tables." % (self))
            tables = dataobject['tables']
        output.append(prefix + '<!-- %s // -->' % (tables))
        if drone:
            output.append(prefix + '<!-- Entered with mode %s // -->' % (drone.mode))
        output.append(prefix + '<!-- Fixed navbar // -->')
        output.append(prefix + '<div class="navbar navbar-default navbar-fixed-top">')
        output.append(prefix + '\t<div class="container">')
        output.append(prefix + '\t\t<div class="navbar-header">')
        output.append(prefix + '\t\t\t<button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">')
        output.append(prefix + '\t\t\t\t<span class="icon-bar"></span>')
        output.append(prefix + '\t\t\t\t<span class="icon-bar"></span>')
        output.append(prefix + '\t\t\t\t<span class="icon-bar"></span>')
        output.append(prefix + '\t\t\t</button>')
        output.append(prefix + '\t\t\t<a class="navbar-brand" href="/">%s</a>' % (name))
        output.append(prefix + '\t\t</div>')
        output.append(prefix + '\t\t<div class="navbar-collapse collapse">')
        output.append(prefix + '\t\t\t<ul class="nav navbar-nav navbar-left">')
        output.append(prefix + '\t\t\t\t<li><a href="/">%s</a></li>' % (name))
        # TODO: for now this is only 2 deep, perhaps we should make this multilevel.
        menu = {"File": {"Quit": "EXIT"}, "Help": {"About": "ABOUT", "Configuration": "CONFIGURATION"}}
        for menu_name,menu_sub in menu.items():
            if type(menu_sub) == type(menu):
                output.append(prefix + '\t\t\t\t<li class="dropdown">')
                output.append(prefix + '\t\t\t\t\t<a href="/%s" class="dropdown-toggle" data-toggle="dropdown">%s <b class="caret"></b></a>' % (menu_name, menu_name))
                output.append(prefix + '\t\t\t\t\t<ul class="dropdown-menu">')
                for label,outmessage in menu_sub.items():
                    output.append(prefix + '\t\t\t\t\t\t<li><a href="/?OUT=%s">%s</a></li>' % (outmessage, label))
                output.append(prefix + '\t\t\t\t\t</ul>')
                output.append(prefix + '\t\t\t\t</li>')
            else:
                output.append(prefix + '\t\t\t\t<li><a href="/?OUT=%s">Stefaan</a></li>' % (menu_sub))
        output.append(prefix + '\t\t\t\t</li>')
        output.append(prefix + '\t\t\t</ul>')

        #output.append(prefix + '\t\t\t<form class="navbar-form navbar-left" action="/search.html" role="search">')
        #output.append(prefix + '\t\t\t\t<div class="form-group">')
        #output.append(prefix + '\t\t\t\t\t<input type="text" required name="q" id="tipue_search_input" class="form-control" placeholder="Search">')
        #output.append(prefix + '\t\t\t\t</div>')
        #output.append(prefix + '\t\t\t</form>')

        #output.append(prefix + '\t\t\t<ul class="nav navbar-nav navbar-right">')
        #output.append(prefix + '\t\t\t\t<li><a href="/seealso.html">See also</a></li>')
        #output.append(prefix + '\t\t\t</ul>')

        output.append(prefix + '\t\t</div><!--/.nav-collapse -->')
        output.append(prefix + '\t</div>')
        output.append(prefix + '</div>')

        output.append(prefix + '<div class="container">')
        output.append(prefix + '\t<ol class="breadcrumb">')
        #output.append(prefix + '\t\t<li><a href="/">Home</a></li>')
        output.append(prefix + '\t\t<li class="active">Home</li>')
        output.append(prefix + '\t</ol>')
        output.append(prefix + '<div class="page-header">')
        output.append(prefix + '\t<h1>%s</h1>' % (name))
        output.append(prefix + '</div>')

        output.append(prefix + '<div class="row">')
        output.append(prefix + '\t<div class="content">')
        output.append(prefix + '\t\t<div class="col-md-7" role="main">')
        #output.append(prefix + '\t\t\t<ul class="pager">')
        #output.append(prefix + '\t\t\t\t<li class="next"><a href="/stefaan.html">Stefaan &rarr;</a></li>')
        #output.append(prefix + '\t\t\t</ul>')

        output.append(prefix + '\t\t\t<main>')
        output.append(prefix + '\t\t\t\t<p>')
        # TODO
        output.append(prefix + '\t\t\t\t</p>')
        output.append(prefix + '\t\t\t</main>')

        #output.append(prefix + '\t\t\t<ul class="pager">')
        #output.append(prefix + '\t\t\t\t<li class="previous"><a href="/start.html">&larr; Partnership SBR</a></li>')
        #output.append(prefix + '\t\t\t\t<li class="next"><a href="/stefaan.html">Stefaan &rarr;</a></li>')
        #output.append(prefix + '\t\t\t</ul>')

        output.append(prefix + '\t\t</div>')
        output.append(prefix + '\t</div>')

        # Possibly have TOC here.

        output.append(prefix + '\t<div class="footer">')
        output.append(prefix + '\t\t<p>This website is powered by <a href="http://suapp.schilduil.com/" target="_blank">SuApp</a></p>')
        output.append(prefix + '\t</div>')

        output.append(prefix + '</div>')
        return (name, "\n".join(output))

    @loguse
    def do_GET(self):
        static = False
        mimetype = "text/html"
        if self.path.startswith("/css/"):
            static = True
            mimetype = "text/css"
        elif self.path.startswith("/js/"):
            static = True
            mimetype = "text/js"
        if static:
            # Static content: css, js, ...
            try:
                localfile = os.path.join(os.path.dirname(__file__), self.path[1:])
                with open(localfile, 'rb') as f:
                    self.send_response(200)
                    self.send_header('Content-type','text/css')
                    self.end_headers()
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                message = "File %s not found.\n%s" % (self.path, localfile)
                self.wfile.write(message.encode('utf-8'))
            return

        message = ""
        try:
            (title, body) = self.content_main(LocalWebHandler.jeeves, LocalWebHandler.start, "        ")
            # AOK
            self.send_response(200)
            # It's HTML in unicode (UTF-8)
            self.send_header('Content-type','text/html; charset=utf-8')
            self.end_headers()
            # Send the html message
            message = html_template % {
                'title': title,
                'body': body
            }
        except err:
            # ERROR
            self.send_response(500)
            # It's just text with the error message.
            self.send_header('Content-type','text/plain; charset=utf-8')
            # Message
            message = "%s" % (err)

        self.wfile.write(message.encode("utf-8"))
        return

    def log_message(self, format, *args):
        # Logging to modules.httpd logger.
        # It is recommended to have a special entry in the configuration for this:
        # ...
        #       "modules": {
        #            ...
        #            "httpd": {
        #                "level": "DEBUG",
        #                "filename": "~/.suapp/log/httpd.accces_log"
        #            }
        #            ...
        # ...
        logging.getLogger("modules.httpd").debug("[%s] %s - - [%s] %s" % (hex(hash(self)), self.address_string(),self.log_date_time_string(),format%args))


class BrowserThread(Thread):

    # @loguse seems to break it.
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        super().__init__()
    
    @loguse
    def run(self):
        import time
        # Waiting for x seconds to be sure the http server is up.
        time.sleep(0)
        webbrowser.open("http://%s:%s/" % (self.ip, self.port))


class Application(suapp.jandw.Wooster):

    @loguse
    def __init__(self, master=None):
        self.name = "Application"
        self.jeeves = None
        self.dataobject = None
        self.testdata = {"ID": "(150112)164", "ring": "BGC/BR23/10/164"}
        self.tables = {}
    
    @loguse
    def inflow(self, jeeves, drone):
        # The port by default is ord(S)+10 + ord(U)
        self.port = 8385 # SU
        self.ip = "127.0.0.1"
        if "httpd" in jeeves.app.configuration:
            if "port" in jeeves.app.configuration:
                self.port = jeeves.app.configuration['httpd']['port']
            else:
                jeeves.app.configuration['httpd']['port'] = self.port
                jeeves.app.configuration['httpd']['ip'] = self.ip
        else:
            jeeves.app.configuration['httpd'] = {'ip': self.ip, 'port': self.port}
        LocalWebHandler.jeeves = jeeves
        LocalWebHandler.drone = drone
        self.server = http.server.HTTPServer((self.ip, self.port), LocalWebHandler)
        browser_thread = BrowserThread(self.ip, self.port)
        browser_thread.start()
        self.server.serve_forever()

    @loguse
    def lock(self):
        pass

    @loguse
    def unlock(self):
        pass

    @loguse
    def close(self):
        '''
        Close as Wooster
        '''
        pass

        
class About(suapp.jandw.Wooster):

    @loguse
    def inflow(self, jeeves, drone):
        self.jeeves = jeeves
        print("=====================")
        print("About")
        print("---------------------")
        try:
            with open("%s" % (drone.dataobject)) as fh:
                for line in fh:
                    print(line, end="")
        except OSError as e:
            logging.getLogger(__name__).warning("Could not open about text file %s.", drone.dataobject)
        except IOError as e:
            logging.getLogger(__name__).warning("Could not open about text file %s.", drone.dataobject)
        print()
        print("---------------------")
        answer = input("Choose option: ")
        print()

        
class Configuration(suapp.jandw.Wooster):

    @loguse
    def inflow(self, jeeves, drone):
        self.jeeves = jeeves
        print("=====================")
        print("Configuration")
        print("---------------------")
        print(json.dumps(self.jeeves.app.configuration, indent = "\t"))
        print("---------------------")
        answer = input("Choose option: ")
        print()

