#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import collections
import hashlib
import http.cookies
import http.server
import json
from threading import Thread
import time
import os.path
import sys
import urllib.parse
import webbrowser

import suapp.jandw
from logdecorator import *


users = {"admin": "admin", "user": "user"}
groups = {"administrators": ["admin"]}

class HtmlTemplatingEngine():

    html_template = """ <!DOCTYPE html>
<html>
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

    @loguse
    def __init__(self, template = None):
        if template:
            self.html_template = str(template)
        else:
            self.html_template = HtmlTemplatingEngine.html_template

    @loguse
    def html(self, session, title, main, prefix = None, menu = None):
        name = "SuApp"
        if prefix == None:
            prefix = ""
        if menu == None:
            # TODO: THIS NEXT LINE IS OBVIOUSLY WRONG - FOR TESTING TEMPORARILY. # DELME
            file_menu = collections.OrderedDict()
            file_menu["Quit"] = "EXIT"
            help_menu = collections.OrderedDict()
            help_menu["Configuration"] = "CONFIGURATION"
            help_menu["About"] = "ABOUT"
            menu = collections.OrderedDict()
            menu["File"] = file_menu
            menu["Help"] = help_menu
        output = []
        # output.append(prefix + '<!-- %s // -->' % (tables))
        # output.append(prefix + '<!-- Entered with mode %s // -->' % (???))
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
        output.append(prefix + '\t<div class="page-header">')
        output.append(prefix + '\t\t<h1>%s</h1>' % (title))
        output.append(prefix + '\t</div>')

        output.append(prefix + '\t<div class="row">')
        output.append(prefix + '\t\t<div class="content">')
        output.append(prefix + '\t\t\t<div class="col-md-7" role="main">')
        #output.append(prefix + '\t\t\t\t<ul class="pager">')
        #output.append(prefix + '\t\t\t\t\t<li class="next"><a href="/stefaan.html">Stefaan &rarr;</a></li>')
        #output.append(prefix + '\t\t\t\t</ul>')

        output.append(prefix + '\t\t\t\t<main>')
        if main:
            output.append(prefix + '\t\t\t\t\t%s' % (main))
        # TODO
        output.append(prefix + '\t\t\t\t</main>')

        #output.append(prefix + '\t\t\t\t<ul class="pager">')
        #output.append(prefix + '\t\t\t\t\t<li class="previous"><a href="/start.html">&larr; Partnership SBR</a></li>')
        #output.append(prefix + '\t\t\t\t\t<li class="next"><a href="/stefaan.html">Stefaan &rarr;</a></li>')
        #output.append(prefix + '\t\t\t\t</ul>')

        #output.append(prefix + '\t\t\t\t<div class="col-md-3" role="complementary">')
        #output.append(prefix + '\t\t\t\t\t<nav class="hidden-print hidden-xs hidden-sm">')
        #output.append(prefix + '\t\t\t\t\t\t<div class="sidebar" data-spy="affix" data-offset-top="80" data-offset-bottom="60">')
        #output.append(prefix + '\t\t\t\t\t\t\t<div class="well">')

        #output.append(prefix + '\t\t\t\t\t\t\t\t<a href="#"><strong>%s</strong></a>' % (name))
        #output.append(prefix + '\t\t\t\t\t\t\t\t<div class="toc">')
        #output.append(prefix + '\t\t\t\t\t\t\t\t\t<ul>')
        #output.append(prefix + '\t\t\t\t\t\t\t\t\t\t<li><a href="#favourite-colours">Favourite colours</a><ul>')
        #output.append(prefix + '\t\t\t\t\t\t\t\t\t\t\t<li><a href="#ino">Ino</a><ul>')
        #output.append(prefix + '\t\t\t\t\t\t\t\t\t\t\t\t<li><a href="#lutino">Lutino</a></li>')
        #output.append(prefix + '\t\t\t\t\t\t\t\t\t\t\t\t<li><a href="#albino">Albino</a></li>')
        #output.append(prefix + '\t\t\t\t\t\t\t\t\t\t\t</ul></li>')
        #output.append(prefix + '\t\t\t\t\t\t\t\t\t\t</ul></li>')
        #output.append(prefix + '\t\t\t\t\t\t\t\t\t\t<li><a href="#band-codes">Band codes</a></li>')
        #output.append(prefix + '\t\t\t\t\t\t\t\t\t</ul>')
        #output.append(prefix + '\t\t\t\t\t\t\t\t</div>')

        #output.append(prefix + '\t\t\t\t\t\t\t</div>')
        #output.append(prefix + '\t\t\t\t\t\t</div>')
        #output.append(prefix + '\t\t\t\t\t</nav>')
        #output.append(prefix + '\t\t\t\t</div>')

        output.append(prefix + '\t\t\t</div>')
        output.append(prefix + '\t\t</div>')
        output.append(prefix + '\t</div>')

        # Possibly have TOC here.

        output.append(prefix + '\t<div class="footer">')
        output.append(prefix + '\t\t<p>This website is powered by <a href="http://suapp.schilduil.com/" target="_blank">SuApp</a></p>')
        output.append(prefix + '\t</div>')

        output.append(prefix + '</div>')
        return self.html_template % {
            'title': title,
            'body': "\n".join(output)
        }


class Session(dict):
    """
    Session is a dictionary that contains all session relevant objects.
    
    There is also a id variable that contains the session id.
    """
    @loguse
    def __init__(self, sessionid):
        self.id = sessionid
        
            
class SessionStore(dict):
    """
    The SessionStore is a dictionary specifically for all the session objects in
    use. 
    
    You however cannot just add a session to it. You must use the new() method
    to create a new session object in the store. It will return the new session 
    object.
    The generated session id is based on the timestamp in HEX preceded with a
    prefix. Unused sessions will be removed from the session store. By default 
    the timeout is 3600 seconds. You can set both the prefix and timeout (in
    seconds) in the constructor:
        SessionStore(prefix = "SUAPP", timeout = 300)
    """
    @loguse
    def __init__(self, prefix = None, timeout = None):
        """
        Constructs the session store.
        
        By default the session id previx is SUAPP and 
        the timeout is 3600 seconds (1 hour).
        """
        if not prefix:
            prefix = "SUAPP"
        self.prefix = str(prefix)
        if not timeout:
            timeout = 3600
        self.timeout = int(timeout)
         
    @loguse
    def new(self, **kwargs):
        """
        Call this method for creating a new session object in the store.
        
        It resturns the session object.
        You can pass any keyword arguments to initialize the session.
        """
        sessionid = self.prefix + hashlib.sha1(time.time().hex().encode('utf-8')).hexdigest()
        now = time.time()
        session = Session(sessionid)
        session.update(kwargs)
        session.update({"created": now, "last-used": now})
        super().__setitem__(sessionid, session)
        return session

    def __setitem__(self, sessionid, session):
        """
        Overridden to block adding a session to the store.
        """
        raise NotImplementedError("You can't just add objects to the SessionStore. Use new to create a new Session object.")
    
    def __getitem__(self, sessionid):
        """
        Overridden to check if the session isn't stale.
        """
        session = super().__getitem__(sessionid)
        now = time.time()
        if session["last-used"] + self.timeout < now:
            # Stale session, removing it and acting as if it never existed.
            del self[sessionid]
            raise KeyError("The session %s has expired." % sessionid)
        session["last-used"] = now
        return session
        
    def __str__(self):
        result = []
        for session in super():
            result.append(session.id)
        return ",".join(result)

        
class LocalWebHandler(http.server.BaseHTTPRequestHandler):

    jeeves = None
    start = None
    sessions = SessionStore()
    html_template_engine = HtmlTemplatingEngine()

    @loguse
    def set_html_template_engine(self, html_template_engine):
        self.html_template_engine = html_template_engine

    @loguse
    def html(self, session, title, body, **kwargs):
        if not self.html_template_engine:
            self.html_template_engine = LocalWebHandler.html_template_engine
        return self.html_template_engine.html(session, title, body, **kwargs)

    @loguse
    def cookies(self):
        """
        Gets the cookie information.
        """
        self.cookie = http.cookies.SimpleCookie()
        #print("Headers: %s" % (self.headers)) # DELME
        if "Cookie" in self.headers:
            #print("Cookie: %s" % (self.headers["Cookie"])) # DELME
            # Not sure why I need .split(";",1)[0], but otherwise it takes the last on on the line.
            # It seems the SimpleCookie only takes the last in case of multiples.
            # Not sure this is the solution: does the browser always put the new one in front?
            self.cookie = http.cookies.SimpleCookie(self.headers["Cookie"].split(";",1)[0])
    
    @loguse
    def session(self):
        """
        Session management
        
        If the client has sent a cookie named sessionId, that is used.
        It returns the corresponding session object from the session store.
        If there is no sessionId or it can't find it in the session store it
        will create a new session and set it as a cookie.
        """
        self.expired_cookie = None
        session = None
        # Getting the session from the cookie.
        if "sessionId" in self.cookie:
            sessionId = self.cookie["sessionId"].value
            try:
                session = LocalWebHandler.sessions[sessionId]
            except KeyError:
                # Not found or it is expired
                # (which is more or less the same thing)
                self.expired_cookie = sessionId
                session = None
        # There was no session or the session expired. Create a new one.
        if not session:
            session = LocalWebHandler.sessions.new(jeeves = LocalWebHandler.jeeves)
            self.cookie["sessionId"] = session.id
        self.session_id = session.id
        return session
    
    @loguse
    def do_service_logoff(self, session, fields, json_object = None, payload = None):
        """
        Service that logs out the user by deleting the session.
        """
        # Delete the session
        try:
            # Remove the current session id.
            del LocalWebHandler.sessions[session.id]
            # Reinitialize the session.
            session()
        except:
            pass
        return (200, "text/json; charset=utf-8", {"result": True})
        
    @loguse
    def do_service_public_logon(self, session, fields, json_object = None, payload = None):
        """
        Service that logs on the user in this session.
        
        It tries to get the credentials from these sources, in this order:
            * json body
            * POST / GET parameters (depending on the http method used)
            * Authentication header (basic authentication)
        """
        #print("LOGON: session: %s" % (session.id)) # DELME
        # First check if someone is already logged in.
        userid = None
        try:
            userid = session["userid"]
        except:
            pass
        # Checking to see if there is a force option in the fields or json.
        # In that case force the logoff first.
        if userid:
            try:
                if "force" in fields:
                    self.do_logoff(session, fields)
                    userid = None
            except:
                pass
        if userid:
            try:
                if "force" in json_object:
                    self.do_logoff(session, fields)
                    userid = None
            except:
                pass
        if userid:
            # There is already someone logged in and it was not forced out.
            return (200, "text/json; charset=utf-8", {"result": False, "message": "User %s is already logged in. Log out first before logging in." % (userid)})

        #print("LOGON: session: %s" % (session.id)) # DELME
        # Logging in
        username = None
        password = None
        # First try to get the credentials from the json.
        try:
            username = json_object["username"]
            password = json_object["password"]
        except:
            pass
        if not username:
            # Try to get the credentials from the fields.
            try:
                username = fields["username"][-1]
                password = fields["password"][-1]
            except:
                pass
        if not username:
            # At last try basic authentication
            try:
                # Get the header "Authorization" and base64 decode it and extract username:password.
                # base64.b64encode("username:password".encode('utf-8'))
                import base64
                auth_header = self.headers["Authorization"] # b'dGVzdDp0ZXN0'
                #print("Authorization: %s" % (auth_header[6:])) # DELME
                if auth_header.startswith("Basic "):
                    #print("Authorization: %s" % (base64.b63decode(auth_header[6:]))) # DELME
                    (username, password) = base64.b64decode(auth_header[6:]).decode('utf-8').split(":", 1)
                    #print("Basic %s:%s" % (username, password)) # DELME
            except:
                pass
        # Authenticate.
        # TODO: Connect to a real repository.
        #print("%s:%s" % (username, password)) # DELME
        #print("LOGON: session: %s" % (session.id)) # DELME
        try:
            if password == users[username]:
                session["userid"] = username
                return (200, "text/json; charset=utf-8", {"result": True, "userid": session["userid"]})
        except KeyError:
            # Couldn't find user in the user repository.
            pass
        return (200, "text/json; charset=utf-8", {"result": False, "message": "Incorrect credentials provided."})

    @loguse
    def authorized(self, session, fields):
        """
        Returns a number indicating the permissions.
        
        TODO: group based authorization: now it's just Y/N an everything.
        Using UNIX filesystem permission rwx
             4: read
             2: write
             1: execute
        """
        # Check the user
        user_id = None
        try:
            user_id = session["userid"]
        except:
            pass
        if self.path.startswith('/service/public/'):
            return 6
        # Not a logged in user, let's see if we can log you in.
        if not user_id:
            (result_code, result_type, result_message) = self.do_service_public_logon(session, fields)
            if result_code == 200:
                if result_message['result']:
                    user_id = result_message['userid']
                else:
                    try:
                        logging.getLogger(self.__module__).info("Automatic authorization failed: %s" % result_message['message'])
                    except:
                        logging.getLogger(self.__module__).info("Automatic authorization failed: %s" % json.dumps(result_message))

        # FOR NOW: anybody logged in has all the rights.
        # Needs mapping from groups > /services/ROLE/... with permissions.
        #     e.g. administrators > admin (bad example as they can do all)
        if user_id:
            if user_id in groups["administrators"]:
                # Admin has all rights.
                return 7
            elif self.path.startswith('/service/admin/'):
                return 0
            else:
                return 4
        # This is not a logged in user: no authorization.
        return None

    @loguse
    def do_service_admin_sessions(self, session, fields, json_object):
        """
        Test service that just returns the sessions.
        """
        return (200, "text/json; charset=utf-8", {"result": True, "sessions": LocalWebHandler.sessions})
        
    @loguse
    def do_service_who(self, session, fields, json_object):
        """
        Test service that just returns the logged in user.
        """
        try:
            return (200, "text/json; charset=utf-8", {"result": True, "userid": session["userid"]})
        except:
            return (200, "text/json; charset=utf-8", {"result": False, "message": "No user logged on."})
        
    @loguse
    def do_service_sessionid(self, session, fields, json_object):
        """
        Test service that just returns the sessionid.
        """
        return (200, "text/json; charset=utf-8", {"result": True, "sessionid": session.id})
        
    @loguse
    def do_service_sessionobject(self, session, fields, json_object):
        """
        DANGER: Test service that returns the content of a session.
        
        Possibly very dangerous because of information leakage.
        By default it will return the session content for the current session
        but you can pass a specific "sessionid" in the json body.
        """
        session_id = session.id
        try:
            # If the request was for a specific session
            session_id = json_object["sessionid"]
        except:
            pass
        
        try:
            out_object = LocalWebHandler.sessions[session_id]
            return (200, "text/json; charset=utf-8", out_object)
        except:
            # Unknown session id:
            return (200, "text/json; charset=utf-8", {})

    @loguse
    def do_dynamic_page(self, session, fields):
        """
        Returns a dynamic page.
        
        Unimplemented, so returns a 404 Page not found.
        """
        return_code = 200
        return_mime = 'text/html; charset=utf-8'
        return_message = ""
        drone_title = "SuApp"
        drone_result = ""
        # Check for an OUT message.
        if "OUT" in fields:
            if fields['OUT'] == "EXIT":
                # TODO: ignoring for the moment.
                drone_result = "EXIT Not implemented yet."
                pass
            else:
                # Mode in a web setting can only be MODAL?
                (drone_title, drone_result) = session['jeeves'].drone(self, fields['OUT'][-1], session['jeeves'].MODE_MODAL, "DATA")
        try:
            return_message = self.html(session, drone_title, drone_result, prefix = "        ")
        except Exception as err:
            ex_type, ex, tb = sys.exc_info()
            import traceback
            # TODO: needs to splilt up between types of errors: 500 (real), 404 (not found)
            # TODO: and do better error handling in general.
            return_code = 500
            return_mime = 'text/plain; charset=utf-8'
            return_message = "%s\n%s" % (err, "".join(traceback.format_exception(ex_type, ex, tb)))

        # The imporant stuff is the OUT message.
        #return (404, "text/plain; charset=utf-8", "Page not found.")
        return (return_code, return_mime, return_message)

    @loguse
    def _do(self, return_code, return_mime, return_message):
        """
        It will create and send the http output.
        
        It does this, including headers, based on the  return_code, return_mime
        and return_message.
        """
        self.send_response(return_code)
        self.send_header('Content-type', return_mime)
        if self.expired_cookie:
            self.send_header('Set-Cookie', "sessionId=%s; Expires=Thu, 01 Jan 1970 00:00:00 GMT" % self.expired_cookie)
            self.expired_cookie = None
        for morsel in self.cookie.values():
            self.send_header('Set-Cookie', morsel.output(header='').lstrip() + '; Path=/')
        # self.send_header("Content-length", len(DUMMY_RESPONSE))
        self.end_headers()
        self.wfile.write(return_message.encode('utf-8'))

    @loguse
    def do_error_page(self, session, return_code, return_mime, return_message):
        logging.getLogger(self.__module__).info("Error page (%s): %s (%s)" % (return_code, return_message, return_mime))
        message = return_message
        if return_mime.startswith("text/plain"):
            # template
            try:
                body = ""
                if return_code == 403:
                    if return_message == "Not logged in.":
                        body = '<p>Go to the logon page <a href="/public/logon">here</a>.</p>'
                    else:
                        body = "<p>Sorry, you don't have access to this.</p>"
                else:
                    body = '<p>Oops, something went wrong.</p>'
                message = self.html(session, "%s: %s" % (return_code, return_message), body, menu = {}, prefix = "        ")
                return_mime = 'text/html; charset=utf-8'
            except:
                pass
        self._do(return_code, return_mime, message)

    @loguse
    def do(self, session, return_code, return_mime, return_message):
        """
        It will create and send the http output or the error page.
        """
        if return_code >= 400:
            self.do_error_page(session, return_code, return_mime, return_message)
        else:
            self._do(return_code, return_mime, return_message)

    @loguse
    def do_dynamic(self, fields, json_object = None, payload = None):
        """
        This method will reply to a dynamic request.
        
        If json is found in the body this is decoded and can be found in
        json_object. Otherwise the body of the request is in payload.
        
        If the request path looks like "/service/*" it looks for the
        self.do_service_*() method to handle it for it. If that doesn't exist it
        returns with a 404. For a service that returns json, you can add the
        "pretty" GET/POST variable to return a nicely formatted answer instead 
        of the default one line short json.
        
        If it isn't a service it passes handling the request to
        do_dynamic_page().
        """
        self.cookies()
        session = self.session()
        return_code = 200
        return_mime = "text/html; charset=utf-8"
        return_message = ""
        # Check authorization
        auth_level = self.authorized(session, fields)
        if self.path.startswith('/public/'):
            auth_level = 7
        if auth_level != None:
            if (auth_level & 4):
                if self.path.startswith("/service/"):
                    # Looking up if we have a do_service_{} method.
                    temp = self.path.split("?")
                    method_name = "do" + "_".join(temp[0].split("/"))
                    try:
                        (return_code, return_mime, return_message) = getattr(self, method_name.lower())(session, fields, json_object)
                    except AttributeError:
                        # Not found
                        return_code = 404
                        return_mime = "text/json; charset=utf-8"
                        return_message = {"result": False, "message": "Service %s not found." % (method_name.lower())}
                    if return_mime == "text/json; charset=utf-8":
                        # The output should be json, so transforming it to json:
                        if "pretty" in fields:
                            return_message = json.dumps(return_message, sort_keys=True, indent=4, separators=(',', ': '))
                        else:
                            return_message = json.dumps(return_message)
                else:
                    (return_code, return_mime, return_message) = self.do_dynamic_page(session, fields)
            else:
                (return_code, return_mime, return_message) = (403,'text/plain; charset=utf-8','Not authorized.')
        else:
            (return_code, return_mime, return_message) = (403,'text/plain; charset=utf-8','Not logged in.')
        # And make a http response from it all.
        self.do(session, return_code, return_mime, return_message)
        
    @loguse
    def do_static(self, fields, mimetype):
        """
        Serve the request from the file system.
        """
        # Get the cookies.
        self.cookies()
        # Initialize the session.
        session = self.session()
        # Check authorization
        auth_level = self.authorized(session, fields)
        # Some mime types are always accessable: css, js
        if self.path.startswith('/public/'):
            auth_level = 7
        elif mimetype.startswith("text/css"):
            auth_level = 4
        elif mimetype.startswith("application/x-javascript"):
            auth_level = 4
        if auth_level != None:
            if (auth_level & 4):
                try:
                    localfile = os.path.join(os.path.dirname(__file__), self.path[1:])
                    with open(localfile, 'rb') as f:
                        self.send_response(200)
                        self.send_header('Content-type', mimetype)
                        self.end_headers()
                        self.wfile.write(f.read())
                except FileNotFoundError:
                    self.send_response(404)
                    self.send_header('Content-type', 'text/plain; charset=utf-8')
                    self.end_headers()
                    message = "File %s not found.\n%s" % (self.path, localfile)
                    self.wfile.write(message.encode('utf-8'))
                except BrokenPipeError as err:
                    logging.getLogger(self.__module__).info("Broken pipe: %s" % (err))
                    pass
                return
            else:
                # 403: Not authorized
                self.do(session, 403,'text/plain; charset=utf-8','Not authorized.')
        else:
            # 403: Not authorized
            self.do(session, 403,'text/plain; charset=utf-8','Not logged in.')

    @loguse
    def do_POST(self):
        """
        Entry point for an http POST request.
        """
        length = int(self.headers['Content-Length'])
        fields = {}
        try:
            fields = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        except:
            # We don't care if we can't get the GET parameters.
            pass
        field_data = self.rfile.read(length)
        # TODO: depending on the mime type.
        #     application/x-www-form-urlencoded # parameters
        #     text/json                         # json
        #     multipart/form-data               # upload
        
        # Fields from the POST body get precedence over those from GET.
        fields.update(urllib.parse.parse_qs(field_data))
        do_dynamic(fields)
    
    @loguse
    def do_PUT(self):
        """
        Entry point for an http PUT request.
        """
        length = int(self.headers.getheader('content-length'))
        field_data = self.rfile.read(length)
        try:
            # See if it is json
            json_object = json.loads(field_data.decode('utf-8'))
            self.do_dynamic(fields, json_object = json_object)
        except:
            self.do_dynamic(fields, payload = field_data)
    
    @loguse
    def do_GET(self):
        """
        Entry point for an http GET request.
        """
        # TODO: this parsing does not work on keys without a variable.
        fields = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        #print("Fields: %s" % (fields)) # DELME
        # Anything starting with /js/, /css/, /img/ is static content.
        if self.path == "/favicon.ico":
            self.do_static(fields)
        elif self.path.startswith("/js/"):
            self.do_static(fields, "application/x-javascript")
        elif self.path.startswith("/img/"):
            file_name = self.path.split("?",1)[0]
            if file_name.endswith(".png"):
                self.do_static(fields, "image/png")
            elif file_name.endswith(".ico"):
                self.do_static(fields, "image/x-icon")
            elif file_name.endswith(".jpg") or file_name.endswith(".jpeg"):
                self.do_static(fields, "image/jpeg")
            elif file_name.endswith(".gif"):
                self.do_static(fields, "image/gif")
            else:
                self.do_static(fields, "binary/octet-stream")
        elif self.path.startswith("/css/"):
            self.do_static(fields, "text/css; charset=utf-8")
        else:
            self.do_dynamic(fields)

    # No @loguse as then we would be logging what we are logging.
    def log_message(self, format, *args):
        """
        Logging to modules.httpd logger.
        
        It is recommended to have a special entry in the configuration for this:
        ...
              "modules": {
                   ...
                   "httpd": {
                       "level": "DEBUG",
                       "filename": "~/.suapp/log/httpd.accces_log"
                   }
                   ...
        ...
        """
        session_id = ""
        try:
            session_id = self.session_id
        except:
            pass
        logging.getLogger("modules.httpd").debug("%s %s %s - - [%s] %s" % (hex(hash(self))[-8:], session_id[-8:], self.address_string(),self.log_date_time_string(),format%args))


class BrowserThread(Thread):

    # @loguse seems to break it.
    def __init__(self, ip, port):
        """
        Set the ip and port for the browser upon creation.
        """
        self.ip = ip
        self.port = port
        super().__init__()

    @loguse
    def run(self):
        """
        Run the thread: i.e. wait and lauch the browser.
        """
        import time
        # Waiting for x seconds to be sure the http server is up.
        time.sleep(0)
        webbrowser.open("http://%s:%s/?username=user&password=user" % (self.ip, self.port))


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
        result = []
        suffix = []
        # Looking for html or txt file
        file_name = self.jeeves.app.configuration["self"].rsplit(".", 1)[0]
        if os.path.isfile(file_name + ".html"):
            file_name += ".html"
        else:
            file_name += ".txt"
            result.append("<tt>\n")
            suffix.append("</tt>")
        try:
            with open(file_name) as fh:
                for line in fh:
                    result.append(line)
        except OSError as e:
            logging.getLogger(self.__module__).warning("Could not open about file %s.", file_name)
        except IOError as e:
            logging.getLogger(self.__module__).warning("Could not open about file %s.", file_name)
        if not result:
            result = ["ERROR: Could not open file %s." % (file_name)]
        return ("About", "".join(result) + "".join(suffix))


class Configuration(suapp.jandw.Wooster):

    @loguse
    def inflow(self, jeeves, drone):
        self.jeeves = jeeves
        result = "<pre><code>\n"
        result += json.dumps(self.jeeves.app.configuration, indent = "    ")
        result += "\n</code></pre>"
        return ("Configuration", result)
 
