#!/usr/bin/env python

from jinja2 import Environment, FileSystemLoader
from os.path import dirname, abspath
import yaml

THIS_DIR = dirname(abspath(__file__))
J2_ENV = Environment(loader=FileSystemLoader(THIS_DIR))

with open('template_variables.yml') as f:
  template_variables = yaml.load(f)

rendered_template = J2_ENV.get_template('settings.yml.j2').render(template_variables)
with open('settings.yml', 'w') as f:
  f.write(rendered_template)
