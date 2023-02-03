# PYTHON IMPORTS
from importlib import import_module
import ast
import dateutil
import dateutil.parser

CACHED_REFLECTIONS = {}


class Reflection:
    """
    Utility class to manage the python reflection and
    dynamic class analysis.
    """

    @staticmethod
    def inheritors(klass):
        """
        Returns the list of inheritors of a specified class
        :param klass: The class to be analyzed
        :return: Returns the list of classes inheriting from source class
        """
        subclasses = set()
        work = [klass]
        while work:
            parent = work.pop()
            for child in parent.__subclasses__():
                if child not in subclasses:
                    subclasses.add(child)
                    work.append(child)
        return subclasses

    @staticmethod
    def parents(klass):
        return list(klass.__bases__)

    @staticmethod
    def load(name):
        """
        Get a class instance by name and returns it
        :param name: The full package class name string
        :return: A class reference
        """
        if name in CACHED_REFLECTIONS:
            return CACHED_REFLECTIONS[name]
        mod_name, obj_name = name.rsplit('.', 1)
        mod = import_module(mod_name)
        obj = getattr(mod, obj_name)
        CACHED_REFLECTIONS[name] = obj
        return obj

    @staticmethod
    def signature(klass) -> str:
        return '{0}.{1}'.format(klass.__module__, klass.__name__)

    @staticmethod
    def deduce(value):
        """
        Safely evaluate an expression node or a Unicode or Latin-1 encoded string containing a Python expression.
        The string or node provided may only consist of the following Python literal structures:
        strings, numbers, tuples, lists, dicts, booleans, and None.
        :param value:
        :return: A  custom type inference, otherwise return the value as a string
        """
        try:
            return ast.literal_eval(value)
        except Exception:
            pass
        try:
            return dateutil.parser.parse(value)
        except Exception:
            pass
        return str(value)
