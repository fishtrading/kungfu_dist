import boto3

import sys

s3 = boto3.resource('s3')
for bucket in s3.buckets.all():
	print(bucket.name)

filename = sys.argv[1]
print("file:",filename)
# Upload a new file
data = open(filename, 'rb')
s3.Bucket('wtkjdata').put_object(Key=filename, Body=data)

bucket = s3.Bucket("wtkjdata")
prefix = ""

for obj in bucket.objects.filter(Prefix=prefix):
	print('{0}:{1}'.format(bucket.name, obj.key))
