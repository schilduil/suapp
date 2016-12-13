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
import random
import string
import sys
import urllib.parse
import webbrowser

import suapp.jandw
from logdecorator import *


users = {
    "admin": ''.join(random.choice(string.ascii_letters.upper() + string.ascii_letters.lower() + string.digits + '-_') for i in range(32)),
    "user": ''.join(random.choice(string.ascii_letters.upper() + string.ascii_letters.lower() + string.digits + '-_') for i in range(32))
}
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

        <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
        <!-- <script src="https://code.jquery.com/jquery.js"></script> -->
        <script src="/js/jquery/2.1.4/jquery.min.js"></script>

%(body)s

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

    @loguse([1,3,'@']) # Not logging session, main nor the return value.
    def html(self, session, title, main, prefix = None, menu = None, shortname = None):
        if not shortname:
            shortname = "SuApp"
        if prefix == None:
            prefix = ""
        if menu == None:
            # TODO: THIS NEXT LINE IS OBVIOUSLY WRONG - FOR TESTING TEMPORARILY. # DELME
            file_menu = collections.OrderedDict()
            file_menu["Quit"] = "EXIT"
            test_menu = collections.OrderedDict()
            test_menu["Table"] = "TABLE"
            test_menu["Record"] = "RECORD"
            help_menu = collections.OrderedDict()
            help_menu["Configuration"] = "CONFIGURATION"
            help_menu["About"] = "ABOUT"
            menu = collections.OrderedDict()
            menu["File"] = file_menu
            menu["Test"] = test_menu
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
        output.append(prefix + '\t\t\t<a class="navbar-brand" href="/">%s</a>' % (shortname))
        output.append(prefix + '\t\t</div>')
        output.append(prefix + '\t\t<div class="navbar-collapse collapse">')
        output.append(prefix + '\t\t\t<ul class="nav navbar-nav navbar-left">')
        output.append(prefix + '\t\t\t\t<li><a href="/">%s</a></li>' % ("Start"))
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

    def send_last_modified_header(self):
        timestamp = time.time()
        year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
        s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
                self.weekdayname[wd],
                day, self.monthname[month], year,
                hh, mm, ss)
        self.send_header('Last-Modified', s)

    @loguse
    def set_html_template_engine(self, html_template_engine):
        self.html_template_engine = html_template_engine

    @loguse([1,3,'@']) # Not logging session, body nor return value.
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
    def callback_drone(self, drone):
        self.session()['drone'] = drone
    
    @loguse([1, 'json_object', 'payload']) # Not logging session, json_object nor payload.
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
        
    @loguse([1, 'json_object', 'payload']) # Not logging session, json_object nor payload.
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

    @loguse(1) # Not logging session.
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

    @loguse([1, 3]) # Not logging session and json_object.
    def do_service_admin_sessions(self, session, fields, json_object):
        """
        Test service that just returns the sessions.
        """
        return (200, "text/json; charset=utf-8", {"result": True, "sessions": LocalWebHandler.sessions})
        
    @loguse([1, 3]) # Not logging session and json_object.
    def do_service_who(self, session, fields, json_object):
        """
        Test service that just returns the logged in user.
        """
        try:
            return (200, "text/json; charset=utf-8", {"result": True, "userid": session["userid"]})
        except:
            return (200, "text/json; charset=utf-8", {"result": False, "message": "No user logged on."})
        
    @loguse([1, 3]) # Not logging session and json_object.
    def do_service_sessionid(self, session, fields, json_object):
        """
        Test service that just returns the sessionid.
        """
        return (200, "text/json; charset=utf-8", {"result": True, "sessionid": session.id})
        
    @loguse([1, 3]) # Not logging session and json_object.
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

    @loguse # ('@')
    def do_object(self, start_object, path):
        """
        Returns json of part of the start_object determined by path.

        Example of paths:
            key -> start_object['key'].name
            key/subkey  -> start_object['key']['subkey'] - done recursively
            key.var     -> start_object['key'].var
        """
        first_path = path
        rest_path = ""
        try:
            (first_path, rest_path) = path.split("/", 1)
        except:
            pass
        key = first_path
        var = ""
        try:
            (key, var) = first_path.split(".")
        except:
            pass
        #print("%s.%s/%s" % (key,var,rest_path)) # DELME
        if isinstance(start_object, list) or isinstance(start_object, tuple):
            index = 0
            try:
                index = int(key)
            except:
                return (200, "text/json; charset=utf-8", {'result': False, 'message': "Index %s is not an integer." % (key)})
            try:
                if var:
                    try:
                        if rest_path:
                            (return_code, return_mime, return_message) = self.do_object(getattr(start_object[index], var), rest_path)
                            extended_message = {'result': return_message['result']}
                            if return_message['result']:
                                extended_message['object'] = return_message['object']
                            else:
                                extended_message['message'] = key + '.' + var + "/" + return_message['message']
                            #print("%s.%s %s > %s" % (key, var, return_message, extended_message)) # DELME
                            return (return_code, return_mime, extended_message)
                        else:
                            return (200, "text/json; charset=utf-8", {'result': True, 'object': getattr(start_object[index], var)})
                    except Exception as err:
                        return (200, "text/json; charset=utf-8", {'result': False, 'message': "%s.%s not found." % (index, var), 'error': str(err)})
                elif rest_path:
                    (return_code, return_mime, return_message) = self.do_object(start_object[index], rest_path)
                    extended_message = {'result': return_message['result']}
                    if return_message['result']:
                        extended_message['object'] = return_message['object']
                    else:
                        extended_message['message'] = str(index) + "/" + return_message['message']
                    return (return_code, return_mime, extended_message)
                else:
                    return (200, "text/json; charset=utf-8", {'result': True, 'object': start_object[index]})
            except:
                return (200, "text/json; charset=utf-8", {'result': False, 'message': "%s not found." % (index)})
        elif isinstance(start_object, dict):
            if key in start_object:
                if var:
                    try:
                        if rest_path:
                            (return_code, return_mime, return_message) = self.do_object(getattr(start_object[key], var), rest_path)
                            extended_message = {'result': return_message['result']}
                            if return_message['result']:
                                extended_message['object'] = return_message['object']
                            else:
                                extended_message['message'] = key + '.' + var + "/" + return_message['message']
                            #print("%s.%s %s > %s" % (key, var, return_message, extended_message)) # DELME
                            return (return_code, return_mime, extended_message)
                        else:
                            return (200, "text/json; charset=utf-8", {'result': True, 'object': getattr(start_object[key], var)})
                    except Exception as err:
                        return (200, "text/json; charset=utf-8", {'result': False, 'message': "%s.%s not found." % (key, var), 'error': str(err)})
                elif rest_path:
                    (return_code, return_mime, return_message) = self.do_object(start_object[key], rest_path)
                    extended_message = {'result': return_message['result']}
                    if return_message['result']:
                        extended_message['object'] = return_message['object']
                    else:
                        extended_message['message'] = key + "/" + return_message['message']
                    return (return_code, return_mime, extended_message)
                else:
                    return (200, "text/json; charset=utf-8", {'result': True, 'object': start_object[key]})
            else:
                #print("%s not in %s" % (key, start_object)) # DELME
                return (200, "text/json; charset=utf-8", {'result': False, 'message': "%s not found." % (key)})
        else:
            return (200, "text/json; charset=utf-8", {'result': False, 'message': "Object is not a dict, list or tuple."})

    @loguse([1,'@']) # Not logging session nor return value.
    def do_dynamic_page(self, session, fields):
        """
        Returns a dynamic page.
        
        Unimplemented, so returns a 404 Page not found.
        """
        return_code = 200
        return_mime = 'text/html; charset=utf-8'
        return_message = ""
        shortname = "SuApp"
        try:
            shortname = session['jeeves'].app.configuration['shortname']
        except:
            pass
        drone_title = shortname
        try:
            drone_title = session['jeeves'].app.configuration['name']
        except:
            pass
        drone_result = ""
        # Check for an OUT message.
        if "OUT" in fields:
            if fields['OUT'] == "EXIT":
                # TODO: ignoring for the moment.
                drone_result = "EXIT Not implemented yet."
                pass
            else:
                # Mode in a web setting can only be MODAL?
                # DELME: creating a testing data object
                data = {'tables': {'test': {'ID': 'testid'}}, 'table_name': 'test', 'table': 'organism', 'object': {'ID': '(GOVAYF)62', 'father': 'GOc', 'mother': 'VAYF'}}
                (drone_title, drone_result) = session['jeeves'].drone(self, fields['OUT'][-1], session['jeeves'].MODE_MODAL, data, callback_drone = self.callback_drone)
        try:
            shortname = session['jeeves'].app.configuration['shortname']
        except:
            pass
        try:
            return_message = self.html(session, drone_title, drone_result, prefix = "        ", shortname = shortname)
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

    @loguse(3) # Not logging return_message.
    def _do(self, return_code, return_mime, return_message):
        """
        It will create and send the http output.
        
        It does this, including headers, based on the  return_code, return_mime
        and return_message.
        """
        self.send_response(return_code)
        self.send_header('Content-type', return_mime)
        self.send_last_modified_header()
        if self.expired_cookie:
            self.send_header('Set-Cookie', "sessionId=%s; Expires=Thu, 01 Jan 1970 00:00:00 GMT" % self.expired_cookie)
            self.expired_cookie = None
        for morsel in self.cookie.values():
            self.send_header('Set-Cookie', morsel.output(header='').lstrip() + '; Path=/')
        # self.send_header("Content-length", len(DUMMY_RESPONSE))
        self.end_headers()
        self.wfile.write(return_message.encode('utf-8'))

    @loguse([1,4]) # Not logging session nor return_message.
    def do_error_page(self, session, return_code, return_mime, return_message):
        logging.getLogger(self.__module__).info("Error page (%s): %s (%s)" % (return_code, return_message, return_mime))
        message = return_message
        if return_mime.startswith("text/plain"):
            # template
            try:
                body = ""
                if return_code == 401:
                    # We don't want to return a 401 as that will trigger the browser to get Authorization credentials.
                    # Instead we want to show a link to the login page.
                    return_code = 403
                    body = '<p>Go to the login page <a href="/public/logon">here</a>.</p>'
                elif return_code == 403:
                    body = "<p>Sorry, you don't have access to this.</p>"
                else:
                    body = '<p>Oops, something went wrong.</p>'
                message = self.html(session, "%s: %s" % (return_code, return_message), body, menu = {}, prefix = "        ")
                return_mime = 'text/html; charset=utf-8'
            except:
                pass
        self._do(return_code, return_mime, message)

    @loguse([1, 4]) # Not logging session nor return_message.
    def do(self, session, return_code, return_mime, return_message):
        """
        It will create and send the http output or the error page.
        """
        if return_code >= 400:
            self.do_error_page(session, return_code, return_mime, return_message)
        else:
            self._do(return_code, return_mime, return_message)

    @loguse(['json_object', 'payload']) # Not logging the json_object nor payload.
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
                if self.path.startswith("/service/session/"):
                    # Getting something from the session.
                    path_part = self.path[17:]
                    try:
                        (path_part, variables) = self.path[17:].rsplit("?", 1)
                    except:
                        pass
                    (return_code, return_mime, return_message) = self.do_object(session, path_part)
                    # The output should be json, so transforming it to json:
                    try:
                        if "pretty" in fields:
                            return_message = json.dumps(return_message, sort_keys=True, indent=4, separators=(',', ': '))
                        else:
                            return_message = json.dumps(return_message)
                    except:
                        if "pretty" in fields:
                            return_message = json.dumps({'result': False, 'message': 'Object not convertible to json.'}, sort_keys=True, indent=4, separators=(',', ': '))
                        else:
                            return_message = json.dumps({'result': False, 'message': 'Object not convertible to json.'})
                elif self.path.startswith("/service/"):
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
                (return_code, return_mime, return_message) = (403,'text/plain; charset=utf-8','Forbidden')
        else:
            (return_code, return_mime, return_message) = (401,'text/plain; charset=utf-8','Unauthorized')
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
                # Save on work by sending a "304 Not Modified"
                # If the request has a "If-Modified-Since" header.
                if "If-Modified-Since" in self.headers:
                    last_modified = self.headers['If-Modified-Since']
                    self.send_response(304)
                    self.send_header('Last-Modified', last_modified)
                    self.end_headers()
                    # And we're done, no body to send.
                    return
                try:
                    localfile = os.path.join(os.path.dirname(__file__), self.path[1:])
                    with open(localfile, 'rb') as f:
                        self.send_response(200)
                        self.send_header('Content-type', mimetype)
                        self.send_last_modified_header()
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
        self.command = 'POST'
        length = int(self.headers['Content-Length'])
        fields = {}
        try:
            fields = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query, keep_blank_values=True)
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
        self.command = 'PUT'
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
        self.command = 'GET'
        # TODO: this parsing does not work on keys without a variable.
        fields = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query, keep_blank_values=True)
        #print("Fields: %s" % (fields)) # DELME
        # Anything starting with /js/, /css/, /img/ is static content.
        if self.path == "/favicon.ico":
            self.do_static(fields, "image/x-icon")
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
        webbrowser.open("http://%s:%s/?username=user&password=%s" % (self.ip, self.port, users['user']))
        print("Admin credentials: admin/%s" % (users['admin']))


