import time
import re
from functools import cmp_to_key

import sublime
import sublime_plugin


semicolon_langs = [
    'source.php',
    'source.js',
    'source.arduino',
    'source.c',
    'source.c++',
    'source.java',
    'source.objc',
    'source.objc++',
    'source.shell',
    'source.css',
    ]


class SimpleMovementBolCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        regions = [region for region in self.view.sel()]
        for region in regions:
            self.run_each(edit, region, **kwargs)

    def run_each(self, edit, region, extend=False):
        line = self.view.line(region.b)
        new_point = line.begin()
        if new_point == region.b:
            # already at BOL, skip to first character
            while self.view.substr(new_point) in [" ", "\t"]:
                new_point += 1
        self.view.sel().subtract(region)
        if extend:
            region = sublime.Region(region.a, new_point)
        else:
            region = sublime.Region(new_point, new_point)
        self.view.sel().add(region)
        self.view.show(region)


class SimpleMovementEolCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        regions = [region for region in self.view.sel()]
        for region in regions:
            self.run_each(edit, region, **kwargs)

    def run_each(self, edit, region, extend=False):
        line = self.view.line(region.b)
        new_point = line.end()
        if new_point == region.b:
            # already at EOL, skip to first character
            new_point = line.end()
            while self.view.substr(new_point - 1) in [" ", "\t"]:
                new_point -= 1
        self.view.sel().subtract(region)
        if extend:
            region = sublime.Region(region.a, new_point)
        else:
            region = sublime.Region(new_point, new_point)
        self.view.sel().add(region)
        self.view.show(region)


class SimpleMovementParseLineCommand(sublime_plugin.TextCommand):
    """
    Base class for SimpleMovementDuplicateLineCommand and SimpleMovementGotoLineCommand
    """
    def get_line(self, line):
        pre = 0
        times = 1
        start = 0
        if line[0] == '+':
            pre = self.first_line
            start = 1
        elif line[0] == '-':
            pre = self.first_line
            start = 1
            times = -1
        elif line == '0':
            pre = self.first_line
        else:
            pre = -1

        stop = start
        while stop < len(line):
            stop += 1
            try:
                int(line[start:stop])
            except ValueError:
                stop -= 1
                break
        return pre + times * int(line[start:stop])

    def get_two_lines(self, text):
        # supported multiline syntax:
        # a,b  =>  lines a to b
        # a,  => just line a
        # a,,,  => line a and next 2 lines (3 lines total)
        # ,b  => current line to line b
        # ,  => just current line
        # ,,  => current and next line
        match = re.match(r'^([^,]*)(,+)(.*)$', text)

        if not match:
            return self.get_line(text), None, 0

        line_a, commas, line_b = match.group(1), match.group(2), match.group(3)

        if line_a:
            line_a = self.get_line(line_a)
        else:
            # ',b'
            line_a = self.first_line

        if line_b:
            line_b = self.get_line(line_b)
            line_b += 1
        else:
            # 'a,' or just ','
            line_b = line_a + len(commas)

        return line_a, line_b

    def demo_line(self, lines):
        '''Goes to the line you've typed after a pause. Hit Esc to go back to the original location.'''
        self.started = time.time()

        def okay_go():
            if time.time() - self.started > .270:
                self.goto_line(lines)
        sublime.set_timeout(okay_go, 300)

    def goto_line(self, lines):
        '''
        Goes to the lines. "lines" are parsed using get_line or get_two_lines,
        from SimpleMovementParseLineCommand.
        '''
        if not len(lines):
            self.restore()
            return

        try:
            if ',' in lines:
                line_a, line_b = self.get_two_lines(lines)
            else:
                line_a = line_b = self.get_line(lines)
        except ValueError:
            self.restore()
            return

        if line_b == line_a:
            # try to go to the same column.  the "too_far" check makes sure we
            # don't go to the next line by accident
            start = self.view.text_point(line_a, self.cursor)
            too_far = self.view.text_point(line_a + 1, 0)
            if start >= too_far:
                start = too_far - 1
            end = start
        else:
            start = self.view.text_point(line_a, 0)
            end = self.view.text_point(line_b, 0)

        # check for additional modifiers at the end of the input
        move_over = re.search(r'[.]+$', lines)
        if move_over:
            start = self.view.text_point(line_a, 0)
            end = start + len(move_over.group(0))

        if start < 0 or end < 0 or start > self.view.size() or end > self.view.size():
            sublime.status_message('Invalid entry')
            self.restore()
            return

        self.view.sel().clear()
        self.view.sel().add(sublime.Region(start, end))
        pos = self.view.viewport_position()
        self.view.show_at_center(sublime.Region(start, end))
        new_pos = self.view.viewport_position()
        if abs(new_pos[0] - pos[0]) <= 1.0 and abs(new_pos[1] - pos[1]) <= 1.0:
            self.view.set_viewport_position((new_pos[0], new_pos[1] + 1))
            self.view.set_viewport_position((new_pos[0], new_pos[1]))

    def restore(self):
        self.view.sel().clear()
        for region in self.start_regions:
            self.view.sel().add(region)


