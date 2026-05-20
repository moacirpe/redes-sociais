#!/usr/bin/env python3
"""
Servidor OAuth para Meta/Instagram
Captura o código de autorização automaticamente
"""

import http.server
import socketserver
import urllib.parse
import threading
import time
import os

class OAuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()

        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)

        if 'code' in query:
            code = query['code'][0]
            print(f'\n✅ CÓDIGO OAUTH RECEBIDO: {code}')

            # Salvar código
            with open('.oauth_code', 'w') as f:
                f.write(code)

            self.wfile.write(b'''
            <html><body style="font-family:Arial;text-align:center;padding:50px">
            <h1 style="color:green">Autorizacao Recebida!</h1>
            <p>Codigo OAuth capturado com sucesso.</p>
            <p><strong>Nao feche esta aba ainda.</strong></p>
            <p>Volte ao terminal e aguarde o processamento.</p>
            </body></html>
            ''')

            # Aguardar um pouco e encerrar servidor
            threading.Timer(2, lambda: os._exit(0)).start()

        elif 'error' in query:
            error = query.get('error_description', ['Erro desconhecido'])[0]
            print(f'\n❌ ERRO: {error}')
            self.wfile.write(f'''
            <html><body style="font-family:Arial;text-align:center;padding:50px">
            <h1 style="color:red">Erro na Autorizacao</h1>
            <p>{error}</p>
            </body></html>
            '''.encode())
        else:
            self.wfile.write(b'''
            <html><body style="font-family:Arial;text-align:center;padding:50px">
            <h1>Aguardando Autorizacao...</h1>
            <p>Esta pagina sera atualizada automaticamente.</p>
            </body></html>
            ''')

    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    print('\n🔌 Servidor OAuth iniciado na porta 8888')
    print('🌐 URL de autorização:')
    print('https://www.facebook.com/v19.0/dialog/oauth?client_id=2159359204835308&redirect_uri=http%3A//localhost%3A8888/callback&scope=instagram_basic,instagram_manage_insights,pages_read_engagement,pages_show_list,business_management&response_type=code')
    print('\n⏳ Aguardando callback...')

    try:
        with socketserver.TCPServer(('', 8888), OAuthHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n🛑 Servidor interrompido')