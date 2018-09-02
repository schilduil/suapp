#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from tkinter import *
from tkinter.ttk import *

import suapp.jandw
import suapp.simple_json as simple_json
from suapp.logdecorator import *


#Extra widgets
class MultiListbox(Frame):
    def __init__(self, master, lists):
        Frame.__init__(self, master)
        self.lists = []
        for l, w in lists:
            frame = Frame(self)
            frame.pack(side=LEFT, expand=YES, fill=BOTH)
            Label(frame, text=l, borderwidth=1, relief=RAISED).pack(fill=X)
            lb = Listbox(frame, width=w, borderwidth=0, selectborderwidth=0, relief=FLAT, exportselection=FALSE)
            lb.pack(expand=YES, fill=BOTH)
            self.lists.append(lb)
            lb.bind('<B1-Motion>', lambda e, s=self: s._select(e.y))
            lb.bind('<Button-1>', lambda e, s=self: s._select(e.y))
            lb.bind('<Leave>', lambda e: 'break')
            lb.bind('<B2-Motion>', lambda e, s=self: s._b2motion(e.x, e.y))
            lb.bind('<Button-2>', lambda e, s=self: s._button2(e.x, e.y))
        frame = Frame(self)
        frame.pack(side=LEFT, fill=Y)
        Label(frame, borderwidth=1, relief=RAISED).pack(fill=X)
        sb = Scrollbar(frame, orient=VERTICAL, command=self._scroll)
        sb.pack(expand=YES, fill=Y)
        self.lists[0]['yscrollcommand'] = sb.set

    def _select(self, y):
        row = self.lists[0].nearest(y)
        self.selection_clear(0, END)
        self.selection_set(row)
        return 'break'

    def _button2(self, x, y):
        for l in self.lists:
            l.scan_mark(x, y)
        return 'break'

    def _b2motion(self, x, y):
        for l in self.lists:
            l.scan_dragto(x, y)
        return 'break'

    def _scroll(self, *args):
        for l in self.lists:
            apply(l.yview, args)

    def curselection(self):
        return self.lists[0].curselection()

    def delete(self, first, last=None):
        for l in self.lists:
            l.delete(first, last)

    def get(self, first, last=None):
        result = []
        for l in self.lists:
            result.append(l.get(first, last))
        if last:
            return apply(map, [None] + result)
        return result

    def index(self, index):
        self.lists[0].index(index)

    def insert(self, index, *elements):
        for e in elements:
            i = 0
            for l in self.lists:
                l.insert(index, e[i])
                i = i + 1

    def size(self):
        return self.lists[0].size()

    def see(self, index):
        for l in self.lists:
            l.see(index)

    def selection_anchor(self, index):
        for l in self.lists:
            l.selection_anchor(index)

    def selection_clear(self, first, last=None):
        for l in self.lists:
            l.selection_clear(first, last)

    def selection_includes(self, index):
        return self.lists[0].selection_includes(index)

    def selection_set(self, first, last=None):
        for l in self.lists:
            l.selection_set(first, last)
#END of extra widgets


class ToplevelWooster(Toplevel, suapp.jandw.Wooster):
    closed = False

    @loguse
    def preClose(self):
        pass

    # Overriding this disables the [X]
    @loguse
    def destroy(self):
        '''
        When you click the [X] (or the parent window gets destroyed)
        '''
        self.closed = True
        # Calling parent destroy() to actually destroy it.
        self.preClose()
        super().destroy()

    @loguse
    def close(self):
        '''
        Close as Wooster
        '''
        self.destroy()


