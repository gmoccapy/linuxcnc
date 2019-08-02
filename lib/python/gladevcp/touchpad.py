#!/usr/bin/env python

#   Popup numberpad for use on all numeric only entries

#   Copyright (c) 2017 Kurt Jacobson
#       <kurtcjacobson@gmail.com>
#
#   This file is part of Hazzy.
#
#   Hazzy is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Hazzy is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Hazzy.  If not, see <http://www.gnu.org/licenses/>.



import gtk
import gobject
import os
import pango
import sys
import locale

locale.setlocale(locale.LC_NUMERIC, '')

MODULEDIR = "/home/gmoccapy/hazzy/hazzy"
sys.path.insert(2, MODULEDIR)

import simpleeval 

pydir = os.path.abspath(os.path.dirname(__file__))
IMAGEDIR = os.path.join(pydir, "ui")

_keymap = gtk.gdk.keymap_get_default()  # Needed for keypress emulation



class Touchpad(gtk.Window):
    '''
    here goes the description of the touchpad widget
    We need at least 
    pos    =   Position in X and Y coordinates to show the widget will be from top left corner
    type   =   to let us know if we want a int or float widget
    '''

    __gtype_name__ = 'SpeedControl'
    __gproperties__ = {
        'pos_x'  : ( gobject.TYPE_INT, 'The X Position to show the widget', 'Set the X Pos of the widget',
                    0, 3600, 100, gobject.PARAM_READWRITE|gobject.PARAM_CONSTRUCT),
        'pos_y'  : ( gobject.TYPE_INT, 'The Y Position to show the widget', 'Set the Y Pos of the widget',
                    0, 3600, 100, gobject.PARAM_READWRITE|gobject.PARAM_CONSTRUCT),
        'type' : ( gobject.TYPE_STRING, 'unit', 'Sets the unit to be shown in the bar after the value',
                    "", gobject.PARAM_READWRITE | gobject.PARAM_CONSTRUCT),
                      }
    __gproperties = __gproperties__

    __gsignals__ = {
                    'value_changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_FLOAT,)),
                    'exit': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
                   }



    def __init__(self, kind='float'):

        super(Touchpad, self).__init__()
        self.dro = None
        self.original_text = None
        
        self.simple_eval = simpleeval.SimpleEval()
        
        self.connect("destroy", gtk.main_quit)
        self.connect("key-press-event", self.on_window_key_press_event)
        
        path = '/home/gmoccapy/hazzy/hazzy/modules/touchpads/ui/float_numpad_background.png'
        self.pixbuf = gtk.gdk.pixbuf_new_from_file(path)

        # GUI setup
        if kind == 'float':
         
            self.table = gtk.Table(rows=6,columns=4)
            
            self.dro = gtk.Entry()
            self.table.attach( self.dro, 0, 4, 5, 6, gtk.EXPAND, gtk.EXPAND)
            
            self.table.set_row_spacings(5)
            self.table.set_col_spacings(5)

            self.btn_pm = gtk.Button("+/-")
            self.btn_pm.set_size_request(56,56)
            self.btn_pm.connect("clicked", self.on_change_sign_clicked)
            self.table.attach( self.btn_pm, 0, 1, 4, 5, gtk.SHRINK, gtk.SHRINK )

            self.btn_0 = gtk.Button("0")
            self.btn_0.set_size_request(56,56)
            self.btn_0.connect("clicked", self.on_button_clicked)
            self.table.attach( self.btn_0, 1, 2, 4, 5, gtk.SHRINK, gtk.SHRINK )
            
            self.btn_sep = gtk.Button(",")
            self.btn_sep.set_size_request(56,56)
            self.btn_sep.connect("clicked", self.on_button_clicked)
            self.table.attach( self.btn_sep, 2, 3, 4, 5, gtk.SHRINK, gtk.SHRINK )

            self.btn_1 = gtk.Button("1")
            self.btn_1.set_size_request(56,56)
            self.btn_1.connect("clicked", self.on_button_clicked)
            self.table.attach( self.btn_1, 0, 1, 3, 4, gtk.SHRINK, gtk.SHRINK )

            self.btn_2 = gtk.Button("2")
            self.btn_2.set_size_request(56,56)
            self.btn_2.connect("clicked", self.on_button_clicked)
            self.table.attach( self.btn_2, 1, 2, 3, 4, gtk.SHRINK, gtk.SHRINK )

            self.btn_3 = gtk.Button("3")
            self.btn_3.set_size_request(56,56)
            self.btn_3.connect("clicked", self.on_button_clicked)
            self.table.attach( self.btn_3, 2, 3, 3, 4, gtk.SHRINK, gtk.SHRINK )

            self.btn_ent = gtk.Button("E")
            self.btn_ent.set_size_request(56,112)
            self.btn_ent.connect("clicked", self.on_enter_clicked)
            self.table.attach( self.btn_ent, 3, 4, 3, 5, gtk.SHRINK, gtk.SHRINK )

            self.btn_4 = gtk.Button("4")
            self.btn_4.set_size_request(56,56)
            self.btn_4.connect("clicked", self.on_button_clicked)
            self.table.attach( self.btn_4, 0, 1, 2, 3, gtk.SHRINK, gtk.SHRINK )

            self.btn_5 = gtk.Button("5")
            self.btn_5.set_size_request(56,56)
            self.btn_5.connect("clicked", self.on_button_clicked)
            self.table.attach( self.btn_5, 1, 2, 2, 3, gtk.SHRINK, gtk.SHRINK )

            self.btn_6 = gtk.Button("6")
            self.btn_6.set_size_request(56,56)
            self.btn_6.connect("clicked", self.on_button_clicked)
            self.table.attach( self.btn_6, 2, 3, 2, 3, gtk.SHRINK, gtk.SHRINK )

            self.btn_7 = gtk.Button("7")
            self.btn_7.set_size_request(56,56)
            self.btn_7.connect("clicked", self.on_button_clicked)
            self.table.attach( self.btn_7, 0, 1, 1, 2, gtk.SHRINK, gtk.SHRINK )

            self.btn_8 = gtk.Button("8")
            self.btn_8.set_size_request(56,56)
            self.btn_8.connect("clicked", self.on_button_clicked)
            self.table.attach( self.btn_8, 1, 2, 1, 2, gtk.SHRINK, gtk.SHRINK )

            self.btn_9 = gtk.Button("9")
            self.btn_9.set_size_request(56,56)
            self.btn_9.connect("clicked", self.on_button_clicked)
            self.table.attach( self.btn_9, 2, 3, 1, 2, gtk.SHRINK, gtk.SHRINK )

            self.btn_plus = gtk.Button("+")
            self.btn_plus.set_size_request(56,56)
            self.btn_plus.connect("clicked", self.on_button_clicked)
            self.table.attach( self.btn_plus, 3, 4, 0, 1, gtk.SHRINK, gtk.SHRINK )
            
            self.btn_div = gtk.Button("/")
            self.btn_div.set_size_request(56,56)
            self.btn_div.connect("clicked", self.on_button_clicked)
            self.table.attach( self.btn_div, 0, 1, 0, 1, gtk.SHRINK, gtk.SHRINK )

            self.btn_mul = gtk.Button("*")
            self.btn_mul.set_size_request(56,56)
            self.btn_mul.connect("clicked", self.on_button_clicked)
            self.table.attach( self.btn_mul, 1, 2, 0, 1, gtk.SHRINK, gtk.SHRINK )

            self.btn_min = gtk.Button("-")
            self.btn_min.set_size_request(56,56)
            self.btn_min.connect("clicked", self.on_button_clicked)
            self.table.attach( self.btn_min, 2, 3, 0, 1, gtk.SHRINK, gtk.SHRINK )

            self.alignment = gtk.Alignment()
            self.alignment.set_padding(20, 20, 20, 20)
            self.alignment.add(self.table)
            self.alignment.connect('expose-event', self.draw_pixbuf)

            self.add(self.alignment)
            self.show_all()
            self.set_keep_above(True)
            self.set_decorated(False)
            self.set_size_request(-1,-1)
            #self.connect('check-resize', self.draw_pixbuf)

        else:
            pass

    def draw_pixbuf(self, widget, event = None):
        allocation = widget.get_allocation()
        pixbuf = self.pixbuf.scale_simple(allocation.width, allocation.height, gtk.gdk.INTERP_BILINEAR)
        widget.window.draw_pixbuf(self.style.bg_gc[gtk.STATE_NORMAL], pixbuf, 0, 0, 0,0)
        #self.queue_draw()
        

    # Handles all the character buttons
    def on_button_clicked(self, widget, data = None):
        self.dro.delete_selection() 
        pos = self.dro.get_position()                  # Get current cursor pos
        self.dro.insert_text(widget.get_label(), pos)  # Insert text at cursor pos
        self.dro.set_position(pos + 1)                 # Move cursor one space right

    # Backspace
    def on_backspace_clicked(self, widget):
        pos = self.dro.get_position()       # Get current cursor pos
        self.dro.delete_text(pos - 1, pos)  # Delete one space to left
        self.dro.set_position(pos - 1)      # Move cursor one space to left

    # Change sign
    def on_change_sign_clicked(self, widget):
        val = self.dro.get_text()
        pos = self.dro.get_position()
        if val == "": # or self.keypad:
            self.dro.insert_text("-", pos)
            self.dro.set_position(pos + 1)
        else:
            if val[0] == '-':
                self.dro.delete_text(0, 1)
            else:
                self.dro.insert_text("-", 0)

    # Change units
    # Note: We don't set the cursor to end to keep the user from
    # being able to backspace and leave a partial units string
    def on_change_units_clicked(self, widget):
        pos = self.dro.get_position()
        val = self.dro.get_text()
        if self.units == 'in' and not 'mm' in val:
            self.dro.set_text(val + 'mm')
            self.dro.set_position(pos)
        elif self.units == 'mm' and not 'in' in val:
            self.dro.set_text(val + 'in')
            self.dro.set_position(pos)
        elif 'mm' in val and self.units == 'in':
            val = val.replace('mm', '')
            self.dro.set_text(val)
            self.dro.set_position(pos)
        elif 'in' in val and self.units == 'mm':
            val = val.replace('in', '')
            self.dro.set_text(val)
            self.dro.set_position(pos)


    # Left arrow
    def on_arrow_left_clicked(self, widget):
        pos = self.dro.get_position()
        if pos > 0: # Can't have -1 or we'd loop to the right
            self.dro.set_position(pos - 1)

    # Right arrow
    def on_arrow_right_clicked(self, widget):
        pos = self.dro.get_position()
        self.dro.set_position(pos + 1)

    # Up arrow
    def on_arrow_up_clicked(self, widget):
        event = gtk.gdk.Event(gtk.gdk.KEY_PRESS)
        event.keyval = gtk.keysyms.Up
        self.dro.emit("key-press-event", event)

    # Down arrow
    def on_arrow_down_clicked(self, widget):
        event = gtk.gdk.Event(gtk.gdk.KEY_PRESS)
        event.keyval = gtk.keysyms.Down
        self.dro.emit("key-press-event", event)

    # Space    
    def on_space_clicked(self, widget, data=None):
        pos = self.dro.get_position()       # Get current cursor pos
        self.dro.insert_text("\t", pos)     # Insert tab at cursor pos
        self.dro.set_position(pos + 1)      # Move cursor one tab right

    # Escape
    def on_esc_clicked(self, widget, data=None):
        self.escape() 

    # Enter
    def on_enter_clicked(self, widget):
        self.enter()

    # Catch real ESC or ENTER keypresses, send the rest on to the DRO
    def on_window_key_press_event(self, widget, event, data=None):
        kv = event.keyval
        if kv == gtk.keysyms.Return or kv == gtk.keysyms.KP_Enter:
            self.enter()
        elif kv == gtk.keysyms.Escape:
            self.escape()
        else: # Pass it on to the dro entry widget
            try:
                self.dro.emit("key-press-event", event)
            except:
                self.destroy()

    # Enter action
    def enter(self):
        try:
            # If entry is nothing escape
            if self.dro.get_text() == "" or self.dro.get_text() == "-":
                self.escape()
            else:
                self.dro.emit('activate')
        except:
            pass
        print("Text = ", self.dro.get_text())
        
        val = self.dro.get_text().replace(",", ".")
        print("Localizated Text = ", val)
        
        try:
            val = self.simple_eval.eval(val)
            print("Evaluated Text = ", locale.format("%f",val))
        except:
            self.escape()
        self.destroy()

    # Escape action
    def escape(self):
        self.dro.set_text(self.original_text)
        try:
            event = gtk.gdk.Event(gtk.gdk.KEY_PRESS)
            event.keyval = int(gtk.gdk.keyval_from_name("Escape"))
            event.hardware_keycode = _keymap.get_entries_for_keyval(event.keyval)[0][0]
            event.window = self.dro.window
            self.dro.emit("key-press-event", event)
        except:
            pass
        self.destroy()


    # Escape on entry focus out 
    def on_entry_loses_focus(self, widget, data=None):
        self.escape()


    def show(self, widget, units='in', position=None):
        self.dro = widget
        self.dro.select_region(0, -1)
        self.dro.connect('focus-out-event', self.on_entry_loses_focus)
        self.units = units

        self.original_text = self.dro.get_text()

        if position is not None:
            self.window.move(position[0], position[1])

        self.window.show()


    # Get properties
    def do_get_property(self, property):
        name = property.name.replace('-', '_')
        if name in self.__gproperties.keys():
            return getattr(self, name)
        else:
            raise AttributeError('unknown property %s' % property.name)

    # Set properties
    def do_set_property(self, property, value):
        try:
            name = property.name.replace('-', '_')
            if name in self.__gproperties.keys():
                setattr(self, name, value)
            else:
                raise AttributeError('unknown property %s' % property.name)
        except:
            pass


def main():    
    touchpad = Touchpad()
    touchpad.dro.set_text("0")
    touchpad.show(touchpad.dro)
    gtk.main()

if __name__ == "__main__":
    main()

