import paramiko
import yaml
import os


class CFConfExtractor(object):

    def __init__(self, config_filename=None):
        self.config_filename = config_filename if config_filename else 'fetcher_config.yml'
        config = self._load_config_yaml(self.config_filename)
        self._hostname = config['machines']['cf-bastion']['hostname']
        self._hostport = config['machines']['cf-bastion']['hostport']
        self._username = config['machines']['cf-bastion']['username']
        self._key_filename = config['machines']['cf-bastion']['key_filename']
        self._key = os.path.expanduser(self._key_filename)
        self._key_password = config['machines']['cf-bastion']['key_password']
        self._is_openstack = config['is_openstack_env']
        self._path_to_cf_tiny_yml = config['machines']['cf-bastion']['path_to_cf_tiny_yml']
        self._path_to_docker_vpc_yml = config['machines']['cf-bastion']['path_to_docker_vpc_yml']

    def __enter__(self):
        extractor = self
        extractor.create_ssh_connection_to_cf_bastion()
        return extractor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection_to_cf_bastion()

    # bastion methods
    def create_ssh_connection_to_cf_bastion(self):
        self.ssh_connection = paramiko.SSHClient()
        self.ssh_connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_connection.connect(self._hostname, username=self._username, key_filename=self._key, password=self._key_password)

    def close_connection_to_cf_bastion(self):
        self.ssh_connection.close()

    def ssh_call_command(self, command):
        ssh_in, ssh_out, ssh_err = self.ssh_connection.exec_command(command)
        return ssh_out.read() if ssh_out is not None else ssh_err.read()

    def _extract_variables(self):
        result = {}
        if self._path_to_cf_tiny_yml is not None and self._path_to_docker_vpc_yml is not None:
            docker_vpc_yml = yaml.load(self.ssh_call_command('cat {0}'.format(self._path_to_docker_vpc_yml)))
            cf_tiny_yml = yaml.load(self.ssh_call_command('cat {0}'.format(self._path_to_cf_tiny_yml)))
        elif self._is_openstack.lower() == 'true':
            docker_vpc_yml = yaml.load(self.ssh_call_command('cat ~/workspace/deployments/docker-services-boshworkspace/deployments/docker-openstack.yml'))
            cf_tiny_yml = yaml.load(self.ssh_call_command('cat ~/workspace/deployments/cf-boshworkspace/deployments/cf-openstack-tiny.yml'))
        else:
            docker_vpc_yml = yaml.load(self.ssh_call_command('cat ~/workspace/deployments/docker-services-boshworkspace/deployments/docker-aws-vpc.yml'))
            cf_tiny_yml = yaml.load(self.ssh_call_command('cat ~/workspace/deployments/cf-boshworkspace/deployments/cf-aws-tiny.yml'))

        if docker_vpc_yml is None or cf_tiny_yml is None:
            raise IOError("Cannot find configuration files on the cf-bastion machine.")

        result['nats_ip'] = docker_vpc_yml['meta']['nats']['machines'][0]
        result['cf_admin_password'] = cf_tiny_yml['meta']['admin_secret']
        result['cf_admin_client_password'] = cf_tiny_yml['meta']['secret']
        result['apps_domain'] = cf_tiny_yml['meta']['app_domains']
        result['developer_console_password'] = cf_tiny_yml['meta']['secret']
        result['email_address'] = cf_tiny_yml['meta']['login_smtp']['senderEmail']
        result['run_domain'] = cf_tiny_yml['meta']['domain']
        result['smtp_pass'] = '"{0}"'.format(cf_tiny_yml['meta']['login_smtp']['password'])
        result['smtp_user'] = '"{0}"'.format(cf_tiny_yml['meta']['login_smtp']['user'])
        result['smtp_port'] = cf_tiny_yml['meta']['login_smtp']['port']
        result['smtp_host'] = cf_tiny_yml['meta']['login_smtp']['host']
        return result

    def get_environment_settings(self):
        return self._extract_variables()

    def _load_config_yaml(self, filename):
        with open(filename, 'r') as stream:
            return yaml.load(stream)