ipsum = '''Lorem ipsum dolor sit amet, consectetur adipiscing elit. \
Suspendisse pretium sapien sit amet magna viverra id faucibus nibh condimentum. \
Fusce dui magna, venenatis vel elementum eu, suscipit at quam. Nullam sed felis lorem, vel pretium leo. \
Cras at neque orci. \
Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. \
Pellentesque ullamcorper quam eu ligula mattis tempor. \
Aliquam erat volutpat. Vivamus feugiat aliquam purus, \
euismod blandit lacus scelerisque vel. \
Phasellus sodales dignissim eros nec accumsan. \
Aenean est lectus, placerat sed ornare ut, congue nec nulla. \
Phasellus at sapien purus. \
Maecenas et sapien at ipsum fringilla tempus.

Donec non quam mauris. \
Vivamus bibendum ante id velit rhoncus molestie. \
Nullam bibendum suscipit elit sed aliquam. \
Maecenas felis magna, laoreet ut volutpat eget, varius at lorem. \
Quisque nisl dolor, aliquet et vestibulum nec, ullamcorper quis libero. \
Aliquam erat volutpat. \
Aenean mauris augue, varius sit amet iaculis quis, rhoncus at eros. \
Phasellus luctus congue cursus. \
Praesent lobortis vestibulum cursus. \
Nulla euismod nisi ac diam semper molestie. \
Curabitur quis leo at velit ultrices consectetur in in tellus. \
Nunc auctor erat ac justo porttitor consectetur. \
Cras vestibulum elit nec nulla consectetur euismod. \
Curabitur sodales vehicula lacus quis iaculis. \
Nulla laoreet eros eget ipsum commodo aliquet.

Cras gravida egestas nunc a hendrerit. \
Quisque consequat arcu ac dolor bibendum a porttitor augue malesuada. \
Etiam suscipit augue ac eros lobortis auctor. \
Vivamus urna sem, ultrices non ultrices in, sodales id justo. \
Aenean gravida bibendum risus, a pharetra arcu rhoncus quis. \
Maecenas interdum fringilla dapibus. \
Sed non diam massa, a sodales eros. \
Cras interdum nibh leo. \
Praesent non urna turpis. \
Pellentesque posuere massa vel ligula porta sed egestas arcu lacinia. \
Curabitur rutrum ultrices vestibulum. \
Mauris posuere, arcu id tempor volutpat, lacus nisl euismod felis, non facilisis purus sem ac sem. \
Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. \
Mauris posuere ornare elit non congue. \
Praesent pretium, nisl eget pulvinar pulvinar, nibh purus sollicitudin tellus, eget malesuada lacus nulla vel neque.

In non elit nisi. \
Phasellus porta vestibulum erat non condimentum. \
Sed sed augue neque, sed venenatis eros. \
In et nunc neque. \
Mauris mi velit, dignissim id vehicula at, semper vitae est. \
Ut porta lacus eget ipsum faucibus vel luctus metus scelerisque. \
Duis ipsum nulla, rutrum sit amet ultricies et, sodales vitae sem. \
Donec suscipit aliquam diam, id mollis nibh gravida vel. \
Quisque in blandit lectus. \
Fusce interdum nulla turpis, sit amet venenatis metus. \
Praesent ac tristique tortor.

Suspendisse ut magna sed nulla cursus rutrum. \
Suspendisse in lacus dui, non bibendum tellus. Nulla facilisi. \
Morbi urna justo, volutpat eu mattis id, facilisis sed sapien. \
Vestibulum vitae sapien orci. \
Proin aliquet euismod neque, vel sodales nulla hendrerit vitae. \
Sed auctor euismod adipiscing. \
Curabitur feugiat dui quis lorem gravida a mattis eros vehicula. \
Aenean eget ullamcorper nunc. \
Mauris sagittis eros aliquam dolor varius sit amet eleifend dolor placerat. \
Vestibulum nec dui metus. \
Nullam nec ante in lectus faucibus condimentum. \
Donec ac enim purus, et bibendum erat. \
Aliquam vestibulum tempus consectetur.'''


