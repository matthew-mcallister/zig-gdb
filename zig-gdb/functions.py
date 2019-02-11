import re

import gdb

from zig import util


class SrcMatch(gdb.Function):
    """A command which matches the source file of an AST node or IR
    instruction against a regex."""

    def __init__(self):
        super(SrcMatch, self).__init__('_zig_src_match')

    def invoke(self, val, pat):
        try:
            node = val['source_node']
        except gdb.error:
            node = val

        # It's really dumb that GDB adds quotes
        pat = str(pat)
        assert pat[0] == '"' and pat[0] == pat[-1]
        pat = re.compile(pat[1:-1])

        path = util.buf_to_string(node['owner']['path'])
        return bool(pat.search(path))


def register_functions():
    SrcMatch()
