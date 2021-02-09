# TODO

- [X] Todos os campos: disabled
- [X] Melhorar visual

- [ ] Fazer testes passar
- [X] Tirar botão de X da tabela quando estiver disabled - Importante
- [ ] Todos os campos: required - Importante
- [ ] Fazer footer no multipleselect - Importante
- [ ] Alinhar container à direita - Importante
- [ ] Fazer h1-6 - Importante
- [ ] notes - Importante, demorado
- [ ] text: Tamanho do campo
- [ ] Fluxograma
- [ ] value nos inputs


## Componentes

- span
- text
- finder
- select
- check
- multipleselect
- button
- container
- textarea
- table


## Sistema de Refresh automatico

- Abrir uma porta
- Detectar quando o arquivo foi modificado
- Refreshar uma página servida quando o arquivo for modificado


## Servindo HTML com python

https://stackabuse.com/serving-files-with-pythons-simplehttpserver-module/
```Python
import http.server
import socketserver
from urllib.parse import urlparse
from urllib.parse import parse_qs

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Sending an '200 OK' response
        self.send_response(200)

        # Setting the header
        self.send_header("Content-type", "text/html")

        # Whenever using 'send_header', you also have to call 'end_headers'
        self.end_headers()

        # Extract query param
        name = 'World'
        query_components = parse_qs(urlparse(self.path).query)
        if 'name' in query_components:
            name = query_components["name"][0]

        # Some custom HTML code, possibly generated by another function
        html = f"<html><head></head><body><h1>Hello {name}!</h1></body></html>"

        # Writing the HTML contents with UTF-8
        self.wfile.write(bytes(html, "utf8"))

        return

# Create an object of the above class
handler_object = MyHttpRequestHandler

PORT = 8000
my_server = socketserver.TCPServer(("", PORT), handler_object)

# Star the server
my_server.serve_forever()
```

Este projeto parece que faz exatamente o que eu preciso:
https://github.com/talwrii/inotify_httpd/blob/master/inotify_httpd/inotify_httpd.py