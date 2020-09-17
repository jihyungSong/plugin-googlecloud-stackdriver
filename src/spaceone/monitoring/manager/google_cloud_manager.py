import logging
import time

from spaceone.core.manager import BaseManager
from spaceone.monitoring.error import *
from spaceone.monitoring.connector.google_cloud_connector import GoogleCloudConnector
_LOGGER = logging.getLogger(__name__)

_STAT_MAP = {
    'AVERAGE': 'Average',
    'MAX': 'Maximum',
    'MIN': 'Minimum',
    'SUM': 'Sum'
}


class GoogleCloudManager(BaseManager):
    gcp_connector = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def verify(self, options, secret_data):
        """ Check connection
        """
        self.google_cloud_connector = self.locator.get_connector('StackDriver')
        r = self.google_cloud_connector.verify(options, secret_data)
        # ACTIVE/UNKNOWN
        return r

    def set_connector(self, secret_data):
        self.gcp_connector: GoogleCloudConnector = self.locator.get_connector('GoogleCloudConnector')
        self.gcp_connector.get_connect({}, secret_data)

    def list_metrics(self, options, secret_data):
        namespace, dimensions = self._get_cloudwatch_query(resource)

        self.aws_connector.create_session(options, secret_data)
        return self.aws_connector.list_metrics(namespace, dimensions)

    def get_metric_data(self, options, secret_data, resource, metric, start, end, period, stat):
        if 'region_name' in resource:
            secret_data['region_name'] = resource.get('region_name')

        namespace, dimensions = self._get_cloudwatch_query(resource)

        if period is None:
            period = self._make_period_from_time_range(start, end)

        stat = self._convert_stat(stat)

        self.aws_connector.create_session(options, secret_data)
        return self.aws_connector.get_metric_data(namespace, dimensions, metric, start, end, period, stat)

    @staticmethod
    def _convert_stat(stat):
        if stat is None:
            stat = 'AVERAGE'

        if stat not in _STAT_MAP.keys():
            raise ERROR_NOT_SUPPORT_STAT(supported_stat=' | '.join(_STAT_MAP.keys()))

        return _STAT_MAP[stat]

    @staticmethod
    def _make_period_from_time_range(start, end):
        start_time = int(time.mktime(start.timetuple()))
        end_time = int(time.mktime(end.timetuple()))
        time_delta = end_time - start_time

        # Max 60 point in start and end time range
        if time_delta <= 60*60:         # ~ 1h
            return 60
        elif time_delta <= 60*60*6:     # 1h ~ 6h
            return 60*10
        elif time_delta <= 60*60*12:    # 6h ~ 12h
            return 60*20
        elif time_delta <= 60*60*24:    # 12h ~ 24h
            return 60*30
        elif time_delta <= 60*60*24*3:  # 1d ~ 2d
            return 60*60
        elif time_delta <= 60*60*24*7:  # 3d ~ 7d
            return 60*60*3
        elif time_delta <= 60*60*24*14:  # 1w ~ 2w
            return 60*60*6
        elif time_delta <= 60*60*24*14:  # 2w ~ 4w
            return 60*60*12
        else:                            # 4w ~
            return 60*60*24

    @staticmethod
    def _get_cloudwatch_query(resource):
        return resource.get('namespace'), resource.get('dimensions')