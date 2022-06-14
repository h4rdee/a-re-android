from utils import ECoreElements

class LogLevelObject:
    priority = None
    name = None
    tag = None

    def __init__(self, priority, name):
        self.priority = priority
        self.name = name
        self.tag = str(self.name.lower()[0:2])

    def modify_message(self, txt):
        return txt
        # return "[" + self.tag + "] " + txt

    def install(self, logger):
        setattr(
            logger, self.name.lower(), 
            (
                lambda message: logger.log(
                    self.modify_message(message), self.tag
                )
            )
        )

class LogLevel:
    INFO     = LogLevelObject(0, "Info")
    EXTERNAL = LogLevelObject(1, "External")
    SPECIAL  = LogLevelObject(2, "Special")
    PLUGIN   = LogLevelObject(3, "Plugin")
    WARNING  = LogLevelObject(4, "Warning")
    ERROR    = LogLevelObject(5, "Error")

class LogOutput:
    on_receive = None
    on_install = None

    def __init__(self, on_receive, on_install):
        self.on_receive = on_receive
        self.on_install = on_install

    def receive(self, message, tag):
        self.on_receive(message, tag)

    def install(self, logger):
        if self.on_install is not None:
            self.on_install(logger)

class Logger:
    log_levels = None
    outputs = None

    def __init__(self, install_stdout = False):
        self.log_levels = []
        self.outputs = []

        self.register_log_level(LogLevel.INFO)
        self.register_log_level(LogLevel.EXTERNAL)
        self.register_log_level(LogLevel.SPECIAL)
        self.register_log_level(LogLevel.PLUGIN)
        self.register_log_level(LogLevel.WARNING)
        self.register_log_level(LogLevel.ERROR)

        if install_stdout:
            self.install_output(LogOutput((lambda message, tag: print(message)), None))

    def construct(self, ui_root):
        logbox = ui_root.get_element_by_opt_id(ECoreElements.LOGGER)

        logbox_level_colors = {
            LogLevel.INFO.tag:     { "foreground": "#FFFFFF", "background": None    },
            LogLevel.EXTERNAL.tag: { "foreground": "#39912D", "background": None    },
            LogLevel.SPECIAL.tag:  { "foreground": "#AAFF00", "background": None    },
            LogLevel.PLUGIN.tag:   { "foreground": "#00FFFF", "background": None    },
            LogLevel.WARNING.tag:  { "foreground": "yellow" , "background": None    },
            LogLevel.ERROR.tag:    { "foreground": "red"    , "background": "black" }
        }

        def setup_logbox(logger):
            for color in logbox_level_colors.items(): 
                logbox.tag_config(
                    color[0], foreground=color[1]["foreground"],
                    background=color[1]["background"]
                )
                
        g_logger.install_output(
            LogOutput(
                (lambda message, tag: logbox.insert('end', message, tag)), 
                setup_logbox
            )
        )

    def install_output(self, output):
        self.outputs.append(output)
        output.install(self)

    def register_log_level(self, level):
        self.log_levels.append(level)
        level.install(self)

    def log(self, message, tag):
        for output in self.outputs:
            output.receive(message, tag)

g_logger = Logger(True)
