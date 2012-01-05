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
            self.view.sel().add(sublime.Region(region.a, new_point))
        else:
            self.view.sel().add(sublime.Region(new_point, new_point))


class SimpleMovementNlCommand(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        e = self.view.begin_edit('simple_movement')
        regions = [region for region in self.view.sel()]
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
                keyword = self.view.find('^[ \t]*(if|elif|else|while|for|do|try|except|finally|def|class)', beginning_of_line)
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

        self.view.replace(edit, region, nl)
        self.view.show(region)
        self.view.sel().add(sublime.Region(region.end() + len(nl), region.end() + len(nl)))
