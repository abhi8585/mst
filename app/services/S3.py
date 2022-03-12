from decouple import config
from botocore.client import Config as BotoConfig
import json, requests,sys,boto3,tempfile,uuid

class FileUploadService:
    # _init_ function to initialize boto3 client 
    def __init__(self):
        try:
            self.client=boto3.resource('s3',
                            endpoint_url=config('AWS_ENDPOINT_URL'),
                            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
                            config=BotoConfig(signature_version='s3v4'),
                            region_name='us-east-1')
        except Exception as e:
            return {'error':e}
    
    # funtion to Upload file
    def upload(self,file,bucket):
        try:
            filename = '{}.{}'.format(uuid.uuid4(),file.filename.split('.')[-1]) #saving filename in uuid format
            path='{}/{}'.format(tempfile.gettempdir(),filename)
            file.save(path)
            self.client.Bucket(bucket).upload_file(path,filename)
            return "{}/{}/{}".format(config('AWS_ENDPOINT_URL'),bucket,filename)
        except Exception as e:
            return {'error':e}
    # function to download file
    def download(self,filename,bucket):
        try:
            path=tempfile.gettempdir()
            path=path+'/'+filename
            self.client.Bucket(bucket).download_file(filename,path)
            return "{}".format(path)
        except Exception as e:
            raise Exception (e)
            return -1
    

    
