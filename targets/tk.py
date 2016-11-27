#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import suapp.jandw
from tkinter import *
from tkinter.ttk import *
from logdecorator import *


#Extra widgets
class MultiListbox(Frame):
    def __init__(self, master, lists):
    	Frame.__init__(self, master)
    	self.lists = []
    	for l,w in lists:
    	    frame = Frame(self); frame.pack(side=LEFT, expand=YES, fill=BOTH)
    	    Label(frame, text=l, borderwidth=1, relief=RAISED).pack(fill=X)
    	    lb = Listbox(frame, width=w, borderwidth=0, selectborderwidth=0,
    			 relief=FLAT, exportselection=FALSE)
    	    lb.pack(expand=YES, fill=BOTH)
    	    self.lists.append(lb)
    	    lb.bind('<B1-Motion>', lambda e, s=self: s._select(e.y))
    	    lb.bind('<Button-1>', lambda e, s=self: s._select(e.y))
    	    lb.bind('<Leave>', lambda e: 'break')
    	    lb.bind('<B2-Motion>', lambda e, s=self: s._b2motion(e.x, e.y))
    	    lb.bind('<Button-2>', lambda e, s=self: s._button2(e.x, e.y))
    	frame = Frame(self); frame.pack(side=LEFT, fill=Y)
    	Label(frame, borderwidth=1, relief=RAISED).pack(fill=X)
    	sb = Scrollbar(frame, orient=VERTICAL, command=self._scroll)
    	sb.pack(expand=YES, fill=Y)
    	self.lists[0]['yscrollcommand']=sb.set

    def _select(self, y):
    	row = self.lists[0].nearest(y)
    	self.selection_clear(0, END)
    	self.selection_set(row)
    	return 'break'

    def _button2(self, x, y):
    	for l in self.lists: l.scan_mark(x, y)
    	return 'break'

    def _b2motion(self, x, y):
    	for l in self.lists: l.scan_dragto(x, y)
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
    	    result.append(l.get(first,last))
    	if last: return apply(map, [None] + result)
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
        super(Toplevel, self).destroy()

    @loguse
    def close(self):
        '''
        Close as Wooster
        '''
        self.destroy()


ipsum = '''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse pretium sapien sit amet magna viverra id faucibus nibh condimentum. Fusce dui magna, venenatis vel elementum eu, suscipit at quam. Nullam sed felis lorem, vel pretium leo. Cras at neque orci. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Pellentesque ullamcorper quam eu ligula mattis tempor. Aliquam erat volutpat. Vivamus feugiat aliquam purus, euismod blandit lacus scelerisque vel. Phasellus sodales dignissim eros nec accumsan. Aenean est lectus, placerat sed ornare ut, congue nec nulla. Phasellus at sapien purus. Maecenas et sapien at ipsum fringilla tempus.

Donec non quam mauris. Vivamus bibendum ante id velit rhoncus molestie. Nullam bibendum suscipit elit sed aliquam. Maecenas felis magna, laoreet ut volutpat eget, varius at lorem. Quisque nisl dolor, aliquet et vestibulum nec, ullamcorper quis libero. Aliquam erat volutpat. Aenean mauris augue, varius sit amet iaculis quis, rhoncus at eros. Phasellus luctus congue cursus. Praesent lobortis vestibulum cursus. Nulla euismod nisi ac diam semper molestie. Curabitur quis leo at velit ultrices consectetur in in tellus. Nunc auctor erat ac justo porttitor consectetur. Cras vestibulum elit nec nulla consectetur euismod. Curabitur sodales vehicula lacus quis iaculis. Nulla laoreet eros eget ipsum commodo aliquet.

Cras gravida egestas nunc a hendrerit. Quisque consequat arcu ac dolor bibendum a porttitor augue malesuada. Etiam suscipit augue ac eros lobortis auctor. Vivamus urna sem, ultrices non ultrices in, sodales id justo. Aenean gravida bibendum risus, a pharetra arcu rhoncus quis. Maecenas interdum fringilla dapibus. Sed non diam massa, a sodales eros. Cras interdum nibh leo. Praesent non urna turpis. Pellentesque posuere massa vel ligula porta sed egestas arcu lacinia. Curabitur rutrum ultrices vestibulum. Mauris posuere, arcu id tempor volutpat, lacus nisl euismod felis, non facilisis purus sem ac sem. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Mauris posuere ornare elit non congue. Praesent pretium, nisl eget pulvinar pulvinar, nibh purus sollicitudin tellus, eget malesuada lacus nulla vel neque.

In non elit nisi. Phasellus porta vestibulum erat non condimentum. Sed sed augue neque, sed venenatis eros. In et nunc neque. Mauris mi velit, dignissim id vehicula at, semper vitae est. Ut porta lacus eget ipsum faucibus vel luctus metus scelerisque. Duis ipsum nulla, rutrum sit amet ultricies et, sodales vitae sem. Donec suscipit aliquam diam, id mollis nibh gravida vel. Quisque in blandit lectus. Fusce interdum nulla turpis, sit amet venenatis metus. Praesent ac tristique tortor.

Suspendisse ut magna sed nulla cursus rutrum. Suspendisse in lacus dui, non bibendum tellus. Nulla facilisi. Morbi urna justo, volutpat eu mattis id, facilisis sed sapien. Vestibulum vitae sapien orci. Proin aliquet euismod neque, vel sodales nulla hendrerit vitae. Sed auctor euismod adipiscing. Curabitur feugiat dui quis lorem gravida a mattis eros vehicula. Aenean eget ullamcorper nunc. Mauris sagittis eros aliquam dolor varius sit amet eleifend dolor placerat. Vestibulum nec dui metus. Nullam nec ante in lectus faucibus condimentum. Donec ac enim purus, et bibendum erat. Aliquam vestibulum tempus consectetur.'''


