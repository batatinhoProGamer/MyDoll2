from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.popup import Popup

from save_and_load import *
from menu.menu import *
from agenda.agenda import *
from estoque.estoque import *
from historico.historico import *
from feiras.feiras import *
from financas.financas import *

from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from plyer import filechooser
from mysql.connector import connect
from PIL import Image
import os
import requests

"""from android.storage import primary_external_storage_path
from android.permissions import request_permissions, Permission
request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE, Permission.INTERNET])
external_storage_path = primary_external_storage_path()
gallery_path = external_storage_path + '/DCIM'"""

Window.keyboard_anim_args = {'d': .2, 't': 'in_out_expo'}
Window.softinput_mode = "below_target"

from kivy.lang.builder import Builder
Builder.load_file('main.kv')


#from woocommerce import API


conexao_sql = carregar("sqlconector")
host = conexao_sql["host"]
user = conexao_sql["user"]
passwd = conexao_sql["passwd"]
port = conexao_sql["port"]
database = conexao_sql["database"]


# previsão do tempo

previsoes_data = carregar("previsao_tempo")
previsoes = {}
cidade = previsoes_data["cidade"]
chave = previsoes_data["chave"]


"""
woocommerce
try:
    resposta = requests.get(f"http://api.openweathermap.org/data/2.5/forecast?q={cidade}&appid={chave}")

    # Analisa a resposta em formato JSON
    dados = resposta.json()

    # Imprime as informações da previsão do tempo para cada período de tempo
    for clima in dados['list']:
        data_hora = clima['dt_txt']
        prob_chuva = clima['pop'] * 100
        data = data_hora.split()[0]
        hora = int(data_hora.split()[1][:2])

        if prob_chuva != 0:
            if data not in previsoes or hora < 18:
                previsoes[data] = round(prob_chuva)
            elif data in previsoes and hora < 18 and previsoes[data] < prob_chuva:
                previsoes[data] = round(prob_chuva)
except:
    pass
"""