class TableWindow(ToplevelWooster):

    name = "TABLE"

    @loguse
    def __init__(self, table, master=None):
        Toplevel.__init__(self, master, class_="Table")
        self.data = table
        self.title("Table %s" % ('TODO'))
        # Don't make it smaller then this
        self.minsize(200, 100)
        # So it doesn't get in the task bar as a separate window but as a child of the master/parent
        self.transient(master)
        self.grid()

    @loguse
    def goTo(self, key):
        self.jeeves.drone(self, "RECORD", self.jeeves.MODE_OPEN, {'key': key, 'table': self.data})

    @loguse
    def goToFunction(self, key):
        '''
        Neede to create this intermediat function because 'key' isn't reused in the for loop and hence all buttons go to the last 'key'
        '''
        return lambda: self.goTo(key)

    @loguse
    def createWidgets(self):
        row = 0
        #if type(self.data) == type({}):
        self.listbox = MultiListbox(self, [["ID", 20], ["Represantation", 50]])  # Listbox(self)
        try:
            for key in self.data:
                # TODO: build in a maximum so we take maximum advantage of iterators
                label = Button(self, text="%s" % (key), command=self.goToFunction(key))
                label.grid(column=0, row=row, sticky=E+W)
                text = Entry(self)
                text.insert(0, "%s" % (self.data[key]))
                text.config(state=DISABLED)
                text.grid(column=1, row=row, sticky=E+W)
                self.listbox.insert(END, ["%s" % (key), "%s" % (self.data[key])])
                row += 1
        except Exception as err:
            logging.getLogger(self.__module__).error(": TableWindow[%r].createWidgets : Not iterable? %s" % (self, err))
            raise
        self.listbox.grid(column=0, columnspan=2, row=row, sticky=E+W)
        row += 1
        self.buttonS = Button(self, text="Close", command=self.close)
        self.buttonS.grid(column=0, row=row, sticky=E+W)
        self.update()

    @loguse
    def inflow(self, jeeves, drone):
        self.jeeves = jeeves
        # TODO: Need to apply the filter in drone.dataobject on self.data
        self.createWidgets()


class Table(suapp.jandw.Wooster):

    @loguse
    def inflow(self, jeeves, drone):
        # TODO: should use the data API for this
        population = {
            '(131GAOC)298': {
                'ID': '(131GAOC)298',
                'band': 'BGC/BR23/2011/298',
                'father': '(AC62)131',
                'mother': 'GAOC',
                'line': 'GA25/(GAOC*)'
            },
            '(AC62)131': {
                'ID': '(AC62)131',
                'band': 'BGC/BR23/2010/131',
                'father': 'AC',
                'mother': '(GOVAYF)62',
                'line': 'GA25/AC*'
            },
            'AC': {
                'ID': 'AC',
                'line': 'GA25/AC'
            },
            '(GOVAYF)62': {
                'ID': '(GOVAYF)62',
                'band': 'BGC/BR23/2008/62',
                'father': 'GOc',
                'mother': 'VAYF',
                'line': 'FS2/GO*HH731/VAYF'
            },
            'GOc': {
                'ID': 'GOc',
                'line': 'FS2/GO'
            },
            'VAYF': {
                'ID': 'VAYF',
                'line': 'HH731/VAYF'
            },
            'GAOC': {
                'ID': 'GAOC',
                'line': 'GA25/GOAC'
            }
        }
        table = population
        if 'table' in drone.dataobject:
            if 'tables' in drone.dataobject:
                if drone.dataobject['table'] in drone.dataobject['tables']:
                    #print("Table: %s: %s" % (drone.dataobject['table'], drone.dataobject['tables'][drone.dataobject['table']]))
                    table = drone.dataobject['tables'][drone.dataobject['table']]
        if isinstance(drone.fromvertex, Frame):
            logging.getLogger(self.__module__).debug(": TableFactory[%r].inflow : Using parent" % (self))
            # TODO: if it has been closed/destroyed then give the parent of fromvertex instead?
            window = TableWindow(table, drone.fromvertex)
        else:
            logging.getLogger(self.__module__).debug(": TableFactory[%r].inflow : Not using parent" % (self))
            window = TableWindow(table)
        window.inflow(jeeves, drone)
        window.lift()
        window.focus_set()


