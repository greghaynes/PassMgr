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

    def set_password(self, id_, passwd, overwrite=False):
        pass_data = self.data['data']
        if id_ in pass_data and not overwrite:
            raise ValueError("%s exists and overwrite is not set" % id_)
        pass_data[id_] = password
        pass_data['version'] = pass_data['version'] + 1

    def get_password(self, id_):
        try:
            return self.data[id_]
        except KeyErro:
            raise ValueError("%s does not exist as a password id" % id_)

    def __str__(self):
        return json.dumps(self.data, sort_keys=True)


class Db(object):
    def __init__(self, path):
        self.path = path
        self._ensure_db_exists()

    @lock_db
    def set_password(self, id_, password, overwrite=False):
        editor = self._inflate_db()

    @lock_db
    def get_password(self, id_):
        try:
            return self._inflate_db().get_password(id_)
        except KeyError:
            raise ValueError("%s not found in db" % id_)

    @lock_db
    def _ensure_db_exists(self):
        if not os.path.isfile(self.path):
            editor = editor({"schema": "passdb", "version": 0, "data": {}})
            self._deflate_db(editor)

    def _inflate_db(self):
        with open(self.path, 'r') as f:
            data = json.load(f)
        if data.get('schema', '') != 'passdb':
            raise ValueError("Invalid database schema")
        version = data.get('version', 0)
        if not isinstance(version, int) or version < 1:
            raise ValueError("Invalid database version")
        return DbEditor(data)

    def _deflate_db(self, editor):
        with open(self.path, 'w') as f:
            f.write(editor.dumps())


if __name__=='__main__':
    db = Db('/home/greghaynes/passdb')
    print(db.get_password('test1'))
