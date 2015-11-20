from collections import namedtuple
import xml.etree.ElementTree as ET
from env_vars_fetcher.cdh_utilities import CdhConfExtractor
import mock
import yaml


class TestSSHConnectionToCdh:

    default_config_name = 'fetcher_config.yml'
    json_config = {
        'is_openstack_env': 'true',
        'is_kerberos': 'true',
        'machines': {
            'cdh-launcher': {
                'hostname': '10.10.10.10',
                'hostport': 22,
                'username': 'centos',
                'key_filename': 'key.pem',
                'key_password': None
            },
            'cdh-manager-ip': ''
        }
    }

    @mock.patch('__builtin__.open', create=True)
    def test_createObjectWithoutArgShouldUseDefaultFilename(self, mock_open):

        mock_config_content = yaml.dump(self.json_config)

        mock_open.side_effect = [
            mock.mock_open(read_data=mock_config_content).return_value
        ]

        cdh = CdhConfExtractor()

        assert cdh.config_filename == self.default_config_name
        assert cdh._hostname == self.json_config['machines']['cdh-launcher']['hostname']
        assert cdh._hostport == self.json_config['machines']['cdh-launcher']['hostport']
        assert cdh._username == self.json_config['machines']['cdh-launcher']['username']
        assert cdh._key_filename == self.json_config['machines']['cdh-launcher']['key_filename']

    @mock.patch('__builtin__.open', create=True)
    def test_createObjectWithoutArgUseFilenameFromArg(self, mock_open):
        custom_filename = "customConfig.yml"
        mock_config_content = yaml.dump(self.json_config)

        mock_open.side_effect = [
            mock.mock_open(read_data=mock_config_content).return_value
        ]

        cdh = CdhConfExtractor(custom_filename)

        assert cdh.config_filename != self.default_config_name
        assert cdh.config_filename == custom_filename
        assert cdh._hostname == self.json_config['machines']['cdh-launcher']['hostname']
        assert cdh._hostport == self.json_config['machines']['cdh-launcher']['hostport']
        assert cdh._username == self.json_config['machines']['cdh-launcher']['username']
        assert cdh._key_filename == self.json_config['machines']['cdh-launcher']['key_filename']

    @mock.patch('__builtin__.open', create=True)
    @mock.patch('paramiko.SSHClient', create=True)
    @mock.patch('paramiko.AutoAddPolicy', create=True)
    def test_createAndCloseSSHConnection(self, mock_policy, ssh_client, mock_open):

        # prepare
        mock_config_content = yaml.dump(self.json_config)

        mock_open.side_effect = [
            mock.mock_open(read_data=mock_config_content).return_value
        ]

        SSHClientMock = namedtuple('SSHClient', 'connect set_missing_host_key_policy close')
        ssh_client_mock = SSHClientMock(
            connect=mock.Mock(),
            set_missing_host_key_policy=mock.Mock(),
            close=mock.Mock()
        )
        ssh_client.return_value = ssh_client_mock

        mock_policy.return_value = mock.Mock()

        # execute
        cdh = CdhConfExtractor()
        cdh.create_ssh_connection_to_cdh()
        cdh.close_connection_to_cdh()

        # attest
        assert ssh_client_mock.set_missing_host_key_policy.call_count == 1
        assert ssh_client_mock.connect.call_count == 1
        assert ssh_client_mock.close.call_count == 1
        assert mock_policy.call_count == 1
        ssh_client_mock.connect.assert_called_with(cdh._hostname, key_filename=cdh._key_filename,
                                                   password=cdh._key_password, username=cdh._username)

    @mock.patch('__builtin__.open', create=True)
    @mock.patch('xml.etree.ElementTree.parse', create=True)
    def test_XmlToJsonConverter(self, xml_etree_mock, mock_open):

        xml_string = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><configuration>" \
                     "<property><name>a</name><value>a1</value></property>" \
                     "<property><name>b</name><value>b1</value></property>" \
                     "<property><name>$.a</name><value>cdh-master</value></property>" \
                     "</configuration>"
        expected_json = {
            'a': 'a1',
            'b': 'b1',
            '\$.a': 'cdh-master'
        }

        mock_config_content = yaml.dump(self.json_config)

        mock_open.side_effect = [
            mock.mock_open(read_data=mock_config_content).return_value
        ]

        XmlMock = namedtuple('XmlMock', 'getroot')
        xml_mock = XmlMock(
            getroot=mock.Mock(return_value=ET.fromstring(xml_string))
        )
        xml_etree_mock.return_value = xml_mock

        cdh = CdhConfExtractor()

        result_json = cdh._xml_to_json_converter('xmlfile')

        assert expected_json == result_json