class TableWindow(ToplevelWooster):

    name = "TABLE"

    @loguse
    def __init__(self, table, master=None):
        Toplevel.__init__(self, master, class_="Table")
        self.data = table
        self.title("Table %s" % ('TODO'))
        # Don't make it smaller then this
        self.minsize(200,100)
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
        self.listbox = MultiListbox(self, [["ID", 20], ["Represantation", 50]]) # Listbox(self)
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
            logging.getLogger(__name__).error(": TableWindow[%r].createWidgets : Not iterable? %s" % (self, err))
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


class TableFactory(suapp.jandw.Wooster):

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
            logging.getLogger(__name__).debug(": TableFactory[%r].inflow : Using parent" % (self))
            # TODO: if it has been closed/destroyed then give the parent of fromvertex instead?
            window = TableWindow(table, drone.fromvertex)
        else:
            logging.getLogger(__name__).debug(": TableFactory[%r].inflow : Not using parent" % (self))
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
        self.minsize(50,50)
        # So it doesn't get in the task bar as a separate window but as a child of the master/parent.
        self.transient(master)
        self.grid()

    @loguse
    def __edit(self, key):
        print("Key: %s" % (key))
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
                text = Entry(self) #, textvariable=self.data[key])
                if key in self.data:
                    if 'toVisual' in self.table.configuration['fields'][key]:
                        text.insert(0, "%s" % self.table.configuration['fields'][key]['toVisual'](self.data[key]))
                    else:
                        text.insert(0, "%s" % (self.data[key]))
                text.config(state=DISABLED)
                text.grid(column=1, row=row, sticky=E+W)
                button = Button(self, text="\u2026", width=2, command=self.__editFunction(key)) # Black pointing left index finger: \u261a ; Triangle: \u2023 ; Tripple bullet: \u2026
                button.grid(column=2, row=row, sticky=E)
                self.columnconfigure(2, weight=0)
                row += 1
        except Exception as err:
            logging.getLogger(__name__).error(": RecordWindow[%r].createWidgets : Not iterable? %s" % (self, err))
            raise
        self.buttonS = Button(self, text="Save", command=self.close) # u25b6
        self.buttonS.grid(column=0, row=row)
        self.buttonC = Button(self, text="Cancel", command=self.__style) # u25b6
        self.buttonC.grid(column=1, row=row, sticky=W)
        self.update()

    @loguse
    def inflow(self, jeeves, drone):
        self.jeeves = jeeves
        if 'table' in drone.dataobject:
            self.table = drone.dataobject['table']
            if 'object' in drone.dataobject:
                self.data = drone.dataobject['object']
            elif 'key' in drone.dataobject:
                self.data = self.table[drone.dataobject['key']]
        self.createWidgets()


class RecordFactory(suapp.jandw.Wooster):
    '''
    Note: it will open a new window. If you want to avoid doubles open, use subclass UniqueRecordFactory
    '''
    @loguse
    def inflow(self, jeeves, drone):
        if isinstance(drone.fromvertex, Frame):
            logging.getLogger(__name__).debug(": RecordFactory[%r].inflow : Using parent" % (self))
            # TODO: if it has been closed/destroyed then give the parent of fromvertex instead?
            RecordWindow(drone.fromvertex).inflow(jeeves, drone)
        else:
            logging.getLogger(__name__).debug(": RecordFactory[%r].inflow : Not using parent" % (self))
            RecordWindow().inflow(jeeves, drone)


