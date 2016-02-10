#!/usr/bin/env python

from jinja2 import Environment, FileSystemLoader
from os.path import join
import os
import yaml

directory = os.getcwd()
J2_ENV = Environment(loader=FileSystemLoader(directory))

with open(join(directory, 'extracted_values.yml')) as f:
    template_variables = yaml.load(f)

for template_file in J2_ENV.list_templates(extensions='j2'):
    template = J2_ENV.get_template(template_file)
    open(join(directory, os.path.splitext(os.path.basename(template.filename.__str__()))[0]), 'w').write(template.render(template_variables))

