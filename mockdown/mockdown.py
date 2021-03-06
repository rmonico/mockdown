#!/usr/bin/env python3
import argparse
import logger_factory
import sys
import yaml
from . extract_params_from_yaml import extract_params_from_yaml
from . import loader

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

    def is_(self, checker):
        self._for_value(checker)

        return self

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
  <meta charset="UTF-8"/>
  <style>
  table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
  }

  table.disabled {
    border: 1px solid #CCC;
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
  fieldset {
    padding: 15px 25px 35px 30px !important;
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

    subcontainer_header = '''
    <div class="row">
      <div class="col-md-8 justify-content-end d-flex">
'''

    container_footer = '''      </div>
    </div><br/>
'''

    def generate(self):
        self._w(MockGenerator.header)

        self._generate_fields(self._in, True)

        self._w(MockGenerator.footer)

    def _generate_fields(self, fields, container=False, **default_kwargs):
        '''
        O paramêtro container se refere ao rootContainer, isto é, é True quando está gerando os fields direto no body
        A string 'container' (como em if 'container' in field) se refere ao field do tipo container
        '''
        for i, field in enumerate(fields):
            if container:
                # O seguinte if precisa (muito) ser extraído para uma classe de componente de container
                if 'container' in field and field['container'][0].get('_kwargs', {}).get('align', 'left') == 'right':
                    # TODO Extract these component to its classes
                    self._w(MockGenerator.subcontainer_header)
                else:
                    self._w(MockGenerator.container_header)

                is_last = i == len(fields) - 1
                if is_last:
                    default_kwargs['br'] = False

            self._generate_field(field, default_kwargs)

            if container:
                self._w(MockGenerator.container_footer)

    def _generate_field(self, field, kwargs_defaults={}):
        fieldKinds = {
            # TODO Remove esta tag, isso não se enquadra na ideia de simplicidade
            # 'br': lambda *args, **kwargs: self._wbrn(),
            'br': lambda *args, **kwargs: self._w(''),
            'span': self._generate_span,
            'header': self._generate_header,
            'text': self._generate_text,
            'finder': self._generate_finder,
            'select': self._generate_select,
            'radio': self._generate_radio,
            'check': self._generate_check,
            'multipleselect': self._generate_multipleselect,
            'button': self._generate_button,
            'container': self._generate_container,
            'textarea': self._generate_textarea,
            'table': self._generate_table,
            'link': self._generate_anchor,
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
        styles = checker.param('styles').default(None).istype(str).get()
        br = checker.param('br').default(True).istype(bool).get()

        _styles = styles.split(',') if styles else []

        self._span(label, _styles)
        if br:
            self._wbr()

        self._wn()

    def _generate_header(self, *args, **kwargs):
        checker.reset('header', args, kwargs)
        level = checker.param('level').default(1).istype(int).is_(lambda v: 1 <= v <= 6).get()
        label = checker.param('label').default(None).istype(str).get()
        br = checker.param('br').default(True).istype(bool).get()

        self._wn(f'<h{level}>{label}</h{level}>{"<br/><br/>" if br else ""}')

    # def _generate_text(self, label=None, placeholder=None, br=True):
    def _generate_text(self, *args, **kwargs):
        checker.reset('text', args, kwargs)
        label = checker.param('label').default(None).istype(str).get()
        enabled = checker.param('enabled').default(True).istype(bool).get()
        placeholder = checker.param('placeholder').default(None).istype(str).get()
        br = checker.param('br').default(True).istype(bool).get()
        required = checker.param('required').default(True).istype(bool).get()

        self._span(label, required=required, enabled=enabled)
        if label:
            self._wbrn()
        self._w('<input')

        self._property(placeholder=placeholder)

        if not enabled:
            self._w(' disabled readonly')
        self._w('/>')

        if br:
            self._wbr()

    # def _generate_finder(self, label=None, placeholder=None, br=True):
    def _generate_finder(self, *args, **kwargs):
        checker.reset('finder', args, kwargs)
        label = checker.param('label').default(None).istype(str).get()
        enabled = checker.param('enabled').default(True).istype(bool).get()
        placeholder = checker.param('placeholder').default(None).istype(str).get()
        br = checker.param('br').default(True).istype(bool).get()
        required = checker.param('required').default(True).istype(bool).get()

        self._span(label, required=required, enabled=enabled)
        self._input(enabled, placeholder)
        self._img('magnifying-glass')
        if br:
            self._wbr()
        self._wn()

    # def _generate_select(self, options, label=None, br=True):
    def _generate_select(self, *args, **kwargs):
        checker.reset('select', args, kwargs)
        label = checker.param('label').default(None).istype(str).get()
        enabled = checker.param('enabled').default(True).istype(bool).get()
        options = checker.param('options').isNotNone().istype(list).get()
        br = checker.param('br').default(True).istype(bool).get()
        required = checker.param('required').default(True).istype(bool).get()

        self._span(label, required=required, enabled=enabled)
        self._wbrn()
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

    def _generate_radio(self, *args, **kwargs):
        checker.reset('check', args, kwargs)
        label = checker.param('label').default(None).istype(str).get()
        enabled = checker.param('enabled').default(True).istype(bool).get()
        checked = checker.param('checked').default(False).istype(bool).get()
        br = checker.param('br').default(True).istype(bool).get()
        required = checker.param('required').default(True).istype(bool).get()

        self._w(f'<label class="form-check-label"><input class="form-check-input" type="radio" name="radio"')

        if checked:
            self._w(' checked')

        if not enabled:
            self._w(' disabled readonly')

        if required and enabled:
            self._w(f'> {label} *</label>')
        else:
            self._w(f'> {label}</label>')

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

        self._w(f'<input type="checkbox"')

        if checked:
            self._w(f' checked="checked"')


        if not enabled:
            self._w(' disabled readonly')

        if not label:
            self._w('/>')

        else:
            self._w(f'><label')

            if not enabled:
                self._w(' class="disabled"')

            self._w(f'> {label}</label></input>')

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
        editable = checker.param('editable').default(False).istype(bool).get()
        placeholder = checker.param('placeholder').default(None).istype(str).get()
        br = checker.param('br').default(True).istype(bool).get()
        required = checker.param('required').default(True).istype(bool).get()

        self._span(label, required=required, enabled=enabled)
        self._wbrn()
        if enabled:
            self._input(enabled, placeholder)
            self._img('plus')
            self._wbrn()

        self._table(columns, enabled, br=br, editable=editable)

    # def _generate_button(self, text, br=True):
    def _generate_button(self, *args, **kwargs):
        colors = {'blue': 'primary', 'green': 'success', 'yellow': 'warning', 'red': 'danger', 'gray': 'secondary'}
        checker.reset('button', args, kwargs)
        text = checker.param('text').isNotNone().istype(str).get()
        enabled = checker.param('enabled').default(True).istype(bool).get()
        color = checker.param('color').default('blue').istype(str).isin(*tuple(colors.keys())).get()
        br = checker.param('br').default(True).istype(bool).get()

        secondary_class = colors[color]
        self._w(f'<input type="button" value="{text}" class="btn btn-{secondary_class}"')

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

        if title:
            self._w(' class="border"')

        if not enabled:
            self._w(' disabled')

        self._wn('>')

        if title:
            self._wn(f'  <legend>{title}</legend>')

        self._generate_fields(args, br=direction == 'vertical' and br)

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
        required = checker.param('required').default(True).istype(bool).get()

        self._span(label, required=required, enabled=enabled)
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

    def _generate_anchor(self, *args, **kwargs):
        checker.reset('anchor', args, kwargs)
        href = checker.param('href').default(None).istype(str).get()
        br = checker.param('br').default(True).istype(bool).get()

        self._wbrn(f'<a href="{href}">{href}</a>')

    def _table(self, columns, enabled, title=None, br=True, editable=False):
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
                if editable:
                    self._w('<div>')
                if type(cell) == dict:
                    self._generate_fields([cell], br=False)
                else:
                    self._w(str(cell))
                if editable:
                    self._img('pencil')
                    self._w('</div>')
                self._wn(f'</td>')

            if enabled:
                self._w('    <td>')
                self._img('circle-x')
                self._wn('</td>')
            self._wn('  </tr>')

        self._wbrn('</table>')

    def _span(self, label, required=True, enabled=True, style=[]):
        if label:
            self._w('<span')
            if len(style) > 0:
                self._w(' style="')
                if 'overstrike' in style:
                    self._w('text-decoration: line-through;')
                self._w('"')

            if not enabled:
                self._w(' class="disabled"')

            self._w(f'>{label}')
            if required and enabled:
                self._w(' *')
            self._w(f'</span>')

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

    input = yaml.load(args.input, Loader=loader.Loader)

    generator = MockGenerator(input, args.output)

    generator.generate()


if __name__ == '__main__':
    main()
