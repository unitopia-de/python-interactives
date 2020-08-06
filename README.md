# Python Efun package for virtually interactive objects

## Overview

These Python efuns override native efuns to simulate interactive objects.
An additional efun is provided to make an object interactive:
 * `void make_interactive(object ob, object|string control_ob, string ip_name, string ip_number, int ip_port, int mud_port)`

The control object is used to send input to the interactive object and
receive messages for it. Only the control object may call the following
new efun:
 * `void send_interactive_input(object ob, string input)`

And the following functions are called in the control object:
 * `void interactive_removed(object ob)`
 * `void interactive_exec(object ob, object new)`
 * `void receive_message(object ob, string msg)`
 * `void receive_binary(object ob, bytes msg)`
 * `void receive_prompt(object ob, string msg)`

The virtual interactive should behave just like a normal interactive,
with the following exceptions that do not work:
 * Snooping (they can be snooped on, but cannot snoop themselves)
 * Editing
 * Tracing
 * Telnet support
 * `object_info(ob, OI_ONCE_INTERACTIVE)` for former interactives

### Build & installation

You'll need to build the package.

First clone the repository
```
git clone https://github.com/unitopia-de/python-interactives.git
```

In the corresponding package directory execute
```
python3 setup.py install --user
```

### Automatically load the modules at startup

Also install the [LDMud Python efuns](https://github.com/ldmud/python-efuns) and use its
[startup.py](https://github.com/ldmud/python-efuns/blob/master/startup.py) as the Python startup script for LDMud.
It will automatically detect the installed Python efuns and load them.

### Manually load the modules at startup

Add lines like the following to your startup script:
```
import ldmudinteractives

ldmudinteractives.register()
```