class RecordWindow(ToplevelWooster):

    @loguse
    def __init__(self, master=None):
        Toplevel.__init__(self, master, class_="About")
        self.title("Record")
        # Don't make it smaller than this.
        self.minsize(50, 50)
        # So it doesn't get in the task bar as a separate window but as a child of the master/parent.
        self.transient(master)
        self.grid()

    @loguse
    def __edit(self, key):
        print("Key: %s" % (key)) # DELME
        # If the value is composite (map), open a RecordWindow modal
        # If the value is singular, open a EditWindow modal
        return

    @loguse
    def __editFunction(self, key):
        return lambda: self.__edit(key)

    @loguse
    def __style(self):
        s = Style()
        styles = s.theme_names()
        i = styles.index(s.theme_use())
        x = styles[0]
        try:
            x = styles[i+1]
        except:
            pass
        s.theme_use(x)
        return "SWITCHING TO STYLE %s" % (x)

    @loguse
    def createWidgets(self):
        row = 0
        try:
            for key in self.table.configuration['fields']:
                if 'auto_increment' in self.table.configuration['fields'][key]:
                    if self.table.configuration['fields'][key]['auto_increment']:
                        continue
                label = Label(self, text="%s: " % (key))
                label.grid(column=0, row=row, sticky=E)
                text = Entry(self)  #, textvariable=self.data[key])
                if key in self.data:
                    if 'toVisual' in self.table.configuration['fields'][key]:
                        text.insert(0, "%s" % self.table.configuration['fields'][key]['toVisual'](self.data[key]))
                    else:
                        text.insert(0, "%s" % (self.data[key]))
                text.config(state=DISABLED)
                text.grid(column=1, row=row, sticky=E+W)
                button = Button(self, text="\u2026", width=2, command=self.__editFunction(key))  # Black pointing left index finger: \u261a ; Triangle: \u2023 ; Tripple bullet: \u2026
                button.grid(column=2, row=row, sticky=E)
                self.columnconfigure(2, weight=0)
                row += 1
        except Exception as err:
            logging.getLogger(self.__module__).error(": RecordWindow[%r].createWidgets : Not iterable? %s" % (self, err))
            raise
        self.buttonS = Button(self, text="Save", command=self.close)  # u25b6
        self.buttonS.grid(column=0, row=row)
        self.buttonC = Button(self, text="Cancel", command=self.__style)  # u25b6
        self.buttonC.grid(column=1, row=row, sticky=W)
        self.update()

    @loguse
    def inflow(self, jeeves, drone):
        self.jeeves = jeeves
        self.table = drone.dataobject.get('table', None)
        self.data = drone.dataobject.get('object', drone.dataobject.get('key', None))
        self.createWidgets()


class Record(suapp.jandw.Wooster):
    '''
    Note: it will open a new window. If you want to avoid doubles open, use subclass UniqueRecordFactory
    '''
    @loguse
    def inflow(self, jeeves, drone):
        if isinstance(drone.fromvertex, Frame):
            logging.getLogger(self.__module__).debug(": RecordFactory[%r].inflow : Using parent" % (self))
            # TODO: if it has been closed/destroyed then give the parent of fromvertex instead?
            RecordWindow(drone.fromvertex).inflow(jeeves, drone)
        else:
            logging.getLogger(self.__module__).debug(": RecordFactory[%r].inflow : Not using parent" % (self))
            RecordWindow().inflow(jeeves, drone)


class UniqueRecord(Record):

    windowreferences = {}

    @loguse
    def inflow(self, jeeves, drone):
        # TODO replace the id and object!
        table = drone.dataobject['table']
        if 'key' in drone.dataobject:
            key = drone.dataobject['key']
        elif 'object' in drone.dataobject:
            object = drone.dataobject['object']
            key = table.getKey(object)
            # We looked it up so we just as wel might put it in.
            drone.dataobject['key'] = key
        logging.getLogger(self.__module__).debug(": UniqueRecordFactory[%r].inflow : windowreferences: %s in %s" % (self, key, self.windowreferences))
        if key in self.windowreferences:
            logging.getLogger(self.__module__).debug(": UniqueRecordFactory[%r].inflow : Reusing for %s" % (self, key))
            if self.windowreferences[key].closed:
                logging.getLogger(self.__module__).debug(": UniqueRecordFactory[%r].inflow : Oops that one is already closed so not reusing it." % (self))
                del self.windowreferences[key]
        if key not in self.windowreferences:
            if isinstance(drone.fromvertex, Frame):
                logging.getLogger(self.__module__).debug(": UniqueRecordFactory[%r].inflow : Using parent" % (self))
                # TODO: if it has been closed/destroyed then give the parent of fromvertex instead?
                self.windowreferences[key] = RecordWindow(drone.fromvertex)
            else:
                logging.getLogger(self.__module__).debug(": UniqueRecordFactory[%r].inflow : Not using parent" % (self))
                self.windowreferences[key] = RecordWindow()
            self.windowreferences[key].inflow(jeeves, drone)
        self.windowreferences[key].lift()
        self.windowreferences[key].focus_set()


