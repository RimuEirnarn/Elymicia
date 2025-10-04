# Elymicia

A simple CLI File Manager made with curses.

## Features

It's file managers. What do you expect?

Also, it's currently only able to move around directories. Please wait until the app is fully implemented.

## Install

To install, follow this guide:

```sh
git clone https://RimuEirnarn/Elymicia
cd Elymicia
python -m venv .venv
pip install -r ./requirements.txt
python main.py
```

To quit, type `:q`. To navigate, use arrow keys.

## Roadmap

- [x] Moveable File UI
- [x] Tabs for multiple File UIs
- [x] Commands (Activate via `:`), see [this part](#commands)
- [ ] File Viewer
- [ ] File opener
- [ ] Copy
- [ ] Move
- [ ] Delete
- [ ] Archive
- [ ] Extract
- [ ] Find
+ [ ] Sort

### Commands

Currently, there's `:q`, `:closetab` / `:ct`, `:newtab` / `:nt`, `:pwd`, `:cd`.
