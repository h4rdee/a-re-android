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
    GENERAL_TAB = 7,
    ADB_TAB = 8,
    PLUGINS_TAB = 9,
    ADB_DEVICES_LABEL = 10,
    ADB_DEVICES = 11
