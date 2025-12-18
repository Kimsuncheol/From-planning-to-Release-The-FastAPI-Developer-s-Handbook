import enum

class AttendanceStatus(enum.StrEnum):
    SCHEDULED = enum.auto()
    ATTENDED = enum.auto()
    CANCELED = enum.auto()
    NO_SHOW = enum.auto()
    SAME_DAY_CANCEL = enum.auto()
    LATE = enum.auto()

