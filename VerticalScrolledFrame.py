# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 03:05:13 2019

@author: wolfg
"""
import tkinter

class VerticalScrolledFrame(tkinter.Frame):
    """A pure Tkinter scrollable frame that actually works!

    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    Source: http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
    """
    def __init__(self, parent, height=20, *args, **kw):
        tkinter.Frame.__init__(self, parent, height=height, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        self.canvas = tkinter.Canvas(self, bd=0, highlightthickness=0, height=height)
        self.canvas.pack(side="left", fill="both", expand=True)
        vscrollbar = tkinter.Scrollbar(self, orient="vertical")
        vscrollbar.pack(fill="y", side="right", expand=False)
        self.canvas.config(yscrollcommand=vscrollbar.set)
        vscrollbar.config(command=self.canvas.yview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tkinter.Frame(self.canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=interior,
                                           anchor="nw")
        
        self.canvas.bind('<Configure>', self._configure_canvas)
        self.canvas.bind('<Configure>', self._configure_canvas)
        self.interior.bind('<Configure>', self._configure_interior)
        self.interior.bind('<Enter>', self._bound_to_mousewheel)
        self.interior.bind('<Leave>', self._unbound_to_mousewheel)

    # track changes to the canvas and frame width and sync them,
    # also updating the scrollbar
    def _configure_interior(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            self.canvas.config(width=self.interior.winfo_reqwidth())
    

    def _configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the inner frame's width to fill the canvas
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())
    

    ### Attempt to include mouse wheel bindings:
    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        def delta(event):
            if event.num == 5 or event.delta < 0:
                return 1
            return -1
        self.canvas.yview_scroll(int((delta(event))), "units")

        

        return
