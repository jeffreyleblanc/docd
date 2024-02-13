# SPDX-FileCopyRightText: Copyright (c) 2023-present Jeffrey LeBlanc
# SPDX-License-Indentifier: UNLICENSED

class DictObj:

    def __init__(self, input_dict):
        assert isinstance(input_dict,dict)
        for k,v in input_dict.items():
            if isinstance(v,(list,tuple)):
                lst = [ DictObj(e) if isinstance(e,dict) else e for e in v ]
                if isinstance(v,tuple):
                    lst = tuple(lst)
                setattr(self,k,lst)
            else:
               setattr(self,k,( DictObj(v) if isinstance(v,dict) else v ))

    def __repr__(self):
        return f"DictObj({self.__dict__.__repr__()})"

    def __iter__(self):
        return iter(self.__dict__)

    def get(self, key, default=None):
        return getattr(self,key) if hasattr(self,key) else default

    def items(self):
        return self.__dict__.items()

    def get_path(self, path, default=None):
        parts = path.split(".")
        parts.reverse()
        e = self
        while len(parts) > 0:
            p = parts.pop()
            e = e.get(p)
            if not isinstance(e,DictObj) and len(parts)>0:
                return default
        return e

    def has_path(self, path):
        parts = path.split(".")
        parts.reverse()
        e = self
        while len(parts) > 0:
            p = parts.pop()
            e = e.get(p)
            if not isinstance(e,DictObj) and len(parts)>0:
                return False
        return True

    def to_dict(self):
        return { k:(v.to_dict() if isinstance(v,DictObj) else v) for k,v in self.items() }

