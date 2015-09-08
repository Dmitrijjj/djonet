# Copyright (c) 2012, Gijs Molenaar <gijsmolenaar@gmail.com>
# Copyright (c) 2009 - 2010, Mark Bucciarelli <mkbucc@gmail.com>
# Copyright (c) 2009 Vikram Bhandoh <vikram@bhandoh.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

from django.db.backends import *
import monetdb.sql as Database
from djonet.introspection import DatabaseIntrospection
from djonet.creation import DatabaseCreation
from djonet.operations import DatabaseOperations
from djonet.features import DatabaseFeatures
from djonet.validation import DatabaseValidation

DatabaseError = Database.DatabaseError
IntegrityError = Database.IntegrityError


class DatabaseWrapper(BaseDatabaseWrapper):
    operators = DatabaseOperations.operators

    Database = Database

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)

        self.features = DatabaseFeatures(self)
        self.ops = DatabaseOperations(self)
        self.validation = DatabaseValidation(self)
        self.introspection = DatabaseIntrospection(self)
        self.creation = DatabaseCreation(self)

    def create_cursor(self):
        if not self.is_usable():
            conn_params = self.get_connection_params()
            self.connection = self.get_new_connection(conn_params)
        cursor = self.connection.cursor()
        cursor.arraysize = 1000
        return cursor

    def get_connection_params(self):
        kwargs = {}
        if self.settings_dict['USER']:
            kwargs['username'] = self.settings_dict['USER']
        if self.settings_dict['NAME']:
            kwargs['database'] = self.settings_dict['NAME']
        if self.settings_dict['PASSWORD']:
            kwargs['password'] = self.settings_dict['PASSWORD']
        if self.settings_dict['HOST']:
            kwargs['hostname'] = self.settings_dict['HOST']
        if self.settings_dict['PORT']:
            kwargs['port'] = int(self.settings_dict['PORT'])
        return kwargs

    def get_new_connection(self, conn_params):
        conn = Database.connect(**conn_params)
        return conn

    def init_connection_state(self):
        pass

    def _set_autocommit(self, autocommit):
        self.connection.set_autocommit(autocommit)

    def is_usable(self):
        if not self.connection:
            return False
        try:
            self.connection.execute('SELECT 1;')
        except Database.Error:
            return False
        else:
            return True

