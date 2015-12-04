try:
    from sshtunnel import SSHTunnelForwarder
except ImportError:
    from sshtunnel.sshtunnel import SSHTunnelForwarder
import paramiko
import json
import yaml
import requests
import subprocess
import zipfile
import shutil
import os
import xml.etree.ElementTree

class CdhConfExtractor(object):

    def __init__(self, config_filename=None):
        self.config_filename = config_filename if config_filename else 'fetcher_config.yml'
        config = self._load_config_yaml(self.config_filename)
        self._hostname = config['machines']['cdh-launcher']['hostname']
        self._hostport = config['machines']['cdh-launcher']['hostport']
        self._username = config['machines']['cdh-launcher']['username']
        self._key_filename = config['machines']['cdh-launcher']['key_filename']
        self._key = os.path.expanduser(self._key_filename)
        self._key_password = config['machines']['cdh-launcher']['key_password']
        self._is_openstack = config['is_openstack_env']
        self._is_kerberos = config['is_kerberos']
        self._cdh_manager_ip = config['machines']['cdh-manager-ip']

    def __enter__(self):
        extractor = self
        extractor.create_tunnel_to_cdh_manager()
        extractor.start_cdh_manager_tunneling()
        return extractor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_cdh_manager_tunneling()

    # Cdh launcher methods
    def create_ssh_connection_to_cdh(self):
        self.ssh_connection = paramiko.SSHClient()
        self.ssh_connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_connection.connect(self._hostname, username=self._username, key_filename=self._key, password=self._key_password)

    def close_connection_to_cdh(self):
        self.ssh_connection.close()

    def ssh_call_command(self, command, subcommands=None):
        ssh_in, ssh_out, ssh_err = self.ssh_connection.exec_command(command, get_pty=True)
        if subcommands != None:
            for subcommand in subcommands:
                ssh_in.write(subcommand + '\n')
                ssh_in.flush()
        return ssh_out.read() if ssh_out is not None else ssh_err.read()

    def extract_cdh_manager_host(self):
        if self._cdh_manager_ip is None:
            self.create_ssh_connection_to_cdh()
            if self._is_openstack.lower() == 'true':
                ansible_ini = self.ssh_call_command('cat ansible-cdh/platform-ansible/inventory/cdh')
            else:
                ansible_ini = self.ssh_call_command('cat ansible-cdh/inventory/cdh')
            self._cdh_manager_ip = self._get_host_ip('cdh-manager', ansible_ini)
            self.close_connection_to_cdh()
        return self._cdh_manager_ip

    # Cdh manager methods
    def create_tunnel_to_cdh_manager(self, local_bind_address='localhost', local_bind_port=7180, remote_bind_port=7180):
        self._local_bind_address = local_bind_address
        self._local_bind_port = local_bind_port
        self.cdh_manager_tunnel = SSHTunnelForwarder(
            (self._hostname, self._hostport),
            ssh_username=self._username,
            local_bind_address=(local_bind_address, local_bind_port),
            remote_bind_address=(self.extract_cdh_manager_host(), remote_bind_port),
            ssh_private_key_password=self._key_password,
            ssh_private_key=self._key
        )

    def start_cdh_manager_tunneling(self):
        try:
            self.cdh_manager_tunnel.start()
        except Exception as e:
            print('Cannot start tunnel: ' + e.message)

    def stop_cdh_manager_tunneling(self):
        try:
            self.cdh_manager_tunnel.stop()
        except Exception as e:
            print('Cannot stop tunnel: ' + e.message)

    def extract_cdh_manager_details(self, settings):
        for host in settings['hosts']:
            if 'cdh-manager' in host['hostname']:
                return host

    def extract_master_nodes_info(self, settings):
        master_nodes = []
        for host in settings['hosts']:
            if 'cdh-master' in host['hostname']:
                master_nodes.append(host)
        return master_nodes

    def extract_service_namenode(self, service_name, role_name, settings):
        hdfs_service = self._find_item_by_attr_value(service_name, 'name', settings['clusters'][0]['services'])
        hdfs_namenode = self._find_item_by_attr_value(role_name, 'name', hdfs_service['roles'])
        host_id = hdfs_namenode['hostRef']['hostId']
        return self._find_item_by_attr_value(host_id, 'hostId', settings['hosts'])['hostname']

    def get_client_config_for_service(self, service_name):
        command = 'wget http://{0}:{1}/api/v10/clusters/CDH-cluster/services/{2}/clientConfig'.format(self._local_bind_address, self._local_bind_port, service_name)
        subprocess.check_call(command.split())
        return self._parse_client_config_zip()

    def generate_keytab(self, principal_name):
        self.create_ssh_connection_to_cdh()
        sftp = self.ssh_connection.open_sftp()
        sftp.put('utils/generate_keytab_script.sh', '/tmp/generate_keytab_script.sh')
        self.ssh_call_command('scp /tmp/generate_keytab_script.sh {0}:/tmp/'.format(self._cdh_manager_ip))
        self.ssh_call_command('ssh -t {0} "chmod 700 /tmp/generate_keytab_script.sh"'.format(self._cdh_manager_ip))
        keytab_hash = self.ssh_call_command('ssh -t {0} "/tmp/generate_keytab_script.sh {1}"'
                                            .format(self._cdh_manager_ip, principal_name))
        self.close_connection_to_cdh()
        lines = keytab_hash.splitlines()
        del lines[-2:]
        return ''.join(lines)

    def get_all_deployments_conf(self, cdh_manager_username='admin', cdh_manager_password='admin'):
        result = {}
        deployments_settings = json.loads(requests.get('http://' + self._local_bind_address + ':'
                                                       + str(self._local_bind_port) + '/api/v10/cm/deployment',
                                                    auth=(cdh_manager_username, cdh_manager_password)).content)
        result['cloudera_manager_internal_host'] = self.extract_cdh_manager_details(deployments_settings)['hostname']

        if self._is_kerberos.lower() == 'true':
            result['kerberos_host'] = result['cloudera_manager_internal_host']
            result['hdfs_keytab_value'] = self.generate_keytab('hdfs')
        else:
            result['hdfs_keytab_value'] = "''"

        master_nodes = self.extract_master_nodes_info(deployments_settings)
        for i, node in enumerate(master_nodes):
            result['master_node_host_' + str(i+1)] = node['hostname']
        result['namenode_internal_host'] = self.extract_service_namenode('HDFS', 'HDFS-NAMENODE', deployments_settings)
        result['hue_node'] = self.extract_service_namenode('HUE', 'HUE-HUE_SERVER', deployments_settings)
        result['import_hadoop_conf_hdfs'] = self.get_client_config_for_service('HDFS')
        result['import_hadoop_conf_hbase'] = self.get_client_config_for_service('HBASE')
        result['import_hadoop_conf_yarn'] = self.get_client_config_for_service('YARN')

        return result

    # helpful methods

    def _find_item_by_attr_value(self, attr_value, attr_name, array_with_dicts):
        return next(item for item in array_with_dicts if item[attr_name] == attr_value)

    def _get_host_ip(self, host, ansible_ini):
        host_info = []
        for line in ansible_ini.split('\n'):
            if host in line:
                host_info.append(line.strip())
        return host_info[host_info.index('[' + host + ']') + 1].split(' ')[1].split('=')[1]

    def _xml_to_json_converter(self, xml_file):
        result_json = {}
        xml_obj = xml.etree.ElementTree.parse(xml_file).getroot()
        for property in xml_obj.findall('property'):
            result_json[str(property.findall('name')[0].text).replace('$', '\$')] = str(property.findall('value')[0].text).replace('$', '\$')

        return result_json

    def _parse_client_config_zip(self):
        hadoop_zip = zipfile.ZipFile('clientConfig')
        hadoop_zip.extractall('hadoop-admin')
        os.remove('clientConfig')
        hadoop_conf_directory = [item for item in os.listdir('hadoop-admin') if os.path.isdir('hadoop-admin/{0}'.format(item))][0]
        xml_files = [item for item in os.listdir('hadoop-admin/{0}'.format(hadoop_conf_directory)) if item.endswith('.xml')]
        result_json = {}
        for xml in xml_files:
            result_json.update(self._xml_to_json_converter('hadoop-admin/{0}/{1}'.format(hadoop_conf_directory, xml)).items())
        shutil.rmtree('hadoop-admin')
        return json.dumps({"HADOOP_CONFIG_KEY": result_json}).replace('\\\\', '\\')

    def _load_config_yaml(self, filename):
        with open(filename, 'r') as stream:
            return yaml.load(stream)

