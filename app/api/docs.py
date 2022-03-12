from flask_restplus import Namespace, fields, reqparse, Resource
api_namespace = Namespace('docs', description="Docs API", path='/docs')
from decouple import config
import boto3
from botocore.client import Config as BotoConfig
import json
QUERY_PARAMS = reqparse.RequestParser()

@api_namespace.route("/<page_id>")
@api_namespace.doc(params={'page_id': 'page no.'})
class Docs(Resource):

    def __init__(self, *args, **kwargs):
        s3=boto3.client('s3',
                            endpoint_url=config('AWS_ENDPOINT_URL'),
                            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
                            config=BotoConfig(signature_version='s3v4'),
                            region_name='us-east-1')
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket='dp-docs',PaginationConfig={'PageSize': 10}) #chanag the Page size value for perpage result
        self.pages_list=[page for page in pages]


    def get(self,page_id):
        page_id=int(page_id)
        if page_id<0 or page_id>=len(self.pages_list):
            return json.dumps({"message":"Page Id out of Bound"}),400
        resp=dict()
        resp['data']=list()
        resp['message']='success'
        for page in self.pages_list[page_id]['Contents']:
            #print(page['Key'])
            resp['data'].append("{}/{}/{}".format(config('AWS_ENDPOINT_URL'),"dp-docs",page['Key']))
        return json.dumps(resp),201



     

