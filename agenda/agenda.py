from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from save_and_load import *
from kivy.app import App
import datetime


class Agenda_scroll(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.editando_agenda = 0
        self.mais_informacoes_agenda = 0
        self.conteudo = App.get_running_app().conteudo
        self.anos = [str(datetime.date.today().year), str(datetime.date.today().year + 1), str(datetime.date.today().year + 2)]
        self.atualizar()

    def procurar_produtos(self, colecao_nome):
        self.conteudo = App.get_running_app().conteudo
        id = 0
        for colecao in self.conteudo["colecoes_estoque"]:
            if colecao["colecao"] == colecao_nome and colecao["ativo"] == 1:
                id = colecao["id"]

        produtos = []
        for produto in self.conteudo["produtos_estoque"]:
            if produto["ativo"] == 1 and produto["id_colecao"] == id:
                produtos.append(produto["produto"])

        return produtos
    
    def colecoes(self):
        self.conteudo = App.get_running_app().conteudo
        colecoes = []
        for colecao in self.conteudo["colecoes_estoque"]:
            if colecao["ativo"] == 1:
                colecoes.append(colecao["colecao"])

        return colecoes
    
    def adicionar_historico(self, forma_pagamento, preco, preco_hint, checkbox_ativo):
        self.conteudo = App.get_running_app().conteudo

        if preco == "":
            preco = float(preco_hint.split()[1])
        else:
            preco = float(preco)

        dic = {
            "id": len(self.conteudo["historico_agenda"]) + 1,
            "id_subproduto": self.conteudo["agenda"][self.mais_informacoes_agenda - 1]["id_subproduto"],
            "quantidade": self.conteudo["agenda"][self.mais_informacoes_agenda - 1]["quantidade"],
            "data_entrega": self.conteudo["agenda"][self.mais_informacoes_agenda - 1]["data_entrega"],
            "descricao": self.conteudo["agenda"][self.mais_informacoes_agenda - 1]["descricao"],
            "forma_pagamento": forma_pagamento,
            "preco_total": preco
        }
        
        if checkbox_ativo:
            self.conteudo["subprodutos_estoque"][self.conteudo["agenda"][self.mais_informacoes_agenda - 1]["id_subproduto"] - 1]["quantidade"] -= self.conteudo["agenda"][self.mais_informacoes_agenda - 1]["quantidade"]
        self.conteudo["historico_agenda"].append(dic)
        self.conteudo["agenda"][self.mais_informacoes_agenda - 1]["ativo"] = 0
        salvar(self.conteudo)
        self.atualizar()

    def editar(self, nome, quantidade, descricao, dia, mes, ano):
        self.conteudo = App.get_running_app().conteudo

        for subproduto in self.conteudo["subprodutos_estoque"]:
            if subproduto["subproduto"] == nome:
                id = subproduto["id"]
                break
        
        dic = {
            "id": self.editando_agenda,
            "id_subproduto": id,
            "quantidade": int(quantidade), 
            "data_entrega": ano + "-" + mes + "-" + dia, 
            "descricao": descricao.strip(),
            "ativo": 1
            }

        self.conteudo["agenda"][self.editando_agenda - 1] = dic
        salvar(self.conteudo)
        self.atualizar()

    def atualizar(self):
        self.conteudo = App.get_running_app().conteudo
        
        ordem = sorted(self.conteudo["agenda"], key=lambda d: d['data_entrega']) 
        ordem.reverse()

        self.clear_widgets(self.children[1:])

        data_atual = ""
        for pos, item in enumerate(ordem):
            if item["ativo"] == 1:
                subproduto = self.conteudo["subprodutos_estoque"][item["id_subproduto"] - 1]
                produto = self.conteudo["produtos_estoque"][subproduto["id_produto"] - 1]
                self.add_widget(Caixa_agenda(
                    id_entrega= item["id"],
                    data= item["data_entrega"],
                    nome_subproduto= subproduto["subproduto"],
                    quantidade= item["quantidade"],
                    preco_produto= produto["preco"],
                    descricao= item["descricao"],
                    imagem= subproduto["imagem"]
                ), index=len(self.children))
                
                try:
                    if ordem[pos + 1]["data_entrega"] != item["data_entrega"]:
                        data_atual = item["data_entrega"]
                        self.add_widget(Label(height=50, size_hint_y=None, text=converter_data(item["data_entrega"]), color=(0.2, 0.2, 0.2, 1), bold=True, font_size=50), index=len(self.children))

                except:
                    data_atual = item["data_entrega"]
                    self.add_widget(Label(height=50, size_hint_y=None, text=converter_data(item["data_entrega"]), color=(0.2, 0.2, 0.2, 1), bold=True, font_size=50), index=len(self.children))

    def excluir(self):
        self.conteudo = App.get_running_app().conteudo
        self.conteudo["agenda"][self.editando_agenda]["ativo"] = 0
        salvar(self.conteudo)
        self.atualizar()

    def adicionar(self, nome, quantidade, descricao, dia, mes, ano):
        self.conteudo = App.get_running_app().conteudo
        
        for subproduto in self.conteudo["subprodutos_estoque"]:
            if subproduto["subproduto"] == nome:
                id_subproduto = subproduto["id"]
                break

        dic = {
            "id": len(self.conteudo["agenda"]) + 1,
            "id_subproduto": id_subproduto,
            "quantidade": int(quantidade), 
            "data_entrega": ano + "-" + mes + "-" + dia, 
            "descricao": descricao.strip(),
            "ativo": 1
            }
        
        self.conteudo["agenda"].append(dic)
        salvar(self.conteudo)
        self.atualizar()


class Caixa_agenda(BoxLayout):
    def __init__(self, id_entrega, data, nome_subproduto, quantidade, preco_produto, descricao, imagem, **kwargs):
        super().__init__(**kwargs)
        self.id_entrega = id_entrega
        self.dia = data[8:]
        self.mes = data[5:7]
        self.ano = data[:4]
        self.nome_subproduto = nome_subproduto
        self.quantidade = str(quantidade)
        self.descricao = descricao
        self.imagem = imagem
        self.ids.data_agenda_caixa.text = converter_data(data)
        self.ids.nome_e_quantidade_subproduto_agenda_caixa.text = nome_subproduto + ":\n" + str(quantidade) + " unidade(s)"
        self.ids.preco_total_agenda_caixa.text = "R$" + "{:,.2f}".format(preco_produto * quantidade)
        self.ids.imagem_agenda_caixa.source = imagem
        if descricao != "" and descricao != "Descrição":
            self.height += 80
            self.add_widget(Label(text=descricao, size_hint_y=0.4, bold=True, font_size=45))


def converter_data(data):
    dia = data[8:]
    mes = data[5:7]
    ano = data[:4]
    data_convertida = dia + "/" + mes + "/" + ano
    return data_convertida


def desconverter_data(data):
    # 01-01-2002
    dia = data[:2]
    mes = data[3:5]
    ano = data[6:]
    data_desconvertida = ano + "-" + mes + "-" + dia
    return data_desconvertida