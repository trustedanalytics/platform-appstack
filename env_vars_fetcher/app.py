import json
import argparse
import os
import yaml

from cdh_utilities import CdhConfExtractor
from bastion_utilities import CFConfExtractor


def fill_template_variables(template, values):
    if isinstance(template, dict) and isinstance(values, dict):
        for key, value in values.iteritems():
            template[key] = value
    return template

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Tools for extracting CF details")
    parser.add_argument('-c', '--config', help='Path to config file')
    args = parser.parse_args()

    with CdhConfExtractor(args.config) as cdh_util:
        cdh_conf = cdh_util.get_all_deployments_conf()

    with CFConfExtractor(args.config) as jumpbox_util:
        env_conf = jumpbox_util.get_environment_settings()

    values = dict(cdh_conf.items() + env_conf.items())

    with open('templates/template_variables.yml', 'r') as f:
        template = json.loads(json.dumps(yaml.load(f)))

    with open('extracted_values.yml', 'w') as f:
        f.write(yaml.safe_dump(fill_template_variables(template, values)))

    os.system('env_vars_fetcher/generate_template.py')