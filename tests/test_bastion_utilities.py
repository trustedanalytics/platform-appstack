from env_vars_fetcher.bastion_utilities import CFConfExtractor
import mock
import yaml

class TestSSHConnectionToBastion:

    @classmethod
    def setup_class(cls):
        cls.default_config_name = 'fetcher_config.yml'
        cls.json_config = {
            'openstack_env': True,
            'kerberos_used': True,
            'machines': {
                'cf-bastion': {
                    'hostname': '10.10.10.10',
                    'hostport': 22,
                    'username': 'centos',
                    'key_filename': 'key.pem',
                    'key_password': None,
                    'path_to_cf_tiny_yml': None,
                    'path_to_docker_vpc_yml': None
                },
                'cdh-manager-ip': ''
            }
        }

        mock_config_content = yaml.dump(cls.json_config)

        with mock.patch('__builtin__.open', mock.mock_open(read_data=mock_config_content), create=True) as m:
            cls.cfUtilities = CFConfExtractor()

    def test_create_without_arg_uses_default_filename(self):
        """ Checks is default file config used """
        assert self.cfUtilities.config_filename == self.default_config_name
        assert self.cfUtilities._hostname == self.json_config['machines']['cf-bastion']['hostname']
        assert self.cfUtilities._hostport == self.json_config['machines']['cf-bastion']['hostport']
        assert self.cfUtilities._username == self.json_config['machines']['cf-bastion']['username']
        assert self.cfUtilities._key_filename == self.json_config['machines']['cf-bastion']['key_filename']

    def test_check_is_smtp_protocol_for_smtp_port(self):
        """ Checks is smtp protocol chosen if port is 25, 587 or 2525"""
        assert 'smtp' == self.cfUtilities._determine_smtp_protocol(25)
        assert 'smtp' == self.cfUtilities._determine_smtp_protocol(587)
        assert 'smtp' == self.cfUtilities._determine_smtp_protocol(2525)

    def test_check_is_smtps_protocol_for_smtps_port(self):
        """ Checks is smtps protocol used for 465 port """
        assert 'smtps' == self.cfUtilities._determine_smtp_protocol(465)

    def test_check_is_not_returned_protocol_for_unknown_custom_port(self):
        """ Checks is not determined protocol if port is not standard """
        assert None == self.cfUtilities._determine_smtp_protocol(111111)

