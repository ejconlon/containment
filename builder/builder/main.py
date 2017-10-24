from collections import OrderedDict
import docker
import os
import shutil
import yaml


ROOT = 'amazonlinux:latest'
BASE = 'base'
CONTAINMENT = 'containment'
COLLECTION = '{}/collection.yml'.format(CONTAINMENT)


def build_order(images, name):
    o = OrderedDict()
    cur = name
    while True:
        body = images[cur]
        if 'extends' in body:
            o[cur] = 1
            nex = body['extends']
            assert nex not in o
            cur = nex
        else:
            break
    return (cur, list(reversed(o.keys())))


class Builder:
    @classmethod
    def from_env(cls):
        client = docker.from_env()
        with open(COLLECTION, 'r') as f:
            collection = yaml.load(f)
        return cls(client, collection)

    def __init__(self, client, collection):
        self.client = client
        self.collection = collection

    def validate(self):
        images = self.collection['images']
        for (name, body) in images.items():
            print('validating attributes for {}'.format(name))
            if 'imports' in body:
                assert 'extends' not in body
                path = os.path.join(CONTAINMENT, 'custom', name, 'Dockerfile')
                assert os.path.isfile(path)
                with open(path, 'r') as f:
                    lines = f.readlines()
                assert 'FROM {}\n'.format(body['imports']) in lines
            else:
                assert body['extends'] in images
                assert len(body['roles']) > 0
                for role in body['roles']:
                    path = os.path.join(CONTAINMENT, 'roles', role, 'tasks.yml')
                    assert os.path.isfile(path)
        for (name, body) in images.items():
            print('validating order for {}'.format(name))
            (b, es) = build_order(images, name)
            if 'imports' in body:
                assert b == name
                assert len(es) == 0
            else:
                assert b in images
                assert 'imports' in images[b]
                assert es[-1] == name
        for ctx in ['docker', 'aws']:
            if ctx in self.collection:
                print('validating context: {}'.format(ctx))
                c = self.collection[ctx]
                roles = c.get('pre_roles', [])
                roles.extend(c.get('pre_roles', []))
                for role in roles:
                    path = os.path.join(CONTAINMENT, 'roles', role, 'tasks.yml')
                    assert os.path.isfile(path)

    def pull_all(self):
        pulled = set()
        for body in self.collection['images'].values():
            if 'imports' in body:
                imports = body['imports']
                if imports not in pulled:
                    print('pulling {}'.format(imports))
                    self.client.images.pull(imports)
                    pulled.add(imports)

    def build(self, org, image):
        gen = os.path.join(CONTAINMENT, 'gen')
        shutil.rmtree(gen, ignore_errors=True)
        os.mkdir(gen)
        images = self.collection['images']
        (b, es) = build_order(images, image)
        for name in es:
            print('generating layer: {}'.format(name))
            subgen = os.path.join(gen, name)
            os.mkdir(subgen)
            body = images[name]
            if 'docker' in self.collection:
                d = self.collection['docker']
                roles = d.get('pre_roles', [])
                roles.extend(body['roles'])
                roles.extend(d.get('post_roles', []))
            else:
                roles = body['roles']
            dockerfile = [
                'ARG ORG',
                'FROM $ORG/base',
                'COPY util/playbook.sh /context/util/playbook.sh'
            ]
            for role in roles:
                copy = 'COPY roles/{0} /context/roles/{0}'.format(role)
                dockerfile.append(copy)
            run = 'RUN ROLES="{}" /context/util/playbook.sh && rm -rf /context'.format(' '.join(roles))
            dockerfile.append(run)
            if 'ports' in body:
                for port in body['ports'].values():
                    expose = 'EXPOSE {}'.format(port)
                    dockerfile.append(expose)
            if 'command' in body:
                cmd = 'CMD {}'.format(body['command'])
                dockerfile.append(cmd)
            contents = '\n'.join(dockerfile) + '\n'
            sink = os.path.join(subgen, 'Dockerfile')
            with open(sink, 'w') as f:
                f.write(contents)
        buildargs = {'ORG': org}
        if True:
            print('building base: {}'.format(b))
            tag = '{}/{}'.format(org, b)
            dockerfile = os.path.join('custom', b, 'Dockerfile')
            self.client.images.build(
                path=CONTAINMENT,
                dockerfile=dockerfile,
                tag=tag,
                buildargs=buildargs)
        for name in es:
            print('building layer: {}'.format(name))
            tag = '{}/{}'.format(org, name)
            dockerfile = os.path.join('gen', name, 'Dockerfile')
            self.client.images.build(
                path=CONTAINMENT,
                dockerfile=dockerfile,
                tag=tag,
                buildargs=buildargs)

# builder = Builder.from_env()
# builder.validate()
# builder.pull_all()
