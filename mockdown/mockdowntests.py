#!/usr/bin/env python3
import unittest
import io
from mockdown import MockGenerator
import yaml


class MockdownTests(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 9999

    def _load(self, content):
        return yaml.load(content, Load=yaml.FullLoader)

    def removeHeadersAndFooters(self, output):
        self.assertTrue(output.startswith(MockGenerator.header))

        output = output.removeprefix(MockGenerator.header)

        self.assertTrue(output.endswith(MockGenerator.footer))

        return output.removesuffix(MockGenerator.footer)

    def mock(self, input):
        entry = yaml.load(input, Loader=yaml.FullLoader)

        with io.StringIO() as out:
            generator = MockGenerator(entry, out)

            generator.generate()

            return self.removeHeadersAndFooters(out.getvalue())

    def test_span(self):
        output = self.mock('''
- span:
    label: Free text
''')

        self.assertEqual(output, '''
<span>Free text</span><br/>
''')

    def test_text(self):
        output = self.mock('''
- text:
    label: Text field
    placeholder: A text field
''')

        self.assertEqual(output, '''
<span>Text field</span><br/>
<input placeholder="A text field"/><br/>
''')

    def test_disabled_text(self):
        output = self.mock('''
- text:
    label: Text field
    enabled: False
    placeholder: A text field
''')

        self.assertEqual(output, '''
<span>Text field</span><br/>
<input placeholder="A text field" disabled readonly/><br/>
''')

    def test_no_placeholder_text(self):
        output = self.mock('''
- text:
    label: Text sem placeholder
''')

        self.assertEqual(output, '''
<span>Text sem placeholder</span><br/>
<input/><br/>
''')

    def test_no_label_text(self):
        output = self.mock('''
- text:
    placeholder: The placeholder
''')

        self.assertEqual(output, '''
<input placeholder="The placeholder"/><br/>
''')

    def test_finder(self):
        output = self.mock('''
- finder:
    label: A finder
    placeholder: A finder field prototype
''')

        self.assertEqual(output, '''
<span>A finder</span><input placeholder="A finder field prototype"/> <img src="./open-iconic/svg/magnifying-glass.svg" height=18 width=18/><br/>
''')

    def test_disabled_finder(self):
        output = self.mock('''
- finder:
    label: A finder
    enabled: False
    placeholder: A finder field prototype
''')

        self.assertEqual(output, '''
<span>A finder</span><input placeholder="A finder field prototype" disabled readonly/> <img src="./open-iconic/svg/magnifying-glass.svg" height=18 width=18/><br/>
''')

    def test_select(self):
        output = self.mock('''
- select:
    label: Select prototype
    options:
        - A option
        - Another option
        - A third option
''')

        self.assertEqual(output, '''
<span>Select prototype</span><select>
  <option>A option</option>
  <option>Another option</option>
  <option>A third option</option>
</select><br/>
''')

    def test_disabled_select(self):
        output = self.mock('''
- select:
    label: Select prototype
    enabled: False
    options:
        - A option
        - Another option
        - A third option
''')

        self.assertEqual(output, '''
<span>Select prototype</span><select disabled readonly>
  <option>A option</option>
  <option>Another option</option>
  <option>A third option</option>
</select><br/>
''')

    def test_check(self):
        output = self.mock('''
- check:
    label: A checked checkbox
    checked: true
''')

        self.assertEqual(output, '''
<input type="checkbox" checked="True"> A checked checkbox</input><br/>
''')

    def test_disabled_check(self):
        output = self.mock('''
- check:
    label: A checked checkbox
    enabled: False
    checked: true
''')

        self.assertEqual(output, '''
<input type="checkbox" checked="True" disabled readonly> A checked checkbox</input><br/>
''')

    def test_multipleselect(self):
        output = self.mock('''
- multipleselect:
    label: Multiple selection field
    placeholder: Type to select a value
    columns:
        ID:
            - 1
            - 2
            - 3
        Name:
            - Alberto
            - Gilberto
            - Roberto
        Idade:
            - 30
            - 27
            - 32
        Cargo:
            - Almoxarifado
            - Porteiro
            - Gerente
''')

        self.maxDiff = 9999
        self.assertEqual(output, '''
<span>Multiple selection field</span><input placeholder="Type to select a value"/> <img src="./open-iconic/svg/plus.svg" height=18 width=18/><br/>
<table>
  <thead>
    <td>ID</td>
    <td>Name</td>
    <td>Idade</td>
    <td>Cargo</td>
    <td>Actions</td>
  </thead>
  <tr>
    <td>1</td>
    <td>Alberto</td>
    <td>30</td>
    <td>Almoxarifado</td>
    <td> <img src="./open-iconic/svg/delete.svg" height=18 width=18/></td>
  </tr>
  <tr>
    <td>2</td>
    <td>Gilberto</td>
    <td>27</td>
    <td>Porteiro</td>
    <td> <img src="./open-iconic/svg/delete.svg" height=18 width=18/></td>
  </tr>
  <tr>
    <td>3</td>
    <td>Roberto</td>
    <td>32</td>
    <td>Gerente</td>
    <td> <img src="./open-iconic/svg/delete.svg" height=18 width=18/></td>
  </tr>
</table><br/>
''')

    def test_disabled_multipleselect(self):
        output = self.mock('''
- multipleselect:
    label: Multiple selection field
    enabled: False
    placeholder: Type to select a value
    columns:
        ID:
            - 1
            - 2
            - 3
        Name:
            - Alberto
            - Gilberto
            - Roberto
        Idade:
            - 30
            - 27
            - 32
        Cargo:
            - Almoxarifado
            - Porteiro
            - Gerente
''')

        self.maxDiff = 9999
        self.assertEqual(output, '''
<span>Multiple selection field</span><br/>
<table class="disabled">
  <thead>
    <td>ID</td>
    <td>Name</td>
    <td>Idade</td>
    <td>Cargo</td>
  </thead>
  <tr>
    <td>1</td>
    <td>Alberto</td>
    <td>30</td>
    <td>Almoxarifado</td>
  </tr>
  <tr>
    <td>2</td>
    <td>Gilberto</td>
    <td>27</td>
    <td>Porteiro</td>
  </tr>
  <tr>
    <td>3</td>
    <td>Roberto</td>
    <td>32</td>
    <td>Gerente</td>
  </tr>
</table><br/>
''')

    def test_button(self):
        output = self.mock('''
- button:
    text: OK
''')

        self.assertEqual(output, '''
<input type="button" value="OK"/><br/>
''')

    def test_disabled_button(self):
        output = self.mock('''
- button:
    text: OK
    enabled: False
''')

        self.assertEqual(output, '''
<input type="button" value="OK" disabled/><br/>
''')

    def test_container(self):
        output = self.mock('''
- container:
    - _kwargs:
        direction: horizontal
        title: Group of buttons
    - button:
        text: OK
    - button:
        text: Cancelar
''')

        self.assertEqual(output, '''
<fieldset>
  <legend>Group of buttons</legend>
<input type="button" value="OK"/>
<input type="button" value="Cancelar"/>
</fieldset><br/>
''')

    def test_disabled_container(self):
        output = self.mock('''
- container:
    - _kwargs:
        direction: horizontal
        title: Group of buttons
        enabled: False
    - button:
        text: OK
    - button:
        text: Cancelar
''')

        self.assertEqual(output, '''
<fieldset disabled>
  <legend>Group of buttons</legend>
<input type="button" value="OK"/>
<input type="button" value="Cancelar"/>
</fieldset><br/>
''')

    def test_titleless_container(self):
        output = self.mock('''
- container:
    - _kwargs:
        direction: horizontal
    - button:
        text: OK
    - button:
        text: Cancelar
''')

        self.assertEqual(output, '''
<div>
<input type="button" value="OK"/>
<input type="button" value="Cancelar"/>
</div><br/>
''')

    def test_vertical_container(self):
        output = self.mock('''
- container:
    - _kwargs:
        direction: vertical
    - button:
        text: OK
    - button:
        text: Cancelar
''')

        self.assertEqual(output, '''
<div>
<input type="button" value="OK"/><br/>
<input type="button" value="Cancelar"/><br/>
</div><br/>
''')

    def test_textarea(self):
        output = self.mock('''
- textarea:
    label: Textarea prototype
    placeholder: Optional placeholder
''')

        self.assertEqual(output, '''
<span>Textarea prototype</span><textarea rows=4 cols=50 placeholder="Optional placeholder"></textarea><br/>
''')

    def test_disabled_textarea(self):
        output = self.mock('''
- textarea:
    label: Textarea prototype
    enabled: False
    placeholder: Optional placeholder
''')

        self.assertEqual(output, '''
<span>Textarea prototype</span><textarea rows=4 cols=50 placeholder="Optional placeholder" disabled readonly></textarea><br/>
''')

    @unittest.skip
    def test_table(self):
        output = self.mock('''
- table:
    title: A table
    columns:
        Data:
            - 10/fev (quarta)
            - 11/fev (quinta)
            - 12/fev (sexta)
        Welcome cofee:
            - container:
                - check:
                - text:
                    placeholder: WC, 10
            - container:
                - check:
                - text:
                    placeholder: WC, 11
            - container:
                - check:
                - text:
                    placeholder: WC, 12
        Cofee break (manhã):
          - container:
            - check:
            - text:
                placeholder: CB, 10
          - container:
            - check:
            - text:
                placeholder: CB, 11
          - container:
            - check:
            - text:
                placeholder: CB, 12
        Cofee break (tarde):
          - container:
            - check:
            - text:
                placeholder: CT, 10
          - container:
            - check:
            - text:
                placeholder: CT, 11
          - container:
            - check:
            - text:
                placeholder: CT, 12
''')

        self.assertEqual('''
<table>
  <thead>
    <td>Data</td>
    <td>Welcome cofee</td>
    <td>Cofee break (manhã)</td>
    <td>Cofee break (tarde)</td>
    <td>Actions</td>
  </thead>
  <tr>
    <td>10/fev (quarta)</td>
    <td><div>
<input type="checkbox" checked="False"/>
<input placeholder="WC, 10"/><br/>
</div>
</td>
    <td><div>
<input type="checkbox" checked="False"/>
<input placeholder="CB, 10"/><br/>
</div>
</td>
    <td><div>
<input type="checkbox" checked="False"/>
<input placeholder="CT, 10"/><br/>
</div>
</td>
    <td> <img src="./open-iconic/svg/delete.svg" height=18 width=18/></td>
  </tr>
  <tr>
    <td>11/fev (quinta)</td>
    <td><div>
<input type="checkbox" checked="False"/>
<input placeholder="WC, 11"/><br/>
</div>
</td>
    <td><div>
<input type="checkbox" checked="False"/>
<input placeholder="CB, 11"/><br/>
</div>
</td>
    <td><div>
<input type="checkbox" checked="False"/>
<input placeholder="CT, 11"/><br/>
</div>
</td>
    <td> <img src="./open-iconic/svg/delete.svg" height=18 width=18/></td>
  </tr>
  <tr>
    <td>12/fev (sexta)</td>
    <td><div>
<input type="checkbox" checked="False"/>
<input placeholder="WC, 12"/><br/>
</div>
</td>
    <td><div>
<input type="checkbox" checked="False"/>
<input placeholder="CB, 12"/><br/>
</div>
</td>
    <td><div>
<input type="checkbox" checked="False"/>
<input placeholder="CT, 12"/><br/>
</div>
</td>
    <td> <img src="./open-iconic/svg/delete.svg" height=18 width=18/></td>
  </tr>
</table><br/>
''', output)

    @unittest.skip
    def test_disabled_table(self):
        output = self.mock('''
- table:
    title: A table
    enabled: False
    columns:
        Data:
            - 10/fev (quarta)
            - 11/fev (quinta)
            - 12/fev (sexta)
        Welcome cofee:
            - container:
                - check:
                - text:
                    placeholder: WC, 10
            - container:
                - check:
                - text:
                    placeholder: WC, 11
            - container:
                - check:
                - text:
                    placeholder: WC, 12
        Cofee break (manhã):
          - container:
            - check:
            - text:
                placeholder: CB, 10
          - container:
            - check:
            - text:
                placeholder: CB, 11
          - container:
            - check:
            - text:
                placeholder: CB, 12
        Cofee break (tarde):
          - container:
            - check:
            - text:
                placeholder: CT, 10
          - container:
            - check:
            - text:
                placeholder: CT, 11
          - container:
            - check:
            - text:
                placeholder: CT, 12
''')

        self.assertEqual(output, '''
<table class="disabled">
  <thead>
    <td>Data</td>
    <td>Welcome cofee</td>
    <td>Cofee break (manhã)</td>
    <td>Cofee break (tarde)</td>
    <td>Actions</td>
  </thead>
  <tr>
    <td>10/fev (quarta)</td>
    <td><div>
<input type="checkbox" checked="False"/>
<input placeholder="WC, 10"/><br/>
</div>
</td>
    <td><div>
<input type="checkbox" checked="False"/>
<input placeholder="CB, 10"/><br/>
</div>
</td>
    <td><div>
<input type="checkbox" checked="False"/>
<input placeholder="CT, 10"/><br/>
</div>
</td>
    <td> <img src="./open-iconic/svg/delete.svg" height=18 width=18/></td>
  </tr>
  <tr>
    <td>11/fev (quinta)</td>
    <td><div>
<input type="checkbox" checked="False"/>
<input placeholder="WC, 11"/><br/>
</div>
</td>
    <td><div>
<input type="checkbox" checked="False"/>
<input placeholder="CB, 11"/><br/>
</div>
</td>
    <td><div>
<input type="checkbox" checked="False"/>
<input placeholder="CT, 11"/><br/>
</div>
</td>
    <td> <img src="./open-iconic/svg/delete.svg" height=18 width=18/></td>
  </tr>
  <tr>
    <td>12/fev (sexta)</td>
    <td><div>
<input type="checkbox" checked="False"/>
<input placeholder="WC, 12"/><br/>
</div>
</td>
    <td><div>
<input type="checkbox" checked="False"/>
<input placeholder="CB, 12"/><br/>
</div>
</td>
    <td><div>
<input type="checkbox" checked="False"/>
<input placeholder="CT, 12"/><br/>
</div>
</td>
    <td> <img src="./open-iconic/svg/delete.svg" height=18 width=18/></td>
  </tr>
</table><br/>
''')

#     def test_align(self):
#         output = self.mock('''
# - span:
#     label: Free text
# ''')

#         self.assertEqual(output, '''
# <span>Free text</span> <br/>
# ''')