class SpinnerOptions(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = [1, 74 / 255, 167 / 255, 1]
        self.bold = True
        

class SpinnerDropdown(Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.option_cls = SpinnerOptions
        self.values = []


class Botao(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bold = True
        self.background_color = (0, 0, 0, 0)
        self.color = (0, 0, 0, 1)
        self.font_size = 80


class Geral(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vezes_clicadas_janela_admin = 0
        Window.bind(on_keyboard=self.Android_back_click)
        self.sql = False
    
    def resetar_screenmanagers(self):
        self.ids.gerenciador_telas_principal.get_screen("estoque").ids.gerenciador_colecoes.current = "mostrar colecoes"
        self.ids.gerenciador_telas_principal.get_screen("estoque").ids.gerenciador_produtos.current = "mostrar produtos"
        self.ids.gerenciador_telas_principal.get_screen("estoque").ids.gerenciador_subprodutos.current = "mostrar subprodutos"
        self.ids.gerenciador_telas_principal.get_screen("feiras").ids.gerenciador_feiras.current = "scroll_feiras_principal"
        self.ids.gerenciador_telas_principal.get_screen("feiras").ids.gerenciador_concluir_feira.current = "concluir feira principal"
        self.ids.gerenciador_telas_principal.get_screen("agenda").ids.gerenciador_agenda.current = "principal"
        self.ids.gerenciador_telas_principal.get_screen("historico").ids.gerenciador_historico.current = "historico_vendas"
        self.ids.gerenciador_telas_principal.get_screen("financas").ids.gerenciador_financas.current = "financas atual"
        self.ids.gerenciador_telas_principal.get_screen("financas").ids.gerenciador_financas_atual.current = "financas atual principal"

    def copiar_imagem(self, widget="", source=""):
        App.get_running_app().copiar_imagem(widget=widget, source=source)

    def sql_to_json(self):
        conteudo = {"colecoes_estoque": [], 
               "produtos_estoque": [], 
               "subprodutos_estoque": [], 
               "agenda": [], 
               "historico_agenda": [], 
               "feiras": [], 
               "subprodutos_feira": [], 
               "historico_feiras": [], 
               "historico_feiras_vendas": [], 
               "feiras_vendas": [], 
               "financas_atual": [], 
               "historico_financas": [], 
               "historico_financas_compras": [],
               "imagens_subprodutos_estoque": []}
        
        try:
            if self.sql == False:
                self.database = connect(
                    host=host,
                    user=user,
                    passwd=passwd,
                    port=port,
                    database=database
                )
                
                self.sql = self.database.cursor()
        except:
            self.ids.administrador_mensagens.text = "Falha ao conectar com a nuvem"

        if self.sql != False:
            try:
                self.sql.execute("SELECT * FROM colecoes_estoque")
                colecoes_estoque = self.sql.fetchall()
                for item in colecoes_estoque:
                    conteudo["colecoes_estoque"].append({
                        "id": item[0],
                        "colecao": item[1],
                        "ativo": item[2],
                        "imagem": item[3],
                        "descricao": item[4],
                        "data_criacao": str(item[5]),
                        "data_edicao": str(item[6])
                    })
            except Exception as e:
                self.ids.administrador_mensagens.text = "Falha ao carregar colecoes_estoque"
                return

            try:
                self.sql.execute("SELECT * FROM produtos_estoque")
                produtos_estoque = self.sql.fetchall()
                for item in produtos_estoque:
                    conteudo["produtos_estoque"].append({
                        "id": item[0],
                        "id_colecao": item[1],
                        "imagem": item[2],
                        "produto": item[3],
                        "preco": item[4],
                        "ativo": item[5],
                        "descricao": item[6],
                        "data_criacao": str(item[7]),
                        "data_edicao": str(item[8])
                    })
            except:
                self.ids.administrador_mensagens.text = "Falha ao carregar produtos_estoque"
                return
            
            try:
                self.sql.execute("SELECT * FROM subprodutos_estoque")
                subprodutos_estoque = self.sql.fetchall()
                for item in subprodutos_estoque:
                    conteudo["subprodutos_estoque"].append({
                        "id": item[0],
                        "id_produto": item[1],
                        "imagem": item[2],
                        "subproduto": item[3],
                        "quantidade": item[4],
                        "ativo": item[5],
                        "data_criacao": str(item[6]),
                        "data_edicao": str(item[7])
                    })
            except:
                self.ids.administrador_mensagens.text = "Falha ao carregar subprodutos_estoque"
                return

            try:
                self.sql.execute("SELECT * FROM agenda")
                agenda = self.sql.fetchall()
                for item in agenda:
                    conteudo["agenda"].append({
                        "id": item[0],
                        "id_subproduto": item[1],
                        "quantidade": item[2],
                        "data_entrega": item[3].strftime("%Y-%m-%d"),
                        "descricao": item[4],
                        "ativo": item[5]
                    })
            except:
                self.ids.administrador_mensagens.text = "Falha ao carregar agenda"
                return

            try:
                self.sql.execute("SELECT * FROM historico_agenda")
                historico_agenda = self.sql.fetchall()
                for item in historico_agenda:
                    conteudo["historico_agenda"].append({
                        "id": item[0],
                        "id_subproduto": item[1],
                        "quantidade": item[2],
                        "data_entrega": item[3].strftime("%Y-%m-%d"),
                        "descricao": item[4],
                        "forma_pagamento": item[5],
                        "preco_total": item[6]
                    })
            except:
                self.ids.administrador_mensagens.text = "Falha ao carregar historico_agenda"
                return

            try:
                self.sql.execute("SELECT * FROM feiras")
                feiras = self.sql.fetchall()
                for item in feiras:
                    conteudo["feiras"].append({
                        "id": item[0],
                        "data_feira": item[1].strftime("%Y-%m-%d"),
                        "horario_inicio": item[2],
                        "horario_final": item[3],
                        "nome_feira": item[4],
                        "local_feira": item[5],
                        "descricao": item[6],
                        "ativo": item[7]
                    })
            except:
                self.ids.administrador_mensagens.text = "Falha ao carregar feiras"
                return

            try:
                self.sql.execute("SELECT * FROM subprodutos_feira")
                subprodutos_feira = self.sql.fetchall()
                for item in subprodutos_feira:
                    conteudo["subprodutos_feira"].append({
                        "id": item[0],
                        "id_feira": item[1],
                        "id_subproduto": item[2],
                        "quantidade": item[3],
                        "ativo": item[4]
                    })
            except:
                self.ids.administrador_mensagens.text = "Falha ao carregar subprodutos_feira"
                return

            try:
                self.sql.execute("SELECT * FROM historico_feiras")
                historico_feiras = self.sql.fetchall()
                for item in historico_feiras:
                    conteudo["historico_feiras"].append({
                        "id": item[0],
                        "horario_inicio": item[1],
                        "horario_final": item[2],
                        "nome_feira": item[3],
                        "local_feira": item[4],
                        "data_feira": item[5].strftime("%Y-%m-%d"),
                        "descricao": item[6]
                    })
            except:
                self.ids.administrador_mensagens.text = "Falha ao carregar historico_feiras"
                return

            try:
                self.sql.execute("SELECT * FROM historico_feiras_vendas")
                historico_feiras_vendas = self.sql.fetchall()
                for item in historico_feiras_vendas:
                    conteudo["historico_feiras_vendas"].append({
                        "id": item[0],
                        "id_historico_feira": item[1],
                        "id_subproduto": item[2],
                        "quantidade": item[3],
                        "descricao": item[4],
                        "preco_total": item[5],
                        "forma_pagamento": item[6]
                    })
            except:
                self.ids.administrador_mensagens.text = "Falha ao carregar historico_feiras_vendas"
                return

            try:
                self.sql.execute("SELECT * FROM feiras_vendas")
                feiras_vendas = self.sql.fetchall()
                for item in feiras_vendas:
                    conteudo["feiras_vendas"].append({
                        "id": item[0],
                        "id_feira": item[1],
                        "id_subproduto": item[2],
                        "quantidade": item[3],
                        "descricao": item[4],
                        "preco": item[5],
                        "forma_pagamento": item[6],
                        "ativo": item[7]
                    })
            except:
                self.ids.administrador_mensagens.text = "Falha ao carregar feiras_vendas"
                return
                
            try:
                self.sql.execute("SELECT * FROM financas_atual")
                financas_atual = self.sql.fetchall()
                for item in financas_atual:
                    conteudo["financas_atual"].append({
                        "id": item[0],
                        "nome": item[1],
                        "local": item[2], 
                        "data": item[3].strftime("%Y-%m-%d"), 
                        "forma_pagamento": item[4],
                        "preco": item[5], 
                        "descricao": item[6], 
                        "ativo": item[7]
                    })
            except:
                self.ids.administrador_mensagens.text = "Falha ao carregar financas_atual"
                return

            try:
                self.sql.execute("SELECT * FROM historico_financas")
                historico_financas = self.sql.fetchall()
                for item in historico_financas:
                    conteudo["historico_financas"].append({
                        "id": item[0],
                        "mes": item[1],
                        "ano": item[2]
                    })
            except:
                self.ids.administrador_mensagens.text = "Falha ao carregar historico_financas"
                return

            try:
                self.sql.execute("SELECT * FROM historico_financas_compras")
                historico_financas_compras = self.sql.fetchall()
                for item in historico_financas_compras:
                    conteudo["historico_financas_compras"].append({
                        "id": item[0], 
                        "id_historico_financas": item[1],
                        "nome": item[2],
                        "local": item[3], 
                        "data": item[4].strftime("%Y-%m-%d"), 
                        "forma_pagamento": item[5],
                        "preco": item[6], 
                        "descricao": item[7]
                    })
            except:
                self.ids.administrador_mensagens.text = "Falha ao carregar historico_financas_compras"
                return

            try:
                self.sql.execute("SELECT * FROM imagens_subprodutos_estoque")
                imagens_subprodutos_estoque = self.sql.fetchall()
                for item in imagens_subprodutos_estoque:
                    conteudo["imagens_subprodutos_estoque"].append({
                        "id": item[0],
                        "imagem": item[1],
                        "id_subproduto": item[2],
                        "ativo": item[3],
                        "data_criacao": str(item[4]),
                        "data_edicao": str(item[5])
                    })
            except:
                self.ids.administrador_mensagens.text = "Falha ao carregar imagens_subprodutos_estoque"
                return
            
            self.ids.administrador_mensagens.text = "Pego informações da nuvem!"
            App.get_running_app().conteudo = conteudo
            self.database.commit()
            salvar(conteudo)

    def json_to_sql(self):
        conteudo = App.get_running_app().conteudo
        if self.sql == False:
            try:
                self.database = connect(
                    host=host,
                    user=user,
                    passwd=passwd,
                    port=port,
                    database=database
                )

                self.sql = self.database.cursor()
            except:
                self.ids.administrador_mensagens.text = "Falha ao conectar com a nuvem"

        if self.sql != False:
            self.sql.execute("SET FOREIGN_KEY_CHECKS=0")

            self.sql.execute("SHOW TABLES")
            tabelas = list(map(lambda x: x[0], self.sql.fetchall()))
            for tabela in tabelas:
                self.sql.execute(f"TRUNCATE TABLE {tabela}")

            try:
                for colecao in conteudo["colecoes_estoque"]:
                    self.sql.execute(f"""INSERT INTO colecoes_estoque (colecao, ativo, descricao, imagem, data_criacao, data_edicao) VALUES 
                    ('{colecao['colecao']}', {colecao['ativo']}, '{colecao['descricao']}', '{colecao['imagem']}', '{colecao['data_criacao']}', '{colecao['data_edicao']}')""")
                self.ids.administrador_mensagens.text = "Coleções salvas em SQL"
            except:
                self.ids.administrador_mensagens.text = "Coleções não salvas em SQL"
                return

            try:
                for produto in conteudo["produtos_estoque"]:
                    self.sql.execute(f"""INSERT INTO produtos_estoque (id_colecao, imagem, produto, preco, ativo, descricao, data_criacao, data_edicao) VALUES 
                    ({produto['id_colecao']}, '{produto['imagem']}', '{produto['produto']}', {produto['preco']}, {produto['ativo']}, '{produto['descricao']}', '{produto['data_criacao']}', '{produto['data_edicao']}')""")
                self.ids.administrador_mensagens.text = "Produtos salvos em SQL"
            except:
                self.ids.administrador_mensagens.text = "Produtos não salvos em SQL"
                return

            try:
                for subproduto in conteudo["subprodutos_estoque"]:
                    self.sql.execute(
                        f"""INSERT INTO subprodutos_estoque (id_produto, imagem, subproduto, quantidade, ativo, data_criacao, data_edicao) VALUES
                        ({subproduto["id_produto"]}, '{subproduto["imagem"]}', '{subproduto["subproduto"]}', {subproduto["quantidade"]}, {subproduto["ativo"]}, '{subproduto["data_criacao"]}', '{subproduto["data_edicao"]}')"""
                    )
                self.ids.administrador_mensagens.text = "Subprodutos salvos em SQL"
            except Exception as e:
                self.ids.administrador_mensagens.text = "Subprodutos não salvos em SQL"
                return

            try:
                for agenda in conteudo["agenda"]:
                    self.sql.execute(
                        f"""INSERT INTO agenda (id_subproduto, quantidade, data_entrega, descricao, ativo) VALUES
                        ({agenda["id_subproduto"]}, {agenda["quantidade"]}, '{agenda["data_entrega"]}', '{agenda["descricao"]}', {agenda["ativo"]})"""
                    )
                self.ids.administrador_mensagens.text = "Agenda salva em SQL"
            except:
                self.ids.administrador_mensagens.text = "Agenda não salva em SQL"
                return

            try:
                for historico_agenda in conteudo["historico_agenda"]:
                    self.sql.execute(
                        f"""INSERT INTO historico_agenda (id_subproduto, quantidade, data_entrega, descricao, forma_pagamento, preco_total) VALUES
                        ({historico_agenda["id_subproduto"]}, {historico_agenda["quantidade"]}, '{historico_agenda["data_entrega"]}', '{historico_agenda["descricao"]}', '{historico_agenda["forma_pagamento"]}', {historico_agenda["preco_total"]})"""
                    )
                self.ids.administrador_mensagens.text = "Histórico da agenda salva em SQL"
            except:
                self.ids.administrador_mensagens.text = "Histórico da agenda não salva em SQL"
                return

            try:
                for feira in conteudo["feiras"]:
                    self.sql.execute(
                        f"""INSERT INTO feiras (data_feira, horario_inicio, horario_final, nome_feira, local_feira, descricao, ativo) VALUES
                        ('{feira["data_feira"]}', '{feira["horario_inicio"]}', '{feira["horario_final"]}', '{feira["nome_feira"]}', '{feira["local_feira"]}', '{feira["descricao"]}', {feira["ativo"]})"""
                    )
                self.ids.administrador_mensagens.text = "Feiras salvas em SQL"
            except:
                self.ids.administrador_mensagens.text = "Feiras não salvas em SQL"
                return

            try:
                for subprodutos_feira in conteudo["subprodutos_feira"]:
                    self.sql.execute(
                        f"""INSERT INTO subprodutos_feira (id_feira, id_subproduto, quantidade, ativo) VALUES
                        ({subprodutos_feira["id_feira"]}, {subprodutos_feira["id_subproduto"]}, {subprodutos_feira["quantidade"]}, {subprodutos_feira["ativo"]})"""
                    )
                self.ids.administrador_mensagens.text = "Produtos das feiras salvos em SQL"
            except:
                self.ids.administrador_mensagens.text = "Produtos das feiras não salvos em SQL"
                return

            try:
                for feiras_vendas in conteudo["feiras_vendas"]:
                    self.sql.execute(
                        f"""INSERT INTO feiras_vendas (id_feira, id_subproduto, quantidade, descricao, preco, forma_pagamento, ativo) VALUES
                        ({feiras_vendas["id_feira"]}, {feiras_vendas["id_subproduto"]}, {feiras_vendas["quantidade"]}, '{feiras_vendas["descricao"]}', {feiras_vendas["preco"]}, '{feiras_vendas["forma_pagamento"]}', {feiras_vendas["ativo"]})"""
                    )
                self.ids.administrador_mensagens.text = "Produtos das feiras vendas salvos em SQL"
            except:
                self.ids.administrador_mensagens.text = "Produtos das feiras vendas não salvos em SQL"
                return

            try:
                for historico_feiras in conteudo["historico_feiras"]:
                    self.sql.execute(
                        f"""INSERT INTO historico_feiras (horario_inicio, horario_final, nome_feira, local_feira, data_feira, descricao) VALUES
                        ('{historico_feiras["horario_inicio"]}', '{historico_feiras["horario_final"]}', '{historico_feiras["nome_feira"]}', '{historico_feiras["local_feira"]}', '{historico_feiras["data_feira"]}', '{historico_feiras["descricao"]}')"""
                    )
                self.ids.administrador_mensagens.text = "Histórico das feiras salvo em SQL"
            except:
                self.ids.administrador_mensagens.text = "Histórico das feiras não salvo em SQL"
                return

            try:
                for historico_feiras_vendas in conteudo["historico_feiras_vendas"]:
                    self.sql.execute(
                        f"""INSERT INTO historico_feiras_vendas (id_historico_feira, id_subproduto, quantidade, descricao, preco_total, forma_pagamento) VALUES
                        ({historico_feiras_vendas["id_historico_feira"]}, {historico_feiras_vendas["id_subproduto"]}, {historico_feiras_vendas["quantidade"]}, '{historico_feiras_vendas["descricao"]}', {historico_feiras_vendas["preco_total"]}, '{historico_feiras_vendas["forma_pagamento"]}')"""
                    )
                self.ids.administrador_mensagens.text = "Histórico das vendas das feiras salvo em SQL"
            except:
                self.ids.administrador_mensagens.text = "Histórico das vendas das feiras salvo em SQL"
                return

            try:
                for financas_atual in conteudo["financas_atual"]:
                    self.sql.execute(
                        f"""INSERT INTO financas_atual (nome, local, data, forma_pagamento, preco, descricao, ativo) VALUES
                        ('{financas_atual["nome"]}', '{financas_atual["local"]}', '{financas_atual["data"]}', '{financas_atual["forma_pagamento"]}', {financas_atual["preco"]}, '{financas_atual["descricao"]}', {financas_atual["ativo"]})"""
                    )
                self.ids.administrador_mensagens.text = "Finanças atual salvo em SQL"
            except:
                self.ids.administrador_mensagens.text = "Finanças atual salvo em SQL"
                return

            try:
                for historico_financas in conteudo["historico_financas"]:
                    self.sql.execute(
                        f"""INSERT INTO historico_financas (mes, ano) VALUES
                        ('{historico_financas["mes"]}', '{historico_financas["ano"]}')"""
                    )
                self.ids.administrador_mensagens.text = "Histórico finanças salvo em SQL"
            except:
                self.ids.administrador_mensagens.text = "Histórico finanças não salvo em SQL"
                return

            try:
                for historico_financas_compras in conteudo["historico_financas_compras"]:
                    self.sql.execute(
                        f"""INSERT INTO historico_financas_compras (id_historico_financas, nome, local, data, forma_pagamento, preco, descricao) VALUES
                        ({historico_financas_compras["id_historico_financas"]}, '{historico_financas_compras["nome"]}', '{historico_financas_compras["local"]}', '{historico_financas_compras["data"]}', '{historico_financas_compras["forma_pagamento"]}', {historico_financas_compras["preco"]}, '{historico_financas_compras["descricao"]}')"""
                    )
                self.ids.administrador_mensagens.text = "Histórico finanças compras salvo em SQL"
            except:
                self.ids.administrador_mensagens.text = "Histórico finanças compras não salvo em SQL"
                return

            try:
                for imagens_subprodutos_estoque in conteudo["imagens_subprodutos_estoque"]:
                    self.sql.execute(
                        f"""INSERT INTO imagens_subprodutos_estoque (imagem, id_subproduto, ativo, data_criacao, data_edicao) VALUES
                        ('{imagens_subprodutos_estoque["imagem"]}', {imagens_subprodutos_estoque["id_subproduto"]}, {imagens_subprodutos_estoque["ativo"]}), '{imagens_subprodutos_estoque["data_criacao"]}', '{imagens_subprodutos_estoque["data_edicao"]}'"""
                    )
                    self.ids.administrador_mensagens.text = "Imagens subprodutos estoque salvo em SQL"
            except:
                self.ids.administrador_mensagens.text = "Imagens subprodutos estoque não salvo em SQL"
                return

            self.sql.execute("SET FOREIGN_KEY_CHECKS=1")

            self.database.commit()
            self.ids.administrador_mensagens.text = f"Concluido JSON -> SQL sem erros"

    def copiar_json(self):
        Clipboard.copy(str(App.get_running_app().conteudo))
        self.ids.administrador_mensagens.text = "Informações copiadas"

    def salvar_json(self, texto):
        try:
            info = eval(texto)
            if type(info) == dict:
                if info.keys() == App.get_running_app().conteudo.keys():
                    salvar(info)
                    App.get_running_app().conteudo = info
                    self.ids.administrador_mensagens.text = "Arquivo JSON salvo"
                    self.ids.salvar_json.text = ""
                else:
                    self.ids.administrador_mensagens.text = "Faltam chaves"
            else:
                self.ids.administrador_mensagens.text = "Não é objeto JSON, falha ao salvar"
        except:
            self.ids.administrador_mensagens.text = "Falha ao salvar arquivo JSON"

    def janela_admin(self):
        self.vezes_clicadas_janela_admin += 1
        if self.vezes_clicadas_janela_admin >= 3:
            self.ids.gerenciador_telas_principal.current = "administrador"
            self.ids.gerenciador_telas_principal.transition.direction = "down"
            self.vezes_clicadas_janela_admin = 0

    def Android_back_click(self, window, key, *largs):
        if key == 27:
            if self.ids.gerenciador_telas_principal.current == "administrador":
                self.ids.gerenciador_telas_principal.current = "menu"
                self.ids.gerenciador_telas_principal.transition.direction = "up"

            elif self.ids.gerenciador_telas_principal.current == "estoque":
                if self.ids.gerenciador_telas_principal.get_screen("estoque").ids.gerenciador_colecoes.current != "mostrar colecoes":
                    if self.ids.gerenciador_telas_principal.get_screen("estoque").ids.gerenciador_produtos.current != "mostrar produtos":
                        if self.ids.gerenciador_telas_principal.get_screen("estoque").ids.gerenciador_subprodutos.current != "mostrar subprodutos":
                            self.ids.gerenciador_telas_principal.get_screen("estoque").ids.gerenciador_subprodutos.transition.direction = "up"
                            self.ids.gerenciador_telas_principal.get_screen("estoque").ids.gerenciador_subprodutos.current = "mostrar subprodutos"
                            return True
                        else:
                            self.ids.gerenciador_telas_principal.get_screen("estoque").ids.gerenciador_produtos.current = "mostrar produtos"
                            self.ids.gerenciador_telas_principal.get_screen("estoque").ids.gerenciador_produtos.transition.direction = "up"
                            return True
                    else:
                        self.ids.gerenciador_telas_principal.get_screen("estoque").ids.gerenciador_colecoes.current = "mostrar colecoes"
                        self.ids.gerenciador_telas_principal.get_screen("estoque").ids.gerenciador_colecoes.transition.direction = "up"
                        return True
                else:
                    self.ids.gerenciador_telas_principal.current = "menu"
                    self.ids.gerenciador_telas_principal.transition.direction = "right"
                    return True
                        
            elif self.ids.gerenciador_telas_principal.current == "feiras":
                if self.ids.gerenciador_telas_principal.get_screen("feiras").ids.gerenciador_feiras.current == "concluir feira":
                    if self.ids.gerenciador_telas_principal.get_screen("feiras").ids.gerenciador_concluir_feira.current == "concluir feira principal":
                        self.ids.gerenciador_telas_principal.get_screen("feiras").ids.gerenciador_feiras.current = "scroll_feiras_principal"
                        self.ids.gerenciador_telas_principal.get_screen("feiras").ids.gerenciador_feiras.transition.direction = "up"
                        return True
                    else:
                        self.ids.gerenciador_telas_principal.get_screen("feiras").ids.gerenciador_concluir_feira.current = "concluir feira principal"
                        self.ids.gerenciador_telas_principal.get_screen("feiras").ids.gerenciador_concluir_feira.transition.direction = "right"
                        return True
                
                elif self.ids.gerenciador_telas_principal.get_screen("feiras").ids.gerenciador_feiras.current != "scroll_feiras_principal":
                    self.ids.gerenciador_telas_principal.get_screen("feiras").ids.gerenciador_feiras.current = "scroll_feiras_principal"
                    self.ids.gerenciador_telas_principal.get_screen("feiras").ids.gerenciador_feiras.transition.direction = "up"
                    return True
                
                else:
                    self.ids.gerenciador_telas_principal.current = "menu"
                    self.ids.gerenciador_telas_principal.transition.direction = "right"
                    return True
            
            elif self.ids.gerenciador_telas_principal.current == "agenda":
                if self.ids.gerenciador_telas_principal.get_screen("agenda").ids.gerenciador_agenda.current != "principal":
                    self.ids.gerenciador_telas_principal.get_screen("agenda").ids.gerenciador_agenda.current = "principal"
                    self.ids.gerenciador_telas_principal.get_screen("agenda").ids.gerenciador_agenda.transition.direction = "up"
                    return True
                
                else:
                    self.ids.gerenciador_telas_principal.current = "menu"
                    self.ids.gerenciador_telas_principal.transition.direction = "right"
                    return True
            
            elif self.ids.gerenciador_telas_principal.current == "historico":
                if self.ids.gerenciador_telas_principal.get_screen("historico").ids.gerenciador_historico.current != "historico_vendas":
                    self.ids.gerenciador_telas_principal.get_screen("historico").ids.gerenciador_historico.current = "historico_vendas"
                    self.ids.gerenciador_telas_principal.get_screen("historico").ids.gerenciador_historico.transition.direction = "right"
                    self.ids.gerenciador_telas_principal.get_screen("historico").ids.gerenciador_historico.current = "historico_vendas"
                    self.ids.gerenciador_telas_principal.get_screen("historico").ids.botao_produtos_historico.parent.background_color = 1, 36/255, 148/255, 1
                    self.ids.gerenciador_telas_principal.get_screen("historico").ids.botao_feiras_historico.parent.background_color = 0, 0, 0, 0.1
                    return True
                
                else:
                    self.ids.gerenciador_telas_principal.current = "menu"
                    self.ids.gerenciador_telas_principal.transition.direction = "right"
                    return True
            
            elif self.ids.gerenciador_telas_principal.current == "financas":
                if self.ids.gerenciador_telas_principal.get_screen("financas").ids.gerenciador_financas.current == "financas atual":
                    if self.ids.gerenciador_telas_principal.get_screen("financas").ids.gerenciador_financas_atual.current !="financas atual principal":
                        self.ids.gerenciador_telas_principal.get_screen("financas").ids.gerenciador_financas_atual.current = "financas atual principal"
                        self.ids.gerenciador_telas_principal.get_screen("financas").ids.gerenciador_financas_atual.transition.direction = "up"
                        return True

                    else:
                        self.ids.gerenciador_telas_principal.current = "menu"
                        self.ids.gerenciador_telas_principal.transition.direction = "right"
                        return True
                
                elif self.ids.gerenciador_telas_principal.get_screen("financas").ids.gerenciador_financas.current != "financas atual":
                    self.ids.gerenciador_telas_principal.get_screen("financas").ids.gerenciador_financas.transition.direction = "right"
                    self.ids.gerenciador_telas_principal.get_screen("financas").ids.gerenciador_financas.current = "financas atual"
                    self.ids.gerenciador_telas_principal.get_screen("financas").ids.botao_financas.parent.background_color = 1, 36/255, 148/255, 1
                    self.ids.gerenciador_telas_principal.get_screen("financas").ids.botao_financas_historico.parent.background_color = 0, 0, 0, 0.1
                    return True
                
                else:
                    self.ids.gerenciador_telas_principal.current = "menu"
                    self.ids.gerenciador_telas_principal.transition.direction = "right"
                    return True
        
        return True
    
    def file_chooser(self, lugar):
        if lugar == "adicionar produtos":
            filechooser.open_file(on_selection=self.adicionar_produtos_imagem)
        
        elif lugar == "editar produtos":
            filechooser.open_file(on_selection=self.editar_produtos_imagem)

        elif lugar == "adicionar subprodutos":
            filechooser.open_file(on_selection=self.adicionar_subprodutos_imagem)
        
        elif lugar == "editar subprodutos":
            filechooser.open_file(on_selection=self.editar_subprodutos_imagem)

        elif lugar == "imagens subprodutos":
            filechooser.open_file(on_selection=self.adicionar_imagens_adicionais_subprodutos)

        elif lugar == "adicionar colecoes":
            filechooser.open_file(on_selection=self.adicionar_colecao_imagem)

        elif lugar == "editar colecoes":
            filechooser.open_file(on_selection=self.editar_colecao_imagem)

    def editar_colecao_imagem(self, selecao):
        if selecao:
            self.ids.gerenciador_telas_principal.get_screen("estoque").ids.adicionar_colecoes_imagem.source = selecao[0]

    def adicionar_colecao_imagem(self, selecao):
        if selecao:
            self.ids.gerenciador_telas_principal.get_screen("estoque").ids.adicionar_colecoes_imagem.source = selecao[0]
    
    def adicionar_imagens_adicionais_subprodutos(self, selecao):
        if selecao:
            self.ids.gerenciador_telas_principal.get_screen("estoque").ids.scroll_imagens_subprodutos.adicionar(selecao[0])
            self.ids.gerenciador_telas_principal.get_screen("estoque").ids.scroll_imagens_subprodutos.atualizar()
    
    def adicionar_produtos_imagem(self, selecao):
        if selecao:
            self.ids.gerenciador_telas_principal.get_screen("estoque").ids.adicionar_produto_imagem.source = selecao[0]

    def editar_produtos_imagem(self, selecao):
        if selecao:
            self.ids.gerenciador_telas_principal.get_screen("estoque").ids.editar_produto_imagem.source = selecao[0]

    def adicionar_subprodutos_imagem(self, selecao):
        if selecao:
            self.ids.gerenciador_telas_principal.get_screen("estoque").ids.adicionar_subproduto_imagem.source = selecao[0]

    def editar_subprodutos_imagem(self, selecao):
        if selecao:
            self.ids.gerenciador_telas_principal.get_screen("estoque").ids.editar_subproduto_imagem.source = selecao[0]


class MyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.previsoes_tempo = previsoes
        self.conteudo = carregar()
        self.width = Window.size[0]
        self.center_x = Window.center[0]
        self.popup = Popup(title='Imagens copiadas!', title_align="center", title_size=70,
                           separator_color=[0, 0, 0, 0],
        size_hint=(None, None), size=(700, 170), separator_height=0)

        informacoes_api = carregar("woocommerce")
        url = informacoes_api["url"]
        consumer_key = informacoes_api["consumer_key"]
        consumer_secret = informacoes_api["consumer_secret"]

        self.wc_conectado = True

        """
        woocommerce 
        try:
            self.wcapi = API(
                url = url,
                consumer_key = consumer_key,
                consumer_secret = consumer_secret,
                timeout=15
            )

            self.params = {
                'per_page': 100
            }

            self.categorias = self.wcapi.get("products/categories", params=self.params).json()
            self.produtos = self.wcapi.get("products/categories", params=self.params).json()
            self

            for pos, afazer in enumerate(informacoes_api["todo"]):
                tipo = afazer["tipo"]
                conteudo = afazer["conteudo"]
                if tipo == "produto":
                    self.enviar_produto_site(conteudo)
                elif tipo == "categoria":
                    self.enviar_categoria_site(conteudo)
                elif tipo == "variante":
                    self.enviar_variante_site(conteudo)
                elif tipo == "imagens":
                    self.enviar_imagens_site(conteudo)

                informacoes_api["todo"].pop(pos)
            salvar(informacoes_api, "woocommerce")
        except:
            self.wc_conectado = False
        """
            
    def enviar_site(self, tipo, conteudo):
        if self.wc_conectado:
            if tipo == "produto":
                self.enviar_produto_site(conteudo)
            elif tipo == "categoria":
                self.enviar_categoria_site(conteudo)
            elif tipo == "variante":
                self.enviar_variante_site(conteudo)
            elif tipo == "imagens":
                self.enviar_imagens_site(conteudo)

        else:
            conteudo = carregar("woocommerce")
            conteudo["todo"].append({
                "tipo": tipo,
                "conteudo": conteudo
            })
            salvar(conteudo, "woocommerce")

    def enviar_imagens_site(self, conteudo):
        pass

    def enviar_variante_site(self, conteudo):
        pass

    def enviar_categoria_site(self, conteudo):
        pass

    def enviar_produto_site(self, conteudo):
        pass
        
    def ajustar_fonte(self, tamanho_fonte, largura, texto):
        label = Label(font_size=tamanho_fonte, width=largura, text=texto)
        label.texture_update()
        largura, altura = label.texture_size

        while largura > label.width:
            label.font_size -= 5
            label.texture_update()
            largura, altura = label.texture_size

        label.font_size -= 1
        return label.font_size
     
    def mostrar_popup(self):
        self.popup.open()

    def copiar_imagem(self, widget="", source=""):
        if source == "":
            source = widget.source
        img = Image.open(source)
        filename = os.path.basename(source)
        filename = os.path.join(gallery_path, filename[:-4] + "_copia" + filename[-4:])
        #filename = os.path.join(filename[:-4] + "_copia" + filename[-4:])
        if os.path.isfile(filename):
            os.remove(filename)
        img.save(filename)
        self.mostrar_popup()

    def build(self):
        return Geral()
    

MyApp().run()