# Calculate Activity

Calculate is the Sugar calculator activity. Students can type expressions in normal math notation, get instant results, and plot equations.

## Features

- Arithmetic with `+ - * / ^`
- Built-in functions like `sin`, `cos`, `log`, and `sqrt`
- Constants such as `pi` and `e`
- Equation plotting and calculation history

## Use in Sugar

1. Open **Calculate** from the activity list.
2. Enter an expression (for example `2+2*3`).
3. Press **Return** to evaluate.
4. Use toolbar buttons to insert operators and functions.

## Dependencies (Debian/Ubuntu package)

The distro package `sugar-calculate-activity` depends on:
`python3`, `python3-gi`, `python3-dbus`, `python3-sugar3`,
`gir1.2-glib-2.0`, `gir1.2-gtk-3.0`, `gir1.2-pango-1.0`,
`gir1.2-rsvg-2.0`, and `gir1.2-telepathyglib-0.12`.

Optional for extended plotting support: `python3-matplotlib`.

## Run from source

```bash
git clone https://github.com/sugarlabs/calculate-activity
cd calculate-activity
python3 calculate.py
```

License: GNU GPL v3. See [COPYING](COPYING).