class AboutWindow(ToplevelWooster):

    @loguse
    def __init__(self, master=None):
        Toplevel.__init__(self, master, class_="About")
        self.title("About")
        # Don't make it smaller then this
        self.minsize(300, 200)
        # So it doesn't get in the task bar as a separate window but as a child of the master/parent
        self.transient(master)
        self.grid()
        self.createWidgets()

    @loguse
    def createWidgets(self):
        self.text = Text(self, wrap=WORD)
        self.text.config(state=DISABLED)
        self.text.grid()
        self.button = Button(self, text="Close", command=self.close)
        self.button.grid()
        self.update()

    @loguse
    def inflow(self, jeeves, drone):
        self.jeeves = jeeves
        # Looking for txt file
        text = []
        file_name = self.jeeves.app.configuration["self"].rsplit(".", 1)[0]
        file_name += ".txt"
        try:
            with open(file_name) as fh:
                for line in fh:
                    text.append(line)
        except OSError as e:
            logging.getLogger(self.__module__).warning("Could not open about file %s.", file_name)
        except IOError as e:
            logging.getLogger(self.__module__).warning("Could not open about file %s.", file_name)
        if not text:
            text = ["ERROR: Could not open file %s." % (file_name)]
        self.text.config(state=NORMAL)
        self.text.delete('1.0', END)
        self.text.insert(END, "\n".join(text))
        self.text.config(state=DISABLED)
        self.update()


class About(suapp.jandw.Wooster):
    '''
    Perhaps I should replace the FACTORY with just a FUNCTION (though it doesn't make a lot of difference in python)
    '''
    @loguse
    def __init__(self):
        self.window = None

    @loguse
    def inflow(self, jeeves, drone):
        if self.window:
            if self.window.closed:
                self.window = None
        if not self.window:
            if isinstance(drone.fromvertex, Frame):
                logging.getLogger(self.__module__).debug(": About[%r].inflow : Using parent" % (self))
                # TODO: if it has been closed/destroyed then give the parent of fromvertex instead?
                self.window = AboutWindow(drone.fromvertex)
            else:
                logging.getLogger(self.__module__).debug(": About[%r].inflow : Not using parent" % (self))
                self.window = AboutFrame()
        self.window.inflow(jeeves, drone)
        self.window.focus_set()


class Application(Frame, suapp.jandw.Wooster):

    name = "APP"
    dataobject = {'name': 'SuApp'}
    testdata = {"ID": "(150112)164", "ring": "BGC/BR23/10/164"}
    tables = {}

    @loguse
    def __init__(self, master=None):
        Frame.__init__(self, master, class_="Application")
        # Default title, could be overriden in inflow
        self._root().title("SuApp")
        self._root().minsize(400, 300)
        self.grid()
        # Moved to inflow self.createWidgets()

    def openTableWindow(self, tablename):
        '''
        Neede to create this intermediat function because 'key' isn't reused in the for loop and hence all buttons go to the last 'key'
        '''
        return lambda: self.__testTable(tablename)

    @loguse
    def createWidgets(self):
        top = self.winfo_toplevel()
        self.menuBar = Menu(top, tearoff=0)
        top['menu'] = self.menuBar

        self.menuFile = Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label="File", menu=self.menuFile)
        self.menuFile.add_command(label="Quit", command=self.close)

        self.menuRecord = Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label="Record", menu=self.menuRecord)
        self.menuRecord.add_command(label="Test record (\u20ac)", command=self.__testRecord)

        self.menuTable = Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label="Table", menu=self.menuTable)
        for table in self.tables:
            self.menuTable.add_command(label="%s" % (table), command=self.openTableWindow(table))

        self.menuHelp = Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label="Help", menu=self.menuHelp)
        self.menuHelp.add_command(label="About", command=self.__about)
        self.menuHelp.add_command(label="Configuration", command=self.__configuration)

    @loguse
    def __testTable(self, tablename):
        self.jeeves.drone(self, "TABLE", self.jeeves.MODE_OPEN, {'tables': self.tables, 'table': tablename})

    @loguse
    def __testRecord(self):
        self.jeeves.drone(self, "RECORD", self.jeeves.MODE_OPEN, {'table': self.tables['organism'], 'object': self.testdata})

    @loguse
    def __about(self):
        self.jeeves.drone(self, "ABOUT", self.jeeves.MODE_MODAL, None)

    @loguse
    def __configuration(self):
        self.jeeves.drone(self, "CONFIGURATION", self.jeeves.MODE_MODAL, None)

    @loguse
    def inflow(self, jeeves, drone):
        if drone.dataobject:
            self.dataobject = drone.dataobject
        if 'name' not in self.dataobject:
            self.dataobject['name'] = 'SuApp'
        self._root().title(self.dataobject['name'])
        if 'tables' in self.dataobject:
            logging.getLogger(self.__module__).debug(": Application[%r].inflow() : Setting tables." % (self))
            self.tables = self.dataobject['tables']
        self.jeeves = jeeves
        self.createWidgets()  # Perhaps this needs to be in mainloop() so we can do a refresh?
        self.mainloop()

    @loguse
    def lock(self):
        pass

    @loguse
    def unlock(self):
        pass

    @loguse
    def destroy(self):
        '''
        When you click the [X]
        '''
        self.preClose()
        super().destroy()

    @loguse
    def preClose(self):
        pass

    @loguse
    def close(self):
        '''
        Close as Wooster
        '''
        self.destroy()
        self.quit()