class Application(suapp.jandw.Wooster):

    @loguse
    def __init__(self, master=None):
        self.name = "Application"
        self.jeeves = None
        self.dataobject = None
        self.testdata = {"ID": "(150112)164", "ring": "BGC/BR23/10/164"}
        self.tables = {}

    @loguse('@') # Not logging the return value.
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

    @loguse('@') # Not logging the return value.
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

    @loguse('@') # Not logging the return value.
    def inflow(self, jeeves, drone):
        self.jeeves = jeeves
        result = "<pre><code>\n"
        result += json.dumps(dict(self.jeeves.app.configuration), indent = "    ")
        result += "\n</code></pre>"
        return ("Configuration", result)


class Table(suapp.jandw.Wooster):

    name = "TABLE"
    raw = True

    # http://api.jquery.com/jquery.getjson/
    # Is more complicated, check on 'result' and next 'object'.
    raw_js = """<script>
(function() {
    var suappAPI = "/service/session/drone.dataobject/tables/%(table_name)s";
    $.getJSON( suappAPI, function( data ) {
      console.log("Got json.")
      console.log(data)
      var items = [];
      console.log("Items (empty)")
      console.log(items)
      items.push( "<tr><th>Key</th><th>Value</th></tr>" )
      console.log("Items key/value")
      console.log(items)
      $.each( data["object"], function( key, val ) {
        items.push( "<tr><td>" + key + "</td><td>" + val + "</td></tr>" );
      });
      $( "<tbody/>", {
        "class": "my-new-list",
        html: items.join( " " )
      }).appendTo("#tableview");
    });
})();
</script>
"""

    def inflow(self, jeeves, drone):
        # TODO put the dataobject in the session...
        params = {"table_name": 'test'}
        if drone.dataobject:
            if not 'table_name' in drone.dataobject:
                # DELME: for testing creating something.
                drone.dataobject['table_name'] = 'test'
                drone.dataobject['tables'] = {'test': {'ID': 'testid'}}
            params = {"table_name": drone.dataobject['table_name']}
        result = []
        if Table.raw:
            result.append('<table id="tableview">')
            # Here the results will end up (see raw_js)
            result.append('</table>')
            return ("Table", Table.raw_js % (params) + "\n".join(result))
        else:
            return ("Table", "TODO: nice output.")


