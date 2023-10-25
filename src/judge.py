from pymongo import MongoClient
import docker
import json

import tarfile
import time
from io import BytesIO


mongo_client = MongoClient('mongodb://localhost:27017')

my_db = mongo_client['judge']

submissions = my_db['submissions']

docker_client = docker.from_env()
no_of_judge_container = 10

judge_containers = []


def judge():
    if len(judge_containers) < no_of_judge_container:
        """
            submission collection:
            {
                _id: message_id
                status: processing
                compiler:
                problem:
                test_case: {
                    t1: {
                        output:
                    }
                }
            }
        """
        for submission in submissions.find({'status': 'processing'}):
            container = docker_client.containers.create(
                'judge', name=submission['_id'], stdin_open=True, tty=True)
            judge_containers.append(submission['_id'])
            for key, test in submission['test_case'].items():
                if test['status'] == 'processing':
                    write_to_docker(
                        container, test['output'], src='input/'+key)
            container.start()
    # done-judging
    for id in judge_containers:
        container = docker_client.containers.get(id)
        if container.status == 'exited':
            submission = submissions.find_one({'_id': id})
            data = json.dumps(container.logs().decode('utf-8'))
            for key, val in data.items:
                submission['test_case'][key]['status'] = val
            submissions.update_one({'_id': id}, submission)
            judge_containers.remove(id)
            container.remove()


def write_to_docker(container, data, name='code.cpp', dest='/judge/'):
    tarstream = BytesIO()
    tar = tarfile.TarFile(fileobj=tarstream, mode='w')
    tarinfo = tarfile.TarInfo(name=name)
    tarinfo.size = len(data)
    tarinfo.mtime = time.time()
    tar.addfile(tarinfo, BytesIO(data))
    tar.close()
    tarstream.seek(0)
    r = container.put_archive(dest, tarstream)


if __name__ == '__main__':
    while True:
        judge()
