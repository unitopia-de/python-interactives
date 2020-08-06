import ldmud
import os, select, traceback

from . import control
from . import util
from . import interactive

queue = []
signal_pipe = None
current_interactive = None

# From input_to.h
INPUT_NOECHO      = 1
INPUT_CHARMODE    = 2
INPUT_PROMPT      = 4
INPUT_NO_TELNET   = 8
INPUT_APPEND      = 16
INPUT_IGNORE_BANG = 128

class InputTo:
    def __init__(self, cb_ob, cb_fun, flag, *args):
        self.cb_ob = cb_ob
        self.cb_fun = cb_fun
        self.flag = flag
        if self.flag & INPUT_PROMPT:
            self.prompt = args[0]
            self.args = args[1:]
            if not isinstance(self.prompt, str) and not isinstance(self.prompt, ldmud.Closure):
                raise ValueError("Bad argument 3 to input_to()")

        else:
            self.prompt = None
            self.args = args

def on_reload():
    global signal_pipe
    if signal_pipe is not None:
        ldmud.unregister_socket(signal_pipe[0])
        os.close(signal_pipe[0])
        os.close(signal_pipe[1])
        signal_pipe = None

def receive_input(event):
    global current_interactive
    try:
        os.read(signal_pipe[0], 1)
    except:
        pass

    if len(queue):
        (inter_ob, inp) = queue.pop(0)
        data = control.interactives.get(inter_ob, None)

        if data is None:
            return

        data.update_idle()

        ldmud.efuns.set_this_player(inter_ob)
        current_interactive = inter_ob

        try:
            if inp is not None:
                # Check for input_tos
                has_bang = len(inp) > 0 and inp[0] == '!'
                found = False
                for idx, it in enumerate(data.inputto):
                    if not has_bang or (it.flag & INPUT_IGNORE_BANG):
                        data.inputto.pop(idx)

                        if isinstance(it.cb_fun, ldmud.Closure):
                            it.cb_fun(inp, *it.args)
                        else:
                            util.lfun_call(it.cb_ob, it.cb_fun, inp, *it.args)

                        found = True
                        break

                # It is an action?
                if not found:
                    if has_bang:
                        inp = inp[1:]
                    ldmud.Closure(inter_ob, "efun::command")(inp, inter_ob)

            # Now handle the prompt
            def print_prompt(prompt):
                if isinstance(prompt, ldmud.Closure):
                    prompt = prompt()
                if not isinstance(prompt, str):
                    return

                data.call_control_ob("receive_prompt", inter_ob, prompt)
                if data.snooper is not None:
                    try:
                        ldmud.efuns.tell_object(data.snooper, "%" + prompt)
                    except:
                        pass

            for it in data.inputto:
                print_prompt(it.prompt)
                return
            print_prompt(data.options.get(interactive.IC_PROMPT, '> '))
        finally:
            current_interactive = None

def signal_input(inter_ob, inp):
    global signal_pipe
    if signal_pipe is None:
        signal_pipe = os.pipe2(os.O_NONBLOCK | os.O_CLOEXEC)
        ldmud.register_socket(signal_pipe[0], receive_input, select.POLLIN)

    queue.append((inter_ob, inp,))
    os.write(signal_pipe[1], b' ')

def efun_send_interactive_input(inter_ob: ldmud.Object, inp: str) -> None:
    """
    SYNOPSIS
            void send_interactive_input(object ob, string input)

    DESCRIPTION
            Sends input to the given virtual interactive object.

            This efun can only be called by the designated control object.
            The input will either be used for a pending input_to or
            as an action.

    SEE ALSO
            make_interactive(E)
    """
    data = control.interactives.get(inter_ob, None)
    if data is None or not data.is_control_ob(ldmud.efuns.this_object()):
        raise RuntimeError("Invalid call of send_interactive_input()")

    signal_input(inter_ob, inp)

def efun_input_to(fun: (str, ldmud.Closure), flag:int = 0, *args) -> None:
    inter_ob = ldmud.efuns.this_player()
    data = control.interactives.get(inter_ob, None)

    if data is None:
        ldmud.efuns.input_to(fun, flag, *args)
    else:
        it = InputTo(ldmud.efuns.this_object(), fun, flag, *args)

        # We currently don't support INPUT_NOECHO, INPUT_CHARMODE and INPUT_NO_TELNET
        if flag & INPUT_APPEND:
            data.inputto.append(it)
        else:
            data.inputto.insert(0, it)

def efun_find_input_to(inter_ob: ldmud.Object, fun: (ldmud.Object, str, ldmud.Closure), it_ob: ldmud.Object = None) -> int:
    data = control.interactives.get(inter_ob, None)

    if data is None:
        if it_ob is None:
            return ldmud.efuns.find_input_to(inter_ob, fun)
        else:
            return ldmud.efuns.find_input_to(inter_ob, fun, it_ob)
    else:
        it_fun = None
        if isinstance(fun, ldmud.Object):
            it_ob = fun
        else:
            it_fun = fun

        for idx, it in enumerate(data.inputto):
            if (it_ob is None or it_ob == it.cb_ob) and (it_fun is None or it_fun == it.cb_fun):
                return idx

        return -1

def efun_input_to_info(inter_ob: ldmud.Object) -> ldmud.Array:
    data = control.interactives.get(inter_ob, None)

    if data is None:
        return ldmud.efuns.input_to_info(inter_ob)
    else:
        result = []
        for it in reversed(data.inputto):
            result.append(ldmud.Array((it.cb_ob, it.cb_fun, *it.args)))
        return ldmud.Array(result)

def efun_remove_input_to(inter_ob: ldmud.Object, fun: (str, ldmud.Object, ldmud.Closure) = None, fun2: str = None) -> int:
    data = control.interactives.get(inter_ob, None)

    if data is None:
        if fun is None:
            return ldmud.efuns.remove_input_to(inter_ob)
        elif fun2 is None:
            return ldmud.efuns.remove_input_to(inter_ob, fun)
        else:
            return ldmud.efuns.remove_input_to(inter_ob, fun, fun2)
    else:
        it_fun = fun2
        it_ob = None
        if isinstance(fun, str):
            it_fun = fun
        elif fun is not None:
            it_ob = fun

        for idx, it in enumerate(data.inputto):
            if (it_ob is None or it_ob == it.cb_ob) and (it_fun is None or it_fun == it.cb_fun):
                data.inputto.pop(idx)
                return 1

        return 0

def efun_caller_stack(add_inter: int = None) -> ldmud.Array:
    if current_interactive is None:
        return ldmud.efuns.caller_stack(add_inter or 0)[1:]
    elif add_inter:
        return ldmud.efuns.caller_stack()[1:] + ldmud.Array((current_interactive,))
    else:
        return ldmud.efuns.caller_stack()[1:]

def efun_this_interactive() -> ldmud.Object:
    if current_interactive is None:
        return ldmud.efuns.this_interactive()
    else:
        return current_interactive

def show_prompt(inter_ob):
    signal_input(inter_ob, None)
