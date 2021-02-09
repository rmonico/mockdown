import unittest
import yaml


def extract_params_from_yaml(entry, args_entry='_args', kwargs_entry='_kwargs', comment_entry= '_comments'):
    if entry is None:
        args = []
        kwargs = {}
    elif type(entry) is list:
        args = list(entry)

        if (kwargs_index := _index_of_dict_with_just_kwargs_entry(args, kwargs_entry)) > -1:
            assert type(args[kwargs_index]) == dict
            kwargs = dict(args.pop(kwargs_index)[kwargs_entry])
        else:
            kwargs = {}
    elif type(entry) is dict:
        kwargs = dict(entry)

        if args_entry in kwargs:
            assert type(kwargs[args_entry]) == list
            args = list(kwargs[args_entry])
            kwargs.pop(args_entry, None)
        else:
            args = []
    else:
        assert False, f'entry should either be list nor dict (its {str(type(entry))})'

    kwargs.pop(comment_entry, None)
    return (args, kwargs)


def _index_of_dict_with_just_kwargs_entry(args, kwargs_entry):
    for i, arg in enumerate(args):
        if type(arg) == dict and kwargs_entry in arg and len(arg) == 1:
            return i
    else:
        return -1

class ExtractParamsFromYamlTests(unittest.TestCase):

    def _load(self, contents):
        return yaml.load(contents, Loader=yaml.FullLoader)

    def test_should_extract_args_from_list_entry(self):
        entry = self._load('''
- first arg
- second arg
''')
        args, kwargs = extract_params_from_yaml(entry)

        self.assertListEqual(args, ['first arg', 'second arg'])
        self.assertDictEqual(kwargs, {})

    def test_should_extract_kwargs_from_object_entry(self):
        entry = self._load('''
key: value
another key: another value
''')

        args, kwargs = extract_params_from_yaml(entry)

        self.assertListEqual(args, [])
        self.assertDictEqual(kwargs, {'key': 'value', 'another key': 'another value'})

    def test_should_extract_args_from_object_entry(self):
        entry = self._load('''
key: value
another key: another value
_args:
  - first arg
  - second arg
''')

        args, kwargs = extract_params_from_yaml(entry)

        self.assertListEqual(args, ['first arg', 'second arg'])
        self.assertDictEqual(kwargs, {'key': 'value', 'another key': 'another value'})

    def test_should_extract_kwargs_from_list_entry(self):
        entry = self._load('''
- first arg
- second arg
- _kwargs:
    key: value
    another key: another value
''')

        args, kwargs = extract_params_from_yaml(entry)

        self.assertListEqual(args, ['first arg', 'second arg'])
        self.assertDictEqual(kwargs, {'key': 'value', 'another key': 'another value'})

    def test_should_ignore_comments_entry_on_list(self):
        entry = self._load('''
key: value
another key: another value
_comments: Comments
''')

        args, kwargs = extract_params_from_yaml(entry)

        self.assertListEqual(args, [])
        self.assertDictEqual(kwargs, {'key': 'value', 'another key': 'another value'})

    def test_should_assign_kwargs_defaults(self):
        entry = self._load('''
key: value
another key: another value
_comments: Comments
''')

        args, kwargs = extract_params_from_yaml(entry)

        self.assertListEqual(args, [])
        self.assertDictEqual(kwargs, {'key': 'value', 'another key': 'another value'})

    def test_should_return_empty_values_when_nothing_is_passed(self):
        args, kwargs = extract_params_from_yaml(None)

        self.assertListEqual(args, [])
        self.assertDictEqual(kwargs, {})
