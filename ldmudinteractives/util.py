import ldmud

def lfun_call(ob, funname, *args):
    if hasattr(ob, "functions"):
        fun = getattr(ob.functions, funname, None)
        if fun is not None:
            argnum = len(fun.arguments)
            if argnum < len(args):
                args = args[:argnum]
            elif argnum > len(args):
                args += (argnum - len(args)) * (0,)
            return fun(*args)
    else:
        return ldmud.Closure(ob, "efun::call_other")(ob, funname, *args)
