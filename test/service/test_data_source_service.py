import unittest
from unittest.mock import patch

from spaceone.core.unittest.result import print_data
from spaceone.core.unittest.runner import RichTestRunner
from spaceone.core import config
from spaceone.core.transaction import Transaction
from spaceone.monitoring.connector.google_cloud_connector import GoogleCloudConnector
from spaceone.monitoring.service.data_source_service import DataSourceService
from spaceone.monitoring.info.data_source_info import PluginInfo


class TestDataSourceService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        config.init_conf(package='spaceone.monitoring')
        cls.transaction = Transaction({
            'service': 'monitoring',
            'api_class': 'DataSource'
        })
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()

    @patch.object(GoogleCloudConnector, '__init__', return_value=None)
    def test_init_data_source(self, *args):
        params = {
            'options': {}
        }

        self.transaction.method = 'init'
        data_source_svc = DataSourceService(transaction=self.transaction)
        response = data_source_svc.init(params.copy())
        print_data(response, 'test_init_data_source')
        PluginInfo(response)

    @patch.object(GoogleCloudConnector, '__init__', return_value=None)
    @patch.object(GoogleCloudConnector, 'set_connect', return_value=None)
    def test_verify_data_source(self, *args):
        params = {
            'options': {},
            'secret_data': {}
        }

        self.transaction.method = 'verify'
        data_source_svc = DataSourceService(transaction=self.transaction)
        for response in data_source_svc.verify(params.copy()):
            print_data(response, 'test_verify_data_source')


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
