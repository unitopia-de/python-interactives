import ldmud
from . import control
from . import util

IC_MAX_WRITE_BUFFER_SIZE        =  0
IC_SOCKET_BUFFER_SIZE           =  1
IC_COMBINE_CHARSET_AS_STRING    =  2
IC_COMBINE_CHARSET_AS_ARRAY     =  3
IC_CONNECTION_CHARSET_AS_STRING =  4
IC_CONNECTION_CHARSET_AS_ARRAY  =  5
IC_QUOTE_IAC                    =  6
IC_TELNET_ENABLED               =  7
IC_MCCP                         =  8
IC_PROMPT                       =  9
IC_MAX_COMMANDS                 = 10
IC_MODIFY_COMMAND               = 11
IC_ENCODING                     = 12

II_IP_NAME                      =  -1
II_IP_NUMBER                    =  -2
II_IP_PORT                      =  -3
II_IP_ADDRESS                   =  -4
II_MUD_PORT                     =  -5
II_MCCP_STATS                   = -10
II_INPUT_PENDING                = -20
II_EDITING                      = -21
II_IDLE                         = -22
II_SNOOP_NEXT                   = -30
II_SNOOP_PREV                   = -31
II_SNOOP_ALL                    = -32

OI_ONCE_INTERACTIVE             = -1

def efun_interactive(inter_ob: ldmud.Object = None) -> int:
    if inter_ob is None:
        inter_ob = ldmud.efuns.this_object()

    data = control.interactives.get(inter_ob, None)

    if data is None:
        return ldmud.efuns.interactive(inter_ob)
    else:
        return 1

def efun_remove_interactive(inter_ob: ldmud.Object) -> None:
    data = control.interactives.get(inter_ob, None)

    if data is None:
        return ldmud.efuns.remove_interactive(inter_ob)
    else:
        del control.interactives[inter_ob]
        data.call_control_ob("interactive_removed", inter_ob)

def efun_exec(inter_ob1: ldmud.Object, inter_ob2: ldmud.Object) -> int:
    data1 = control.interactives.get(inter_ob1, None)
    data2 = control.interactives.get(inter_ob2, None)

    if data2 is None:
        if not ldmud.efuns.exec(inter_ob1, inter_ob2):
            return 0
    elif data1 is None and ldmud.efuns.interactive(inter_ob1):
        if not ldmud.efuns.exec(inter_ob2, inter_ob1):
            return 0
    else:
        master = ldmud.get_master()
        result = util.lfun_call(master, "valid_exec", ldmud.efuns.program_name(), inter_ob1, inter_ob2)
        if not isinstance(result, int) or result == 0:
            return 0

    if data1 is not None:
        del control.interactives[inter_ob1]
        control.interactives[inter_ob2] = data1
        data1.call_control_ob("interactive_exec", inter_ob1, inter_ob2)

    if data2 is not None:
        if data1 is None:
            del control.interactives[inter_ob2]
        control.interactives[inter_ob1] = data2
        data2.call_control_ob("interactive_exec", inter_ob2, inter_ob1)

    return 1

def efun_configure_interactive(inter_ob: ldmud.Object, what: int, value) -> None:
    data = control.interactives.get(inter_ob, None)

    if data is None:
        return ldmud.efuns.configure_interactive(inter_ob, what, value)
    else:
        current_ob = ldmud.efuns.this_object()

        if current_ob not in (inter_ob, ldmud.get_master(), ldmud.get_simul_efun(),):
            master = ldmud.get_master()
            result = util.lfun_call(master, "privilege_violation", "configure_interactive", current_ob, inter_ob, what, value)
            if not isinstance(result, int) or result < 0:
                raise RuntimeError("Privilege violation: configure_interactive")
            elif result == 0:
                return

        data.options[what] = value

def efun_interactive_info(inter_ob: ldmud.Object, what: int):
    data = control.interactives.get(inter_ob, None)

    if data is None:
        return ldmud.efuns.interactive_info(inter_ob, what)
    else:
        if what >= 0 and what in data.options:
            return data.options[what]

        def error():
            raise ValueError("Illegal value for interactive_into()")

        def query_snooper():
            master = ldmud.get_master()
            if master != ldmud.efuns.this_object():
                result = util.lfun_call(master, "valid_query_snoop", inter_ob)
                if not isinstance(result, int) or result == 0:
                    return 0
            return data.snooper

        def query_snoopers():
            snooper = query_snooper()
            if snooper:
                return ldmud.Array((snooper,))
            else:
                return ldmud.Array()

        return {
            IC_MAX_WRITE_BUFFER_SIZE        : lambda: ldmud.efuns.interactive_info(0, what),
            IC_SOCKET_BUFFER_SIZE           : lambda: 0,
            IC_COMBINE_CHARSET_AS_STRING    : lambda: "",
            IC_COMBINE_CHARSET_AS_ARRAY     : lambda: ldmud.Array((0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)),
            IC_CONNECTION_CHARSET_AS_STRING : lambda: ''.join(map(chr,range(1,128))),
            IC_CONNECTION_CHARSET_AS_ARRAY  : lambda: ldmud.Array((254,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255)),
            IC_QUOTE_IAC                    : lambda: 1,
            IC_TELNET_ENABLED               : lambda: 1,
            IC_MCCP                         : lambda: 0,
            IC_PROMPT                       : lambda: 0,
            IC_MAX_COMMANDS                 : lambda: -1,
            IC_MODIFY_COMMAND               : lambda: 0,
            IC_ENCODING                     : lambda: ldmud.efuns.interactive_info(0, what),

            II_IP_NAME                      : lambda: data.hostname,
            II_IP_NUMBER                    : lambda: data.hostaddr,
            II_IP_PORT                      : lambda: data.hostport,
            II_IP_ADDRESS                   : lambda: data.get_sockaddr(),
            II_MUD_PORT                     : lambda: data.mudport,
            II_MCCP_STATS                   : lambda: 0,
            II_INPUT_PENDING                : lambda: len(data.inputto) and data.inputto[0].cb_ob,
            II_EDITING                      : lambda: 0,
            II_IDLE                         : lambda: data.get_idle(),
            II_SNOOP_NEXT                   : query_snooper,
            II_SNOOP_PREV                   : lambda: 0,
            II_SNOOP_ALL                    : query_snoopers,
        }.get(what, error)()

def efun_object_info(inter_ob: ldmud.Object, what: int):
    data = control.interactives.get(inter_ob, None)

    if data is None or what != OI_ONCE_INTERACTIVE:
        return ldmud.efuns.object_info(inter_ob, what)
    else:
        return 1
