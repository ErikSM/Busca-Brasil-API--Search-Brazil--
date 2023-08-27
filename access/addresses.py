
bank_and_stockbroker = dict()
address_and_register = dict()

cptec_meteorology = dict()
holidays = dict()

fipe_vehicles = dict()
isnb_books = dict()
ncm_products = dict()


taxes = dict()


bank_and_stockbroker["Todos os bancos"] = ("https://brasilapi.com.br/api/banks/v1", False)
bank_and_stockbroker["Banco por codigo"] = ("https://brasilapi.com.br/api/banks/v1", True)
bank_and_stockbroker["Corretoras"] = ("https://brasilapi.com.br/api/cvm/corretoras/v1", False)
bank_and_stockbroker["Corretoras por CNPJ"] = ("https://brasilapi.com.br/api/cvm/corretoras/v1", True)
bank_and_stockbroker["Participantes do pix"] = ("https://brasilapi.com.br/api/pix/v1/participants", False)

address_and_register["Busca CEP"] = ("https://brasilapi.com.br/api/cep/v1", True)
address_and_register["Busca CNPJ"] = ("https://brasilapi.com.br/api/cnpj/v1", True)
address_and_register["Busca DDD"] = ("https://brasilapi.com.br/api/ddd/v1", True)
address_and_register["Busca Dominio BR"] = ("https://brasilapi.com.br/api/registrobr/v1", True)

cptec_meteorology["Cidades da CPTEC"] = ("https://brasilapi.com.br/api/cptec/v1/cidade", True)
cptec_meteorology["Clima em capitais"] = ("https://brasilapi.com.br/api/cptec/v1/clima/capital", False)
cptec_meteorology["Clima em aeroportos"] = ("https://brasilapi.com.br/api/cptec/v1/clima/aeroporto", True)
cptec_meteorology["Clima em cidade"] = ("https://brasilapi.com.br/api/cptec/v1/clima/previsao", True)
cptec_meteorology["Onda em cidade"] = ("https://brasilapi.com.br/api/cptec/v1/ondas", True)

holidays["Feriados do ano"] = ("https://brasilapi.com.br/api/feriados/v1", True)

fipe_vehicles["Marcas por tipo de veiculo"] = ("https://brasilapi.com.br/api/fipe/marcas/v1", True)
fipe_vehicles["Preco do veiculo"] = ("https://brasilapi.com.br/api/fipe/preco/v1", True)
fipe_vehicles["Todas as ta tabelas FIPE"] = ("https://brasilapi.com.br/api/fipe/tabelas/v1", False)

isnb_books["Busca Livro da ISNB"] = ("https://brasilapi.com.br/api/isbn/v1", True)

ncm_products["Produtos da NCM"] = ("https://brasilapi.com.br/api/ncm/v1", False)
ncm_products["Produto por codigo"] = ("https://brasilapi.com.br/api/ncm/v1", False)

taxes["Taxas oficiais"] = ("https://brasilapi.com.br/api/taxas/v1", False)
taxes["Taxa por sigla"] = ("https://brasilapi.com.br/api/taxas/v1", True)
