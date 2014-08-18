blackbird-sqs
=============

Get Amazon Simple Queue Service(SQS) CloudWatch Metrics.


What metrics this script get?
-----------------------------

### Metrics Table

| Metric Name                           | Statistics Type |
|---------------------------------------|-----------------|
| NumberOfMessagesSent                  | Sum             |
| SentMessageSize                       | Minumum         |
| SentMessageSize                       | Maximum         |
| SentMessageSize                       | Average         |
| SentMessageSize                       | Sum             |
| NumberOfMessagesReceived              | Sum             |
| NumberOfEmptyReceives                 | Sum             |
| NumberOfMessagesDeleted               | Sum             |
| ApproximateNumberOfMessagesDelayd     | Average         |
| ApproximateNumberOfMessagesVisible    | Average         |
| ApproximateNumberOfMessagesNotVisible | Average         |


Configurations
--------------

| Key Name                 | Default   | Type                        | Require | Notes                                    |
|--------------------------|-----------|-----------------------------|---------|------------------------------------------|
| aws\_region\_name        | us-east-1 | str                         | Yes     | AWS region name                          |
| aws\_access\_key\_id     | -         | str                         | Yes     | AWS access key id                        |
| aws\_secret\_access\_key | -         | str                         | Yes     | AWS secret access key                    |
| queue_name               | -         | str                         | Yes     | SQS queue name(as Cloudwatch dimentions) |
| hostname                 | -         | str                         | Yes     | hostname used in zabbix                  |
| module                   | -         | str                         | Yes     | You must specify `sqs` to module name    |
| ignore\_metrics          | -         | str(comma-separated values) | No      | Ignore metric names                      |


Notes
-----

If you don't want to get any metrics, you can use `ignore_metrics` option.

e.g: your `sqs.cfg` file
```
[SQS.QUEUE_NAME]
ignore_metrics = SentMessageSize, NumberOfMessagesReceived, NumberOfEmptyReceives
```
