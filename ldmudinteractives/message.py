import ldmud
from . import control
from . import util

call_catch_tell = None

def receive_message(inter_ob, data, txt):
    global call_catch_tell

    if call_catch_tell is None:
        symbol_ob = ldmud.Symbol('ob')
        symbol_txt = ldmud.Symbol('txt')
        call_catch_tell = ldmud.efuns.unbound_lambda(ldmud.Array((symbol_ob, symbol_txt,)), ldmud.Array((ldmud.Closure(ldmud.get_master(), "efun::call_resolved"), ldmud.Array((ldmud.Closure(ldmud.get_master(), '&'), ldmud.Symbol('result'))), symbol_ob, "catch_tell", symbol_txt)))

    current_ob = ldmud.efuns.this_object()
    if current_ob == inter_ob or not ldmud.efuns.bind_lambda(call_catch_tell, current_ob)(inter_ob, txt):
        data.call_control_ob("receive_message", inter_ob, txt)

    if data.snooper is not None:
        try:
            ldmud.efuns.tell_object(data.snooper, "%" + txt)
        except:
            pass

def efun_printf(fmt: str, *args) -> None:
    inter_ob = ldmud.efuns.this_player()
    data = control.interactives.get(inter_ob, None)

    if data is None:
        ldmud.efuns.printf(fmt, *args)
    else:
        receive_message(inter_ob, data, ldmud.efuns.sprintf(fmt, *args))

def efun_write(msg) -> None:
    inter_ob = ldmud.efuns.this_player()
    data = control.interactives.get(inter_ob, None)

    if data is None:
        ldmud.efuns.write(msg)
    else:
        if isinstance(msg, str):
            receive_message(inter_ob, data, msg)
        elif isinstance(msg, bytes):
            receive_message(inter_ob, data, "<BYTES>")
        elif isinstance(msg, ldmud.Object):
            receive_message(inter_ob, data, "OBJ(%s)" % (msg.name,))
        elif isinstance(msg, int):
            receive_message(inter_ob, data, "%d" % (msg,))
        elif isinstance(msg, float):
            receive_message(inter_ob, data, "%g" % (msg,))
        elif isinstance(msg, ldmud.Array):
            receive_message(inter_ob, data, "<ARRAY>")
        elif isinstance(msg, ldmud.Mapping):
            receive_message(inter_ob, data, "<MAPPING>")
        elif isinstance(msg, ldmud.Closure):
            receive_message(inter_ob, data, "<CLOSURE>")
        else:
            receive_message(inter_ob, data, "<OTHER>")

def efun_say(msg: (str, ldmud.Array, ldmud.Object, ldmud.Mapping, ldmud.Struct), excludes: (ldmud.Object, ldmud.Array,) = None) -> None:
    def base_efun():
        if excludes is None:
            ldmud.efuns.say(msg)
        else:
            ldmud.efuns.say(msg, excludes)

    if not isinstance(msg, str):
        return base_efun()

    # Determine the recipients
    current_ob = ldmud.efuns.this_object()
    if ldmud.efuns.living(current_ob):
        initiator = current_ob
    else:
        initiator = ldmud.efuns.this_player()
        if not initiator:
            initiator = current_ob

    recipients = set()
    env = ldmud.efuns.environment(initiator)
    if env:
        recipients.add(env)
        recipients.update(ldmud.efuns.all_inventory(env))
    recipients.update(ldmud.efuns.all_inventory(initiator))

    if isinstance(excludes, ldmud.Object):
        recipients.discard(excludes)
        recipients.discard(initiator)
    elif isinstance(excludes, ldmud.Array):
        recipients.difference_update(excludes)
    else:
        recipients.discard(initiator)

    # Check if there are any of us in there
    inter_obs = recipients.intersection(control.interactives)
    if not len(inter_obs):
        return base_efun()

    # Send to the remaining...
    if len(inter_obs) < len(recipients):
        if isinstance(excludes, ldmud.Object):
            excludes = ldmud.Array((excludes, initiator, *inter_obs))
        elif isinstance(excludes, ldmud.Array):
            excludes += ldmud.Array(inter_obs)
        else:
            excludes = ldmud.Array((initiator, *inter_obs))
        ldmud.efuns.say(msg, excludes)

    # And now send to all our interactives
    for inter_ob in inter_obs:
        data = control.interactives.get(inter_ob, None)
        if data:
            receive_message(inter_ob, data, msg)

