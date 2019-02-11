# zig-gdb

Commands and pretty printers for debugging the Zig compiler (stage 1).

## Installing

Clone this repository somewhere that's on GDB's Python path; name it
`zig`. For example, if `~/.config/gdb/python` is on your path, do
```
git clone https://github.com/matthew-mcallister/zig-gdb.git ~/.config/gdb/python/zig
```

If you haven't configured your path yet, try adding this to your
`.gdbinit`:
```gdb
python
import os
import sys
sys.path.append(os.expanduser('~/.config/gdb/python'))
end
```

Next, configure GDB to automatically load the package and install its
printers. If you haven't already, configure your auto-load path:
```gdb
add-auto-load-safe-path "/home/<username>/.config/gdb/auto-load"
add-auto-load-scripts-directory "/home/<username>/.config/gdb/auto-load"
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
executable were at `/usr/bin/zig` and you followed the previous
examples, name it `~/.config/gdb/auto-load/usr/bin/zig-gdb.py`.
