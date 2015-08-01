from datetime import datetime

class Entry():
    """Describes an individual TODO item for use in agendas and TODO lists"""
    def __init__(self, level, heading, tags=None, content=None, starter_char=None):
        if starter_char:
            self.starter_char = starter_char
        else:
            self.starter_char = "*"
        self.level = self.starter_char * int(level)
        self.heading = heading
        if tags:
            _tag_list = [":{0}:".format(tag) for tag in tags]
            self.tags = "".join(_tag_list)
        else:
            self.tags = ""
        self.content = content

    def __str__(self):
        # print(type(self.level))
        # print(type(self.heading))
        # print(type(self.tags))
        header = self.level + " " + self.heading + " " + self.tags
        if self.content:
            entry = header + "\n" + self.content
        else:
            entry = header
        return entry

def make_property(prop, value):
    return ":{0}: {1}".format(prop.upper(), str(value))

def get_org_date(active=None):
    if active:
        _sep = ["<", ">"]
    else:
        _sep = ["[", "]"]
    wd = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    _n = datetime.now()
    org_date = "{0}{1}-{2}-{3} {4} {5}:{6}{7}".format(
        _sep[0],
        _n.year,
        "{:0>2d}".format(_n.month),
        "{:0>2d}".format(_n.day),
        wd[_n.weekday()],
        "{:0>2d}".format(_n.hour),
        "{:0>2d}".format(_n.minute),
        _sep[1],)
    return org_date