def efun_tell_room(room: (ldmud.Object, str), msg: (str, ldmud.Array, ldmud.Object, ldmud.Mapping, ldmud.Struct), excludes: (ldmud.Object, ldmud.Array,) = None) -> None:
    def base_efun():
        if excludes is None:
            ldmud.efuns.tell_room(room, msg)
        else:
            ldmud.efuns.tell_room(room, msg, excludes)

    if not isinstance(msg, str):
        return base_efun()

    # Determine the recipients
    if isinstance(room, str):
        env = ldmud.efuns.find_object(room)
        if not env:
            # If the room does not exist, there isn't one of ours in it.
            return base_efun()
    else:
        env = room

    recipients = set()
    recipients.add(env)
    recipients.update(ldmud.efuns.all_inventory(env))

    if isinstance(excludes, ldmud.Object):
        recipients.discard(excludes)
    elif isinstance(excludes, ldmud.Array):
        recipients.difference_update(excludes)

    # Check if there are any of us in there
    inter_obs = recipients.intersection(control.interactives)
    if not len(inter_obs):
        return base_efun()

    # Send to the remaining...
    if len(inter_obs) < len(recipients):
        if isinstance(excludes, ldmud.Object):
            excludes = ldmud.Array((excludes, *inter_obs))
        elif isinstance(excludes, ldmud.Array):
            excludes += ldmud.Array(inter_obs)
        else:
            excludes = ldmud.Array(inter_obs)
        ldmud.efuns.tell_room(room, msg, excludes)

    # And now send to all our interactives
    for inter_ob in inter_obs:
        data = control.interactives.get(inter_ob, None)
        if data:
            receive_message(inter_ob, data, msg)

def efun_tell_object(inter_ob: (ldmud.Object, str), msg: (str, ldmud.Array, ldmud.Object, ldmud.Mapping, ldmud.Struct)) -> None:
    if not isinstance(msg, str):
        return ldmud.efuns.tell_object(inter_ob, msg)

    data = control.interactives.get(inter_ob, None)

    if data is None:
        ldmud.efuns.tell_object(inter_ob, msg)
    else:
        receive_message(inter_ob, data, msg)

def efun_binary_message(msg: (ldmud.Array, bytes), flags: int = 0) -> int:
    inter_ob = ldmud.efuns.this_object()
    data = control.interactives.get(inter_ob, None)

    if data is None:
        return ldmud.efuns.binary_message(msg)
    else:
        if isinstance(msg, ldmud.Array):
            buf = bytes(msg)
        else:
            buf = msg
        return data.call_control_ob("receive_binary", inter_ob, buf)

snoopers = {}
def efun_snoop(snooper: ldmud.Object, snoopee: ldmud.Object = 0) -> int:
    data = control.interactives.get(snoopee, None)
    if data is None:
        if snoopee == 0:
            result = ldmud.efuns.snoop(snooper)
        else:
            result = ldmud.efuns.snoop(snooper, snoopee)
        if (result > 0 or snoopee == 0) and snooper in snoopers:
            snoopers.pop(snooper)[1].snooper = None
            return 1
        return result

    master = ldmud.get_master()

    result = util.lfun_call(master, "valid_snoop", snooper, snoopee)
    if not isinstance(result, int) or result == 0:
        return 0

    if snooper in snoopers:
        snoopers[snooper][1].snooper = None
    snoopers[snooper] = (snoopee, data)
    data.snooper = snooper

    ldmud.efuns.snoop(snooper)

    return 1
