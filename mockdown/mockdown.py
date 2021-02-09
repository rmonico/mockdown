#!/usr/bin/env python3
import argparse
import logger_factory
import sys
import yaml
from extract_params_from_yaml import extract_params_from_yaml


def parse_command_line():
    parser = argparse.ArgumentParser()

    logger_factory.make_verbosity_argument(parser)

    parser.add_argument('input', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help='Mock input file, defaults to stdin')
    parser.add_argument('output', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help='HTML output file, defaults to stdout')

    return parser.parse_args()


class ArgsChecker(object):

    def reset(self, context, args, kwargs):
        self._context = context
        self._args = args
        self._kwargs = kwargs
        self._reset()

    def _reset(self):
        self._param = None
        self._value = None
        self._default = None
        self._value_set_from_default = False
        self._allArgs = False

    def param(self, param):
        self._reset()
        self._param = param

        return self

    def default(self, value):
        self._default = value

        return self

    def istype(self, ptype):
        def _istype(value):
            self._assert(type(value) == ptype, f'Must be of type "{ptype}", its "{type(value)}"')

        self._for_value(lambda v: _istype(v))

        return self

    def _for_value(self, checker: callable):
        if self._allArgs:
            self._value_set_from_default = False
            for value in self._args:
                checker(value)
        else:
            self._value_set_from_default = self._param not in self._kwargs
            value = self._kwargs.get(self._param, self._default)
            checker(value)
            self._value = value

    def _assert(self, assertion, message):
        if not assertion and not self._value_set_from_default:
            raise AssertionError(f'{self._context}.{self._param}: {message}')

    def get(self):
        value = self._value

        self._reset()

        return value

    def isin(self, *values):
        def _isin(value):
            self._assert(value in values, f'Must be in "{values}"')

        self._for_value(lambda v: _isin(v))

        return self

    def allArgs(self):
        '''
        In this case .get() should not be called. Because this _value is not set here
        '''
        self._reset()
        self._allArgs = True

        return self

    def isNotNone(self):
        def _isNotNone(value):
            self._assert(value is not None, f'Can\'t be none')

        self._for_value(lambda v: _isNotNone(v))

        return self

checker = ArgsChecker()


