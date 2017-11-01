#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
from GUI import About_GUI

class About(About_GUI.MyFrame):
    def __init__(self, parent):
        About_GUI.MyFrame.__init__(self, parent, -1, "")
        self.SetTitle('About')
        self.buttonClose.Bind(wx.EVT_BUTTON, self.OnClose)
        
        self.Refresh()
        self.Layout()
    
    def OnClose(self,event):
        self.Close()


