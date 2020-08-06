import ldmud

from . import control
from . import input
from . import interactive
from . import message

ldmud.register_hook(ldmud.ON_OBJECT_DESTRUCTED, control.clean_ob)

def register():
    ldmud.register_efun('make_interactive'      , control.efun_make_interactive)
    ldmud.register_efun('users'                 , control.efun_users)
    ldmud.register_efun('send_interactive_input', input.efun_send_interactive_input)
    ldmud.register_efun('input_to'              , input.efun_input_to)
    ldmud.register_efun('find_input_to'         , input.efun_find_input_to)
    ldmud.register_efun('input_to_info'         , input.efun_input_to_info)
    ldmud.register_efun('remove_input_to'       , input.efun_remove_input_to)
    ldmud.register_efun('caller_stack'          , input.efun_caller_stack)
    ldmud.register_efun('this_interactive'      , input.efun_this_interactive)
    ldmud.register_efun('interactive'           , interactive.efun_interactive)
    ldmud.register_efun('remove_interactive'    , interactive.efun_remove_interactive)
    ldmud.register_efun('exec'                  , interactive.efun_exec)
    ldmud.register_efun('configure_interactive' , interactive.efun_configure_interactive)
    ldmud.register_efun('interactive_info'      , interactive.efun_interactive_info)
    ldmud.register_efun('object_info'           , interactive.efun_object_info)
    ldmud.register_efun('printf'                , message.efun_printf)
    ldmud.register_efun('write'                 , message.efun_write)
    ldmud.register_efun('say'                   , message.efun_say)
    ldmud.register_efun('tell_room'             , message.efun_tell_room)
    ldmud.register_efun('tell_object'           , message.efun_tell_object)
    ldmud.register_efun('binary_message'        , message.efun_binary_message)
    ldmud.register_efun('snoop'                 , message.efun_snoop)
