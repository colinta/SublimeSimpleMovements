SimpleMovement plugin
=====================

Adds caret moving and newline entering commands.  `super+left` / `home` go to the *real* beginning of line, and some nifty `enter` commands.

Installation
------------

1. Using Package Control, install "SimpleMovement"

Or:

1. Open the Sublime Text Packages folder
    - OS X: ~/Library/Application Support/Sublime Text 3/Packages/
    - Windows: %APPDATA%/Sublime Text 3/Packages/
    - Linux: ~/.Sublime Text 3/Packages/ or ~/.config/sublime-text-3/Packages

2. clone this repo
3. Install keymaps for the commands (see Example.sublime-keymap for my preferred keys)

### Sublime Text 2

1. Open the Sublime Text 2 Packages folder
2. clone this repo, but use the `st2` branch

       git clone -b st2 git@github.com:colinta/SublimeSimpleMovements

Commands
--------

`simple_movement_bol`: Moves the caret to the beginning of the line.
- If the cursor is already at the beginning of the line, it will move to the first non-whitespace character.
- accepts an `extend` option, which moves the cursor *while selecting* from the previous cursor location.

`simple_movement_eol`: Moves the caret to the end of the line.
- If the cursor is already at the beginning of the line, it will move *back* to the first non-whitespace character.
- accepts an `extend` option, which moves the cursor *while selecting* from the previous cursor location.

`simple_movement_insert`: Inserts a character.  Used to insert literal quotes, tabs, anything.
- If you use smart quoting plugins, this is a way to bypass those.  I use `ctrl+v,"` for example, to insert just a single `"`
- you *must* provide the `insert: "text"` option to this command.

`simple_movement_select_block`: Changes a multi-line selection into multiple block selections.  Each block will begin and end at the same column, as determined by the start and end points of the original region.
- So you select a block of text, activate this plugin, and now you'll have each line selected.  I often use this to select and entire file, then this command gives me a cursor on every line.  Like if I'm editing a log file for instance.

`simple_movement_align_cursor`: Inserts spaces so that all the cursors are on the same column.  If `move` is `left`, it removes spaces (so the text moves to the left) instead of adding them.
- This tries to be pretty smart about what cursors to give you when you're done. For example, if the first line looks like a "header", it will deselect that line. Useful for any code editing, but also has support for "objc-style alignment", where you want all the `:` to line up
- accepts the `move: 'left'|'right'|'align'` option, defaults to `right`.  Move all the text to the left, to the right, or align the current cursors (objc-style `:` alignment)

`simple_movement_goto_line`: Can be given a line number or line numbers, and that will become the selection.
- Great "goto line" replacement.  It can parse the input to "goto" multiple lines, in which case it also selects those lines.
- Jumps to the line(s) you type while typing, hit esc to go back, so a great way to preview a section of code, then go back to where you were

`simple_movement_duplicate_line`: Takes the same arguments as `simple_movement_goto_line` and copies those lines to the current cursor.  Try `-1` to duplicate the line above.
- uses the same line(s) parsing as `simple_movement_goto_line`.  Inserts the lines you specify at the current cursor(s).

goto_line and duplicate_line both support cool line selection tricks:

* `123`: Goes to line 123
* `123,`: Goes to line 123 and selects it
* `123,125`: Selects lines 123-125
* `-1,+1`: Selects one line up, the current line, and one line below

The duplicate line command supports all these, but duplicates those lines at the *current* cursor location rather than moving the cursor.

`simple_movement_nl`: Inserts a newline, or moves caret to end of line.  Can also insert line-ending characters and unindent. Quite a few options:

1. `hard_nl true|false`: inserts a newline, and keeps the cursor at the first position; doesn't try to match whitespace
2. `with_terminator true|false`: in languages that use a `;` as the line terminator, this option inserts the terminator at the end of the current line.
3. `insert_nl true|false`: if false, it *doesn't* insert a newline! weird, but makes sense when you combine it with `with_terminator`. Inserts a semicolon if there isn't one there, then goes to the end of the line.
4. `unindent: true|false`: Useful in python, where there's no real way for the editor to detect unindention, so you can explicitly tell it to unindent with this option.
5. `with_comment: true|false`: If this is `true`, then it will take comments into account - for instance it will 'continue' a block of comments, or it will *end* a block of comments if `unindent` is true.

Honestly, this command does a ton of stuff.  Check out the example key bindings for my configuration, then practice them to see how they work.

`simple_movement_select_next`: At one point, some version of Sublime Text changed how "Quick Find Next" (`super+d`) worked.  This command makes `super+d` the same simple powerhouse it's meant to be.
- works intuitively (for me!) with multiple cursors
- has a `select_all` option to select *all* instances of the current selections.