class ConfigurationWindow(ToplevelWooster):

    @loguse
    def __init__(self, master=None):
        Toplevel.__init__(self, master, class_="Configuration")
        self.title("Configuration")
        # Don't make it smaller then this
        self.minsize(300, 200)
        # So it doesn't get in the task bar as a separate window but as a child of the master/parent
        self.transient(master)
        self.grid()
        self.createWidgets()

    @loguse
    def createWidgets(self):
        self.text = Text(self, wrap=WORD)
        self.text.config(state=DISABLED)
        self.text.grid()
        self.button = Button(self, text="Close", command=self.close)
        self.button.grid()
        self.update()

    @loguse
    def inflow(self, jeeves, drone):
        self.jeeves = jeeves
        self.text.config(state=NORMAL)
        self.text.delete(1.0, END)
        print(type(self.jeeves.app.configuration))
        self.text.insert(END, "Configuration of the Application:\n\n%s" % (simple_json.dumps(dict(self.jeeves.app.configuration), indent="    ")))
        self.text.config(state=DISABLED)
        self.update()


class Configuration(suapp.jandw.Wooster):

    name = "CONFIGURATION"

    '''
    Perhaps I should replace the FACTORY with just a FUNCTION (though it doesn't make a lot of difference in python)
    '''
    @loguse
    def __init__(self):
        self.window = None

    @loguse
    def inflow(self, jeeves, drone):
        if self.window:
            if self.window.closed:
                self.window = None
        if not self.window:
            if isinstance(drone.fromvertex, Frame):
                logging.getLogger(self.__module__).debug(": Configuration[%r].inflow : Using parent" % (self))
                # TODO: if it has been closed/destroyed then give the parent of fromvertex instead?
                self.window = ConfigurationWindow(drone.fromvertex)
            else:
                logging.getLogger(self.__module__).debug(": Configuration[%r].inflow : Not using parent" % (self))
                self.window = AboutFrame()
        self.window.inflow(jeeves, drone)
        self.window.focus_set()


