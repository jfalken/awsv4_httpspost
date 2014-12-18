''' library used to sign POST requests using Amazon v4
    some examples and samples:
    (primarily):
      http://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-authentication-HTTPPOST.html
      http://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-post-example.html
      http://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-HTTPPOSTForms.html

    (others):
      http://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-authentication-HTTPPOST.html
      http://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html
      http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python

    (examples for testing):
      http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html
      http://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-post-example.html
'''

import hmac
import json
import hashlib

def hmac_sha256(key, msg):
    ''' HMAC signs 'msg' using 'key'.
        docs: http://docs.aws.amazon.com/AmazonS3/latest/API/sig-v4-authenticating-requests.html

        :param key: string of key to use for signing.
        :param msg: message to sign

        returns digest of sha-256 signature
    '''
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def get_signing_key(aws_secret_access_key, date_stamp, regionName, serviceName):
    ''' Creates a signature key, as per the process outlined in:
        http://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-authentication-HTTPPOST.html

        :param aws_secret_access_key: aws secret access key
        :param date_stamp: todays date, in yyyymmdd format
        :regionName: region where this is valid, eg 'us-east-1'
        :serviceName: service name, eg 's3'.

        returns a signing key
    '''
    date_key = hmac_sha256(('AWS4' + aws_secret_access_key).encode('utf-8'), date_stamp)
    date_region_key = hmac_sha256(date_key, regionName)
    date_region_service_key = hmac_sha256(date_region_key, serviceName)
    signing_key = hmac_sha256(date_region_service_key, 'aws4_request')
    return signing_key


def gen_policy(expiry_date_string, bucket_name, key_name,
               aws_access_key, signing_date, region):
    ''' Generates a POST policy for an s3 bucket
        docs: http://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-HTTPPOSTConstructPolicy.html

        :param expiry_date_string: expiration of the upload in ISO format
                       ie, datetime.strptime('2014-12-31', '%Y-%m-%d').isoformat() + 'Z'

        :param bucket_name: name of the s3 bucket where the upload is stored
        :param key_name: keyname of the upload (ie, directory)
        :param signing_date: date used in creating signing key (eg '20141212')
        :param region: region where this is valid; eg 'us-east-1'

        returns base64 json of policy
        '''

    x_amz_credential = '%s/%s/%s/s3/aws4_request' % (aws_access_key, signing_date, region)

    policy = {'expiration' : expiry_date_string,
              'conditions': [{'bucket': bucket_name},
                            ['starts-with', '$key', key_name + '/'],
                            {'acl': 'private'},
                            {'x-amz-credential': x_amz_credential},
                            {'x-amz-algorithm': 'AWS4-HMAC-SHA256'},
                            {'x-amz-date': signing_date + 'T000000Z'}
                            ]
              }
    return json.dumps(policy).encode('utf-8').encode('base64').replace('\n','')

