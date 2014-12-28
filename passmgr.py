import argparse
import json
from lockfile import FileLock
import os
from random import choice
import string

def create_pass(length):
    chars = string.letters + string.digits + '&<>:|.,()[]{}'

    return ''.join(choice(chars) for _ in range(length))


lock_path = '/tmp/passdb.lock'
def lock_db(func):
    def wrapper(self, *args, **kwargs):
        with FileLock(lock_path) as lock:
            return func(self, *args, **kwargs)
    return wrapper


class DbEditor(object):
    def __init__(self, data):
        self.data = data

    def set_password(self, id_, password, overwrite=False):
        pass_data = self.data['passwords']
        if id_ in pass_data and not overwrite:
            raise ValueError("%s exists and overwrite is not set" % id_)
        pass_data[id_] = password
        self.data['version'] = self.data['version'] + 1

    def get_password(self, id_):
        try:
            return self.data[id_]
        except KeyErro:
            raise ValueError("%s does not exist as a password id" % id_)

    def __str__(self):
        return json.dumps(self.data, sort_keys=True, indent=4,
                          separators=(',', ': '))


class Db(object):
    def __init__(self, path):
        self.path = path
        self._ensure_db_exists()

    @lock_db
    def set_password(self, id_, password, overwrite=False):
        editor = self._inflate_db()
        editor.set_password(id_, password, overwrite)
        self._deflate_db(editor)

    @lock_db
    def get_password(self, id_):
        try:
            return self._inflate_db().get_password(id_)
        except KeyError:
            raise ValueError("%s not found in db" % id_)

    @lock_db
    def _ensure_db_exists(self):
        if not os.path.isfile(self.path):
            editor = DbEditor({"schema": "passdb-1",
                               "version": 1,
                               "passwords": {}})
            self._deflate_db(editor)

    def _inflate_db(self):
        with open(self.path, 'r') as f:
            data = json.load(f)
        if data.get('schema', '') != 'passdb-1':
            raise ValueError("Invalid database schema")
        version = data.get('version', 0)
        if not isinstance(version, int) or version < 1:
            raise ValueError("Invalid database version")
        return DbEditor(data)

    def _deflate_db(self, editor):
        with open(self.path, 'w') as f:
            f.write(str(editor))
            f.flush()
            os.fsync(f.fileno())


def help():
    print("usage: %s [db_path]")


if __name__=='__main__':
    parser = argparse.ArgumentParser(prog='passmgr.py')
    parser.add_argument('--db', type=str, required=True,
                        help='Path to database')
    op_subparsers = parser.add_subparsers(dest='op',
                                          help='operation to perform')

    op_add_parser = op_subparsers.add_parser('add', help='Add a password')
    op_add_parser.add_argument('-overwrite', action='store_true',
                               help='Overwrite an existing password')
    op_add_parser.add_argument('name', type=str, help='Name for password')
    op_add_parser.add_argument('password', type=str, help='Password to add')

    op_get_parser = op_subparsers.add_parser('get', help='Get a password')
    op_get_parser.add_argument('name', type=str, help='Name for password')

    res = parser.parse_args()

    db = Db(res.db)
    if res.op == 'add':
        db.set_password(res.name, res.password)
    elif res.op == 'get':
        print(db.get_password(res.name))
