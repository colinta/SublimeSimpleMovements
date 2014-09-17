SimpleMovement plugin
=====================

This plugin started very humbly, and is now my dumping ground for all movement,
selection, and very simple insertion commands.

If you use it to the fullest, you'll have what **I** consider to be better
newline, selection, and movement commands.  Each command is mostly documented at
the bottom.  Here's an overview of what is in here:

###### Newline

- Pressing enter while writing comments *continues* writing comments
- Pressing `super+alt+enter` inserts a `;` in languages that need it, in places
  where they are needed.  In Python, it inserts a `:` at the end of lines that
  start with`def/for/while/etc`
- `alt+enter` inserts a "\n" and begins at the beginning of the line
- `super+shift+enter` inserts a line *above* the current line

###### Beginning/End of Line
Pressing `super+left` goes to the very beginning, unless you're already there,
then it goes to the first non-whitespace character.

`super+right` does the same, but for the end of line

###### Goto line
`super+l` has super powers.  You can select a range (`12,20`) a single line
(`40,`), or use relative locations (`-1,+1`)

###### Duplicate line
`ctrl+d` uses the same line parsing as goto-line, but inserts the lines you
choose at the current cursor(s) location(s).

###### Selecting "block" of text
Use the keyboard to select a bunch of text, then `ctrl+shift+b` to turn it into
separate selections.  Useful for doing ASCII art, among other things.

###### Inserting text
Sometimes you just need a way to insert some text. I bind `ctrl+v,(` to insert a
literal '(', otherwise typing '(' auto-inserts (thanks to SublimeBracketeer) a
pair of parentheses. `simple_movement_insert`

Also handy is a command that brings up a palette to *select* some text to
insert. The `simple_movement_snippet_picker` command is additionally useful
because it actually inserts using the `insert_snippet` command, so you can bind
a collection of related snippets to a keypress and choose them using
quick-search.  I use it to make it easy to find ⌘⇧⌃⌥.

###### Aligning the cursor
Actually, wbond has a much better plugin, but this one works using multiple
cursors.

###### Moving the viewport
I used this ability in TextMate a lot, and wanted it here.  It's basically using
the keyboard to scroll, by a little or a lot.

###### Select next
I don't like the way "Incremental Find" works in sublime text.  I prefer the
quick-and-immediate search that TextMate provided via `ctrl+s`.  To that, I
added regex search, search+extend-selection (with support for multiple cursors)
and reverse search.  You should master these, they are **REALLY REALLY** useful!

###### Multiple cursors => less cursors
I really love the multiple cursors feature of Sublime Text.  The
`simple_movement_one_selection` command can either remove one cursor, or select
one of the cursors.  For instance, I might select five things, then iterate
through then using `super+1..5`.  Or select all of them in the document, and go
to the first or last.  Or unselect the first and last.  Again, really useful,
but you'll need to learn them.

###### Select duplicates
This is a weird one, honestly I don't remember when I use it, but it's bound to
`F6` and I guess I use it often enough... anyway it's based on multiple
selections.  Select a bunch of things that might be similar, then activate this
command.  It will unselect the *first* of each unique item.  wat?  yeah, well,
I said it's a weird one.


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

##### `simple_movement_bol`

Moves the caret to the beginning of the line.
- If the cursor is already at the beginning of the line, it will move to the first non-whitespace character.
- accepts an `extend` option, which moves the cursor *while selecting* from the previous cursor location.

##### `simple_movement_eol`

Moves the caret to the end of the line.
- If the cursor is already at the beginning of the line, it will move *back* to the first non-whitespace character.
- accepts an `extend` option, which moves the cursor *while selecting* from the previous cursor location.

##### `simple_movement_insert`

Inserts a character.  Used to insert literal quotes, tabs, anything.
- If you use smart quoting plugins, this is a way to bypass those.  I use `ctrl+v,"` for example, to insert just a single `"`
- you *must* provide the `insert: "text"` option to this command.

##### `simple_movement_select_block`

Changes a multi-line selection into multiple block selections.  Each block will begin and end at the same column, as determined by the start and end points of the original region.
- So you select a block of text, activate this plugin, and now you'll have each line selected.  I often use this to select and entire file, then this command gives me a cursor on every line.  Like if I'm editing a log file for instance.

##### `simple_movement_align_cursor`

Inserts spaces so that all the cursors are on the same column.  If `move` is `left`, it removes spaces (so the text moves to the left) instead of adding them.
- This tries to be pretty smart about what cursors to give you when you're done. For example, if the first line looks like a "header", it will deselect that line. Useful for any code editing, but also has support for "objc-style alignment", where you want all the `:` to line up
- accepts the `move: 'left'|'right'|'align'` option, defaults to `right`.  Move all the text to the left, to the right, or align the current cursors (objc-style `:` alignment)

##### `simple_movement_goto_line`

Can be given a line number or line numbers, and that will become the selection.
- Great "goto line" replacement.  It can parse the input to "goto" multiple lines, in which case it also selects those lines.
- Jumps to the line(s) you type while typing, hit esc to go back, so a great way to preview a section of code, then go back to where you were

##### `simple_movement_duplicate_line`

Takes the same arguments as `simple_movement_goto_line` and copies those lines to the current cursor.  Try `-1` to duplicate the line above.
- uses the same line(s) parsing as `simple_movement_goto_line`.  Inserts the lines you specify at the current cursor(s).

goto_line and duplicate_line both support cool line selection tricks:

* `123`: Goes to line 123
* `123,`: Goes to line 123 and selects it
* `123,,,,`: Goes to line 123 and selects it and the next 3 lines
* `123,125`: Selects lines 123-125
* `-1,+1`: Selects one line up, the current line, and one line below
* `,,,`: Select the current line and next 2 lines

The duplicate line command supports all these, but duplicates those lines at the *current* cursor location rather than moving the cursor.

##### `simple_movement_nl`

Inserts a newline, or moves caret to end of line.  Can also insert line-ending characters and unindent. Quite a few options:

1. `hard_nl true|false`: inserts a newline, and keeps the cursor at the first position; doesn't try to match whitespace
2. `with_terminator true|false`: in languages that use a `;` as the line terminator, this option inserts the terminator at the end of the current line.
3. `insert_nl true|false`: if false, it *doesn't* insert a newline! weird, but makes sense when you combine it with `with_terminator`. Inserts a semicolon if there isn't one there, then goes to the end of the line.
4. `unindent: true|false`: Useful in python, where there's no real way for the editor to detect unindention, so you can explicitly tell it to unindent with this option.
5. `with_comment: true|false`: If this is `true`, then it will take comments into account - for instance it will 'continue' a block of comments, or it will *end* a block of comments if `unindent` is true.

Honestly, this command does a ton of stuff.  Check out the example key bindings for my configuration, then practice them to see how they work.

##### `simple_movement_select_next`

At one point, some version of Sublime Text changed how "Quick Find Next" (`super+d`) worked.  This command makes `super+d` the same simple powerhouse it's meant to be.
- works intuitively (for me!) with multiple cursors
- has a `select_all` option to select *all* instances of the current selections.

##### `simple_movement_one_selection`

This command is used to select or UNselect one of your cursors. I work with
multiple cursors A LOT, and I love this command. I have it bound to
`super+1..0`, but super+0 selects the *last* cursor, which is often very handy.

`super+shift+1..0` unselects a cursor, usually I just need to use
`super+shift+1` or `super+shift+0` to unselect the first or last cursor.