class Record(suapp.jandw.Wooster):

    name = "RECORD"
    raw = True

    # http://api.jquery.com/jquery.getjson/
    # Is more complicated, check on 'result' and next 'object'.
    raw_js = """<script>
(function() {
    var suappAPI = "/service/session/drone.dataobject/%(object)s";
    $.getJSON( suappAPI, function( data ) {
      console.log("Got json.")
      console.log(data)
      var items = [];
      console.log("Items (empty)")
      console.log(items)
      items.push( "<tr><th>Key</th><th>Value</th></tr>" )
      console.log("Items key/value")
      console.log(items)
      $.each( data["object"], function( key, val ) {
        items.push( "<tr><td>" + key + "</td><td>" + val + "</td></tr>" );
      });
      $( "<tbody/>", {
        "class": "my-new-list",
        html: items.join( " " )
      }).appendTo("#tableview");
    });
})();
</script>
"""

    def inflow(self, jeeves, drone):
        self.jeeves = jeeves
        params = {'object': None}
        if drone.dataobject:
            if 'table' in drone.dataobject:
                self.table = drone.dataobject['table']
                # Either we pass in an object or we pass a full table and key.
                if 'object' in drone.dataobject:
                    params['object'] = 'object'
                elif 'key' in drone.dataobject:
                    params['object'] = "table/%s" % drone.dataobject['key']
        result = []
        if Record.raw:
            result.append('<table id="tableview">')
            # Here the results will end up (see raw_js)
            result.append('</table>')
            return ("Record", Record.raw_js % (params) + "\n".join(result))
        else:
            return ("Record", "TODO: nice output.")

