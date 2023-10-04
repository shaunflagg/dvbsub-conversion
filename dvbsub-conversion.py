import subprocess
import os
import boto3

def lambda_handler(event, context):
    # Assuming the video is passed as an S3 URL in the event
    bucket_name = event['bucket_name']
    file_key = event['file_key']
    
    # Download the file from S3 to the Lambda's temp space
    s3 = boto3.client('s3')
    download_path = '/tmp/{}'.format(file_key)
    s3.download_file(bucket_name, file_key, download_path)
    
    # Use ccextractor to extract captions
    output_path = '/tmp/output.dvbsub'
    cmd = [
        './ccextractor',  # Assuming the ccextractor binary is in the Lambda root
        '-out=dvbsub',
        download_path,
        '-o', output_path
    ]
    
    try:
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        # Handle exception and logging
        return {
            'statusCode': 500,
            'body': e.output
        }
    
    # Upload the output to S3 or return as needed
    output_bucket_name = event['output_bucket_name']
    output_file_key = 'captions/{}'.format(os.path.basename(file_key))
    s3.upload_file(output_path, output_bucket_name, output_file_key)
    
    return {
        'statusCode': 200,
        'body': 'Captions generated and saved to: {}/{}'.format(output_bucket_name, output_file_key)
    }

