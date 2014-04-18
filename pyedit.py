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

    # Save text to file
    def save(self, filename = None):
        if filename is not None: 
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
        self.__label.set_text("*" + os.path.basename(self.__filename))
        self.__has_changed = True

    def __init__(self, buffer, filename, newfile):
        self.__buffer = buffer
        self.__label = gtk.Label(os.path.basename(filename))
        self.__filename = filename
        self.__newfile = newfile
        self.__has_changed = False
        self.__buffer.connect("insert_text", self.__changed)


class PyEdit:
    def close_tab(self, button, num):
        self.notebook.remove_page(num)

    def add_tab(self, document):
        # Sourceview
        sv = gtksourceview2.View(document.get_buffer())
        sv.show()

        sw = gtk.ScrolledWindow()
        sw.add(sv)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.show()

        # Button to close the current tab
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        button = gtk.Button()
        button.set_image(image)
        button.set_relief(gtk.RELIEF_NONE)

       
        # Horizontal box for the close button and the filename
        box = gtk.HBox()
        box.pack_start(document.get_label(), True, True, 0)
        box.pack_end(button, False, False, 0)
        box.show_all()
        self.notebook.append_page(sw, box)
            
        self.notebook.next_page()
        page = self.notebook.get_current_page()

        while len(self.documents) <= page:
            self.documents.append(None)
        self.documents[page] = document

        button.connect('clicked', self.close_tab, page)

    def get_current_document(self):
        page = self.notebook.get_current_page()
        return self.documents[page]

    ######################################
    # Signal Functions
    ######################################

    def new_file(self, widget = None):
        tab = 1
        while tab in self.tabs:
            tab += 1   
        self.tabs.append(tab)
        filename = "Unsaved Document " + str(tab)

        # Create buffer for sourceview
        buffer = gtksourceview2.Buffer()
        buffer.set_data("languages-manager", gtksourceview2.LanguageManager())
        buffer.place_cursor(buffer.get_start_iter())
        buffer.set_data('filename', filename)
        language = buffer.get_data("languages-manager").guess_language(filename)

        # Get syntax colors for language the file extension if possible
        if language:
            buffer.set_highlight_syntax(True)
            buffer.set_language(language)
        else:
            buffer.set_highlight_syntax(False)
        self.add_tab(PyEditDocument(buffer, filename, True))

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

        # Create buffer for sourceview
        buffer = gtksourceview2.Buffer()
        buffer.begin_not_undoable_action()
        buffer.set_data("languages-manager", gtksourceview2.LanguageManager())
        buffer.place_cursor(buffer.get_start_iter())
        buffer.set_data('filename', filename)

        # Get text from file
        f = open(filename, "r")
        text = f.read()
        f.close()
        dialog.destroy()
        
        if text is not None:
            buffer.set_text(text)
        buffer.end_not_undoable_action()
        self.add_tab(PyEditDocument(buffer, filename, False))

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
        if document.is_newfile():
            self.save_file_as(None)
        else:
            document.save()

    def quit(self, widget):
        gtk.main_quit()

    def undo(self, widget):
        document = self.get_current_document()
        document.undo()

    def __init__(self):
        self.xml = gtk.glade.XML("pyedit.glade")
        self.window = self.xml.get_widget("wndMain")
        self.notebook = self.xml.get_widget("nbDocument")
        self.window.connect("destroy", self.quit)
        self.tabs = [ ]
        self.documents = [ ]

        signals = { "on_imiOpen_activate"    : self.open_file,
                    "on_imiSave_activate"    : self.save_file,
                    "on_imiSaveAs_activate"  : self.save_file_as,
                    "on_imiNew_activate"     : self.new_file,
                    "on_imiQuit_activate"    : self.quit,
                    "on_tbtnNew_clicked"     : self.new_file, 
                    "on_tbtnOpen_clicked"    : self.open_file,
                    "on_tbtnSave_clicked"    : self.save_file,
                    "on_tbtnUndo_clicked"    : self.undo}

        self.xml.signal_autoconnect(signals)
        self.window.show()
        self.new_file()
        gtk.main()

if __name__ == "__main__":
    PyEdit()
