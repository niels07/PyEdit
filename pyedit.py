#!/usr/bin/env python
""" 
 PyEdit ~ A simple texteditor written in Python
 
 Copyright (c) 2014 "PyEdit" Niels Vanden Eynde 
   
 Permission is hereby granted, free of charge, to any person
 obtaining a copy of this software and associated documentation
 files (the "Software"), to deal in the Software without
 restriction, including without limitation the rights to use,
 copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the
 Software is furnished to do so, subject to the following
 conditions:

 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 OTHER DEALINGS IN THE SOFTWARE.
"""

import os
import pygtk
import gtk
import gtk.glade
import gtksourceview2
import pango

pygtk.require('2.0')

class PyEditDocument:
    def set_text(self, text):
        self.__buffer.set_text(text)

    # Return the text in buffer, from START to END
    # if iters are not specified, return the entire
    # text 
    def get_text(self, start = None, end = None):
        if start is None:
            start = self.__buffer.get_start_iter()

        if end is None:
            end = self.__buffer.get_end_iter()

        return self.__buffer.get_text(start, end)

    # Set the Filename and label for the current tab
    def set_filename(self, filename):
        self.__filename = filename
        self.__label.set_text(os.path.basename(self.__filename))

    # Save text to file.
    def save(self, filename = None):
        if filename != None: 
            self.__filename = filename
            
        self.__label.set_text(os.path.basename(self.__filename))

        file = open(self.__filename, "w")
        file.write(self.get_text())
        file.close()
        self.__has_changed = False

    # Undo last action if possible
    def undo(self):
        if self.__buffer.can_undo():
            self.__buffer.undo()

    # Redo next action if possible
    def redo(self):
        if self.__buffer.can_redo():
            self.__buffer.redo()

    # Return TRUE if buffer is undoable
    def can_undo(self):
        return self.__buffer.can_undo()

    # return TRUE if file is a newly created file
    def is_newfile(self):
        return self.__newfile

    def get_filename(self):
        return self.__filename

    def get_label(self):
        return self.__label

    def get_buffer(self):
        return self.__buffer

    def has_changed(self):
        return self.__has_changed
    
    # Signal for when text in the buffer has changed
    def __changed(self, data, iter, string, length):
        # Prepend the filename in the label with a '*' so
        # the user knows the file has been edited
        self.__label.set_text("*" + os.path.basename(self.__filename))
        self.__has_changed = True

    # Undo last action if possible
    def undo(self):
        if self.__buffer.can_undo():
            self.__buffer.undo()

    # Redo next action if possible
    def redo(self):
        if self.__buffer.can_redo():
            self.__buffer.redo()

    # Return TRUE if buffer is undoable
    def can_undo(self):
        return self.__buffer.can_undo()

    # return TRUE if file is a newly created file
    def is_newfile(self):
        return self.__newfile

    def get_filename(self):
        return self.__filename

    def get_label(self):
        return self.__label

    def get_buffer(self):
        return self.__buffer

    def get_view(self):
        return self.__view;

    def has_changed(self):
        return self.__has_changed
    
    # Apply a specific tag to text, if the tag has
    # already been supplied remove it instead.
    def apply_tag(self, tag):
        bounds = self.__buffer.get_selection_bounds()
        if len(bounds) == 0:
            return

        start, end = bounds
        if start.has_tag(tag):
            self.__buffer.remove_tag(tag, start, end)
        else:
            self.__buffer.apply_tag(tag, start, end)

    def bold(self):
        self.apply_tag(self.tag_bold)

    def italic(self):
        self.apply_tag(self.tag_italic)

    def underline(self):
        self.apply_tag(self.tag_underline)

    def justify(self, j):
        self.__view.set_justification(j)

    def __create_buffer(self):
        # Create buffer for sourceview
        buffer = gtksourceview2.Buffer()
        buffer.begin_not_undoable_action()

        self.tag_bold       = buffer.create_tag("bold",      weight    = pango.WEIGHT_BOLD)
        self.tag_italic     = buffer.create_tag("italic",    style     = pango.STYLE_ITALIC)
        self.tag_underline  = buffer.create_tag("underline", underline = pango.UNDERLINE_SINGLE)
        
        buffer.set_data("languages-manager", gtksourceview2.LanguageManager())
        buffer.place_cursor(buffer.get_start_iter())
        buffer.set_data('filename', self.__filename)
        language = buffer.get_data("languages-manager").guess_language(self.__filename)
        
        # Get syntax colors for language the file extension if possible
        if language:
            buffer.set_highlight_syntax(True)
            buffer.set_language(language)
        else:
            buffer.set_highlight_syntax(False)

        buffer.end_not_undoable_action()
        self.__buffer = buffer

    def __create_view(self):
        self.__view = gtksourceview2.View(self.__buffer)
        self.__view.show()

    # Signal for when text in the buffer has changed
    def __changed(self, data, iter, string, length):
        # Prepend the filename in the label with a '*' so
        # the user knows the file has been edited
        self.__label.set_text("*" + os.path.basename(self.__filename))
        self.__has_changed = True

    def __init__(self, filename, newfile):
        self.__filename = filename
        self.__label = gtk.Label(os.path.basename(filename))
        self.__newfile = newfile
        self.__create_buffer()
        self.__create_view()
        if not newfile:
            file = open(filename, "r")
            text = file.read()
            self.set_text(text)
        self.__has_changed = False
        self.__buffer.connect("insert_text", self.__changed)


