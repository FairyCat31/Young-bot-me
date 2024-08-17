from sqlalchemy import String, DateTime, Integer, Text, UnicodeText, BIGINT


map_types = {
    "gender": UnicodeText(1),
    "str_16": UnicodeText(16),
    "str_1024": UnicodeText(1024),
    "str_4096": UnicodeText(4096),
    "str": UnicodeText(4096),
    "int": Integer,
    "int_big": BIGINT,
    "date": UnicodeText(10)
}
