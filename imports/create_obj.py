from collections import defaultdict
from django.db.models import Subquery, OuterRef, Q

from main.models import *
from users.models import Person


class ImportObjects:
    def __init__(self, user_villages_ids):
        self.rows = []
        self.create_cells = []
        self.update_cells = defaultdict(list)
        self.update_cellvalues = defaultdict(list)
        self.values = []
        self.user_villages = user_villages_ids
        self.indicators, self.tables = self.get_indicators()
        self.fields = self.get_tables_fields(self.tables)
        self.villages = self.get_villages()

    def get_indicators(self):
        sq = Cell.objects.filter(col__id=53, row__id=OuterRef('row__id'))
        sq1 = Cell.objects.filter(col__id=54, row__id=OuterRef('row__id'))
        table_sq = Cell.objects.filter(value__ref_value=OuterRef('id'))
        cells = Cell.objects.filter(row__table__id=22, col__id=45). \
            annotate(min_val=Subquery(sq.values('value__float_value'))). \
            annotate(max_val=Subquery(sq1.values('value__float_value'))). \
            annotate(ind_table=Subquery(table_sq.values('row__table')))
        t = Table.objects.filter(id__in=cells.values_list('ind_table', flat=True))
        return dict(zip(cells.values_list('value__char200_value', flat=True), cells)), \
               dict(zip(t.values_list('id', flat=True), t))

    def get_villages(self):
        sq = Person.objects.filter(villages__id=OuterRef('id'), user__groups__name='Operator', user__is_active=True,
                                   is_regional=False)
        o = Cell.objects.filter(col__brief_name='ОКТМО', row__table__id=14).order_by('row__number').values_list(
            'value__char50_value', flat=True)
        v = Cell.objects.filter(col__brief_name='Название', row__table__id=14).order_by('row__number'). \
            annotate(user=Subquery(sq.values('user__id')))
        return dict(zip(o, v))

    def get_tables_fields(self, tables):
        f = {}
        for table_id in tables.keys():
            f[table_id] = tables[table_id].fields.filter(
                Q(brief_name='Наслег') | Q(brief_name='Показатель') | Q(brief_name='Значение')).order_by('number')
        return f

    def add_object(self, report_date, oktmo, ind_name, value):
        if ind_name not in self.indicators.keys():
            return 5
        if not self.is_float(value):
            return 3
        value = float(value)
        if (self.indicators[ind_name].max_val is not None and value > self.indicators[ind_name].max_val) or\
                (self.indicators[ind_name].min_val is not None and value < self.indicators[ind_name].min_val):
            return 1
        if len(self.fields[self.indicators[ind_name].ind_table]) != 3:
            return 2
        if self.villages[oktmo].id not in self.user_villages:
            return 4

        cell_rows = Cell.objects.filter(row__report__report_date=report_date, value__ref_value__id=self.indicators[ind_name].id).values_list('row__id', flat=True)
        vil_cell = Cell.objects.filter(row__id__in=cell_rows, col__brief_name='Наслег', value__ref_value__id=self.villages[oktmo].id).first()
        cell = Cell.objects.filter(row__id=vil_cell.row_id, col__brief_name='Значение').first() if vil_cell is not None else None
        if cell is None:
            row = Row()
            row.number = 1
            row.table = self.tables[self.indicators[ind_name].ind_table]
            # This method is not good - too many queries to db
            row.report = Report.objects.get(user__id=self.villages[oktmo].user, report_date=report_date)
            row.save()
            self.rows.append(row)
            val, obj = self.create_cell(row, self.fields[row.table.id][0], self.villages[oktmo].id)
            self.values.append(val)
            self.create_cells.append(obj)
            val1, obj1 = self.create_cell(row, self.fields[row.table.id][1], self.indicators[ind_name].id)
            self.values.append(val1)
            self.create_cells.append(obj1)
            val2, obj2 = self.create_cell(row, self.fields[row.table.id][2], value)
            self.values.append(val2)
            self.create_cells.append(obj2)
        else:
            self.update_cell(cell, value)

        return 0

    def update_cell(self, cell, new_value):
        if cell.value is not None:
            cell.value.set_value(cell.col.column_type, new_value)
            self.update_cellvalues[cell_value_fields[cell.col.column_type - 1]].append(cell.value)
        else:
            new_cellvalue = CellValue()
            new_cellvalue.set_value(cell.col.column_type, new_value)
            new_cellvalue.save()
            cell.value = new_cellvalue
            self.update_cells['value'].append(cell)

    def create_cell(self, row, column, value):
        val = CellValue()
        val.set_value(column.column_type, value)
        val.save()
        obj = Cell()
        obj.row = row
        obj.col = column
        obj.value = val
        return val, obj

    def create_all(self):
        #Row.objects.bulk_create(self.rows)
        #CellValue.objects.bulk_create(self.values)
        if len(self.create_cells)>0:
            Cell.objects.bulk_create(self.create_cells)
        for key in self.update_cellvalues.keys():
            CellValue.objects.bulk_update(self.update_cellvalues[key], [key])
        for key in self.update_cells.keys():
            Cell.objects.bulk_update(self.update_cells[key], [key])

    def is_float(self, value):
        try:
            float(value)
            return True
        except:
            return False


class ImportTableTemplate(ImportObjects):
    def __init__(self, user_villages_ids):
        super().__init__(user_villages_ids)

    def add_object(self, report_date, oktmo, ind_name, value):
        pass