class View(suapp.jandw.Wooster):
    """
    Generic view page for showing.
    """
    @loguse('@')  # Not logging the return value.
    def inflow(self, jeeves, drone):
        """
        Entry point for the view.
        """
        self.jeeves = jeeves

        # Getting the flow (usually uppercase) and ref (lowercase) names.
        flow_name = drone.name
        ref_name = flow_name.lower()
        name = ref_name.capitalize()

        # Getting the view definition.
        definition = jeeves.views.get(flow_name, {})

        # Getting the session, params and preparing the scope.
        session = drone.dataobject.get('session', {})
        # Setting default dabase paging parameters for the query.
        query_params = {"pagenum": 1, "pagesize": 5}
        # Getting the http request params.
        for param in drone.dataobject['params']:
            query_params[param] = drone.dataobject['params'][param][0]
        scope = {} # NOTUSED
        # scope.update(jeeves.ormscope) # jeeves.ormscope is always empty.

        # JS parameters
        js_params = {}
        if drone.dataobject:
            js_params['query'] = "query/%(query)s?pagenum=%(pagenum)s&pagesize=%(pagesize)s"
        result = []
        js_params['service_url'] = jeeves.app.configuration['httpd']['service_url']

        """"
        # Title
        title = definition.get('name', name)
        if logging.getLogger(self.__module__).isEnabledFor(logging.DEBUG):
            html.append('<!-- DEBUG title = %s -->' % (title))

        def_tabs = definition.get('tabs', {0: {'title': ''}})
        if logging.getLogger(self.__module__).isEnabledFor(logging.DEBUG):
            html.append('<!-- DEBUG def_tabs = %s -->' % (def_tabs))

        tabs = collections.OrderedDict()
        tab_count = 0
        if 'query' in def_tabs:
            if logging.getLogger(self.__module__).isEnabledFor(logging.DEBUG):
                html.append('<!-- DEBUG query = %s -->' % (def_tabs['query']))
            tab_title = def_tabs.get('title', name)
            tab_objects = self.jeeves.do_query(def_tabs['query'], params=query_params)
            parameters = self.jeeves.pre_query(def_tabs['query'], params=query_params)[1]
            parameters['query'] = def_tabs['query']
            js_query_params = with_expanded_values(js_params, params=parameters)
            js_query_params['view'] = "testview" # TODO
            html.append(View.raw_js % (js_query_params))
            # TESTVIEW
            html.append('<table id="testview">')
            html.append('</table>')
            if logging.getLogger(self.__module__).isEnabledFor(logging.DEBUG):
                html.append('<!-- DEBUG tab_objects = %s -->' % (tab_objects))
            for tab in tab_objects:
                if tab_title[0] == ".":
                    tabs[tab_count] = (getattr(tab, tab_title[1:]), tab)
                else:
                    tabs[tab_count] = (tab_title, tab)
                tab_count += 1
        else:
            # Loop over all integer keys and get out the titles.
            for i in def_tabs:
                # TODO: is this second element in the tuple correct?
                tabs[i] = (def_tabs[i]['title'], def_tabs[i])
                if logging.getLogger(self.__module__).isEnabledFor(logging.DEBUG):
                    html.append('<!-- DEBUG tabs: %s -->' % (tabs))

        # Tab headers
        html.append('<ul class="nav nav-tabs">')
        for i in sorted(tabs): # CHECKME: DO WE NEED SORTED HERE?
            if i is 0:
                html.append('\t<li class="active"><a data-toggle="tab" href="#tab%s">%s</a></li>' % (i, tabs[i][0]))
            else:
                html.append('\t<li><a data-toggle="tab" href="#tab%s">%s</a></li>' % (i, tabs[i][0]))
        html.append('</ul>')

        # Tabs
        html.append('<div class="tab-content">')
        for i in sorted(tabs):
            if logging.getLogger(self.__module__).isEnabledFor(logging.DEBUG):
                html.append('<!-- DEBUG tab: %s = %s -->' % (i, tabs[i]))
            if i is 0:
                html.append('\t<div id="tab%s" class="tab-pane fade in active">' % (i))
            else:
                html.append('\t<div id="tab%s" class="tab-pane fade">' % (i))
            # Sections
            sections = tabs[i][1].get('sections', definition.get('sections', {0: {'title': ''}}))
            if logging.getLogger(self.__module__).isEnabledFor(logging.DEBUG):
                html.append('<!-- DEBUG sections: %s -->' % (sections))
            for s in sorted(sections.keys(), key=str):
                if logging.getLogger(self.__module__).isEnabledFor(logging.DEBUG):
                    html.append('<!-- DEBUG section: %s -->' % (s))
                if not str(s).isdigit():
                    continue
                section_title = sections[s].get('title', '')
                html.append('\t\t<div class="panel panel-default">')  # panel-primary <> panel-default ?
                if section_title != tabs[i][0]:
                    html.append('\t\t\t<div class="panel-heading">%s</div>' % (section_title))
                html.append('\t\t\t<div class="panel-body" id="section%s_%s">' % (i, s))
                # Lines
                lines = sections[s].get('lines', tabs.get('lines', definition.get('sections', {0: {'title': ''}})))
                # DEBUGGING
                if logging.getLogger(self.__module__).isEnabledFor(logging.DEBUG):
                    html.append('<!-- DEBUG lines = %s -->' % (lines))
                line_objects = []
                if 'query' in lines:
                    line_objects = self.jeeves.do_query(lines['query'], params=query_params)
                    query_template, parameters = self.jeeves.pre_query(lines['query'], params=query_params)
                    parameters['query'] = lines['query']
                    js_query_params = with_expanded_values(js_params, params=parameters)
                    js_query_params['view'] = "section%s_%s" % (i, s)
                    if 'elements' in lines:
                        for e in sorted(lines['elements']):
                            value = lines['elements'][e].get('value', '#')
                            element_type = lines['elements'][e].get('type', 'label').lower()
                            outmessage = lines['elements'][e].get('outmessage', '')
                            if value[0] == ".":
                                value = '\' + data["objects"][elementid]["' + value[1:] + '"] + \''
                            html_element = "&nbsp;"
                            if element_type == "button":
                                # Button
                                html_element = View._button_as_button(
                                    value=value,
                                    outmessage=outmessage
                                )
                            else:
                                # Label
                                pass
                            js_query_params['html'] = html_element
                    html.append(View.raw_js % (js_query_params))
                else:
                    for line_object in line_objects:
                        if logging.getLogger(self.__module__).isEnabledFor(logging.DEBUG):
                            html.append('<!-- DEBUG line_object = %s (%s in %s) -->' % (line_object, type(line_object), line_object.__module__))
                        line_elements = []
                        # Line elements
                        if 'elements' in lines:
                            for e in sorted(lines['elements']):
                                if logging.getLogger(self.__module__).isEnabledFor(logging.DEBUG):
                                    html.append('<!-- DEBUG element = %s -->' % (e))
                                value = lines['elements'][e].get('value', '#')
                                element_type = lines['elements'][e].get('type', 'label').lower()
                                outmessage = lines['elements'][e].get('outmessage', '')
                                if value[0] == ".":
                                    value = getattr(line_object, value[1:])
                                if element_type == "button":
                                    html.append("\t\t\t\t" +
                                        View.button(
                                            value=value,
                                            outmessage=outmessage,
                                            module=line_object.__module__,
                                            table=line_object.__class__.__name__.split("_")[-1],
                                            key=line_object._pk_
                                        )
                                    )
                                else:
                                    html.append("\t\t\t\t" + View.label(value=value))
                    for l in sorted(lines.keys(), key=str):
                        if str(l).isdigit():
                            # Line elements
                            if 'elements' in lines[l]:
                                for e in sorted(lines[l]['elements']):
                                    if logging.getLogger(self.__module__).isEnabledFor(logging.DEBUG):
                                        html.append('<!-- DEBUG element = %s -->' % (e))
                                    value = lines[l]['elements'][e].get('value', '#')
                                    l_type = lines[l]['elements'][e].get('type', 'button').lower()
                                    outmessage = lines[l]['elements'][e].get('outmessage', '')
                                    if value[0] == ".":
                                        value = getattr(line_object, value[1:])
                                    if element_type == "button":
                                        html.append("\t\t\t" +
                                            View.button(
                                                value=value,
                                                outmessage=outmessage,
                                                module=line_object.__module__,
                                                table=line_object.__class__.__name__.split("_")[-1],
                                                key=line_object._pk_
                                            )
                                        )
                                    else:
                                        html.append("\t\t\t" + View.label(value=value))
                html.append('\t\t\t</div>')
                html.append('\t\t</div>')

            html.append('\t</div>')
        html.append('</div>')

        return (title, "\n".join(html))
        """


if __name__ == "__main__":
    logging.getLogger(__name__).setLevel(logging.DEBUG)  # DEBUG/INFO
    flow = suapp.jandw.Jeeves()
    flow.flow = {
        "": {
            "START": suapp.jandw.Drone("START", Application()),
            "RECORD": suapp.jandw.Drone("RECORD", UniqueRecord())
        },
        "APP": {
            "ABOUT": suapp.jandw.Drone("ABOUT", About()),
            "TABLE": suapp.jandw.Drone("TABLE", Table())
        }
    }
    flow.start()