class SimpleMovementDuplicateLineCommand(SimpleMovementParseLineCommand):
    def run(self, edit, **kwargs):
        last_region = self.view.sel()[-1]
        self.cursor = self.view.rowcol(last_region.b)[1]
        # the row of the beginning of the line that contains the beginning of the last region
        self.first_line = self.view.rowcol(self.view.line(last_region.begin()).begin())[0]
        self.start_regions = list(self.view.sel())
        self.view.window().show_input_panel('Line(s):', '', self.duplicate_line, self.demo_line, None)

    def duplicate_line(self, lines):
        self.restore()
        if not len(lines):
            lines = "-1"

        regions = list(self.view.sel())

        # sort by region.end() DESC
        regions.sort(key=lambda region: region.end(), reverse=True)

        for region in regions:
            self.first_line = self.view.rowcol(self.view.line(region.begin()).begin())[0]

            try:
                if ',' in lines:
                    line_a, line_b = self.get_two_lines(lines)
                else:
                    line_a = self.get_line(lines)
                    line_b = line_a + 1
            except ValueError as e:
                sublime.status_message('Invalid entry')
                return

            # get content between lines line_a and line_b
            a = self.view.text_point(line_a, 0)
            b = self.view.text_point(line_b, 0)
            content = self.view.substr(sublime.Region(a, b))
            self.view.run_command('simple_movement_duplicate_line_dummy', {'region_a': region.a, 'region_b': region.b, 'content': content})


class SimpleMovementDuplicateLineDummyCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        region = kwargs.get('region')
        region_a = kwargs.get('region_a')
        region_b = kwargs.get('region_b')

        region = sublime.Region(region_a, region_b)
        content = kwargs.get('content')
        self.view.replace(edit, region, content)


class SimpleMovementGotoLineCommand(SimpleMovementParseLineCommand):
    def run(self, edit, **kwargs):
        last_region = self.view.sel()[-1]
        self.cursor = self.view.rowcol(last_region.b)[1]
        # the row of the beginning of the line that contains the beginning of the last region
        self.first_line = self.view.rowcol(self.view.line(last_region.begin()).begin())[0]
        self.start_regions = list(self.view.sel())
        self.view.window().show_input_panel('Line(s):', '', self.goto_line, self.demo_line, self.restore)


class SimpleMovementSelectBlockCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        for region in self.view.sel():
            self.run_each(edit, region, **kwargs)

    def run_each(self, edit, region):
        a = region.begin()
        b = region.end()

        row_a, col_a = self.view.rowcol(a)
        row_b, col_b = self.view.rowcol(b)
        if row_a == row_b:
            return

        if col_b < col_a:
            col_a, col_b = col_b, col_a

        self.view.sel().subtract(region)
        for row in range(row_a, row_b + 1):
            start = self.view.text_point(row, col_a)
            if self.view.rowcol(start)[0] > row:
                # skip if the line isn't as long as start
                continue

            end = self.view.text_point(row, col_b)
            while self.view.rowcol(end)[0] > row:
                # shorten if the line isn't as long as end
                end -= 1
            self.view.sel().add(sublime.Region(start, end))


class SimpleMovementSelectCharsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            self.run_each(edit, region)

    def run_each(self, edit, region):
        if len(region) == 0:
            return

        self.view.sel().subtract(region)
        for c in range(region.begin(), region.end()):
            r = sublime.Region(c, c+1)
            self.view.sel().add(r)


class SimpleMovementInsertCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        restore_translate_tabs_to_spaces = self.view.settings().get('translate_tabs_to_spaces')
        self.view.settings().set('translate_tabs_to_spaces', False)
        for region in self.view.sel():
            self.run_each(edit, region, **kwargs)
        self.view.settings().set('translate_tabs_to_spaces', restore_translate_tabs_to_spaces)

    def run_each(self, edit, region, insert):
        self.view.replace(edit, region, '')
        self.view.insert(edit, region.begin(), insert)
        self.view.sel().subtract(region)
        self.view.sel().add(sublime.Region(region.begin() + len(insert), region.begin() + len(insert)))
        self.view.show(region)


class SimpleMovementSnippetPickerCommand(sublime_plugin.TextCommand):
    def run(self, edit, choices):
        prompts = []
        snippets = []
        for prompt, insert in choices:
            prompts.append(prompt)
            snippets.append(insert)
        self.view.window().show_quick_panel(prompts, self.handler(snippets))

    def handler(self, snippets):
        def _handler(index):
            if index != -1:
                self.view.run_command('insert_snippet', {'contents': snippets[index]})
        return _handler


