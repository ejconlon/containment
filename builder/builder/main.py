import argparse
import boto3
from collections import OrderedDict
import docker
import json
import os
import shutil
import yaml


DEFAULT_CONTAINMENT = 'containment'


class BuilderState:
    def __init__(self):
        self.done_imports = set()
        self.done_images = set()


class Builder:
    @classmethod
    def from_env(cls, containment):
        with open(os.path.join(containment, 'collection.yml'), 'r') as f:
            collection = yaml.load(f)
        state = BuilderState()
        return cls(containment, collection, state)

    def __init__(self, containment, collection, state):
        self.containment = containment
        self.collection = collection
        self.state = state

    def clear_state(self):
        self.state = BuilderState()

    def build_order(self, name):
        o = OrderedDict()
        cur = name
        while True:
            body = self.collection['images'][cur]
            if 'extends' in body:
                o[cur] = 1
                nex = body['extends']
                assert nex not in o
                cur = nex
            else:
                break
        return (cur, list(reversed(o.keys())))

    def validate_start(self):
        images = self.collection['images']
        for (name, body) in images.items():
            print('validating attributes for {}'.format(name))
            if 'imports' in body:
                assert 'extends' not in body
                assert 'roles' not in body
                assert 'vars' not in body
                path = os.path.join(self.containment, 'custom', name, 'Dockerfile')
                assert os.path.isfile(path)
                with open(path, 'r') as f:
                    lines = f.readlines()
                assert 'FROM {}\n'.format(body['imports']) in lines
            else:
                assert body['extends'] in images
                assert len(body['roles']) > 0
                for role in body['roles']:
                    path = os.path.join(self.containment, 'roles', role, 'tasks.yml')
                    assert os.path.isfile(path)
                if 'vars' in body:
                    for role in body['vars'].keys():
                        assert role in body['roles']
        for (name, body) in images.items():
            print('validating order for {}'.format(name))
            (b, es) = self.build_order(name)
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
                roles.extend(c.get('post_roles', []))
                roles.extend(c.get('required_roles', []))
                for role in roles:
                    path = os.path.join(self.containment, 'roles', role, 'tasks.yml')
                    assert os.path.isfile(path)

    def generate_all(self):
        gen = os.path.join(self.containment, 'gen')
        shutil.rmtree(gen, ignore_errors=True)
        os.mkdir(gen)
        for (name, body) in self.collection['images'].items():
            if 'imports' in body:
                continue
            print('generating layer: {}'.format(name))
            subgen = os.path.join(gen, name)
            os.mkdir(subgen)
            if 'docker' in self.collection:
                d = self.collection['docker']
                roles = d.get('pre_roles', [])
                roles.extend(body['roles'])
                roles.extend(d.get('post_roles', []))
            else:
                roles = body['roles']
            dockerfile = [
                'ARG ORG',
                'FROM $ORG/{}'.format(body['extends']),
                'COPY util/playbook.sh /context/util/playbook.sh'
            ]
            for role in roles:
                copy = 'COPY roles/{0} /context/roles/{0}'.format(role)
                dockerfile.append(copy)
            if 'vars' in body:
                varz = body['vars']
            else:
                varz = {}
            run = "RUN ROLES='{}' VARS='{}' /context/util/playbook.sh && rm -rf /context".format(' '.join(roles), json.dumps(varz))
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

    def validate_generated(self):
        for (name, body) in self.containment['images'].items():
            print('validating generated for {}'.format(name))
            raise Exception('TODO')

    def pull(self, client, imports):
        if imports not in self.state.done_imports:
            print('pulling imports {}'.format(imports))
            client.images.pull(imports)
            self.state.done_imports.add(imports)
        else:
            print('skipping imports {}'.format(imports))

    def pull_all(self, client, state):
        for body in self.collection['images'].values():
            if 'imports' in body:
                self.pull(client, body['imports'])

    def build_without_deps(self, client, org, image_name):
        if image_name not in self.state.done_images:
            print('building image {}'.format(image_name))
            body = self.collection['images'][image_name]
            tag = '{}/{}'.format(org, image_name)
            buildargs = {'ORG': org}
            if 'imports' in body:
                loc = 'custom'
                self.pull(client, body['imports'])
            else:
                loc = 'gen'
            dockerfile = os.path.join(loc, image_name, 'Dockerfile')
            print('client build {}'.format(image_name))
            client.images.build(
                path=self.containment,
                dockerfile=dockerfile,
                tag=tag,
                buildargs=buildargs)
            self.state.done_images.add(image_name)
        else:
            print('skipping image {}'.format(image_name))

    def build(self, client, org, image_name):
        (base, layers) = self.build_order(image_name)
        print('building deps for {}'.format(image_name))
        self.build_without_deps(client, org, base)
        for layer in layers:
            self.build_without_deps(client, org, layer)

    def build_all(self, client, org):
        print('building all')
        for name in self.collection['images']:
            self.build(client, org, name)


def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--containment', default=DEFAULT_CONTAINMENT)
    parser.add_argument('--org')
    return parser


def main(args):
    builder = Builder.from_env(args.containment)
    builder.validate_start()
    builder.generate_all()
    client = docker.from_env()
    builder.build_all(client, args.org)


if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()
    main(args)
