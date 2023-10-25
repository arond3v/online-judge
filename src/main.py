import docker
import os
import tarfile
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueServiceClient, QueueClient
import pymongo

import tarfile
import time
from io import BytesIO

import json

test_container = 10
mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
my_db = mongo_client['judge']
submissions = my_db['submissions']

docker_client = docker.from_env()
uri = 'https://.queue.core.windows.net/'

credential = DefaultAzureCredential()


my_queue = 'contest'
queue_client = QueueClient(
    account_url=uri, queue_name=my_queue, credential=credential)


containers = []


def process():
    codes = queue_client.receive_messages()
    if len(containers) < test_container:
        for code in codes:
            """
                in submissions collection:
                {
                    _id : message_id
                    status : probabaly testing
                    problem : problem name
                    compiler : language
                }
            """
            data = submissions.find_one({'_id': code.id})
            containers.append(code.id)
            print(data)
            # docker start
            container = docker_client.containers.create(
                data['compiler'] + '-judge', name=code.id, stdin_open=True, tty=True)
            os.system('for f in ./input/' + data['problem'] + '/*; do docker container cp $f ' +
                      code.id + ':/judge/input/; done')
            write_to_docker(container, code.content.encode('utf-8'))
            container.start()
            queue_client.delete_message(code)

    # polling check
    for id in containers:
        container = docker_client.containers.get(id)
        if container.status == 'exited':
            log = container.logs().decode('utf-8')
            print(log)
            data = json.loads(
                log, strict=False)
            submissions.update_one({'_id': id}, {'$set': data})
            containers.remove(id)
            os.system('docker container rm ' + id)


def write_to_docker(container, data, src='code.cpp', dest='/judge/'):
    tarstream = BytesIO()
    tar = tarfile.TarFile(fileobj=tarstream, mode='w')
    tarinfo = tarfile.TarInfo(name=src)
    tarinfo.size = len(data)
    tarinfo.mtime = time.time()
    tar.addfile(tarinfo, BytesIO(data))
    tar.close()
    tarstream.seek(0)
    r = container.put_archive(dest, tarstream)


if __name__ == '__main__':
    while True:
        process()
