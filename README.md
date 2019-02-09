# zig-gdb

Commands and pretty printers for debugging the Zig compiler (stage 1).

## Installing

Add the following to your `.gdbinit` or any script sourced by it:
```gdb
python
import sys
sys.path.append('<path to this repo>')
end
```

Alternatively, you could copy/symlink the `zig-gdb` directory somewhere
that's already on GDB's Python path.

Next, configure GDB to automatically load the package and install its
printers. If you haven't already, configure your auto-load path:
```gdb
add-auto-load-safe-path <path to auto-load dir>
add-auto-load-scripts-directory <path to auto-load dir>
# Uncomment if you have trouble getting auto-load working
#set debug auto-load on
```

Finally, create the following auto-load script:
```python
import zig
zig.register_printers()
```

The script must be named `zig-gdb.py` and placed in a precise location,
namely `<auto-load dir>/<zig binary dir>/zig-gdb.py`. E.g., if the `zig`
executable were at `/usr/bin/zig` and `/usr/share/gdb/auto-load` is on
your auto-load, create `/usr/share/gdb/auto-load/usr/bin/zig-gdb.py`.
