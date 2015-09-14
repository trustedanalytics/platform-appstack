#!/usr/bin/env python

from jinja2 import Environment, FileSystemLoader
from os.path import dirname, abspath, join
import yaml
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-d",
                    "--directory",
                    default=None,
                    help="directory where this file is")
args, unknown = parser.parse_known_args()

if args.directory:
    directory = args.directory
else:
    directory = dirname(abspath(__file__))
J2_ENV = Environment(loader=FileSystemLoader(directory))

with open(join(directory, 'template_variables.yml')) as f:
    template_variables = yaml.load(f)

rendered_template = J2_ENV.get_template('settings.yml.j2').render(template_variables)
with open(join(directory, 'settings.yml'), 'w') as f:
    f.write(rendered_template)
