# Xmap for kitty

[kitty](https://sw.kovidgoyal.net/kitty/) is a fast, feature-rich, GPU based terminal emulator.

This kitten let you define shortcut for kiity which are pass through when use with a program running in kitty.

It is equivalent to set a shortcut with the parameter normal only. See [send-text](https://sw.kovidgoyal.net/kitty/conf/#shortcut-kitty.Send-arbitrary-text-on-key-presses) for more detail.

## Requirements

kitty 0.15.0 or higher

## Installation

Copy or symlink xmap.py into the kitty configuration folder (`~/.config/kitty`) and add shortcut in your `kitty.conf`.

## Configuration

The first argument is the shortcut send to the application when one is used. The rest is the normal command as if it is used by the `map` command.

### Examples

Scrolling
```
map shift+page_up   kitten xmap.py shift+page_up   scroll_page_up
map shift+page_down kitten xmap.py shift+page_down scroll_page_down
```

Combine command (beware to double escape)
```
map ctrl+l kitten xmap.py ctrl+l combine : clear_terminal scroll active : send_text normal,application \\x0c
```
