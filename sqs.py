#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fetch SQS metrics of cloudwatch.
"""

import datetime

from boto.ec2 import cloudwatch

from blackbird.plugins import base


class ConcreteJob(base.JobBase):

    def __init__(self, options, queue=None, logger=None):
        super(ConcreteJob, self).__init__(options, queue, logger)
        self.metrics_config = [
            {'NumberOfMessageSent': 'Sum'},
            {'SentMessageSize': 'Minimum'},
            {'SentMessageSize': 'Maximum'},
            {'SentMessageSize': 'Average'},
            {'SentMessageSize': 'Sum'},
            {'NumberOfMessagesReceived': 'Sum'},
            {'NumberOfEmptyReceives': 'Sum'},
            {'NumberOfMessagesDeleted': 'Sum'},
            {'ApproximateNumberOfMessagesDelayed': 'Average'},
            {'ApproximateNumberOfMessagesVisible': 'Average'},
            {'ApproximateNumberOfMessagesNotVisible': 'Average'},
        ]

    def _enqueue(self, item):
        self.queue.put(item, block=False)
        self.logger.debug(
            'Inseted to queue {key}:{value}'
            ''.format(
                key=item.key,
                value=item.value
            )
        )

    def _create_connection(self):
        conn = cloudwatch.connect_to_region(
            self.options.get('aws_region_name'),
            aws_access_key_id=self.options.get(
                'aws_access_key_id'
            ),
            aws_secret_access_key=self.options.get(
                'aws_secret_access_key'
            )
        )
        return conn

    def _fetch_statistics(self):
        conn = self._create_connection()
        result = dict()

        period = int(self.options.get('interval', 300))
        if period <= 60:
            period = 60
            delta_seconds = 120
        else:
            delta_seconds = period
        end_time = datetime.datetime.utcnow()
        start_time = end_time - datetime.timedelta(
            seconds=delta_seconds
        )
        dimensions = {
            'QueueName': self.options.get('queue_name')
        }

        for entry in self.metrics_config:
            for metric_name, statistics in entry.items():
                if (
                    metric_name not in
                    self.options.get('ignore_metrics', list())
                ):
                    stat = conn.get_metric_statistics(
                        period=period,
                        start_time=start_time,
                        end_time=end_time,
                        metric_name=metric_name,
                        namespace='AWS/SQS',
                        statistics=statistics,
                        dimensions=dimensions
                    )
                    key = '{0}.{1}'.format(
                        metric_name,
                        statistics
                    )
                    if len(stat) > 0:
                        result[key] = str(stat[0][statistics])
                    else:
                        result[key] = None

        conn.close()
        return result

    def build_items(self):
        """
        Main loop.
        """
        raw_items = self._fetch_statistics()
        hostname = self.options.get('hostname')

        for key, raw_value in raw_items.iteritems():
            if raw_value is None:
                value = 0
            else:
                value = raw_value

            item = SQSItem(
                key=key,
                value=value,
                host=hostname
            )
            self._enqueue(item)


class Validator(base.ValidatorBase):
    """
    Validate configuration object.
    """

    def __init__(self):
        self.__spec = None

    @property
    def spec(self):
        self.__spec = (
            "[{0}]".format(__name__),
            "aws_access_key_id = string()",
            "aws_secret_access_key = string()",
            "aws_region_name = string(default=us-east-1)",
            "queue_name = string()",
            "hostname = string()",
            "ignore_metrics = list(default=list())",
            "interval = 300"
        )
        return self.__spec


class SQSItem(base.ItemBase):
    """
    Enqueued item.
    """

    def __init__(self, key, value, host):
        super(SQSItem, self).__init__(key, value, host)

        self.__data = dict()
        self._generate()

    @property
    def data(self):
        """
        Dequeued data.
        """
        return self.__data

    def _generate(self):
        self.__data['key'] = 'cloudwatch.sqs.{0}'.format(self.key)
        self.__data['value'] = self.value
        self.__data['host'] = self.host
        self.__data['clock'] = self.clock


if __name__ == '__main__':
    import json
    OPTIONS = {
        'aws_region_name': 'us-east-1',
        'aws_access_key_id': 'YOUR_AWS_ACCESS_KEY_ID',
        'aws_secret_access_key': 'YOUR_AWS_SECRET_ACCESS_KEY',
        'queue_name': 'YOUR_QUEUE_NAME',
        'ignore_metrics': list(),
        'interval': 300
    }
    JOB = ConcreteJob(
        options=OPTIONS
    )
    print json.dumps(JOB._fetch_statistics())