class UniqueRecordFactory(RecordFactory):

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
        logging.getLogger(__name__).debug(": UniqueRecordFactory[%r].inflow : windowreferences: %s in %s" % (self, key, self.windowreferences))
        if key in self.windowreferences:
            logging.getLogger(__name__).debug(": UniqueRecordFactory[%r].inflow : Reusing for %s" % (self, key))
            if self.windowreferences[key].closed:
                logging.getLogger(__name__).debug(": UniqueRecordFactory[%r].inflow : Oops that one is already closed so not reusing it." % (self))
                del self.windowreferences[key]
        if key not in self.windowreferences:
            if isinstance(drone.fromvertex, Frame):
                logging.getLogger(__name__).debug(": UniqueRecordFactory[%r].inflow : Using parent" % (self))
                # TODO: if it has been closed/destroyed then give the parent of fromvertex instead?
                self.windowreferences[key] = RecordWindow(drone.fromvertex)
            else:
                logging.getLogger(__name__).debug(": UniqueRecordFactory[%r].inflow : Not using parent" % (self))
                self.windowreferences[key] = RecordWindow()
            self.windowreferences[key].inflow(jeeves, drone)
        self.windowreferences[key].lift()
        self.windowreferences[key].focus_set()


class AboutTL(ToplevelWooster):

    @loguse
    def __init__(self, master=None):
        Toplevel.__init__(self, master, class_="About")
        self.title("About")
        # Don't make it smaller then this
        self.minsize(300,200)
        # So it doesn't get in the task bar as a separate window but as a child of the master/parent
        self.transient(master)
        self.grid()
        self.createWidgets()

    @loguse
    def createWidgets(self):
        self.text = Text(self, wrap=WORD)
        self.text.insert(END, "About the Application.\n\t1. Yes\n\t2. No\n\t3. %s" % (ipsum))
        self.text.config(state=DISABLED)
        self.text.grid()
        self.button = Button(self, text="Close", command=self.close)
        self.button.grid()
        self.update()

    @loguse
    def inflow(self, jeeves, drone):
        self.jeeves = jeeves


class About(suapp.jandw.Wooster):
    '''
    Perhaps I should replace the FACTORY with just a FUNCTION (though it doesn't make a lot of difference in python)
    '''
    @loguse
    def __init__(self):
        self.window = None

    @loguse
    def inflow(self, jeeves, drone):
        print("About window: %s" % self.window)
        if self.window:
            if self.window.closed:
                self.window = None
        if not self.window:
            if isinstance(drone.fromvertex, Frame):
                logging.getLogger(__name__).debug(": About[%r].inflow : Using parent" % (self))
                # TODO: if it has been closed/destroyed then give the parent of fromvertex instead?
                self.window = AboutFrame(drone.fromvertex)
            else:
                logging.getLogger(__name__).debug(": About[%r].inflow : Not using parent" % (self))
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
        self._root().minsize(400,300)
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
    def inflow(self, jeeves, drone):
        if drone.dataobject:
            self.dataobject = drone.dataobject
        if 'name' not in self.dataobject:
            self.dataobject['name'] = 'SuApp'
        self._root().title(self.dataobject['name'])
        if 'tables' in self.dataobject:
            logging.getLogger(__name__).debug(": Application[%r].inflow() : Setting tables." % (self))
            self.tables = self.dataobject['tables']
        self.jeeves = jeeves
        self.createWidgets() # Perhaps this needs to be in mainloop() so we can do a refresh?
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
        super(Frame, self).destroy()

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

class ConfigurationTL(ToplevelWooster):

    @loguse
    def __init__(self, master=None):
        Toplevel.__init__(self, master, class_="Configuration")
        self.title("Configuration")
        # Don't make it smaller then this
        self.minsize(300,200)
        # So it doesn't get in the task bar as a separate window but as a child of the master/parent
        self.transient(master)
        self.grid()
        self.createWidgets()

    @loguse
    def createWidgets(self):
        self.text = Text(self, wrap=WORD)
        self.text.insert(END, "Configuration of the Application.\n\t1. Yes\n\t2. No\n\t3.")
        self.text.config(state=DISABLED)
        self.text.grid()
        self.button = Button(self, text="Close", command=self.close)
        self.button.grid()
        self.update()

    @loguse
    def inflow(self, jeeves, drone):
        self.jeeves = jeeves


class Configuration(suapp.jandw.Wooster):
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
                logging.getLogger(__name__).debug(": Configuration[%r].inflow : Using parent" % (self))
                # TODO: if it has been closed/destroyed then give the parent of fromvertex instead?
                self.window = AboutFrame(drone.fromvertex)
            else:
                logging.getLogger(__name__).debug(": Configuration[%r].inflow : Not using parent" % (self))
                self.window = AboutFrame()
        self.window.inflow(jeeves, drone)
        self.window.focus_set()


if __name__ == "__main__":
    logging.getLogger(__name__).setLevel(logging.DEBUG) # DEBUG/INFO
    flow = Jeeves()
    flow.flow = {
        "": {
            "START": Drone("START", Application()),
            "RECORD": Drone("RECORD", UniqueRecordFactory())
        },
        "APP" : {
            "ABOUT": Drone("ABOUT", AboutFactory()),
            "TABLE": Drone("TABLE", TableFactory())
        }
    }
    flow.start()
