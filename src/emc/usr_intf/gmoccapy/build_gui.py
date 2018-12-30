#!/usr/bin/env python
# -*- coding:UTF-8 -*-
"""
This file is part of gmoccapy and contains all information to rearrange
the widgets of GUI to fit the users needs
Most information we need, can be taken from the INI file

    Copyright 2017 Norbert Schechner
    nieson@web.de

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
import traceback                   # needed to launch trace python errors

import sys                         # handle system calls
import os                          # needed to get the paths and directories
import gtk                         # base for pygtk widgets and constants
import gobject                     # needed to send signals
import locale                      # for setting the language of the GUI
import gettext                     # to extract the strings to be translated
import subprocess                  # to launch onboard and other processes
import tempfile                    # needed only if the user click new in edit
                                   # mode to open a new empty file

# ToDo : is this necessary ?
from time import sleep             # needed to wait for command complete
# ToDo : is this necessary ?


#import gladevcp.makepins                  # needed for the dialog"s calculator widget
from gladevcp.combi_dro import Combi_DRO  # we will need it to make the DRO

#from gmoccapy import widgets              # a class to handle the widgets
from gmoccapy import getiniinfo           # this handles the INI File reading
from gmoccapy import preferences          # this handles the preferences

BASE = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), ".."))
LOCALEDIR = os.path.join(BASE, "share", "locale")
DATADIR = os.path.join(BASE, "share", "gmoccapy")
IMAGEDIR = os.path.join(DATADIR, "images")

# set up paths to files, part two
#CONFIGPATH = os.environ['CONFIG_DIR']
XMLNAME = os.path.join(DATADIR, "gmoccapy.glade")
#THEMEDIR = "/usr/share/themes"
#USERTHEMEDIR = os.path.join(os.path.expanduser("~"), ".themes")

# localization
#LOCALEDIR = os.path.join(BASE, "share", "locale")
#import locale
#locale.setlocale(locale.LC_ALL, '')

# path to TCL for external programs eg. halshow
TCLPATH = os.environ['LINUXCNC_TCL_DIR']

# this is for hiding the pointer when using a touch screen
pixmap = gtk.gdk.Pixmap(None, 1, 1, 1)
color = gtk.gdk.Color()
INVISABLE = gtk.gdk.Cursor(pixmap, pixmap, color, color, 0, 0)

_INCH = 0                         # imperial units are active
_MM = 1                           # metric units are active

# set names for the tab numbers, its easier to understand the code
# Bottom Button Tabs
_BB_MANUAL = 0
_BB_MDI = 1
_BB_AUTO = 2
_BB_HOME = 3
_BB_TOUCH_OFF = 4
_BB_SETUP = 5
_BB_EDIT = 6
_BB_TOOL = 7
_BB_LOAD_FILE = 8
#_BB_HOME_JOINTS will not be used, we will reorder the notebooks to get the correct page shown

# Throws up a dialog with debug info when an error is encountered
def excepthook(exc_type, exc_obj, exc_tb):
    try:
        w = app.widgets.window1
    except KeyboardInterrupt:
        sys.exit()
    except NameError:
        w = None
    lines = traceback.format_exception(exc_type, exc_obj, exc_tb)
    m = gtk.MessageDialog(w,
                          gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                          gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                          ("Found an error!\nThe following information may be useful in troubleshooting:\n\n")
                          + "".join(lines))
    m.show()
    m.run()
    m.destroy()

sys.excepthook = excepthook


# the class must inherit from gobject to be able to send signals
class Build_GUI(gobject.GObject):
    
    '''
    This file is part of gmoccapy and will handle all the GUI related code.
    It will build part of the GUI dynamically, according to the user 
    configuration. All relevant information will be read from the INI File.
    '''

    __gtype_name__ = 'Build_GUI'
    __gproperties__ = {    }
    __gproperties = __gproperties__

    __gsignals__ = {
                    'estop_active'    : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,)),
                    'on_active'       : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,)),
                    'set_manual'      : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
                    'set_mdi'         : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
                    'set_auto'        : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
                    'set_motion_mode' : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_INT,)),
                    'mdi_command'     : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
                    'mdi_abort'       : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
                    'home_clicked'    : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
                    'unhome_clicked'  : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
                    'touch_clicked'   : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
                    'jog_incr_changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
                    'jog_btn_pressed' : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_STRING,)),
                    'jog_btn_released': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_STRING,)),
                    'error'           : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
                    'exit'            : (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
                   }


    def __init__(self, widgets, _RELEASE):
        super(Build_GUI, self).__init__()
        
        # prepare for translation / internationalization
        locale.setlocale(locale.LC_ALL, '')
        locale.bindtextdomain("gmoccapy", LOCALEDIR)
        gettext.install("gmoccapy", localedir=LOCALEDIR, unicode=True)
        gettext.bindtextdomain("gmoccapy", LOCALEDIR)

        # get all widgets as class, so they can be called directly
        self.widgets = widgets

        self.get_ini_info = getiniinfo.GetIniInfo()
        self.prefs = preferences.preferences(self.get_ini_info.get_preference_file_path())
        self._RELEASE = _RELEASE

        self._get_ini_data()
        self._get_pref_data()

        # make all widgets we create dynamically
        self._make_DRO()
        self._make_ref_button()
        self._make_touch_button()
        self._make_jog_increments()
        self._make_jog_button()
        self._make_macro_button()
 
        # check for virtual keyboard
        self._init_keyboard()

        # set initial values for all widgets
        self._init_widgets()
        #self._activate_widgets()

        #self._init_gremlin()

        # if we have a lathe, we need to rearrange some stuff
        # we will do that in a separate function
        if self.lathe_mode:
            self._make_lathe()
        
        self._arrange_dro()
        self._arrange_jog_button()

        # set initial values for the GUI
#        self._set_initial_values()

#        panel = gladevcp.makepins.GladePanel(self.XMLNAME, self.builder, None)

        # Show the main window
#        self.widgets.window1.show()


###############################################################################
##                     create widgets dynamically                            ##
###############################################################################    

    def _make_DRO(self):
        print("**** GMOCCAPY build_GUI INFO ****")
        print("**** Entering make_DRO")
        print("axis_list = {0}".format(self.axis_list))
        
        # we build one DRO for each axis
        self.dro_dic = {} 
        for pos, axis in enumerate(self.axis_list):
            joint = self._get_joint_from_joint_axis_dic(axis)
            dro = Combi_DRO()
            dro.set_joint_no(joint)
            dro.set_axis(axis)
            dro.change_axisletter(axis.upper())
            dro.show()
            dro.set_property("name", "Combi_DRO_{0}".format(pos))
            dro.set_property("abs_color", gtk.gdk.color_parse(self.abs_color))
            dro.set_property("rel_color", gtk.gdk.color_parse(self.rel_color))
            dro.set_property("dtg_color", gtk.gdk.color_parse(self.dtg_color))
            dro.set_property("homed_color", gtk.gdk.color_parse(self.homed_color))
            dro.set_property("unhomed_color", gtk.gdk.color_parse(self.unhomed_color))
            dro.set_property("actual", self.dro_actual)
            dro.connect("clicked", self._on_DRO_clicked)
            self.dro_dic[dro.name] = dro

    def _make_ref_button(self):
        print("**** GMOCCAPY build_GUI INFO ****")
        print("**** Entering make ref button")

        # check if we need axis or joint homing button
        if self.trivial_kinematics:
            # lets find out, how many axis we got
            dic = self.axis_list
            name_prefix = "axis"
        else:
            # lets find out, how many joints we got
            dic = self.joint_axis_dic
            name_prefix = "joint"
        num_elements = len(dic)
        
        # as long as the number of axis is less 6 we can use the standard layout
        # we can display 6 axis without the second space label
        # and 7 axis if we do not display the first space label either
        # if we have more than 7 axis, we need arrows to switch the visible ones
        if num_elements < 7:
            lbl = self._get_space_label("lbl_space_0")
            self.widgets.hbtb_ref.pack_start(lbl)
    
        file = "ref_all.png"
        filepath = os.path.join(IMAGEDIR, file)
        btn = self._get_button_with_image("ref_all", filepath, None)
        btn.set_property("tooltip-text", _("Press to home all {0}".format(name_prefix)))
        btn.connect("clicked", self._on_btn_home_clicked)
        # we use pack_start, so the widgets will be moved from right to left
        # and are displayed the way we want
        self.widgets.hbtb_ref.pack_start(btn)

        if num_elements > 7:
            # show the previous arrow to switch visible homing button)
            btn = self._get_button_with_image("previous_button", None, gtk.STOCK_GO_BACK)
            btn.set_sensitive(False)
            btn.set_property("tooltip-text", _("Press to display previous homing button"))
            btn.connect("clicked", self._on_btn_previous_clicked)
            self.widgets.hbtb_ref.pack_start(btn)

        # do not use this label, to allow one more axis
        if num_elements < 6:
            lbl = self._get_space_label("lbl_space_2")
            self.widgets.hbtb_ref.pack_start(lbl)

        for pos, elem in enumerate(dic):

            file = "ref_{0}.png".format(elem)
            filepath = os.path.join(IMAGEDIR, file)

            name = "home_{0}_{1}".format(name_prefix, elem)
            btn = self._get_button_with_image(name, filepath, None)
            btn.set_property("tooltip-text", _("Press to home {0} {1}".format(name_prefix, elem)))
            btn.connect("clicked", self._on_btn_home_clicked)

            self.widgets.hbtb_ref.pack_start(btn)

            # if we have more than 7 axis we need to hide some button
            if num_elements > 7:
                if pos > 4:
                    btn.hide()

        if num_elements > 7:
            # show the next arrow to switch visible homing button)
            btn = self._get_button_with_image("next_button", None, gtk.STOCK_GO_FORWARD)
            btn.set_property("tooltip-text", _("Press to display next homing button"))
            btn.connect("clicked", self._on_btn_next_clicked)
            self.widgets.hbtb_ref.pack_start(btn)

        # if there is space left, fill it with space labels
        start = self.widgets.hbtb_ref.child_get_property(btn,"position")
        for count in range( start + 1 , 8):
            lbl = self._get_space_label("lbl_space_{0}".format(count))
            self.widgets.hbtb_ref.pack_start(lbl)
 
        file = "unhome.png"
        filepath = os.path.join(IMAGEDIR, file)
        name = "unref_all"
        btn = self._get_button_with_image(name, filepath, None)
        btn.set_property("tooltip-text", _("Press to unhome all {0}".format(name_prefix)))
        btn.connect("clicked", self._on_btn_unhome_clicked)
        self.widgets.hbtb_ref.pack_start(btn)
        
        name = "home_back"
        btn = self._get_button_with_image(name, None, gtk.STOCK_UNDO)
        btn.set_property("tooltip-text", _("Press to return to main button list"))
        btn.connect("clicked", self._on_btn_home_back_clicked)
        self.widgets.hbtb_ref.pack_start(btn)
        
        self.ref_button_dic = {}
        children = self.widgets.hbtb_ref.get_children()
        for child in children:
            self.ref_button_dic[child.name] = child

    def _make_touch_button(self):
        print("**** GMOCCAPY build_GUI INFO ****")
        print("**** Entering make touch button")

        dic = self.axis_list
        num_elements = len(dic)
        end = 7

        if self._check_toolmeasurement():
            # we will have 3 buttons on the right side
            end -= 1

        btn = gtk.ToggleButton(_("  edit\noffsets"))
        btn.connect("toggled", self.on_tbtn_edit_offsets_toggled)
        btn.set_property("tooltip-text", _("Press to edit the offsets"))
        btn.set_property("name", "edit_offsets")
        btn.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))
        self.widgets.hbtb_touch_off.pack_start(btn)
        btn.show()

        if num_elements > 6:
            # show the previous arrow to switch visible touch button)
            btn = self._get_button_with_image("previous_button", None, gtk.STOCK_GO_BACK)
            btn.set_property("tooltip-text", _("Press to display previous homing button"))
            btn.connect("clicked", self._on_btn_previous_touch_clicked)
            self.widgets.hbtb_touch_off.pack_start(btn)
            end -= 1
            btn.hide()
        
        for pos, elem in enumerate(dic):
            file = "touch_{0}.png".format(elem)
            filepath = os.path.join(IMAGEDIR, file)

            name = "touch_{0}".format(elem)
            btn = self._get_button_with_image(name, filepath, None)
            btn.set_property("tooltip-text", _("Press to set touch off value for axis {0}".format(elem.upper())))
            #btn.connect("clicked", self._on_btn_t)

            self.widgets.hbtb_touch_off.pack_start(btn)
            
            if pos > end - 2:
                btn.hide()

        if num_elements > (end - 1):
            # show the next arrow to switch visible homing button)
            btn = self._get_button_with_image("next_button", None, gtk.STOCK_GO_FORWARD)
            btn.set_property("tooltip-text", _("Press to display next homing button"))
            btn.connect("clicked", self._on_btn_next_touch_clicked)
            self.widgets.hbtb_touch_off.pack_start(btn)
            btn.show()
            end -= 1

        # if there is space left, fill it with space labels
        start = self.widgets.hbtb_touch_off.child_get_property(btn,"position")
        for count in range( start + 1 , end):
            print("Count = ", count)
            lbl = self._get_space_label("lbl_space_{0}".format(count))
            self.widgets.hbtb_touch_off.pack_start(lbl)
            lbl.show()

        btn = gtk.Button(_("zero\n G92"))
#        btn.connect(self.on_btn_zero_g92_clicked)
        btn.set_property("tooltip-text", _("Press to reset all G92 offsets"))
        btn.set_property("name", "zero_offsets")
        self.widgets.hbtb_touch_off.pack_start(btn)
        btn.show()

        if self._check_toolmeasurement():
            btn = gtk.Button(_(" Block\nHeight"))
#            btn.connect(self.on_btn_block_height_clicked)
            btn.set_property("tooltip-text", _("Press to enter new value for block height"))
            btn.set_property("name", "block_height")
            self.widgets.hbtb_touch_off.pack_start(btn)
            btn.show()

        print("tool measurement OK = ",self._check_toolmeasurement())

        btn = gtk.Button(_("    set\nselected"))
        #btn.connect(self._on_btn_set_selected_clicked)
        btn.set_property("tooltip-text", _("Press to set the selected coordinate system to be the active one"))
        btn.set_property("name", "set_active")
        self.widgets.hbtb_touch_off.pack_start(btn)
        btn.show()

        name = "touch_back"
        btn = self._get_button_with_image(name, None, gtk.STOCK_UNDO)
        btn.set_property("tooltip-text", _("Press to return to main button list"))
        btn.connect("clicked", self._on_btn_home_back_clicked)
        self.widgets.hbtb_touch_off.pack_start(btn)
        btn.show()
        
        self.touch_button_dic = {}
        children = self.widgets.hbtb_touch_off.get_children()
        for child in children:
            self.touch_button_dic[child.name] = child

    def _make_jog_increments(self):
        print("**** GMOCCAPY build_GUI INFO ****")
        print("**** Entering make jog increments")
        # Now we will build the option buttons to select the Jog-rates
        # We do this dynamically, because users are able to set them in INI File
        # because of space on the screen only 10 items are allowed
        # jogging increments

        self.incr_rbt_list = []

        # We get the increments from INI File
        if len(self.jog_increments) > 10:
            print(_("**** GMOCCAPY build_GUI INFO ****"))
            print(_("**** To many increments given in INI File for this screen ****"))
            print(_("**** Only the first 10 will be reachable through this screen ****"))
            # we shorten the increment list to 10 (first is default = 0)
            self.jog_increments = self.jog_increments[0:11]

        # The first radio button is created to get a radio button group
        # The group is called according the name off  the first button
        # We use the pressed signal, not the toggled, otherwise two signals will be emitted
        # One from the released button and one from the pressed button
        # we make a list of the buttons to later add the hardware pins to them
        label = _("Continuous")
        rbt0 = gtk.RadioButton(None, label)
        rbt0.set_property("name","rbt_0")
        rbt0.connect("pressed", self._jog_increment_changed, 0)
        self.widgets.vbtb_jog_incr.pack_start(rbt0, True, True, 0)
        rbt0.set_property("draw_indicator", False)
        rbt0.show()
        rbt0.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))
        self.incr_rbt_list.append(rbt0)
        # the rest of the buttons are now added to the group
        # self.no_increments is set while setting the hal pins with self._check_len_increments
        for item in range(1, len(self.jog_increments)):
            print self.jog_increments[item]
            name = "rbt_{0}".format(item)
            rbt = gtk.RadioButton(rbt0, self.jog_increments[item])
            rbt.set_property("name",name)
            rbt.connect("pressed", self._jog_increment_changed, self.jog_increments[item])
            self.widgets.vbtb_jog_incr.pack_start(rbt, True, True, 0)
            rbt.set_property("draw_indicator", False)
            rbt.show()
            rbt.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))
            self.incr_rbt_list.append(rbt)
        rbt0.set_active(True)
        self.active_increment = rbt0

    def _make_jog_button(self):
        self.jog_button_dic = {}

        print ("Trivial kinematics = ", self.trivial_kinematics)
        #ToDo : we have to check for non trivial kinematics, as in that case we need also Joint joggin button
        if not self.trivial_kinematics:
            # we need joint jogging button
            print ("Trivial kinematics = ", self.trivial_kinematics)

        self.jog_button_dic = {}
        
        for axis in self.axis_list:
            for direction in ["+","-"]:
                name = "{0}{1}".format(str(axis), direction)
                btn = gtk.Button(name.upper())
                btn.set_property("name", name)
                btn.connect("pressed", self._on_btn_jog_pressed, axis, direction)
                btn.connect("released", self._on_btn_jog_released, axis, direction)
                btn.set_property("tooltip-text", _("Press to jog axis {0}".format(axis)))
                btn.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))

                self.jog_button_dic[name] = btn

    # if this is a lathe we need to rearrange some button and add a additional DRO
    def _make_lathe(self):
        print("**** GMOCCAPY build_GUI INFO ****")
        print("**** we have a lathe here")

        # if we have a lathe, we will need an additional DRO to display
        # diameter and radius simultaneous, we will call that one Combi_DRO_9, as that value
        # should never be used due to the limit in axis from 0 to 8
        dro = Combi_DRO()
        dro.set_property("name", "Combi_DRO_9")
        dro.set_property("abs_color", gtk.gdk.color_parse(self.abs_color))
        dro.set_property("rel_color", gtk.gdk.color_parse(self.rel_color))
        dro.set_property("dtg_color", gtk.gdk.color_parse(self.dtg_color))
        dro.set_property("homed_color", gtk.gdk.color_parse(self.homed_color))
        dro.set_property("unhomed_color", gtk.gdk.color_parse(self.unhomed_color))
        dro.set_property("actual", self.dro_actual)

        joint = self._get_joint_from_joint_axis_dic("x")
        dro.set_joint_no(joint)
        dro.set_axis("x")
        dro.change_axisletter("D")
        dro.set_property("diameter", True)
        dro.show()

        dro.connect("clicked", self._on_DRO_clicked)
        self.dro_dic[dro.name] = dro

        self.dro_dic["Combi_DRO_0"].change_axisletter("R")

        # For gremlin we don"t need the following button
        if self.backtool_lathe:
            self.widgets.rbt_view_y2.set_active(True)
            self.widgets.gremlin.set_property("view", "y2")
            self.prefs.putpref("gremlin_view", "rbt_view_y2")
        else:
            self.widgets.rbt_view_y.set_active(True)
            self.widgets.gremlin.set_property("view", "y")
            self.prefs.putpref("gremlin_view", "rbt_view_y")

        self.widgets.rbt_view_p.hide()
        self.widgets.rbt_view_x.hide()
        self.widgets.rbt_view_z.hide()
        self.widgets.rbt_view_y2.show()
                
#    def _on_btn_set_value_clicked(self, widget, data = None):
#        if widget == self.widgets.btn_set_value_x:
#            axis = "x"
#        elif widget == self.widgets.btn_set_value_y:
#            axis = "y"
#        elif widget == self.widgets.btn_set_value_z:
#            axis = "z"
#        elif widget == self.widgets.btn_set_value_4:
#            axis = self.axisletter_four
#        elif widget == self.widgets.btn_set_value_5:
#            axis = self.axisletter_five
#        else:
#            axis = "Unknown"
#            message = _("Offset {0} could not be set, because off unknown axis").format(axis)
#            self.dialogs.warning_dialog(self, _("Wrong offset setting!"), message)
#            return
#        if self.gui.lathe_mode and axis == "x":
#            if self.diameter_mode:
#                preset = self.prefs.getpref("diameter offset_axis_{0}".format(axis), 0, float)
#                offset = self.dialogs.entry_dialog(self, data = preset, header = _("Enter value for diameter"),
#                                                   label = _("Set diameter to:"), integer = False)
#            else:
#                preset = self.prefs.getpref("radius offset_axis_{0}".format(axis), 0, float)
#                offset = self.dialogs.entry_dialog(self, data = preset, header = _("Enter value for radius"),
#                                                   label = _("Set radius to:"), integer = False)
#        else:
#            preset = self.prefs.getpref("offset_axis_{0}".format(axis), 0, float)
#            offset = self.dialogs.entry_dialog(self, data = preset, header = _("Enter value for axis {0}").format(axis),
#                                               label = _("Set axis {0} to:").format(axis), integer = False)
#        if offset == "CANCEL":
#            return
#        elif offset == "ERROR":
#            print(_("Conversion error in btn_set_value"))
#            self.dialogs.warning_dialog(self, _("Conversion error in btn_set_value!"),
#                                        _("Please enter only numerical values. Values have not been applied"))
#        else:
#            self.command.mode(linuxcnc.MODE_MDI)
#            self.command.wait_complete()
#            command = "G10 L20 P0 {0}{1:f}".format(axis, offset)
#            self.command.mdi(command)
#            self.widgets.hal_action_reload.emit("activate")
#            self.command.mode(linuxcnc.MODE_MANUAL)
#            self.command.wait_complete()
#            self.prefs.putpref("offset_axis_{0}".format(axis), offset, float)

    def _on_btn_jog_pressed(self, widget, axis, direction):
        print(widget, axis, direction)
        print ("Axis pressed = {0}".format(widget.get_property("name")))
        self.emit("jog_btn_pressed", axis, direction)

    def _on_btn_jog_released(self, widget, axis, direction):
        print(widget, axis, direction)
        print ("Axis released = {0}".format(widget.get_property("name")))
        self.emit("jog_btn_released", axis, direction)

    def on_btn_jog_pressed(self, widget):
        print(widget.get_label())
        name = widget.get_label()
        print ("Joint pressed = {0}".format(name))
        self.emit("jog_btn_pressed", name[0], name[-1])

    def on_btn_jog_released(self, widget):
        print(widget.get_label())
        name = widget.get_label()
        print ("Joint released = {0}".format(name))
        self.emit("jog_btn_released", name[0], name[-1])

    # check if macros are in the INI file and add them to MDI Button List
    def _make_macro_button(self):
        print("**** GMOCCAPY build_GUI INFO ****")
        print("**** Entering make macro button")

        macros = self.get_ini_info.get_macros()

        # if no macros at all are found, we receive a NONE, so we have to check:
        if not macros:
            num_macros = 0
            # no return here, otherwise we will not get filling labels
        else:
            num_macros = len( macros )

        if num_macros > 9:
            message = _( "**** GMOCCAPY INFO ****\n" )
            message += _( "**** found more than 9 macros, only the first 9 will be used ****" )
            print( message )
            num_macros = 9

        for pos in range(0, num_macros):
            name = macros[pos]
            lbl = name.split()[0]
            # shorten / break line of the name if it is to long
            if len( lbl ) > 11:
                lbl = lbl[0:10] + "\n" + lbl[11:20]
            btn = gtk.Button( lbl, None, False )
            btn.set_property("name","macro_{0}".format(pos))
            btn.connect( "pressed", self._on_btn_macro_pressed, name )
            btn.position = pos
            btn.show()
            self.widgets.hbtb_MDI.pack_start(btn, True, True, 0)

        # if there is still place, we fill it with empty labels, to be sure the button will not be on different
        # places if the amount of macros change.
        if num_macros < 9:
            for pos in range(num_macros, 9):
                lbl = gtk.Label()
                lbl.set_property("name","lbl_space_{0}".format(pos))
                lbl.set_text("")
                self.widgets.hbtb_MDI.pack_start(lbl, True, True, 0)
                lbl.show()

#        self.widgets.hbtb_MDI.non_homogeneous = False

        file = "keyboard.png"
        filepath = os.path.join(IMAGEDIR, file)

        name = "keyboard"
        btn = self._get_button_with_image(name, filepath, None)
        btn.set_property("tooltip-text", _("Press to display the virtual keyboard"))
        btn.connect("clicked", self.on_btn_show_kbd_clicked)
        btn.set_property("name", name)
        self.widgets.hbtb_MDI.pack_start(btn)

        self.macro_dic = {}
        
        children = self.widgets.hbtb_MDI.get_children()
        for child in children:
            self.macro_dic[child.name] = child

###############################################################################
##                        Onboard keybord handling                          ##
###############################################################################

    # shows "onboard" or "matchbox" virtual keyboard if available
    # else error message
    def _init_keyboard(self, args="", x="", y=""):
        self.onboard = False

        # now we check if onboard or matchbox-keyboard is installed
        try:
            if os.path.isfile("/usr/bin/onboard"):
                self.onboard_kb = subprocess.Popen(["onboard", "--xid", args, x, y],
                                                   stdin=subprocess.PIPE,
                                                   stdout=subprocess.PIPE,
                                                   close_fds=True)
                print (_("**** GMOCCAPY build_GUI INFO ****"))
                print (_("**** virtual keyboard program found : <onboard>"))
            elif os.path.isfile("/usr/bin/matchbox-keyboard"):
                self.onboard_kb = subprocess.Popen(["matchbox-keyboard", "--xid"],
                                                   stdin=subprocess.PIPE,
                                                   stdout=subprocess.PIPE,
                                                   close_fds=True)
                print (_("**** GMOCCAPY build_GUI INFO ****"))
                print (_("**** virtual keyboard program found : <matchbox-keyboard>"))
            else:
                print (_("**** GMOCCAPY build_GUI INFO ****"))
                print (_("**** No virtual keyboard installed, we checked for <onboard> and <matchbox-keyboard>."))
                self._no_virt_keyboard()
                return
            sid = self.onboard_kb.stdout.readline()
            socket = gtk.Socket()
            self.widgets.key_box.add(socket)
            socket.add_id(long(sid))
            socket.show()
            self.onboard = True
        except Exception, e:
            print (_("**** GMOCCAPY build_GUI ERROR ****"))
            print (_("**** Error with launching virtual keyboard,"))
            print (_("**** is onboard or matchbox-keyboard installed? ****"))
            traceback.print_exc()
            self._no_virt_keyboard()

    def _no_virt_keyboard(self):
        # In this case we will disable the corresponding part on the settings page
        self.widgets.chk_use_kb_on_offset.set_active(False)
        self.widgets.chk_use_kb_on_tooledit.set_active(False)
        self.widgets.chk_use_kb_on_edit.set_active(False)
        self.widgets.chk_use_kb_on_mdi.set_active(False)
        self.widgets.chk_use_kb_on_file_selection.set_active(False)
        self.widgets.frm_keyboard.set_sensitive(False)
        self.widgets.btn_show_kbd.set_sensitive(False)
        self.widgets.btn_show_kbd.set_image(self.widgets.img_brake_macro)
        self.widgets.btn_show_kbd.set_property("tooltip-text", _("interrupt running macro"))
#        self.widgets.btn_keyb.set_sensitive(False)
        self.macro_dic["keyboard"].set_sensitive(False)

    def _kill_keyboard(self):
        try:
            self.onboard_kb.kill()
            self.onboard_kb.terminate()
            self.onboard_kb = None
        except:
            try:
                self.onboard_kb.kill()
                self.onboard_kb.terminate()
                self.onboard_kb = None
            except:
                pass


###############################################################################
##                        hide or display widgets                            ##
###############################################################################

    # the user want a Logo
    def logo(self,logofile):
        self.widgets.img_logo.set_from_file(logofile)
        self.widgets.img_logo.show()

        page2 = self.widgets.ntb_jog_JA.get_nth_page(2)
        self.widgets.ntb_jog_JA.reorder_child(page2, 0)
        page1 = self.widgets.ntb_jog_JA.get_nth_page(1)
        self.widgets.ntb_jog_JA.reorder_child(page1, -1)

    # if we have an angular axis we will show the angular jog speed slider
    def _angular_axis_availible(self):
        self.widgets.spc_ang_jog_vel.hide()
        for axis in ("a","b","c"):
            if axis in self.joint_axis_dic.values():
                self.widgets.spc_ang_jog_vel.show()
                print("**** GMOCCAPY build_GUI INFO ****")
                print("**** axis {0} is a rotary axis\n".format(self.joint_axis_dic[dro]))
                print("**** Will display the angular jog slider\n")
                break

    def _remove_button(self, dic, box):
        for child in dic:
            box.remove(dic[child])

    def _put_home_all_and_previous(self):
        self.widgets.hbtb_ref.pack_start(self.ref_button_dic["ref_all"])
        self.widgets.hbtb_ref.pack_start(self.ref_button_dic["previous_button"])

    def _put_button(self, start, end, dic, box):
        if dic == self.ref_button_dic:
            prefix = "home_axis"
        elif dic == self.touch_button_dic:
            prefix = "touch"
        for axis in self.axis_list[start : end]:
            name = prefix + "_{0}".format(axis.lower())
            dic[name].show()
            box.pack_start(dic[name])

    def _put_set_active_and_back(self):
        self.widgets.hbtb_touch_off.pack_start(self.touch_button_dic["set_active"])
        self.widgets.hbtb_touch_off.pack_start(self.touch_button_dic["touch_back"])

    def _put_unref_and_back(self):
        self.widgets.hbtb_ref.pack_start(self.ref_button_dic["next_button"])
        self.widgets.hbtb_ref.pack_start(self.ref_button_dic["unref_all"])
        self.widgets.hbtb_ref.pack_start(self.ref_button_dic["home_back"])

    def _hide_button(self, start, end, dic, box):
        if dic == self.ref_button_dic:
            prefix = "home_axis"
        elif dic == self.touch_button_dic:
            prefix = "touch"
         
        for axis in self.axis_list[start:end]:
            name = prefix + "_{0}".format(axis.lower())
            dic[name].hide()
            box.pack_start(dic[name])


###############################################################################
##                       internal button handling                            ##
##                          right side buttons                               ##
###############################################################################

    def on_tbtn_estop_toggled(self, widget, data = None):
        state = widget.get_active()
#        if state:
#            print("estop OK")
#            self.widgets.tbtn_estop.set_image(self.widgets.img_emergency_off)
#            self.widgets.tbtn_on.set_image(self.widgets.img_machine_off)
#            self.widgets.tbtn_on.set_sensitive(True)
#            self.widgets.ntb_jog.set_sensitive(True)
#            self.widgets.ntb_jog_JA.set_sensitive(False)
#            self.widgets.vbtb_jog_incr.set_sensitive(False)
#            self.widgets.hbox_jog_vel.set_sensitive(False)
#            self.widgets.chk_ignore_limits.set_sensitive(True)
#        else:
#            print("estop NOK")
#            self.widgets.tbtn_estop.set_image(self.widgets.img_emergency)
#            self.widgets.tbtn_on.set_image(self.widgets.img_machine_on)
#            self.widgets.tbtn_on.set_sensitive(False)
#            self.widgets.chk_ignore_limits.set_sensitive(False)
#            self.widgets.tbtn_on.set_active(False)

#        self.emit("estop_active", not state)

#    # toggle machine on / off button
#    def on_tbtn_on_toggled(self, widget, data=None):
#        print("build GUI  on toggled", widget.get_active())
#        self.emit("on_active", widget.get_active())
#
#    # The mode buttons
#    def on_rbt_manual_pressed(self, widget, data=None):
#        print("build GUI manual pressed")
#        self.emit("set_manual")
#
#    def on_rbt_mdi_pressed(self, widget, data=None):
#        print("build GUI mdi pressed")
#        self.emit("set_mdi")
#
#    def on_rbt_auto_pressed(self, widget, data=None):
#        print("build GUI auto pressed")
#        self.emit("set_auto")
#
#    def on_tbtn_setup_toggled(self, widget, data=None):
#        # first we set to manual mode, as we do not allow changing settings in other modes
#        # otherwise external halui commands could start a program while we are in settings
#        self.emit("set_manual")
#        
#        if widget.get_active():
#            # deactivate the mode buttons, so changing modes is not possible while we are in settings mode
#            self.widgets.rbt_manual.set_sensitive(False)
#            self.widgets.rbt_mdi.set_sensitive(False)
#            self.widgets.rbt_auto.set_sensitive(False)
#            code = False
#            # here the user don"t want an unlock code
#            if self.widgets.rbt_no_unlock.get_active():
#                code = True
#            # if hal pin is true, we are allowed to enter settings, this may be
#            # realized using a key switch
#            if self.widgets.rbt_hal_unlock.get_active() and self.unlock-settings"]:
#                code = True
#            # else we ask for the code using the system.dialog
#            if self.widgets.rbt_use_unlock.get_active():
#                if self.dialogs.system_dialog(self):
#                    code = True
#            # Lets see if the user has the right to enter settings
#            if code:
#                self.widgets.ntb_main.set_current_page(1)
#                self.widgets.ntb_setup.set_current_page(0)
#                self.widgets.ntb_button.set_current_page(_BB_SETUP)
#            else:
#                if self.widgets.rbt_hal_unlock.get_active():
#                    message = _("Hal Pin is low, Access denied")
#                else:
#                    message = _("wrong code entered, Access denied")
#                self.dialogs.warning_dialog(self, _("Just to warn you"), message)
#                self.widgets.tbtn_setup.set_active(False)
#        else:
#            # check witch button should be sensitive, depending on the state of the machine
#            if self.estop_active:
#                # estoped no mode available
#                self.widgets.rbt_manual.set_sensitive(False)
#                self.widgets.rbt_mdi.set_sensitive(False)
#                self.widgets.rbt_auto.set_sensitive(False)
#            if self.machine_on and not self.all_homed:
#                # machine on, but not homed, only manual allowed
#                self.widgets.rbt_manual.set_sensitive(True)
#                self.widgets.rbt_mdi.set_sensitive(False)
#                self.widgets.rbt_auto.set_sensitive(False)
#            if self.machine_on and (self.all_homed or self.no_force_homing):
#                # all OK, make all modes available
#                self.widgets.rbt_manual.set_sensitive(True)
#                self.widgets.rbt_mdi.set_sensitive(True)
#                self.widgets.rbt_auto.set_sensitive(True)
#            # this is needed here, because we do not
#            # change mode, so on_hal_status_manual will not be called
#            self.widgets.ntb_main.set_current_page(0)
#            self.widgets.ntb_button.set_current_page(_BB_MANUAL)
#            self.widgets.ntb_info.set_current_page(0)
#            self.widgets.ntb_jog.set_current_page(0)
#
#            # if we are in user tabs, we must reset the button
#            if self.widgets.tbtn_user_tabs.get_active():
#                self.widgets.tbtn_user_tabs.set_active(False)
#
#    # Show or hide the user tabs
#    def on_tbtn_user_tabs_toggled(self, widget, data=None):
#        if widget.get_active():
#            self.widgets.ntb_main.set_current_page(2)
#            self.widgets.tbtn_fullsize_preview.set_sensitive(False)
#        else:
#            self.widgets.ntb_main.set_current_page(0)
#            self.widgets.tbtn_fullsize_preview.set_sensitive(True)

###############################################################################
##                       internal button handling                            ##
##                       bottom buttons (manual)                             ##
###############################################################################

#    # display the homing button
#    def on_btn_homing_clicked(self, widget, data=None):
#        self.widgets.ntb_button.set_current_page(_BB_HOME)
#
#    # display the offste button
#    def on_btn_touch_clicked(self, widget, data=None):
#        self.widgets.ntb_button.set_current_page(_BB_TOUCH_OFF)
#        self._show_offset_tab(True)
#        if self.widgets.rbtn_show_preview.get_active():
#            self.widgets.ntb_preview.set_current_page(0)
#
#    # display the tool button
#    def on_btn_tool_clicked(self, widget, data=None):
#        if self.widgets.tbtn_fullsize_preview.get_active():
#            self.widgets.tbtn_fullsize_preview.set_active(False)
#        self.widgets.ntb_button.set_current_page(_BB_TOOL)
#        self._show_tooledit_tab(True)
#
#    def on_tbtn_switch_mode_toggled(self, widget):
#        if widget.get_active():
#            self.widgets.tbtn_switch_mode.set_label(_(" Joint\nmode"))
#            # Mode 1 = joint ; Mode 2 = MDI ; Mode 3 = teleop
#            # so in mode 1 we have to show Joints and in Modes 2 and 3 axis values
#            self.emit("set_motion_mode", 0)
#        else:
#            self.widgets.tbtn_switch_mode.set_label(_("World\nmode"))
#            self.emit("set_motion_mode", 1)
#
#    def on_tbtn_fullsize_preview_toggled(self, widget, data=None):
#        if widget.get_active():
#            self.widgets.box_info.hide()
#            self.widgets.vbx_jog.hide()
#            dro = self.dro_dic[self.dro_dic.keys()[0]]
#            self.widgets.gremlin.set_property("metric_units", dro.metric_units)
#            self.widgets.gremlin.set_property("enable_dro", True)
#            if self.lathe_mode:
#                self.widgets.gremlin.set_property("show_lathe_radius", not self.diameter_mode)
#        else:
#            self.widgets.box_info.show()
#            self.widgets.vbx_jog.show()
#            if not self.widgets.chk_show_dro.get_active():
#                self.widgets.gremlin.set_property("enable_dro", False)
#
#    # If button exit is clicked, press emergency button before closing the application
#    def on_btn_exit_clicked(self, widget, data=None):
#        self.widgets.window1.destroy()


###############################################################################
##                       internal button handling                            ##
##                       bottom buttons (homing)                             ##
###############################################################################

         # ToDo Start : must fit also the joints button
    def _on_btn_previous_clicked(self, widget):
        self._remove_button(self.ref_button_dic, self.widgets.hbtb_ref)
        self._put_home_all_and_previous()
        self._put_button(0 , 5,
                         self.ref_button_dic, self.widgets.hbtb_ref)
        self._put_unref_and_back()
        self._hide_button(5,len(self.axis_list),
                          self.ref_button_dic, self.widgets.hbtb_ref)
        
        self.ref_button_dic["previous_button"].set_sensitive(False)
        self.ref_button_dic["next_button"].set_sensitive(True)

    def _on_btn_next_clicked(self, widget):
        self._remove_button(self.ref_button_dic, self.widgets.hbtb_ref)
        self._put_home_all_and_previous()
        self._put_button(len(self.axis_list) - 5 , len(self.axis_list),
                             self.ref_button_dic, self.widgets.hbtb_ref)
        self._put_unref_and_back()
        self._hide_button(0,len(self.axis_list) - 5,
                                self.ref_button_dic, self.widgets.hbtb_ref)
        
        self.ref_button_dic["previous_button"].set_sensitive(True)
        self.ref_button_dic["next_button"].set_sensitive(False)
        
    def _on_btn_next_touch_clicked(self, widget):
        self._remove_button(self.touch_button_dic, self.widgets.hbtb_touch_off)

        self.widgets.hbtb_touch_off.pack_start(self.touch_button_dic["edit_offsets"])
        self.widgets.hbtb_touch_off.pack_start(self.touch_button_dic["previous_button"])
        self.touch_button_dic["previous_button"].show()

        self._put_button(len(self.axis_list) - 6 , len(self.axis_list),
                         self.touch_button_dic, self.widgets.hbtb_touch_off)
        self._put_set_active_and_back()

        self._hide_button(0,len(self.axis_list) - 6,
                          self.touch_button_dic, self.widgets.hbtb_touch_off)
        

    def _on_btn_previous_touch_clicked(self, widget):
        self._remove_button(self.touch_button_dic, self.widgets.hbtb_touch_off)

        if self._check_toolmeasurement():
            correct = 1

        self.widgets.hbtb_touch_off.pack_start(self.touch_button_dic["edit_offsets"])

        if self._check_toolmeasurement():
            end = 4
        else:
            end = 5
            
        self._put_button(0 , end,
                         self.touch_button_dic, self.widgets.hbtb_touch_off)

        self.widgets.hbtb_touch_off.pack_start(self.touch_button_dic["next_button"])
        self.touch_button_dic["next_button"].show()

        if self._check_toolmeasurement():
            self.widgets.hbtb_touch_off.pack_start(self.touch_button_dic["block_height"])

        self.widgets.hbtb_touch_off.pack_start(self.touch_button_dic["zero_offsets"])
        self._put_set_active_and_back()

        self._hide_button(end,len(self.axis_list),
                          self.touch_button_dic, self.widgets.hbtb_touch_off)
     
    def _on_btn_home_clicked(self, widget):
        # home axis or joint?
        print("on button home clicker = ", widget.name)
        if "axis" in widget.name:
            value = widget.name[-1]
            # now get the joint from directory by the value
            joint_or_axis = self._get_joint_from_joint_axis_dic(value)
        elif "joint" in widget.name:
            joint_or_axis = int(widget.name[-1])
        elif "all" in widget.name:
            joint_or_axis = -1

        self.emit("home_clicked", joint_or_axis)

    def _on_btn_unhome_clicked(self, widget):
        self.emit("unhome_clicked", -1)

    def _on_btn_home_back_clicked(self, widget):
        self.widgets.ntb_button.set_current_page(_BB_MANUAL)
        self.widgets.ntb_main.set_current_page(0)
        self.widgets.ntb_preview.set_current_page(0)

###############################################################################
##                       internal button handling                            ##
##                          touch off buttons                                ##
###############################################################################

    def on_tbtn_edit_offsets_toggled(self, widget):
        state =  not widget.get_active()
        self.widgets.offsetpage1.edit_button.set_active(not state)

        for widget in self.touch_button_dic:
            if self.touch_button_dic[widget].name == "edit_offsets":
                continue
            else:
                self.touch_button_dic[widget].set_sensitive(state)

        widgetlist = ["ntb_jog"]
        self._sens_widgets(widgetlist, state)

        if state:
            self.widgets.ntb_preview.set_current_page(0)
        else:
            self.widgets.ntb_preview.set_current_page(1)

        # we must switch back to manual mode, otherwise jogging is not possible
        if not state:
            self.emit("set_manual")
            sleep(0.1)

        # show virtual keyboard?
        if state and self.widgets.chk_use_kb_on_offset.get_active():
            self.widgets.ntb_info.set_current_page(1)
            self.widgets.ntb_preview.set_current_page(1)


###############################################################################
##                       internal button handling                            ##
##                         tool editor buttons                               ##
###############################################################################

    # Three back buttons to be able to leave notebook pages
    # All use the same callback offset
    def on_btn_back_clicked(self, widget, data=None):
        # edit mode, go back to auto_buttons
        if self.widgets.ntb_button.get_current_page() == _BB_EDIT:
            self.widgets.ntb_button.set_current_page(_BB_AUTO)
            if self.widgets.tbtn_fullsize_preview1.get_active():
                self.widgets.vbx_jog.set_visible(False)
        # File selection mode
        elif self.widgets.ntb_button.get_current_page() == _BB_LOAD_FILE:
            self.widgets.ntb_button.set_current_page(_BB_AUTO)
        # we are in tool edit, go to main button on manual
        else:
            self._reset_GUI()




###############################################################################
##                       internal button handling                            ##
##                         bottom buttons (mdi)                              ##
###############################################################################

    def _on_btn_macro_pressed(self, widget, data):
        o_codes = data.split()

        command = str( "O<" + o_codes[0] + "> call" )

        for code in o_codes[1:]:
            parameter = self.dialogs.entry_dialog(self, data=None, header=_("Enter value:"),
                                                  label=_("Set parameter {0} to:").format(code), integer=False)
            if parameter == "ERROR":
                print(_("conversion error"))
                self.dialogs.warning_dialog(self, _("Conversion error !"),
                                            ("Please enter only numerical values\nValues have not been applied"))
                return
            elif parameter == "CANCEL":
                return
            else:
                pass
            command = command + " [" + str(parameter) + "] "

# TODO: Should not only clear the plot, but also the loaded program?
        # self.command.program_open("")
        # self.command.reset_interpreter()
        self.widgets.gremlin.clear_live_plotter()
# TODO: End

        self.emit("mdi_command", command)
        for pos in self.macro_dic:
            self.macro_dic[pos].set_sensitive(False)
        # we change the widget_image and use the button to interrupt running macros
        if not self.onboard:
            self.widgets.btn_show_kbd.set_sensitive(True)
        self.widgets.btn_show_kbd.set_image(self.widgets.img_brake_macro)
        self.widgets.btn_show_kbd.set_property("tooltip-text", _("interrupt running macro"))
        self.widgets.ntb_info.set_current_page(0)

    def on_btn_show_kbd_clicked(self, widget):
        print("show Keyboard clicked")
        print self.dro_dic
        
#        self.dro_dic["Combi_DRO_2"].set_property("abs_color", gtk.gdk.color_parse("#F2F1F0"))
#        self.dro_dic["Combi_DRO_2"].set_property("rel_color", gtk.gdk.color_parse("#F2F1F0"))
#        self.dro_dic["Combi_DRO_2"].set_property("dtg_color", gtk.gdk.color_parse("#F2F1F0"))
       
        # if the image is img_brake macro, we want to interrupt the running macro
        if self.macro_dic["keyboard"].get_image() == self.widgets.img_brake_macro:
            self.emit("mdi_abort")
            for pos in self.macro_dic:
                self.macro_dic[pos].set_sensitive(True)
            if self.onboard:
                self.macro_dic["keyboard"].set_image(self.widgets.img_keyboard)
                self.macro_dic["keyboard"].set_property("tooltip-text", _("This button will show or hide the keyboard"))
            else:
                self.macro_dic["keyboard"].set_sensitive(False)
        elif self.widgets.ntb_info.get_current_page() == 1:
            self.widgets.ntb_info.set_current_page(0)
        else:
            self.widgets.ntb_info.set_current_page(1)

        # special case if we are in edit mode
        if self.widgets.ntb_button.get_current_page() == _BB_EDIT:
            if self.widgets.ntb_info.get_visible():
                self.widgets.box_info.set_size_request(-1, 50)
                self.widgets.ntb_info.hide()
            else:
                self.widgets.box_info.set_size_request(-1, 250)
                self.widgets.ntb_info.show()



################################################################################
###                       internal button handling                            ##
###                         bottom buttons (setup)                            ##
################################################################################
## this are hal-tools copied from gsreen function
#    def on_btn_show_hal_clicked(self, widget, data=None):
#        p = os.popen("tclsh {0}/bin/halshow.tcl &".format(TCLPATH))
#
#    def on_btn_calibration_clicked(self, widget, data=None):
#        p = os.popen("tclsh {0}/bin/emccalib.tcl -- -ini {1} > /dev/null &".format(TCLPATH, sys.argv[2]), "w")
#
#    def on_btn_hal_meter_clicked(self, widget, data=None):
#        p = os.popen("halmeter &")
#
#    def on_btn_status_clicked(self, widget, data=None):
#        p = os.popen("linuxcnctop  > /dev/null &", "w")
#
#    def on_btn_hal_scope_clicked(self, widget, data=None):
#        p = os.popen("halscope  > /dev/null &", "w")
#
#    def on_btn_classicladder_clicked(self, widget, data=None):
#        if hal.component_exists("classicladder_rt"):
#            p = os.popen("classicladder  &", "w")
#        else:
#            self.dialogs.warning_dialog(self, _("INFO:"),
#                                   _("Classicladder real-time component not detected"))
#
#
################################################################################
###                       internal button handling                            ##
###                           gremlin buttons                                 ##
################################################################################
#
#    def on_rbt_view_p_toggled(self, widget):
#        if self.widgets.rbt_view_p.get_active():
#            self.widgets.gremlin.set_property("view", "p")
#        self.prefs.putpref("gremlin_view", "rbt_view_p")
#        self.prefs.putpref("view", "p")
#
#    def on_rbt_view_x_toggled(self, widget):
#        if self.widgets.rbt_view_x.get_active():
#            self.widgets.gremlin.set_property("view", "x")
#        self.prefs.putpref("gremlin_view", "rbt_view_x")
#        self.prefs.putpref("view", "x")
#
#    def on_rbt_view_y_toggled(self, widget):
#        if self.widgets.rbt_view_y.get_active():
#            self.widgets.gremlin.set_property("view", "y")
#        self.prefs.putpref("gremlin_view", "rbt_view_y")
#        self.prefs.putpref("view", "y")
#
#    def on_rbt_view_z_toggled(self, widget):
#        if self.widgets.rbt_view_z.get_active():
#            self.widgets.gremlin.set_property("view", "z")
#        self.prefs.putpref("gremlin_view", "rbt_view_z")
#        self.prefs.putpref("view", "z")
#
#    def on_rbt_view_y2_toggled(self, widget):
#        print("widget = ", widget.get_active())
#        if self.widgets.rbt_view_y2.get_active():
#            self.widgets.gremlin.set_property("view", "y2")
#        self.prefs.putpref("gremlin_view", "rbt_view_y2")
#        self.prefs.putpref("view", "y2")
#
#    def on_btn_zoom_in_clicked(self, widget):
#        self.widgets.gremlin.zoom_in()
#
#    def on_btn_zoom_out_clicked(self, widget):
#        self.widgets.gremlin.zoom_out()
#
#    def on_btn_delete_view_clicked(self, widget):
#        self.widgets.gremlin.clear_live_plotter()
#
#    def on_tbtn_view_dimension_toggled(self, widget):
#        self.widgets.gremlin.set_property("show_extents_option", widget.get_active())
#        self.prefs.putpref("view_dimension", self.widgets.tbtn_view_dimension.get_active())
#
#    def on_tbtn_view_tool_path_toggled(self, widget):
#        self.widgets.gremlin.set_property("show_live_plot", widget.get_active())
#        self.prefs.putpref("view_tool_path", self.widgets.tbtn_view_tool_path.get_active())
#
#    def on_gremlin_line_clicked(self, widget, line):
#        self.widgets.gcode_view.set_line_number(line)


###############################################################################
##                       internal button handling                            ##
##                             setup page                                    ##
###############################################################################


###############################################################################
##                            signal handling                                ##
###############################################################################

    def _jog_increment_changed(self, widget, increment):
        print("widget = ", widget.name)
        print("jog_incr_dic = ", self.incr_dic)
        print("increment = ", increment)
        self.emit("jog_incr_changed", increment)

###############################################################################
##                       internal event handling                             ##
##                           in no category                                  ##
###############################################################################

    def _on_DRO_clicked(self, widget, joint, order):
        for dro in self.dro_dic:
            self.dro_dic[dro].set_order(order)
        return

###############################################################################
##                          helper functions                                 ##
###############################################################################

    def _check_toolmeasurement(self):
        # tool measurement probe settings
        xpos, ypos, zpos, maxprobe = self.get_ini_info.get_tool_sensor_data()
        if not xpos or not ypos or not zpos or not maxprobe:
            self.widgets.chk_use_tool_measurement.set_active(False)
            self.widgets.chk_use_tool_measurement.set_sensitive(False)
            self.widgets.lbl_tool_measurement.show()
            print(_("**** GMOCCAPY INFO ****"))
            print(_("**** no valid probe config in INI File ****"))
            print(_("**** disabled tool measurement ****"))
            return False
        else:
            self.widgets.lbl_tool_measurement.hide()
            self.widgets.spbtn_probe_height.set_value(self.prefs.getpref("probeheight", -1.0, float))
            self.widgets.spbtn_search_vel.set_value(self.prefs.getpref("searchvel", 75.0, float))
            self.widgets.spbtn_probe_vel.set_value(self.prefs.getpref("probevel", 10.0, float))
            self.widgets.chk_use_tool_measurement.set_active(self.prefs.getpref("use_toolmeasurement", False, bool))
            # to set the hal pin with correct values we emit a toogled
            self.widgets.lbl_x_probe.set_label(str(xpos))
            self.widgets.lbl_y_probe.set_label(str(ypos))
            self.widgets.lbl_z_probe.set_label(str(zpos))
            self.widgets.lbl_maxprobe.set_label(str(maxprobe))
            print(_("**** GMOCCAPY INFO ****"))
            print(_("**** found valid probe config in INI File ****"))
            print(_("**** will use auto tool measurement ****"))
            return True

    def _get_button_with_image(self, name, filepath, stock):
        image = gtk.Image()
        image.set_size_request(48,48)
        btn = self._get_button(name, image)
        if filepath:
            image.set_from_file(filepath)
        else:
            image.set_from_stock(stock, 48)
        return btn

    def _get_button(self, name, image):
        btn = gtk.Button()
        btn.set_size_request(85,56)
        btn.add(image)
        btn.set_property("name", name)
        btn.show_all()
        return btn

    def _get_space_label(self, name):
        lbl = gtk.Label("")
        lbl.set_property("name", name)
        lbl.set_size_request(85,56)
        lbl.show()
        return lbl

    # this handles the relation between hardware button and the software button    
    def _get_child_button(self, location, number = None):
        # get the position of each button to be able to connect to hardware button
        self.child_button_dic = {}
        
        if location == "bottom":
            page = self.widgets.ntb_button.get_current_page()
            container = self.widgets.ntb_button.get_children()[page]
        elif location == "right":
            container = self.widgets.vbtb_main
        else:
            print(_("got wrong location to locate the childs"))
            
        children = container.get_children()
        hidden = 0
        for child in children:
            if not child.get_visible():
                hidden +=1
            else:
                if type(child) != gtk.Label:
                    pos = container.child_get_property(child, "position")
                    name = child.name
                    if name == None:
                        name = gtk.Buildable.get_name(child)
                    self.child_button_dic[pos - hidden] = (child, name)
        
        if number is not None:
            try:
                if self.child_button_dic[number][0].get_sensitive():
                    return self.child_button_dic[number]
                else:
                    return -1
            except:
                return None
        else:
            return self.child_button_dic
        
    def _get_joint_from_joint_axis_dic(self, value):
        # if the selected axis is a double axis we will get the joint from the
        # master axis, witch should end with 0 
        if value in self.double_axis_letter:
            value = value + "0"
        return self.joint_axis_dic.keys()[self.joint_axis_dic.values().index(value)]

    def get_widget_from_dic(self, dic, name):
        print dic
        return dic.keys()[dic.values().index(name)]

    def _arrange_dro(self):
        # if we have less than 4 axis, we can resize the table, as we have 
        # enough space to display each one in it's own line

        if len(self.dro_dic) < 4:
            self._place_in_table(len(self.dro_dic),1, self.dro_size)

        # having 4 DRO we need to reduce the size, to fit the available space
        elif len(self.dro_dic) == 4:
            self._place_in_table(len(self.dro_dic),1, self.dro_size * 0.75)

        # having 5 axis we will display 3 in an one line and two DRO share 
        # the last line, the size of the DRO must be reduced also
        # this is a special case so we do not use _place_in_table
        elif len(self.dro_dic) == 5:
            self.widgets.tbl_DRO.resize(4,2)
            for dro, axis in enumerate(self.axis_list):
                dro_name = "Combi_DRO_{0}".format(axis)
                if dro < 3:
                    size = self.dro_size * 0.75
                    self.widgets.tbl_DRO.attach(self.dro_dic[dro_name], 
                                                0, 2, int(dro), int(dro + 1), ypadding = 0)
                else:
                    size = self.dro_size * 0.65
                    if dro == 3:
                        self.widgets.tbl_DRO.attach(self.dro_dic[dro_name], 
                                                    0, 1, int(dro), int(dro + 1), ypadding = 0)
                    else:
                        self.widgets.tbl_DRO.attach(self.dro_dic[dro_name], 
                                                    1, 2, int(dro-1), int(dro), ypadding = 0)
                self.dro_dic[dro_name].set_property("font_size", size)

        else:
            print("**** GMOCCAPY build_GUI INFO ****")
            print("**** more than 5 axis ")
            # check if amount of axis is an even number, adapt the needed lines
            if len(self.dro_dic) % 2 == 0:
                rows = len(self.dro_dic) / 2
            else:
                rows = (len(self.dro_dic) + 1) / 2
            self._place_in_table(rows, 2, self.dro_size * 0.65)

        # set values to dro size adjustments
        self.widgets.adj_dro_size.set_value(self.dro_size)

    def _place_in_table(self, rows, cols, dro_size):
        print("gmoccapy build_gui INFO")
        print ("we are in place in table")

        self.widgets.tbl_DRO.resize(rows, cols)
        col = 0
        row = 0

        # if Combi_DRO_9 exist we have a lathe with an additional DRO for diameter mode
        if "Combi_DRO_9" in self.dro_dic.keys():
            children = self.widgets.tbl_DRO.get_children()
            print (children)
            dro_order = ["Combi_DRO_0", "Combi_DRO_9", "Combi_DRO_1", "Combi_DRO_2", "Combi_DRO_3",
                         "Combi_DRO_4", "Combi_DRO_5", "Combi_DRO_6", "Combi_DRO_7", "Combi_DRO_8"]
        else:
            dro_order = sorted(self.dro_dic.keys())

        for dro, dro_name in enumerate(dro_order):
            # as a lathe might not have all Axis, we check if the key is in directory
            if dro_name not in self.dro_dic.keys():
                continue
            self.dro_dic[dro_name].set_property("font_size", dro_size)

            self.widgets.tbl_DRO.attach(self.dro_dic[dro_name],
                                        col, col+1, row, row + 1, ypadding = 0)
            if cols > 1:
                # calculate if we have to place in the first or the second column
                if (dro % 2 == 1):
                    col = 0
                    row +=1
                else:
                    col += 1
            else:
                row += 1

    def _arrange_jog_button(self):
        num_axis = len(self.jog_button_dic)
        print("length of button dictionary = {0}".format(num_axis))

        if num_axis <= 3:
            # we can resize the jog_btn_table
            self.widgets.tbl_jog_btn_axes.resize(3, 3)
            # This is probably a lathe, but we will better check that

        for btn in self.jog_button_dic:

            name = btn
            if name == "x+":
                col = 2
                row = 1
            if name =="x-":
                col = 0
                row = 1
            if name == "y+":
                col = 1
                row = 0
            if name =="y-":
                col = 1
                row = 2
            if name == "z+":
                col = 2
                row = 0
            if name =="z-":
                col = 0
                row = 2
            if name == "a+":
                col = 4
                row = 3
            if name =="a-":
                col = 3
                row = 3
            if name == "b+":
                col = 2
                row = 3
            if name =="b-":
                col = 0
                row = 3
            if name == "c+":
                col = 2
                row = 2
            if name =="c-":
                col = 0
                row = 0
            if name == "u+":
                col = 4
                row = 0
            if name =="u-":
                col = 3
                row = 0
            if name == "v+":
                col = 4
                row = 1
            if name =="v-":
                col = 3
                row = 1
            if name == "w+":
                col = 4
                row = 2
            if name =="w-":
                col = 3
                row = 2
                
                
            self.widgets.tbl_jog_btn_axes.attach(self.jog_button_dic[name], col, col + 1, row, row + 1)
            self.jog_button_dic[name].show()

            print("Jog Button = {0}".format(name))
            print("Position = {0},{1}".format(col,row))
            
#        if self.lathe_mode:
#            # OK this is a lathe, lets see if it is a backtool_lathe
#            if self.backtool_lathe:
#                # Now we are sure we have a backtool lathe
#                # as we only expect X an Z, lets place them in the table
#                for btn in btnlst:
#                    name = btn.get_property("name")
#                    if name == "x+":
#                        col = 1
#                        row = 0
#                    if name == "x-":
#                        col = 1
#                        row = 2
#                    if name == "y+":
#                        col = 2
#                        row = 0
#                    if name == "y-":
#                        col = 0
#                        row = 2
#                    if name == "z+":
#                        col = 0
#                        row = 1
#                    if name == "z-":
#                        col = 2
#                        row = 1


    def _get_ini_data(self):
        # get the axis list from INI
        self.axis_list = self.get_ini_info.get_axis_list()
        # get the joint axis relation from INI
        self.joint_axis_dic, self.double_axis_letter = self.get_ini_info.get_joint_axis_relation()
        # if it's a lathe config, set the tool editor style
        self.lathe_mode = self.get_ini_info.get_lathe()
        if self.lathe_mode:
            # we do need to know also if we have a backtool lathe
            self.backtool_lathe = self.get_ini_info.get_backtool_lathe()
        # check if the user want actual or commanded for the DRO
        self.dro_actual = self.get_ini_info.get_position_feedback_actual()
        # the given Jog Increments
        self.jog_increments = self.get_ini_info.get_increments()
        # check if NO_FORCE_HOMING is used in ini
        self.no_force_homing = self.get_ini_info.get_no_force_homing()
        # do we use a identity kinematics or do we have to distingish 
        # JOINT and Axis modes?
        self.trivial_kinematics = self.get_ini_info.get_trivial_kinematics()
        units = self.get_ini_info.get_machine_units()
        if units == "mm" or units == "cm":
            self.metric = True
        else:
            self.metric = False

    def _get_pref_data(self):
        # the size of the DRO
        self.dro_size = self.prefs.getpref("dro_size", 28, int)
        # the colors of the DRO
        self.abs_color = self.prefs.getpref("abs_color", "#0000FF", str)         # blue
        self.rel_color = self.prefs.getpref("rel_color", "#000000", str)         # black
        self.dtg_color = self.prefs.getpref("dtg_color", "#FFFF00", str)         # yellow
        self.homed_color = self.prefs.getpref("homed_color", "#00FF00", str)     # green
        self.unhomed_color = self.prefs.getpref("unhomed_color", "#FF0000", str) # red
        
        # the velocity settings
        self.min_spindle_rev = self.prefs.getpref("spindle_bar_min", 0.0, float)
        self.max_spindle_rev = self.prefs.getpref("spindle_bar_max", 6000.0, float)
        
        self.unlock_code = self.prefs.getpref("unlock_code", "123", str)  # get unlock code


    def _sens_widgets(self, widgetlist, value):
        for name in widgetlist:
            try:
                self.widgets[name].set_sensitive(value)
            except Exception, e:
                print (_("**** GMOCCAPY ERROR ****"))
                print _("**** No widget named: {0} to sensitize ****").format(name)
                traceback.print_exc()

    def _toggle_on_off(self, state):
        widgetlist = ["rbt_manual", "tbtn_on",
              "btn_homing",  "btn_tool",
              "ntb_jog", 
              "rbt_forward", "rbt_stop", "rbt_reverse", 
              "tbtn_flood", "tbtn_mist", 
              "btn_spindle_100", "spc_spindle",
        ]
        
        if self.widgets.rbt_mdi.get_sensitive() or self.widgets.rbt_auto.get_sensitive():
            widgetlist.extend(["rbt_mdi", "rbt_auto"])
        
        if self.no_force_homing:
            widgetlist.extend(["rbt_mdi", "rbt_auto", "btn_touch", "spc_feed", 
                               "btn_feed_100", "btn_index_tool",
                               "btn_change_tool", "btn_select_tool_by_no",
                               "spc_rapid", 
                               "btn_tool_touchoff_x", "btn_tool_touchoff_z"])
        
        self._sens_widgets(widgetlist, state)
        self.widgets.btn_exit.set_sensitive(not state)
        self.widgets.chk_ignore_limits.set_sensitive(not state)

    def _reset_GUI(self):
        # on switching the machine on, we reset the GUI to standard view
        self.widgets.ntb_main.set_current_page(0)
        self.widgets.ntb_preview.set_current_page(0)
        self.widgets.ntb_button.set_current_page(0)
        self.widgets.vbx_jog.show()
        self.widgets.ntb_info.set_current_page(0)
        self.widgets.tbtn_fullsize_preview.set_active(False)
        self._show_offset_tab(False)
        self._show_tooledit_tab(False)
        self._show_iconview_tab(False)


    def switch_to_g7(self, state):
        # we do this only if we have a lathe, the check for lathe is done in gmoccapy
        print state
        if state:
            self.dro_dic["Combi_DRO_0"].set_property("abs_color", gtk.gdk.color_parse("#F2F1F0"))
            self.dro_dic["Combi_DRO_0"].set_property("rel_color", gtk.gdk.color_parse("#F2F1F0"))
            self.dro_dic["Combi_DRO_0"].set_property("dtg_color", gtk.gdk.color_parse("#F2F1F0"))
            self.dro_dic["Combi_DRO_9"].set_property("abs_color", gtk.gdk.color_parse(self.abs_color))
            self.dro_dic["Combi_DRO_9"].set_property("rel_color", gtk.gdk.color_parse(self.rel_color))
            self.dro_dic["Combi_DRO_9"].set_property("dtg_color", gtk.gdk.color_parse(self.dtg_color))
            self.diameter_mode = True
        else:
            self.dro_dic["Combi_DRO_9"].set_property("abs_color", gtk.gdk.color_parse("#F2F1F0"))
            self.dro_dic["Combi_DRO_9"].set_property("rel_color", gtk.gdk.color_parse("#F2F1F0"))
            self.dro_dic["Combi_DRO_9"].set_property("dtg_color", gtk.gdk.color_parse("#F2F1F0"))
            self.dro_dic["Combi_DRO_0"].set_property("abs_color", gtk.gdk.color_parse(self.abs_color))
            self.dro_dic["Combi_DRO_0"].set_property("rel_color", gtk.gdk.color_parse(self.rel_color))
            self.dro_dic["Combi_DRO_0"].set_property("dtg_color", gtk.gdk.color_parse(self.dtg_color))
            self.diameter_mode = False

        print("diameter mode = {0}".format(self.diameter_mode))


###############################################################################
##                       modify / hide widgets                               ##
###############################################################################

    # the user want to use a security mode
    def user_mode(self):
        self.user_mode = True
        self.widgets.tbtn_setup.set_sensitive(False)
        
    def _show_offset_tab(self, state):
        print("Build GUI _show offset tab")
        page = self.widgets.ntb_preview.get_nth_page(1)
        if page.get_visible() and state or not page.get_visible() and not state:
            return
        if state:
            page.show()
            self.widgets.ntb_preview.set_property("show-tabs", state)
            self.widgets.ntb_preview.set_current_page(1)
            self.widgets.offsetpage1.mark_active(self.system)
            if self.widgets.chk_use_kb_on_offset.get_active():
                self.widgets.ntb_info.set_current_page(1)
        else:
            names = self.widgets.offsetpage1.get_names()
            for system, name in names:
                system_name = "system_name_{0}".format(system)
                self.prefs.putpref(system_name, name)
            page.hide()
            btn = self.touch_button_dic["edit_offsets"]
            btn.set_active(False)
            self.widgets.ntb_preview.set_current_page(0)
            self.widgets.ntb_info.set_current_page(0)
            if self.widgets.ntb_preview.get_n_pages() <= 4:  # else user tabs are available
                self.widgets.ntb_preview.set_property("show-tabs", state)
            else:
                self.widgets.ntb_preview.set_property("show-tabs", not state)

    def _show_tooledit_tab(self, state):
        page = self.widgets.ntb_preview.get_nth_page(2)
        if page.get_visible() and state or not page.get_visible() and not state:
            return
        if state:
            page.show()
            self.widgets.ntb_preview.set_property("show-tabs", not state)
            self.widgets.vbx_jog.hide()
            self.widgets.ntb_preview.set_current_page(2)
            self.widgets.tooledit1.set_selected_tool(self.tool_in_spindle)
            if self.widgets.chk_use_kb_on_tooledit.get_active():
                self.widgets.ntb_info.set_current_page(1)
        else:
            page.hide()
            if self.widgets.ntb_preview.get_n_pages() > 4:  # user tabs are available
                self.widgets.ntb_preview.set_property("show-tabs", not state)
            self.widgets.vbx_jog.show()
            self.widgets.ntb_preview.set_current_page(0)
            self.widgets.ntb_info.set_current_page(0)

    def _show_iconview_tab(self, state):
        page = self.widgets.ntb_preview.get_nth_page(3)
        if page.get_visible() and state or not page.get_visible() and not state:
            return
        if state:
            page.show()
            self.widgets.ntb_preview.set_property("show-tabs", not state)
            self.widgets.ntb_preview.set_current_page(3)
            if self.widgets.chk_use_kb_on_file_selection.get_active():
                self.widgets.box_info.show()
                self.widgets.ntb_info.set_current_page(1)
        else:
            page.hide()
            if self.widgets.ntb_preview.get_n_pages() > 4:  # user tabs are available
                self.widgets.ntb_preview.set_property("show-tabs", not state)
            self.widgets.ntb_preview.set_current_page(0)
            self.widgets.ntb_info.set_current_page(0)

###############################################################################
##                     set widgets to start value                            ##
###############################################################################    

    def _init_widgets(self):
        # set the title of the window, to show the release
        self.widgets.window1.set_title("gmoccapy for linuxcnc {0}".format(self._RELEASE))
        self.widgets.lbl_version.set_label("<b>gmoccapy\n{0}</b>".format(self._RELEASE))
        
        # this sets the background colors of several buttons
        # the colors are different for the states of the button
        self.widgets.tbtn_on.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))
        self.widgets.tbtn_estop.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FF0000"))
        self.widgets.tbtn_estop.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#00FF00"))
        self.widgets.rbt_manual.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))
        self.widgets.rbt_mdi.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))
        self.widgets.rbt_auto.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))
        self.widgets.tbtn_setup.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))
        self.widgets.rbt_forward.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#00FF00"))
        self.widgets.rbt_reverse.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#00FF00"))
        self.widgets.rbt_stop.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))
        self.widgets.rbt_view_p.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))
        self.widgets.rbt_view_x.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))
        self.widgets.rbt_view_y.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))
        self.widgets.rbt_view_y2.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))
        self.widgets.rbt_view_z.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))
        self.widgets.tbtn_flood.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#00FF00"))
        self.widgets.tbtn_fullsize_preview.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))
        self.widgets.tbtn_fullsize_preview1.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))
        self.widgets.tbtn_mist.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#00FF00"))
        self.widgets.tbtn_optional_blocks.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))
        self.widgets.tbtn_optional_stops.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))
        self.widgets.tbtn_user_tabs.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))
        self.widgets.tbtn_view_dimension.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))
        self.widgets.tbtn_view_tool_path.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))
        self.widgets.tbtn_switch_mode.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.color_parse("#FFFF00"))

        # set start colors of the color selection button
        self.widgets.abs_colorbutton.set_color(gtk.gdk.color_parse(self.abs_color))
        self.widgets.rel_colorbutton.set_color(gtk.gdk.color_parse(self.rel_color))
        self.widgets.dtg_colorbutton.set_color(gtk.gdk.color_parse(self.dtg_color))
        self.widgets.homed_colorbtn.set_color(gtk.gdk.color_parse(self.homed_color))
        self.widgets.unhomed_colorbtn.set_color(gtk.gdk.color_parse(self.unhomed_color))

        # set the velocity settings to adjustments
        self.widgets.adj_spindle_bar_min.set_value(self.min_spindle_rev)
        self.widgets.adj_spindle_bar_max.set_value(self.max_spindle_rev)
        self.widgets.spindle_feedback_bar.set_property("min", float(self.min_spindle_rev))
        self.widgets.spindle_feedback_bar.set_property("max", float(self.max_spindle_rev))
        
        # should the tool in spindle be reloaded on startup?
        self.widgets.chk_reload_tool.set_active(self.prefs.getpref("reload_tool", True, bool))
        
        # set the buttons on the settings page for additional DRO button 
        self.widgets.chk_show_dro.set_active(self.prefs.getpref("enable_dro", False, bool))
        self.widgets.chk_show_offsets.set_active(self.prefs.getpref("show_offsets", False, bool))
        self.widgets.chk_show_dtg.set_active(self.prefs.getpref("show_dtg", False, bool))
        self.widgets.chk_show_offsets.set_sensitive(self.widgets.chk_show_dro.get_active())
        self.widgets.chk_show_dtg.set_sensitive(self.widgets.chk_show_dro.get_active())

        # gremlin related stuff
        self.widgets.tbtn_view_tool_path.set_active(self.prefs.getpref("view_tool_path", True, bool))
        self.widgets.tbtn_view_dimension.set_active(self.prefs.getpref("view_dimension", True, bool))
        #view = self.prefs.getpref("gremlin_view", "rbt_view_p", str)
        #self.widgets[view].set_active(True)
        self.widgets.cmb_mouse_button_mode.set_active(self.prefs.getpref("mouse_btn_mode", 4, int))

        # Popup Messages position and size
        self.widgets.adj_x_pos_popup.set_value(self.prefs.getpref("x_pos_popup", 45, float))
        self.widgets.adj_y_pos_popup.set_value(self.prefs.getpref("y_pos_popup", 55, float))
        self.widgets.adj_width_popup.set_value(self.prefs.getpref("width_popup", 250, float))
        self.widgets.adj_max_messages.set_value(self.prefs.getpref("max_messages", 10, float))
        self.widgets.fontbutton_popup.set_font_name(self.prefs.getpref("message_font", "sans 10", str))
        self.widgets.chk_use_frames.set_active(self.prefs.getpref("use_frames", True, bool))
        
        # get when the keyboard should be shown
        # and set the corresponding button active
        # only if onbaoard keyboard is ok.
        if self.onboard:
            self.widgets.chk_use_kb_on_offset.set_active(self.prefs.getpref("show_keyboard_on_offset",
                                                                            False, bool))
            self.widgets.chk_use_kb_on_tooledit.set_active(self.prefs.getpref("show_keyboard_on_tooledit",
                                                                              False, bool))
            self.widgets.chk_use_kb_on_edit.set_active(self.prefs.getpref("show_keyboard_on_edit",
                                                                          True, bool))
            self.widgets.chk_use_kb_on_mdi.set_active(self.prefs.getpref("show_keyboard_on_mdi",
                                                                         True, bool))
            self.widgets.chk_use_kb_on_file_selection.set_active(self.prefs.getpref("show_keyboard_on_file_selection",
                                                                                    False, bool))
        else:
            self.widgets.chk_use_kb_on_offset.set_active(False)
            self.widgets.chk_use_kb_on_tooledit.set_active(False)
            self.widgets.chk_use_kb_on_edit.set_active(False)
            self.widgets.chk_use_kb_on_mdi.set_active(False)
            self.widgets.chk_use_kb_on_file_selection.set_active(False)
            self.widgets.frm_keyboard.set_sensitive(False) 
        
        # disable reload tool on start up, if True
        if self.no_force_homing:
            self.widgets.chk_reload_tool.set_sensitive(False)
            self.widgets.chk_reload_tool.set_active(False)
            self.widgets.lbl_reload_tool.set_visible(True)

        self._show_tooledit_tab(False)
        self._show_offset_tab(False)
        self._show_iconview_tab(False)

        # call the function to change the button status
        # so every thing is ready to start
        widgetlist = ["rbt_manual", "rbt_mdi", "rbt_auto", "btn_homing", "btn_touch", "btn_tool",
                      "ntb_jog", "spc_feed", "btn_feed_100", "rbt_forward", "btn_index_tool",
                      "rbt_reverse", "rbt_stop", "tbtn_flood", "tbtn_mist", "btn_change_tool",
                      "btn_select_tool_by_no", "btn_spindle_100", "spc_rapid", "spc_spindle",
                      "btn_tool_touchoff_x", "btn_tool_touchoff_z", "tbtn_on"
        ]
        self._sens_widgets(widgetlist, False)

        # initialize the kinematics related widgets
        if not self.trivial_kinematics:
            self.widgets.gremlin.set_property( "enable_dro", True )
            self.widgets.gremlin.use_joints_mode = True
            self.widgets.tbtn_switch_mode.show()
            self.widgets.tbtn_switch_mode.set_label(_(" Joint\nmode"))
            self.widgets.tbtn_switch_mode.set_sensitive(False)
            self.widgets.tbtn_switch_mode.set_active(True)
            self.widgets.lbl_replace_mode_btn.hide()
            self.widgets.ntb_jog_JA.set_page(1)
        else:
            self.widgets.gremlin.set_property( "enable_dro", False )
            self.widgets.gremlin.use_joints_mode = False
            self.widgets.tbtn_switch_mode.hide()
            self.widgets.lbl_replace_mode_btn.show()
            self.widgets.ntb_jog_JA.set_page(0)

        # get the way to unlock the setting
        unlock = self.prefs.getpref("unlock_way", "use", str)
        # and set the corresponding button active
        self.widgets["rbt_{0}_unlock".format(unlock)].set_active(True)
#        # if Hal pin should be used, only set the button active, if the pin is high
#        if unlock == "hal" and not self.halcomp["unlock-settings"]:
#            self.widgets.tbtn_setup.set_sensitive(False)

###############################################################################
##                   initial clicking and toggling                           ##
###############################################################################

    def _activate_widgets(self):
        pass

###############################################################################
##                  set initial global values value                          ##
###############################################################################    

    # initial values for the GUI
    def _set_initial_values(self):
        # needed to react to system changes
        system_list = ("0", "G54", "G55", "G56", "G57", "G58", "G59", "G59.1", "G59.2", "G59.3")
        self.system_dic = {}
        for pos, system in enumerate(system_list):
            self.system_dic[str(pos)] = system
        self.system = self.system_dic["1"]
        self.initialized = False  # will be set True after the window has been shown and all
                                  # basic settings has been finished, so we avoid some actions
                                  # because we cause click or toggle events when initializing
                                  # widget states.

        self.estop_active = True  # will handle the estop state
        self.machine_on = False   # will handle the machine is on state
        self.mode = "MAN"         # The actual mode
        self.interpreter = "IDLE" # The interpreter state

        self.motion_mode = 0      # initial start will be done in Joints mode
 
        self.user_mode = False    # user is not allowed to access settings page
 
        self.all_homed = False    # will hold True if all axis are homed
        
        self.tool_in_spindle = 0  # will hold the toolnumber mounted in spindle
        self.tool_change = False  # this is needed to get back to manual mode after a tool change
        self.load_tool = False    # We use this avoid mode switching on reloading the tool on start up of the GUI
        
        self.diameter_mode = False # Check if in lathe mode we are in diameter mode (G7 or G8)

