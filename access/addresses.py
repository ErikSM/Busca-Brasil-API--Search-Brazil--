from access.about_api import *

bank_and_stockbroker = dict()
address_and_register = dict()

cptec_meteorology = dict()
holidays = dict()

fipe_vehicles = dict()
isnb_books = dict()
ncm_products = dict()


taxes = dict()


bank_and_stockbroker["Todos os bancos"] = ("https://brasilapi.com.br/api/banks/v1", False,
                                           about_banks)
bank_and_stockbroker["Banco por codigo"] = ("https://brasilapi.com.br/api/banks/v1", True,
                                            about_banks_specific)
bank_and_stockbroker["Todas as Corretoras"] = ("https://brasilapi.com.br/api/cvm/corretoras/v1", False,
                                               about_stockbrokers)
bank_and_stockbroker["Corretoras por CNPJ"] = ("https://brasilapi.com.br/api/cvm/corretoras/v1", True,
                                               about_stockbroke_specific)
bank_and_stockbroker["Participantes do pix"] = ("https://brasilapi.com.br/api/pix/v1/participants", False,
                                                about_pix)

address_and_register["Busca por CEP"] = ("https://brasilapi.com.br/api/cep/v1", True, about_cep)
address_and_register["Busca por CNPJ"] = ("https://brasilapi.com.br/api/cnpj/v1", True, about_cnpj)
address_and_register["Busca por DDD"] = ("https://brasilapi.com.br/api/ddd/v1", True, about_ddd)
address_and_register["Busca por Dominio BR"] = ("https://brasilapi.com.br/api/registrobr/v1", True, about_domain)

cptec_meteorology["Cidades da CPTEC"] = ("https://brasilapi.com.br/api/cptec/v1/cidade", False,
                                         about_cptec)
cptec_meteorology["CPTEC por cidade"] = ("https://brasilapi.com.br/api/cptec/v1/cidade", True,
                                         about_cptec_cities)
cptec_meteorology["Clima em capitais"] = ("https://brasilapi.com.br/api/cptec/v1/clima/capital", False,
                                          about_cptec_capital)
cptec_meteorology["Clima em aeroportos por codigo"] = ("https://brasilapi.com.br/api/cptec/v1/clima/aeroporto", True,
                                                       about_cptec_airport)
cptec_meteorology["Clima em cidade por codigo"] = ("https://brasilapi.com.br/api/cptec/v1/clima/previsao", True,
                                                   about_cptec_city_meteorology)
cptec_meteorology["Onda em cidade por codigo"] = ("https://brasilapi.com.br/api/cptec/v1/ondas", True,
                                                  about_cptec_sea_waves)

holidays["Feriados por ano"] = ("https://brasilapi.com.br/api/feriados/v1", True, about_holidays)

fipe_vehicles["Marcas por caminhoes, carros ou moto"] = ("https://brasilapi.com.br/api/fipe/marcas/v1", True,
                                                         about_fipe_types)
fipe_vehicles["Preco de veiculo por codigo FIPE"] = ("https://brasilapi.com.br/api/fipe/preco/v1", True,
                                                     about_fipe_price)
fipe_vehicles["Todas as tabelas FIPE"] = ("https://brasilapi.com.br/api/fipe/tabelas/v1", False,
                                          about_fipe)

isnb_books["Busca Livro por ISNB"] = ("https://brasilapi.com.br/api/isbn/v1", True, about_isbn)

ncm_products["Produtos da NCM"] = ("https://brasilapi.com.br/api/ncm/v1", False, about_ncm)
ncm_products["Produto por codigo"] = ("https://brasilapi.com.br/api/ncm/v1", True, about_ncm_product)

taxes["Taxas oficiais"] = ("https://brasilapi.com.br/api/taxas/v1", False, about_taxes)
taxes["Taxa por sigla"] = ("https://brasilapi.com.br/api/taxas/v1", True, about_specific_taxes)
