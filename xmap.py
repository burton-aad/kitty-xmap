"""Simple kitten to map shortcut only in normal screen.

kitten xmap.py <shortcut> <normal command>

kitty will run the command (as set with the map shortcut) while application would
receive the shortcut key command directly.
Because of kitty internal parsing, send_text command need double '\' to escape properly.

Inspired by the smart_scroll kitten.
"""

from typing import List, Tuple
from kitty.boss import Boss
from kitty.window import Window
from kitty.constants import version


def main(args: List[str]) -> str:
    pass


def send_to_window(w: Window, shortcut: str) -> None:
    """Simulate press/release of a shortcut into the window"""
    import kitty.key_encoding as ke
    mods, key = ke.parse_shortcut(shortcut)
    if "kitty_mod" in shortcut:
        import kitty.fast_data_types as fdtypes
        mods |= fdtypes.get_options().kitty_mod
    shift, alt, ctrl, super, hyper, meta, caps_lock, num_lock = (
        bool(mods & bit) for bit in (
           ke.SHIFT, ke.ALT, ke.CTRL, ke.SUPER,
           ke.HYPER, ke.META, ke.CAPS_LOCK, ke.NUM_LOCK))
    for action in [ke.EventType.PRESS, ke.EventType.RELEASE]:
        key_event = ke.KeyEvent(
            type=action, mods=mods, key=key,
            shift=shift, alt=alt, ctrl=ctrl, super=super,
            hyper=hyper, meta=meta, caps_lock=caps_lock, num_lock=num_lock)
        window_system_event = key_event.as_window_system_event()
        sequence = w.encoded_key(window_system_event)
        w.write_to_child(sequence)


from kittens.tui.handler import result_handler
@result_handler(no_ui=True)
def handle_result(args: List[str], answer: str, target_window_id: int, boss: Boss) -> None:
    # get the kitty window into which to paste answer
    w = boss.window_id_map.get(target_window_id)
    if w is None:
        return

    if not w.screen.is_main_linebuf():
        send_to_window(w, args[1])
        return

    if args[2] == "combine":
        # combine need more stuff
        if version < (0, 24):
            from kitty.options.utils import combine_parse
            _, args = combine_parse(args[2], " ".join(args[3:]))
            return boss.combine(*args)
        else:
            return boss.combine(" ".join(args[2:]))

    # Send the command to the window in normal screen.
    for o in [boss, w, w.tabref()]:
        command = getattr(o, args[2], None)
        if command:
            break
    else:
        w.write_to_child("Invalid command '{}'".format(args[2]))
        return

    try:
        if len(args) > 3:
            command(*args[3:])
        else:
            command()
    except Exception as e:
        w.write_to_child("Error in command {} : {}".format(args[1], e))

