import os
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from panda3d.core import *
from otp.settings.Settings import Settings
from toontown.toonbase import ToontownGlobals

class BookmarkManager:
    def __init__(self):
        self.bookmarks = Settings("bookmarks.json");
        self.convertData();
        
    def addBookmark(self, ip, name):
        if ip not in self.bookmarks:
            self.bookmarks[ip] = name;
            return 1; # Success!
        else:
            return 2; # Already Exists!
        
    def removeBookmark(self, ip):
        if ip in self.bookmarks:
            self.bookmarks.remove(ip);
            return 1; # Success
        else:
            return 2; # Doesn't exist! (How did you manage my dood)
            
    def getBookmarks(self):
        return self.bookmarks;
        
    def convertData(self):
        # Convert bookmark format 1.0 to 2.0 format
        oldbookmarks = []
        if os.path.exists(os.path.join(ToontownGlobals.CurrentDirectory, 'bookmarks.dat')):
            file = open(os.path.join(ToontownGlobals.CurrentDirectory, 'bookmarks.dat'), 'rb');
            data = file.read();
            file.close();
            
            dg = PyDatagram(data);
            data = PyDatagramIterator(dg);
            
            def getBookmark(index, dgi):
                name = dgi.get_string();
                address = dgi.get_string();
                if address != '':
                    oldbookmarks.append([name, address]);
            
            for index in xrange(data.get_uint8()):
                getBookmark(index, data);
        
            for bookmark in oldbookmarks:
                name = bookmark[0];
                address = bookmark[1];
                self.bookmarks[address] = name;
            os.unlink(os.path.join(ToontownGlobals.CurrentDirectory, 'bookmarks.dat'));