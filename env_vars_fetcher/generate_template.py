#!/usr/bin/env python

from jinja2 import Environment, FileSystemLoader
from os.path import join
import os
import yaml

directory = os.getcwd()
J2_ENV = Environment(loader=FileSystemLoader(directory))

with open(join(directory, 'extracted_values.yml')) as f:
    template_variables = yaml.load(f)

rendered_template = J2_ENV.get_template('templates/settings.yml.j2').render(template_variables)

with open(join(directory, 'settings.yml'), 'w') as f:
    f.write(rendered_template)
