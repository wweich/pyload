# -*- coding: utf-8 -*-

"""
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License,
    or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, see <http://www.gnu.org/licenses/>.
    
    @author: RaNaN
"""

from traceback import print_exc

#from functools import wraps
from module.utils import has_method

from Base import Base

def class_name(p):
    return p.rpartition(".")[2]

class Expose(object):
    """ used for decoration to declare rpc services """
    def __new__(cls, f, *args, **kwargs):
        hookManager.addRPC(class_name(f.__module__), f.func_name, f.func_doc)
        return f

def AddEventListener(event):
    """ used to register method for events """
    class _klass(object):
        def __new__(cls, f, *args, **kwargs):
            hookManager.addEventListener(class_name(f.__module__), f.func_name, event)
            return f
    return _klass


class ConfigHandler(object):
    """ register method as config handler """
    def __new__(cls, f, *args, **kwargs):
        hookManager.addConfigHandler(class_name(f.__module__), f.func_name)
        return f

def threaded(f):
    #@wraps(f)
    def run(*args,**kwargs):
        hookManager.startThread(f, *args, **kwargs)
    return run

class Hook(Base):
    """
    Base class for hook plugins. Please use @threaded decorator for all longer running task.
    """

    #: automatically register event listeners for functions, attribute will be deleted dont use it yourself
    event_map = None

    # Alternative to event_map
    #: List of events the plugin can handle, name the functions exactly like eventname.
    event_list = None  # dont make duplicate entries in event_map


    #: periodic call interval in secondc
    interval = 60

    def __init__(self, core, manager):
        Base.__init__(self, core)

        #: Provide information in dict here, usable by API `getInfo`
        self.info = None

        #: Callback of periodical job task, used by hookmanager
        self.cb = None

        #: `HookManager`
        self.manager = manager

        #register events
        if self.event_map:
            for event, funcs in self.event_map.iteritems():
                if type(funcs) in (list, tuple):
                    for f in funcs:
                        self.evm.addEvent(event, getattr(self,f))
                else:
                    self.evm.addEvent(event, getattr(self,funcs))

            #delete for various reasons
            self.event_map = None

        if self.event_list:
            for f in self.event_list:
                self.evm.addEvent(f, getattr(self,f))

            self.event_list = None

        self.initPeriodical()
        self.init()
        self.setup()

    def initPeriodical(self):
        if self.interval >=1:
            self.cb = self.core.scheduler.addJob(0, self._periodical, threaded=False)

    def _periodical(self):
        try:
            if self.isActivated(): self.periodical()
        except Exception, e:
            self.core.log.error(_("Error executing hooks: %s") % str(e))
            if self.core.debug:
                print_exc()

        self.cb = self.core.scheduler.addJob(self.interval, self._periodical, threaded=False)


    def __repr__(self):
        return "<Hook %s>" % self.__name__

    def isActivated(self):
        """ checks if hook is activated"""
        return self.getConfig("activated")

    def init(self):
        pass

    def setup(self):
        """ more init stuff if needed """
        pass

    def activate(self):
        """  Used to activate the hook """
        if has_method(self.__class__, "coreReady"):
            self.logDebug("Deprecated method .coreReady() use activated() instead")
            self.coreReady()

    def deactivate(self):
        """ Used to deactivate the hook. """
        pass

    def periodical(self):
        pass

    def newCaptchaTask(self, task):
        """ new captcha task for the plugin, it MUST set the handler and timeout or will be ignored """
        pass

    def captchaCorrect(self, task):
        pass

    def captchaInvalid(self, task):
        pass

    # public events starts from here
    def downloadPreparing(self, pyfile):
        pass
    
    def downloadFinished(self, pyfile):
        pass

    def downloadFailed(self, pyfile):
        pass

    def packageFinished(self, pypack):
        pass

    def beforeReconnecting(self, ip):
        pass
    
    def afterReconnecting(self, ip):
        pass