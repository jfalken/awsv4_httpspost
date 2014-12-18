# AWS v4 HTTPS POST Presigned URLs

This library was created to assist in creating pre-signed URLs using v4 of the AWS signing method.

## Background

AWS provides alot of examples on how to do this; however I had a hard time getting this to work properly and understand the proper syntax. The date format needed varies in different spots, and some areas use base64 encoding while others use hex. 

This library and this readme is an attempt to better document the encodings and formats required for this to work properly.

This high level process is described [here](http://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-authentication-HTTPPOST.html).

## Usage

### Generating a HTTPS POST Policy

```python
from awsv4_httpspost import gen_policy
from datetime import datetime

# expiration date
exp = datetime.strptime('2014-12-31', '%Y-%m-%d').isoformat() + 'Z'

# a 'folder'/key of where to place all uploads
keynamne_preface = 'uploads'

# signing date (date_stamp) format
date_stamp = datetime.utcnow().strftime('%Y%m%d')

bucket_name = 'jfalken'
region = 'us-east-1'
aws_access_key = access key (not secret)

policy = gen_policy(exp, bucket_name, keyname_preface, aws_access_key, date_stamp, region)
```

The returned policy will be base64 encoded

### Generating a Signing Key

```python
from awsv4_httpspost import get_signing_key

secret_key = aws secret key
service = 's3'

signing_key = get_signing_key(secret_key, date_stamp, region, service)
```

Signing key will be raw bytes

### Generate Signature

The policy must be signed by the signing key. Then, on an HTTPS POST, the policy (in base64) must be uploaded along with the signature **(in hex)**
```python
from awsv4_httpspost import hmac_sha256

signature = hmac_sha256(signing_key, policy)
signature_hex = signature.encode('hex')
```

`signature_for_post` is what you would place in your HTTPS POST form; shown below

### POST FORM

Example POST form; variables are shown as in a template format.

```html
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  </head>
  <body>
  
  <form action="https://{{bucket_name}}.s3.amazonaws.com/" method="post" enctype="multipart/form-data">
    <input type="hidden"  name="key" value="uploads/${filename}"/><br />
    <input type="hidden" name="acl" value="private" /><br/>
    <input type="hidden"   name="x-amz-credential" value="{{aws access key}}/{{date_stamp}}/{{region}}/{{service}}/aws4_request" />
    <input type="hidden"   name="x-amz-algorithm" value="AWS4-HMAC-SHA256" />
    <input type="hidden"   name="x-amz-date" value="{{date_stamp}}T000000Z" />
    <input type="hidden" name="policy" value="{{policy}}"/>
    <input type="hidden" name="x-amz-signature" value="{{signature_hex}}" />
    File: 
    <input type="file"   name="file" /> <br />
    <input type="submit" name="submit" value="Upload to Amazon S3" />
  </form>
</html>
```

## Testing Yourself

You can test to confirm your signatures are being calculated properly via the examples provided here:

      http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html
      http://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-post-example.html

