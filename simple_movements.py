import time
import sublime
import sublime_plugin


semicolon_langs = [
    'source.php',
    'source.js',
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
        e = self.view.begin_edit('simple_movement')
        regions = [region for region in self.view.sel()]
        for region in regions:
            self.run_each(edit, region, **kwargs)
        self.view.end_edit(e)

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
        e = self.view.begin_edit('simple_movement')
        regions = [region for region in self.view.sel()]
        for region in regions:
            self.run_each(edit, region, **kwargs)
        self.view.end_edit(e)

    def run_each(self, edit, region, extend=False):
        line = self.view.line(region.b)
        new_point = line.end()
        if new_point == region.b:
            # already at EOL, skip to first character
            new_point = line.begin()
            while self.view.substr(new_point) in [" ", "\t"]:
                new_point += 1
        self.view.sel().subtract(region)
        if extend:
            region = sublime.Region(region.a, new_point)
        else:
            region = sublime.Region(new_point, new_point)
        self.view.sel().add(region)
        self.view.show(region)


class SimpleMovementParseLineCommand(sublime_plugin.TextCommand):
    def get_line(self, line):
        if line[0] == '+':
            return self.first_line + int(line[1:])
        elif line[0] == '-':
            return self.first_line - int(line[1:])
        elif line == '0':
            return self.first_line
        else:
            return int(line) - 1

    def get_two_lines(self, text, c):
        # supported multiline syntax:
        # a,b  =>  lines a to b
        # a,  => just line a
        # ,b  => current line to line b
        # ,  => just current line
        line_a, line_b = text.split(c)
        if not line_a:
            # ,b
            line_a = self.first_line
        else:
            line_a = self.get_line(line_a)

        if line_b:
            line_b = self.get_line(line_b)
        else:
            line_b = line_a

        line_b += 1

        return line_a, line_b


class SimpleMovementDuplicateLineCommand(SimpleMovementParseLineCommand):
    def run(self, edit, **kwargs):
        last_region = self.view.sel()[-1]
        self.cursor = self.view.rowcol(last_region.b)[1]
        # the row of the beginning of the line that contains the beginning of the last region
        self.first_line = self.view.rowcol(self.view.line(last_region.begin()).begin())[0]
        self.view.window().show_input_panel('Line(s):', '', self.duplicate_line, None, None)

    def duplicate_line(self, lines):
        if not len(lines):
            lines = "-1"

        regions = [region for region in self.view.sel()]

        # sort by region.end() DESC
        def compare(region_a, region_b):
            return cmp(region_b.end(), region_a.end())
        regions.sort(compare)

        e = self.view.begin_edit('simple_movement')
        for region in regions:
            self.first_line = self.view.rowcol(self.view.line(region.begin()).begin())[0]

            try:
                if ',' in lines:
                    line_a, line_b = self.get_two_lines(lines, ',')
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

            self.view.replace(e, region, content)
        self.view.end_edit(e)


class SimpleMovementGotoLineCommand(SimpleMovementParseLineCommand):
    def run(self, edit, **kwargs):
        last_region = self.view.sel()[-1]
        self.cursor = self.view.rowcol(last_region.b)[1]
        # the row of the beginning of the line that contains the beginning of the last region
        self.first_line = self.view.rowcol(self.view.line(last_region.begin()).begin())[0]
        self.start_regions = [region for region in self.view.sel()]
        self.view.window().show_input_panel('Line(s):', '', self.goto_line, self.demo_line, self.restore)

    def demo_line(self, lines):
        self.started = time.time()

        def okay_go():
            if time.time() - self.started > .270:
                self.goto_line(lines)
        sublime.set_timeout(okay_go, 300)

    def goto_line(self, lines):
        if not len(lines):
            self.restore()
            return

        try:
            if ',' in lines:
                line_a, line_b = self.get_two_lines(lines, ',')
            else:
                line_a = line_b = self.get_line(lines)
        except ValueError:
            self.restore()
            return

        if line_b == line_a:
            start = self.view.text_point(line_a, self.cursor)
            too_far = self.view.text_point(line_a + 1, 0)
            if start >= too_far:
                start = too_far - 1
            end = start
        else:
            start = self.view.text_point(line_a, 0)
            end = self.view.text_point(line_b, 0)

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


class SimpleMovementSelectBlockCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        e = self.view.begin_edit('simple_movement')
        regions = [region for region in self.view.sel()]
        for region in regions:
            self.run_each(edit, region, **kwargs)
        self.view.end_edit(e)

    def run_each(self, edit, region, extend=False):
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


class SimpleMovementInsertCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        e = self.view.begin_edit('simple_movement')
        regions = [region for region in self.view.sel()]

        # sort by region.end() DESC
        def compare(region_a, region_b):
            return cmp(region_b.end(), region_a.end())
        regions.sort(compare)

        restore_translate_tabs_to_spaces = self.view.settings().get('translate_tabs_to_spaces')
        self.view.settings().set('translate_tabs_to_spaces', False)
        for region in regions:
            self.run_each(edit, region, **kwargs)
        self.view.end_edit(e)
        self.view.settings().set('translate_tabs_to_spaces', restore_translate_tabs_to_spaces)

    def run_each(self, edit, region, insert):
        self.view.replace(edit, region, '')
        self.view.insert(edit, region.begin(), insert)
        self.view.sel().subtract(region)
        self.view.sel().add(sublime.Region(region.begin() + len(insert), region.begin() + len(insert)))
        self.view.show(region)


class SimpleMovementAlignCursorCommand(sublime_plugin.TextCommand):
    def run(self, edit, move="right"):
        if any(region for region in self.view.sel() if self.view.rowcol(region.a)[0] != self.view.rowcol(region.b)[0]):
            sublime.status_message('Selections that span multiple lines don\'t really make sense in simple_movement_align_cursor')
            return

        e = self.view.begin_edit('simple_movement')
        regions = [region for region in self.view.sel()]

        # sort by region.end() DESC
        def compare(region_a, region_b):
            return cmp(region_b.end(), region_a.end())
        regions.sort(compare)

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
        else:
            max_right = max(self.view.rowcol(region.begin())[1] for region in regions)

            for region in regions:
                spaces = max_right - self.view.rowcol(region.begin())[1]
                if spaces:
                    self.view.insert(edit, region.begin(), ' ' * spaces)

        self.view.settings().set('translate_tabs_to_spaces', restore_translate_tabs_to_spaces)
        self.view.end_edit(e)


class SimpleMovementNlCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        e = self.view.begin_edit('simple_movement')
        regions = [region for region in self.view.sel()]

        # sort by region.end() DESC
        def compare(region_a, region_b):
            return cmp(region_b.end(), region_a.end())
        regions.sort(compare)

        for region in regions:
            self.run_each(edit, region, **kwargs)
        self.view.end_edit(e)

    def run_each(self, edit, region, insert_nl=True, hard_nl=False, with_terminator=False, unindent=False):
        self.view.sel().subtract(region)
        nl = "\n" if insert_nl else ""

        if self.view.settings().get('translate_tabs_to_spaces'):
            tab = ' ' * self.view.settings().get('tab_size')
        else:
            tab = "\t"

        row, col = self.view.rowcol(region.end())
        beginning_of_line = self.view.text_point(row, 0)
        end_of_line = self.view.find("$", region.end()).end()

        if with_terminator:
            # each language has special rules.  tedious, but feature rich!
            if self.view.score_selector(region.b, 'source.python'):
                keyword = self.view.find('^[ \t]*(if|elif|else|while|for|do|try|except|finally|def|class|with)', beginning_of_line)
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

        # remove "tab" from next line
        if unindent and nl[-len(tab):] == tab:
            nl = nl[:-len(tab)]

        new_cursor = sublime.Region(region.begin() + len(nl), region.begin() + len(nl))
        self.view.replace(edit, region, nl)
        self.view.show(region)
        self.view.sel().add(new_cursor)
