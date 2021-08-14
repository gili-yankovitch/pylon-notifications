from os import listdir
from os.path import dirname, sep
from importlib import import_module

filters = {}

for f in listdir(dirname(__file__)):
	if f.endswith(".py") and f != "__init__.py":
		#filters[f[:-3]] = __import__("app.filters.{MODULE}".format(MODULE = f[:-3]))
		filters[f[:-3]] = import_module("app.filters.{MODULE}".format(MODULE = f[:-3]))
		print("app.filters.{MODULE}".format(MODULE = f[:-3]))