class MockGenerator(object):

    def __init__(self, input, output):
        self._in = input
        self._out = output

    header = '''<html>
<head>
  <style>
  table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
  }

  .disabled {
    color: #CCC;
  }
  input, select, table, textarea {
    width: 95%;
  }
  input[type=button], input[type=checkbox] {
    width: initial;
  }
  </style>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" crossorigin="anonymous">
</head>
<body>
  <div class="container">
'''

    footer = '''
  </div>
  <br/>
</body>
</html>
'''

    container_header = '''
    <div class="row">
      <div class="col-md-8">
'''

    container_footer = '''      </div>
    </div>
'''

    def generate(self):
        self._w(MockGenerator.header)

        self._generate_fields(self._in, True)

        self._w(MockGenerator.footer)

    def _generate_fields(self, fields, container=False, **default_kwargs):
        for field in fields:
            if container:
                self._w(MockGenerator.container_header)

            self._generate_field(field, default_kwargs)

            if container:
                self._w(MockGenerator.container_footer)

    def _generate_field(self, field, kwargs_defaults={}):
        fieldKinds = {
            'span': self._generate_span,
            'text': self._generate_text,
            'finder': self._generate_finder,
            'select': self._generate_select,
            'check': self._generate_check,
            'multipleselect': self._generate_multipleselect,
            'button': self._generate_button,
            'container': self._generate_container,
            'textarea': self._generate_textarea,
            'table': self._generate_table,
        }

        for kind, generator in fieldKinds.items():
            if kind in field:
                field_args, field_kwargs = extract_params_from_yaml(field[kind])

                field_kwargs.update(kwargs_defaults)

                generator(*field_args, **field_kwargs)

                break

    # def _generate_span(self, label=None, br=True):
    def _generate_span(self, *args, **kwargs):
        checker.reset('span', args, kwargs)
        label = checker.param('label').default(None).istype(str).get()
        br = checker.param('br').default(True).istype(bool).get()

        self._span(label)
        if br:
            self._wbr()
        self._wn()

    # def _generate_text(self, label=None, placeholder=None, br=True):
    def _generate_text(self, *args, **kwargs):
        checker.reset('text', args, kwargs)
        label = checker.param('label').default(None).istype(str).get()
        enabled = checker.param('enabled').default(True).istype(bool).get()
        placeholder = checker.param('placeholder').default(None).istype(str).get()
        br = checker.param('br').default(True).istype(bool).get()

        self._span(label)
        if label:
            self._wbrn()
        self._w('<input')

        self._property(placeholder=placeholder)

        if not enabled:
            self._w(' disabled readonly')
        self._wbrn('/>')

    # def _generate_finder(self, label=None, placeholder=None, br=True):
    def _generate_finder(self, *args, **kwargs):
        checker.reset('finder', args, kwargs)
        label = checker.param('label').default(None).istype(str).get()
        enabled = checker.param('enabled').default(True).istype(bool).get()
        placeholder = checker.param('placeholder').default(None).istype(str).get()
        br = checker.param('br').default(True).istype(bool).get()

        self._span(label)
        self._input(enabled, placeholder)
        self._img('magnifying-glass')
        self._wbrn()

    # def _generate_select(self, options, label=None, br=True):
    def _generate_select(self, *args, **kwargs):
        checker.reset('select', args, kwargs)
        label = checker.param('label').default(None).istype(str).get()
        enabled = checker.param('enabled').default(True).istype(bool).get()
        options = checker.param('options').isNotNone().istype(list).get()
        br = checker.param('br').default(True).istype(bool).get()

        self._span(label)
        self._w('<select')

        if not enabled:
            self._w(' disabled readonly')

        self._wn('>')

        for option in options:
            self._wn(f'  <option>{option}</option>')

        self._w('</select>')
        if br:
            self._wbr()
        self._wn()

    # def _generate_check(self, label=None, checked=False, br=True):
    def _generate_check(self, *args, **kwargs):
        checker.reset('check', args, kwargs)
        label = checker.param('label').default(None).istype(str).get()
        enabled = checker.param('enabled').default(True).istype(bool).get()
        checked = checker.param('checked').default(False).istype(bool).get()
        br = checker.param('br').default(True).istype(bool).get()

        self._w(f'<input type="checkbox" checked="{checked}"')

        if not enabled:
            self._w(' disabled readonly')

        self._w(f'> {label}</input>' if label else '/>')

        # self._span(label)
        if br:
            self._wbr()
        self._wn()

    # def _generate_multipleselect(self, columns, label=None, placeholder=None, br=True):
    def _generate_multipleselect(self, *args, **kwargs):
        checker.reset('multipleselect', args, kwargs)
        columns = checker.param('columns').isNotNone().istype(dict).get()
        label = checker.param('label').default(None).istype(str).get()
        enabled = checker.param('enabled').default(True).istype(bool).get()
        placeholder = checker.param('placeholder').default(None).istype(str).get()
        br = checker.param('br').default(True).istype(bool).get()

        self._span(label)
        if enabled:
            self._input(enabled, placeholder)
            self._img('plus')
        self._wbrn()
        self._table(columns, enabled, br=br)

    # def _generate_button(self, text, br=True):
    def _generate_button(self, *args, **kwargs):
        checker.reset('button', args, kwargs)
        text = checker.param('text').isNotNone().istype(str).get()
        enabled = checker.param('enabled').default(True).istype(bool).get()
        br = checker.param('br').default(True).istype(bool).get()

        self._w(f'<input type="button" value="{text}"')

        if not enabled:
            self._w(' disabled')

        self._w('/>')

        if br:
            self._wbr()

        self._wn()

    def _generate_container(self, *args, **kwargs):
        checker.reset('container', args, kwargs)
        checker.allArgs().istype(dict)
        direction = checker.param('direction').default('horizontal').isin('horizontal', 'vertical').get()
        title = checker.param('title').default(None).istype(str).get()
        enabled = checker.param('enabled').default(True).istype(bool).get()
        br = checker.param('br').default(True).istype(bool).get()

        tag = 'fieldset' if title else 'div'

        self._w(f'<{tag}')

        if not enabled:
            self._w(' disabled')

        self._wn('>')

        if title:
            self._wn(f'  <legend>{title}</legend>')

        self._generate_fields(args, br=direction == 'vertical')

        self._w(f'</{tag}>')

        if br:
            self._wbr()

        self._wn()

    # def _generate_textarea(self, placeholder, label=None, br=True):
    def _generate_textarea(self, *args, **kwargs):
        checker.reset('textarea', args, kwargs)
        placeholder = checker.param('placeholder').isNotNone().istype(str).get()
        label = checker.param('label').default(None).istype(str).get()
        enabled = checker.param('enabled').default(True).istype(bool).get()
        br = checker.param('br').default(True).istype(bool).get()

        self._span(label)
        self._w(f'<textarea')
        self._property(rows=4, cols=50, placeholder=placeholder)
        if not enabled:
            self._w(' disabled readonly')
        self._w('></textarea>')
        if br:
            self._wbr()
        self._wn()

    # def _generate_table(self, columns, title=None, br=True):
    def _generate_table(self, *args, **kwargs):
        checker.reset('table', args, kwargs)
        title = checker.param('title').default(None).istype(str).get()
        enabled = checker.param('enabled').default(True).istype(bool).get()
        columns = checker.param('columns').isNotNone().istype(dict).get()
        br = checker.param('br').default(True).istype(bool).get()

        self._table(columns, enabled, title=title, br=br)

    def _table(self, columns, enabled, title=None, br=True):
        self._w('<table')
        if not enabled:
            self._w(' class="disabled"')
        self._wn('>')

        self._wn('  <thead>')
        for column in columns.keys():
            self._wn(f'    <td>{column}</td>')

        if enabled:
            self._wn(f'    <td>Actions</td>')

        self._wn('  </thead>')

        firstColumn = list(columns.keys())[0]

        rowCount = len(columns[firstColumn])

        for row in range(rowCount):
            self._wn('  <tr>')
            for key, value in columns.items():
                cell = value[row]

                self._w(f'    <td>')
                if type(cell) == dict:
                    self._generate_fields([cell], br=False)
                else:
                    self._w(str(cell))
                self._wn(f'</td>')

            if enabled:
                self._w('    <td>')
                self._img('delete')
                self._wn('</td>')
            self._wn('  </tr>')

        self._wbrn('</table>')

    def _span(self, label):
        if label:
            self._w(f'<span>{label}</span>')

    def _input(self, enabled, placeholder):
        self._w('<input')
        self._property(placeholder=placeholder)

        if not enabled:
            self._w(' disabled readonly')

        self._w('/>')

    def _property(self, **kwargs):
        for key, value in kwargs.items():
            if not value:
                continue
            elif type(value) == str:
                self._w(f' {key}="{value}"')
            else:
                self._w(f' {key}={str(value)}')

    def _img(self, image):
        self._w(f' <img src="./open-iconic/svg/{image}.svg" height=18 width=18/>')

    def _w(self, value):
        self._out.write(value)

    def _wn(self, value=''):
        self._w(value + '\n')

    def _wbr(self, value=''):
        self._w(value)
        self._w('<br/>')

    def _wbrn(self, value=''):
        self._wbr(value)
        self._wn()


def main():
    global args

    args = parse_command_line()

    global logger
    logger = logger_factory.create(__name__, args.verbosity)

    """
    Logger reference: https://docs.python.org/3/library/logging.html
    """
    logger.debug('args: ' + str(args))

    input = yaml.load(args.input, Loader=yaml.FullLoader)

    generator = MockGenerator(input, args.output)

    generator.generate()


if __name__ == '__main__':
    main()
