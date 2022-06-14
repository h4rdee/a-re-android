from enum import IntEnum

# core elements ids that we will need throughout g_app lifecycle
class ECoreElements(IntEnum):
    NONE = 0,
    LOGGER = 1,
    APK_INFO_LABEL = 2,
    APK_ICON_VIEW = 3,
    PROGRESS_BAR = 4,
    TAB_CONTROL_ROOT = 5,
    TAB_CONTROL_PLUGINS = 6,
    TAB_CONTROL_ADB = 7,
    GENERAL_TAB = 8,
    ADB_TAB = 9,
    PLUGINS_TAB = 10,
    ADB_DEVICES_LABEL = 11,
    ADB_DEVICES = 12,
    ADB_SHELL_LABEL = 13,
    ADB_SHELL_TERMINAL = 14
