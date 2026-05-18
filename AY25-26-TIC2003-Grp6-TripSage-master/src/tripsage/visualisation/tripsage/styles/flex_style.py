FLEX_GAP_0 = {
    "spacing": "0"
}
FLEX_GAP_1 = {
    "spacing": "2"
}
FLEX_GAP_2 = {
    "spacing": "4"
}
FLEX_GAP_3 = {
    "spacing": "7"
}

FLEX_COLUMN = {
    **FLEX_GAP_1,
    "display": "flex",
    "direction": "column",
    "align": "start",
    "flex_wrap": "wrap",
}
FLEX_COLUMN_CENTER = {
    **FLEX_COLUMN,
    "align": "center",
}
FLEX_COLUMN_STRETCH = {
    **FLEX_COLUMN,
    "align": "stretch",
}
FLEX_COLUMN_CENTER_BETWEEN = {
    **FLEX_COLUMN_CENTER,
    "justify": "between",
}

FLEX_ROW = {
    **FLEX_GAP_1,
    "display": "flex",
    "direction": "row",
    "align": "start",
    "flex_wrap": "wrap",
}
FLEX_ROW_STRETCH = {
    **FLEX_ROW,
    "align": "stretch",
}