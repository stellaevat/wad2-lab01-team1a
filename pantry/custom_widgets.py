import math
from itertools import chain
from django import forms
from django.utils.encoding import force_text
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

# Code modified from https://djangosnippets.org/snippets/2236/
class ColumnCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """
    Widget that renders multiple-select checkboxes in columns.
    Constructor takes number of columns and css class to apply
    to the <div> element that makes up the checkbox are.
    """
    def __init__(self, columns=3, class_whole=None, class_column=None, separator=None, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.columns = columns
        self.class_whole = class_whole
        self.class_column = class_column
        self.separator = separator
        
    def render(self, name, value, attrs=None, choices=(), renderer=None):
        if value is None:
            value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(self.attrs)
        choices_enum = list(enumerate(chain(self.choices, choices)))
        
        # This is the part that splits the choices into columns.
        # Slices vertically.  Could be changed to slice horizontally, etc.
        column_sizes = columnize(len(choices_enum), self.columns)
        columns = []
        for column_size in column_sizes:
            columns.append(choices_enum[:column_size])
            choices_enum = choices_enum[column_size:]
        output = []
        if self.class_whole:
            output.append(u'<div class="%s">' % self.class_whole)
        else:
            output.append(u'<div>')
        for column in columns:
            if self.class_column:
                output.append(u'<div class="%s">' % self.class_column)
            else:
                output.append(u'<div>')
            # Normalize to strings
            str_values = set([force_text(v) for v in value])
            for i, (option_value, option_label) in column:
                # If an ID attribute was given, add a numeric index as a suffix,
                # so that the checkboxes don't all have the same ID attribute.
                if has_id:
                    final_attrs = dict(final_attrs, id='%s_%s' % (
                            attrs['id'], i))
                    label_for = u' for="%s"' % final_attrs['id']
                else:
                    label_for = ''

                cb = forms.CheckboxInput(
                    final_attrs, check_test=lambda value: value in str_values)
                option_value = force_text(option_value)
                rendered_cb = cb.render(name, option_value)
                option_label = conditional_escape(force_text(option_label))
                output.append(u'<div><label%s>%s %s</label></div>' % (
                        label_for, rendered_cb, option_label))
                output.append("<br />")
            output.append(u'</div>')
        output.append(u'</div>')
        return mark_safe(u'\n'.join(output))


def columnize(items, columns):
    """
    Return a list containing numbers of elements per column if `items` items
    are to be divided into `columns` columns.

    >>> columnize(10, 1)
    [10]
    >>> columnize(10, 2)
    [5, 5]
    >>> columnize(10, 3)
    [4, 3, 3]
    >>> columnize(3, 4)
    [1, 1, 1, 0]
    """
    elts_per_column = []
    for col in range(columns):
        col_size = int(math.ceil(float(items) / columns))
        elts_per_column.append(col_size)
        items -= col_size
        columns -= 1
    return elts_per_column