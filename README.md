SimpleMovement plugin for Sublime Text 2
========================================

Adds caret moving and newline entering commands.  `super+left` / `home` go to the *real* beginning of line, and some nifty `enter` commands.


Installation
------------

1. Using Package Control, install "SimpleMovement"

Or:

1. Open the Sublime Text 2 Packages folder

    - OS X: ~/Library/Application Support/Sublime Text 2/Packages/
    - Windows: %APPDATA%/Sublime Text 2/Packages/
    - Linux: ~/.Sublime Text 2/Packages/

2. clone this repo

Commands
--------

`simple_movement_bol`: Moves the caret to the beginning of the line.

`simple_movement_nl`: Inserts a newline, or moves caret to end of line.  Can also insert line-ending characters and unindent.

`simple_movement_insert`: Inserts a character.  Used to insert literal quotes, tabs, anything.

`simple_movement_select_block`: Changes a multi-line selection into multiple block selections.  Each block will begin and end at the same column, as determined by the start and end points of the original region.

`simple_movement_align_cursor`: Inserts spaces so that all the cursors are on the same column.  If `move` is `left`, it removes spaces (so the text moves to the left) instead of adding them.

`simple_movement_goto_line`: Can be given a line number or line numbers, and that will become the selection.

* `123`: Goes to line 123
* `123,`: Goes to line 123 and selects it
* `123,125`: Selects lines 123-125
* `-1,+1`: Selects one line up, the current line, and one line below

`simple_movement_duplicate_line`: Takes the same arguments as `simple_movement_goto_line` and copies those lines to the current cursor.  Try `-1` to duplicate the line above.
