import ldmud, sys

from . import ob
from . import input

interactives = {}

def clean_ob(ob):
    """Object <ob> was destructed, remove from our list."""
    interactives.pop(ob, None)

    stale = []
    for inter_ob, data in interactives.items():
        if data.control_ob == ob:
            stale.append(inter_ob)

    for inter_ob in stale:
        del interactives[inter_ob]


def efun_make_interactive(inter_ob: ldmud.Object, control_ob: (ldmud.Object, str), ip_name: str, ip_number: str, ip_port: int, mud_port: int) -> None:
    """
    SYNOPSIS
            void make_interactive(object ob, object|string control_ob, string ip_name, string ip_number, int ip_port, int mud_port)

    DESCRIPTION
            Makes the object <ob> an interactive object.

            <control_ob> is used to send and receive messages for <ob>.

            <ip_name>, <ip_number> and <ip_port> are the simulated host name,
            host address and port number of <ob>, <mud_port> is the simulated
            mud port used. This information is of no relevance, it is just
            returned by interactive_info(E).

    SEE ALSO
            send_interactive_input(E)
    """
    if ldmud.efuns.interactive(inter_ob):
        raise ValueError("Object is already interactive.")
    if inter_ob in interactives:
        raise ValueError("Object was already made interactive.")

    interactives[inter_ob] = ob.Interactive(control_ob, ip_name, ip_number, ip_port, mud_port)
    input.show_prompt(inter_ob)

def efun_users() -> ldmud.Array:
    return ldmud.efuns.users() + ldmud.Array(interactives.keys())

def on_reload_delayed():
    ldmud.unregister_hook(ldmud.ON_HEARTBEAT, on_reload_delayed)

    newmodule = sys.modules.get(__name__, None)
    if newmodule:
        newmodule.interactives.update(interactives)

def on_reload():
    ldmud.register_hook(ldmud.ON_HEARTBEAT, on_reload_delayed)
