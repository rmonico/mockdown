# Mockdown

A form wireframe creator, inspired on markdown. Converts yaml to HTML.


## Usage

Given a file `input.mock.yaml`:

```yaml
- text:
    label: Text field
    placeholder: A text field
```

After run `mockdown input.mock.yaml output.html`, contents of `output.html` will be (among other stuff):

```html
<span>Text field</span><br/>
<input placeholder="A text field"/><br/>
```

See `examples` folder for other controls.