class PyEdit:
    # Close the current tab.
    # TODO: ask to save file.
    def close_tab(self, button, num):
        self.notebook.remove_page(num)

    def add_tab(self, document):
        # Create scrolled window for view.
        sw = gtk.ScrolledWindow()
        sw.add(document.get_view())
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.show()

        # Button to close the current tab.
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        button = gtk.Button()
        button.set_image(image)
        button.set_relief(gtk.RELIEF_NONE)

        # Horizontal box for the close button and the filename.
        box = gtk.HBox()
        box.pack_start(document.get_label(), True, True, 0)
        box.pack_end(button, False, False, 0)
        box.show_all()
        self.notebook.append_page(sw, box)
            
        # Switch to the new tab,
        self.notebook.next_page()
        page = self.notebook.get_current_page()

        while len(self.documents) <= page:
            self.documents.append(None)
        self.documents[page] = document

        button.connect('clicked', self.close_tab, page)

    def get_current_document(self):
        page = self.notebook.get_current_page()
        return self.documents[page]

    # Create a new empty file
    def new_file(self, widget = None):
        tab = 1
        while tab in self.tabs:
            tab += 1   
        self.tabs.append(tab)
        filename = "Unsaved Document " + str(tab)

        # Create buffer for sourceview
        buffer = gtksourceview2.Buffer()
        buffer.set_data("languages-manager", gtksourceview2.LanguageManager())
        self.add_tab(PyEditDocument(filename, True))

    def open_file(self, widget):
        # Create file filter for the dialog
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")

        # Create dialog to open a file
        dialog = gtk.FileChooserDialog("Open", 
                                        None,
                                        gtk.FILE_CHOOSER_ACTION_OPEN,
                                       (gtk.STOCK_CANCEL,
                                        gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN,
                                        gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.show()
        response = dialog.run()
        if response != gtk.RESPONSE_OK:
            dialog.destroy()
            return
        filename = dialog.get_filename()
        dialog.destroy()

        document = PyEditDocument(filename, False)
        self.add_tab(document)

    # Save file, but always prompt for a filename.
    def save_file_as(self, widget):
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog = gtk.FileChooserDialog("Open", 
                                        None,
                                        gtk.FILE_CHOOSER_ACTION_SAVE,
                                       (gtk.STOCK_CANCEL,
                                        gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_SAVE,
                                        gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.show()
        response = dialog.run()
        if response != gtk.RESPONSE_OK:
            dialog.destroy()
            return
        document = self.get_current_document()
        document.save(dialog.get_filename())
        dialog.destroy()

    def save_file(self, widget):
        document = self.get_current_document()

        # If the document is a new file, request a filename, 
        # otherwise just overwrite the one that's currently 
        # open.
        if document.is_newfile():
            self.save_file_as(None)
        else:
            document.save()

    # Callback functions.
    def quit(self, widget):
        gtk.main_quit()

    def undo(self, widget):
        document = self.get_current_document()
        document.undo()

    def redo(self, widget):
        document = self.get_current_document()
        document.redo()

    def bold(self, widget):
        document = self.get_current_document()
        document.bold()
    
    def italic(self, widget):
        document = self.get_current_document()
        document.italic()

    def underline(self, widget):
        document = self.get_current_document()
        document.underline()
 
    def justify(self, j):
        document = self.get_current_document()
        document.justify(j)

    def jright(self, widget):
        self.justify(gtk.JUSTIFY_RIGHT)

    def jleft(self, widget):
        self.justify(gtk.JUSTIFY_LEFT)

    def jcenter(self, widget):
        self.justify(gtk.JUSTIFY_CENTER)

    def __init__(self):
        self.xml = gtk.glade.XML("pyedit.glade")
        self.window = self.xml.get_widget("wndMain")
        self.notebook = self.xml.get_widget("nbDocument")
        self.window.connect("destroy", self.quit)
        self.tabs = [ ]
        self.documents = [ ]

        signals = { "on_imiOpen_activate"       : self.open_file,
                    "on_imiSave_activate"       : self.save_file,
                    "on_imiSaveAs_activate"     : self.save_file_as,
                    "on_imiNew_activate"        : self.new_file,
                    "on_imiQuit_activate"       : self.quit,
                    "on_tbtnNew_clicked"        : self.new_file, 
                    "on_tbtnOpen_clicked"       : self.open_file,
                    "on_tbtnSave_clicked"       : self.save_file,
                    "on_tbtnUndo_clicked"       : self.undo,
                    "on_tbtnBold_clicked"       : self.bold,
                    "on_tbtnItalic_clicked"     : self.italic,
                    "on_tbtnUnderline_clicked"  : self.underline,
                    "on_tbtnRight_clicked"      : self.jright,
                    "on_tbtnLeft_clicked"       : self.jleft,
                    "on_tbtnCenter_clicked"     : self.jcenter,
                    "on_tbtnRedo_clicked"       : self.redo }

        self.xml.signal_autoconnect(signals)
        self.window.show()

        # Create a new file when starting the program so the
        # user doesn't have to press "new" everytime when starting
        # the application.
        self.new_file()
        gtk.main()

if __name__ == "__main__":
    PyEdit()
