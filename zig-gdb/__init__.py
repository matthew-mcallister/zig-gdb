def register():
    from zig.functions import register_functions
    register_functions()
    from zig.printers import register_printers
    register_printers()
