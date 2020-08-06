import setuptools

setuptools.setup(
    name="ldmud-efun-virtual-interactives",
    version="0.0.1",
    author="UNItopia Administration",
    author_email="mudadm@UNItopia.DE",
    description="Implements virtual interactives",
    long_description="Allows objects without network connections to behave as interactives.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'ldmud_efun': [
              'make_interactive       = ldmudinteractives.control:efun_make_interactive',
              'users                  = ldmudinteractives.control:efun_users',
              'send_interactive_input = ldmudinteractives.input:efun_send_interactive_input',
              'input_to               = ldmudinteractives.input:efun_input_to',
              'find_input_to          = ldmudinteractives.input:efun_find_input_to',
              'input_to_info          = ldmudinteractives.input:efun_input_to_info',
              'remove_input_to        = ldmudinteractives.input:efun_remove_input_to',
              'caller_stack           = ldmudinteractives.input:efun_caller_stack',
              'this_interactive       = ldmudinteractives.input:efun_this_interactive',
              'interactive            = ldmudinteractives.interactive:efun_interactive',
              'remove_interactive     = ldmudinteractives.interactive:efun_remove_interactive',
              'exec                   = ldmudinteractives.interactive:efun_exec',
              'configure_interactive  = ldmudinteractives.interactive:efun_configure_interactive',
              'interactive_info       = ldmudinteractives.interactive:efun_interactive_info',
              'object_info            = ldmudinteractives.interactive:efun_object_info',
              'printf                 = ldmudinteractives.message:efun_printf',
              'write                  = ldmudinteractives.message:efun_write',
              'say                    = ldmudinteractives.message:efun_say',
              'tell_room              = ldmudinteractives.message:efun_tell_room',
              'tell_object            = ldmudinteractives.message:efun_tell_object',
              'binary_message         = ldmudinteractives.message:efun_binary_message',
              'snoop                  = ldmudinteractives.message:efun_snoop',
        ]
    },
    zip_safe=False,
)
