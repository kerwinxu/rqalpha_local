# -*- coding: utf-8 -*-
#
# Last Change:  2018-01-10 00:39:40
# Copyright 2017 Ricequant, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import bcolz
import numpy as np
import six

from rqalpha.utils.i18n import gettext as _


class DayBarStore(object):
    def __init__(self, main, converter):
        self._table = bcolz.open(main, 'a')
        self._index = self._table.attrs['line_map']
        self._converter = converter

    @staticmethod
    def _remove_(l, v):
        try:
            l.remove(v)
        except ValueError:
            pass

    def add_indicator(self, order_book_id, field_name, field_list):
        """
            Description : 给数据添加指标的。
            Arg :
                @order_book_id : 股票id
                @field_name : 列名
                @field_list : 列数据
            Returns :
            Raises	 :
        """
        try:
            s, e = self._index[order_book_id]
            # 判断是否有这个列名
            if field_name not in self._table.cols.names:
                import numpy as np
                _data = np.zeros(len(self._table))
                self._table.addcol(_data, name=field_name)
            self._table.cols[field_name][s:e] = field_list
            # 刷新到磁盘
            self.flush()
        except KeyError:
            six.print_(_(u"No data for {}").format(order_book_id))
            return
    def flush(self):
        """
            Description : 刷新到磁盘
            Arg :
            Returns :
            Raises	 :
        """
        self._table.flush()
        pass

    def get_bars(self, order_book_id, fields=None):
        try:
            s, e = self._index[order_book_id]
        except KeyError:
            six.print_(_(u"No data for {}").format(order_book_id))
            return

        if fields is None:
            # the first is date
            fields = self._table.names[1:]

        if len(fields) == 1:
            return self._converter.convert(fields[0], self._table.cols[fields[0]][s:e])

        # remove datetime if exist in fields
        self._remove_(fields, 'datetime')

        dtype = np.dtype([('datetime', np.uint64)] +
                         [(f, self._converter.field_type(f, self._table.cols[f].dtype))
                          for f in fields])
        result = np.empty(shape=(e - s, ), dtype=dtype)
        for f in fields:
            result[f] = self._converter.convert(f, self._table.cols[f][s:e])
        result['datetime'] = self._table.cols['date'][s:e]
        result['datetime'] *= 1000000

        return result

    def get_date_range(self, order_book_id):
        s, e = self._index[order_book_id]
        return self._table.cols['date'][s], self._table.cols['date'][e - 1]
