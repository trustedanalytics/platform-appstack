from collections import namedtuple
from env_vars_fetcher.cdh_utilities import CdhConfExtractor
import mock
import yaml


class TestSSHConnectionToCdh:

    @classmethod
    def setup_class(cls):
        cls.default_config_name = 'fetcher_config.yml'
        cls.json_config = {
            'openstack_env': True,
            'kerberos_used': True,
            'machines': {
                'cdh-launcher': {
                    'hostname': '10.10.10.10',
                    'hostport': 22,
                    'username': 'centos',
                    'key_filename': 'key.pem',
                    'key_password': None
                },
                'cdh-manager': {
                    'ip': '',
                    'user': 'test',
                    'password': 'test',
                    'sshtunnel_required': True
                }
            }
        }

        cls.mock_config_content = yaml.dump(cls.json_config)

        with mock.patch('__builtin__.open', mock.mock_open(read_data=cls.mock_config_content), create=True) as m:
            cls.cdhUtilities = CdhConfExtractor()

    def test_create_without_arg_uses_default_filename(self):
        """ Checks is default file config used """
        assert self.cdhUtilities.config_filename == self.default_config_name
        assert self.cdhUtilities._hostname == self.json_config['machines']['cdh-launcher']['hostname']
        assert self.cdhUtilities._hostport == self.json_config['machines']['cdh-launcher']['hostport']
        assert self.cdhUtilities._username == self.json_config['machines']['cdh-launcher']['username']
        assert self.cdhUtilities._key_filename == self.json_config['machines']['cdh-launcher']['key_filename']

    def test_create_without_arg_uses_filename_from_arg(self):
        """ Checks is custom config used for calling constructor with arg """
        custom_filename = "customConfig.yml"

        with mock.patch('__builtin__.open', mock.mock_open(read_data=self.mock_config_content), create=True) as m:
            cdh_with_custom_config = CdhConfExtractor(custom_filename)

        assert cdh_with_custom_config.config_filename != self.default_config_name
        assert cdh_with_custom_config.config_filename == custom_filename
        assert cdh_with_custom_config._hostname == self.json_config['machines']['cdh-launcher']['hostname']
        assert cdh_with_custom_config._hostport == self.json_config['machines']['cdh-launcher']['hostport']
        assert cdh_with_custom_config._username == self.json_config['machines']['cdh-launcher']['username']
        assert cdh_with_custom_config._key_filename == self.json_config['machines']['cdh-launcher']['key_filename']

    @mock.patch('paramiko.SSHClient', create=True)
    @mock.patch('paramiko.AutoAddPolicy', create=True)
    def test_create_and_close_SSHConnection(self, mock_policy, ssh_client):
        """ Checks is ssh connection created and closed properly """
        SSHClientMock = namedtuple('SSHClient', 'connect set_missing_host_key_policy close')
        ssh_client_mock = SSHClientMock(
            connect=mock.Mock(),
            set_missing_host_key_policy=mock.Mock(),
            close=mock.Mock()
        )
        ssh_client.return_value = ssh_client_mock
        mock_policy.return_value = mock.Mock()

        # execute
        self.cdhUtilities.create_ssh_connection(self.cdhUtilities._hostname, self.cdhUtilities._username,
                                                                  self.cdhUtilities._key_filename, self.cdhUtilities._key_password)
        self.cdhUtilities.close_ssh_connection()

        # attest
        assert ssh_client_mock.set_missing_host_key_policy.call_count == 1
        assert ssh_client_mock.connect.call_count == 1
        assert ssh_client_mock.close.call_count == 1
        assert mock_policy.call_count == 1
        ssh_client_mock.connect.assert_called_with(self.cdhUtilities._hostname, key_filename=self.cdhUtilities._key_filename,
                                                   password=self.cdhUtilities._key_password, username=self.cdhUtilities._username)
