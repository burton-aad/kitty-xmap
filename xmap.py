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


try:
    from kittens.tui.handler import result_handler
except ImportError:
    # for kitty < 0.17.0
    def result_handler(no_ui):
        def wrapper(func):
            func.no_ui = no_ui
            return func
        return wrapper


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


@result_handler(no_ui=True)
def handle_result(args: List[str], answer: str, target_window_id: int, boss: Boss) -> None:
    # get the kitty window into which to paste answer
    w = boss.window_id_map.get(target_window_id)
    if w is None:
        return

    _, shortcut, cmd, *cmd_args = args

    if not w.screen.is_main_linebuf():
        send_to_window(w, shortcut)
        return

    if cmd == "combine":
        # combine need more stuff
        if version < (0, 24):
            if version < (0, 21):
                from kitty.config import combine_parse
            else:
                from kitty.options.utils import combine_parse
            _, args = combine_parse(cmd, " ".join(cmd_args))
            return boss.combine(*args)
        else:
            return boss.combine("{} {}".format(cmd, " ".join(cmd_args)))

    # Send the command to the window in normal screen.
    for o in [boss, w, w.tabref()]:
        command = getattr(o, cmd, None)
        if command:
            break
    else:
        w.write_to_child("Invalid command '{}'".format(cmd))
        return

    try:
        if len(cmd_args) > 0:
            command(*cmd_args)
        else:
            command()
    except Exception as e:
        w.write_to_child("Error in command {} : {}".format(cmd, e))

