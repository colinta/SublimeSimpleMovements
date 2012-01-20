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
    ]


class SimpleMovementBolCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        e = self.view.begin_edit('simple_movement')
        regions = [region for region in self.view.sel()]
        for region in regions:
            self.run_each(edit, region, **kwargs)
        self.view.end_edit(e)

    def run_each(self, edit, region, extend=False):
        row, col = self.view.rowcol(region.b)
        new_point = self.view.text_point(row, 0)
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
        self.view.replace(edit, region, insert)
        self.view.show(region)


class SimpleMovementAlignCursorCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
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
        max_right = max(self.view.rowcol(region.begin())[1] for region in regions)

        restore_translate_tabs_to_spaces = self.view.settings().get('translate_tabs_to_spaces')
        self.view.settings().set('translate_tabs_to_spaces', False)
        for region in regions:
            spaces = max_right - self.view.rowcol(region.begin())[1]
            if spaces:
                self.view.insert(edit, region.begin(), ' ' * spaces)

        self.view.end_edit(e)
        self.view.settings().set('translate_tabs_to_spaces', restore_translate_tabs_to_spaces)


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

        self.view.sel().subtract(region)
        self.view.replace(edit, region, nl)
        self.view.show(region)
        self.view.sel().add(sublime.Region(region.begin() + len(nl), region.begin() + len(nl)))