class SimpleMovementAlignCursorCommand(sublime_plugin.TextCommand):
    def run(self, edit, move="right"):
        if any(region for region in self.view.sel() if self.view.rowcol(region.a)[0] != self.view.rowcol(region.b)[0]):
            sublime.status_message('Selections that span multiple lines don\'t really make sense in simple_movement_align_cursor')
            return

        regions = self.view.sel()

        cursors = []
        first = True

        # find max right
        restore_translate_tabs_to_spaces = self.view.settings().get('translate_tabs_to_spaces')
        self.view.settings().set('translate_tabs_to_spaces', False)
        if move == "left":
            min_right = min(self.view.rowcol(region.begin())[1] for region in regions)

            for region in regions:
                spaces = self.view.rowcol(region.begin())[1] - min_right
                replace_region = sublime.Region(region.begin() - spaces, region.begin())
                if spaces and self.view.substr(replace_region) == ' ' * spaces:
                    self.view.replace(edit, replace_region, '')
                if spaces or not first:
                    cursors.append(sublime.Region(replace_region.begin(), replace_region.begin()))
                first = False
        elif move == "align":
            max_right = max(self.view.rowcol(region.begin())[1] for region in regions)

            for region in regions:
                spaces = max_right - self.view.rowcol(region.begin())[1]
                if spaces:
                    begin = self.view.line(region).begin()
                    self.view.insert(edit, begin, ' ' * spaces)
                if spaces or not first:
                    cursors.append(sublime.Region(region.begin() + spaces, region.begin() + spaces))
                first = False
        else:
            max_right = max(self.view.rowcol(region.begin())[1] for region in regions)

            for region in regions:
                spaces = max_right - self.view.rowcol(region.begin())[1]
                if spaces:
                    self.view.insert(edit, region.begin(), ' ' * spaces)
                if spaces or not first:
                    cursors.append(sublime.Region(region.begin() + spaces, region.begin() + spaces))
                first = False

        if cursors:
            self.view.sel().clear()
            for cursor in cursors:
                self.view.sel().add(cursor)
        self.view.settings().set('translate_tabs_to_spaces', restore_translate_tabs_to_spaces)


class SimpleMovementMoveViewportCommand(sublime_plugin.TextCommand):
    def run(self, edit, direction, factor=1):
        position = self.view.viewport_position()
        delta = self.view.line_height() * factor

        if direction == 'up':
            new_position = position[0], position[1] - delta
        elif direction == 'down':
            new_position = position[0], position[1] + delta
        elif direction == 'center':
            regions = self.view.sel()
            if regions:
                self.view.show_at_center(regions[0])
                new_position = None
            else:
                new_position = position

        if new_position:
            self.view.set_viewport_position(new_position)


class SimpleMovementPageCommand(sublime_plugin.TextCommand):
    def run(self, edit, direction):
        position = self.view.viewport_position()
        height = self.view.viewport_extent()[1]
        if direction == "up":
            height *= -1

        self.view.set_viewport_position((position[0], position[1] + height), True)


class SimpleMovementNlCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        regions = list(self.view.sel())

        # sort by region.end() DESC
        def get_end(region):
            return region.end()
        regions.sort(key=get_end, reverse=True)

        for region in regions:
            self.run_each(edit, region, **kwargs)

    def run_each(self, edit, region, insert_nl=True, hard_nl=False,
                 with_terminator=False, unindent=False, with_comment=False):
        self.view.sel().subtract(region)
        nl = "\n" if insert_nl else ""

        if self.view.settings().get('translate_tabs_to_spaces'):
            tab = ' ' * self.view.settings().get('tab_size')
        else:
            tab = "\t"

        original_region = sublime.Region(region.a, region.b)
        row, col = self.view.rowcol(region.end())
        line = self.view.line(region.end())
        beginning_of_line = line.begin()
        end_of_line = line.end()
        new_cursor_offset = 0

        if with_comment:
            # test validity of "with_comment" - if the line does not *start*
            # with a comment (after whitespace), forget it.
            after_whitespace = self.view.find(r'^\s*', beginning_of_line).end()
            with_comment = bool(self.view.score_selector(after_whitespace, 'comment'))

        if with_terminator:
            # each language has special rules.  tedious, but feature rich!
            if self.view.score_selector(region.b, 'source.python'):
                keyword = self.view.find(r'^[ \t]*(if|elif|else|while|for|do|try|except|finally|def|class|with)', beginning_of_line)
                if keyword and keyword.contains(beginning_of_line):
                    if self.view.substr(end_of_line - 1) != ':':
                        nl = ':' + nl
                    if insert_nl:
                        nl += tab
            else:
                for lang in semicolon_langs:
                    if self.view.score_selector(region.b, lang):
                        if self.view.substr(end_of_line - 1) != ';':
                            nl = ";" + nl
                        break

        if not hard_nl:
            # move region to end of line first
            region = sublime.Region(end_of_line, end_of_line)
            if insert_nl:
                # and add indent
                indent_region = self.view.find('^[ \t]*', beginning_of_line)
                indent = self.view.substr(indent_region)
                nl += indent

        if with_comment:
            comment_range = self.view.find(r'\/?(#+|[*]|//+|--+|[\']+)\|? *', beginning_of_line)
            if comment_range:
                if comment_range.end() == end_of_line and unindent:
                    # remove comment!
                    space = self.view.find(r'^\s*', beginning_of_line)
                    spaces = self.view.substr(space)
                    self.view.replace(edit, line, spaces)
                    new_cursor = sublime.Region(line.begin() + len(spaces))
                    self.view.sel().add(new_cursor)
                    return

                if not unindent:
                    comment = self.view.substr(comment_range)
                    if re.match(r'\/\*', comment):
                        comment = ' ' + comment[1:] + ' '
                    nl += comment

            if original_region.end() != end_of_line:
                remove = sublime.Region(original_region.end(), end_of_line)
                copy = self.view.substr(remove)
                self.view.replace(edit, remove, "")
                region = sublime.Region(region.a - len(copy), region.b - len(copy))
                copy = copy.strip()

                nl += copy
                new_cursor_offset -= len(copy)
        # remove "tab" from next line
        elif unindent and nl[-len(tab):] == tab:
            nl = nl[:-len(tab)]

        new_cursor = region.begin() + len(nl) + new_cursor_offset
        new_cursor = sublime.Region(new_cursor, new_cursor)
        self.view.replace(edit, region, nl)
        self.view.show(region)
        self.view.sel().add(new_cursor)


class SimpleMovementSelectNextCommand(sublime_plugin.TextCommand):
    def run(self, edit, select_all=False, remove_last=False):
        regions = list(self.view.sel())

        # sort by region.end() DESC
        def get_end(region):
            return region.end()
        regions.sort(key=get_end, reverse=True)

        if len(regions) == 1 and len(regions[0]) == 0:
            self.view.run_command('expand_selection', {'to': 'word'})
        else:
            previous_region = None
            previous_match = None
            for region in regions:
                match = self.view.substr(region)
                self.select_next(region, match, previous_region, previous_match, select_all=select_all)
                previous_region = region
                previous_match = match
            if remove_last:
                self.view.sel().subtract(regions[0])
            self.select_next(region, match, previous_region, previous_match, select_all=select_all)

    def select_next(self, region, match, previous_region, previous_match, select_all):
        if match == previous_match:
            return

        if select_all:
            found_all = self.view.find_all(match, sublime.LITERAL)

            for found in found_all:
                self.view.sel().add(found)
        else:
            found = self.view.find(match, region.end(), sublime.LITERAL)

            if found:
                self.view.sel().add(found)
                self.view.show(found)
            else:
                sublime.status_message('Cound not find "{0}"'.format(match))


class SimpleMovementOneSelectionCommand(sublime_plugin.TextCommand):
    def __init__(self, view):
        view.previous_regions = []
        super(SimpleMovementOneSelectionCommand, self).__init__(view)

    def run(self, edit, index, select=True):
        regions = [region for region in self.view.sel()]

        if len(regions) == 1:
            regions = self.view.previous_regions
        else:
            self.view.previous_regions = regions

        if index == 'evens':
            keep = False
            for region in regions:
                if not keep:
                    self.view.sel().subtract(region)
                keep = not keep
        elif index == 'odds':
            keep = True
            for region in regions:
                if not keep:
                    self.view.sel().subtract(region)
                keep = not keep
        else:
            try:
                if select:
                    regions = [regions[index]]
                else:
                    regions.pop(index)

                self.view.sel().clear()
                self.view.sel().add_all(regions)

                if select or index == 0:
                    self.view.show(regions[0])
                elif index == -1:
                    self.view.show(regions[-1])
            except IndexError:
                pass


class SimpleMovementRemoveDups(sublime_plugin.TextCommand):
    def run(self, edit):
        # store the first position in each line
        line_starts = []
        for region in self.view.sel():
            for line in self.view.split_by_newlines(region):
                line_starts.append(self.view.line(line.begin()).begin())
        keep = []
        delete_regions = []
        for point in line_starts:
            line = self.view.full_line(point)
            text = self.view.substr(line)
            if text not in keep:
                keep.append(text)
            else:
                delete_regions.append(line)
        if delete_regions:
            self.view.sel().clear()
            for region in delete_regions:
                self.view.sel().add(region)
        else:
            sublime.status_message('No duplicate lines found')
