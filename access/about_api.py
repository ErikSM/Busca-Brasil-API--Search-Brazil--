
general_information = "\nAcesso programático de informações é algo fundamental \n" \
                      "na comunicação entre sistemas, mas, para nossa surpresa, \n" \
                      "uma informação tão útil e pública quanto um CEP não \n" \
                      "consegue ser acessada diretamente por um navegador por \n" \
                      "conta da API dos Correios não possuir CORS habilitado. Dado \n" \
                      "a isso, este projeto experimental tem como objetivo \n" \
                      "centralizar e disponibilizar endpoints modernos com \n" \
                      "baixíssima latência utilizando tecnologias como Vercel Smart \n" \
                      "CDN responsável por fazer o cache das informações em atualmente \n" \
                      "23 regiões distribuídas ao longo do mundo (incluindo Brasil). \n" \
                      "Então não importa o quão devagar for a fonte dos dados, nós \n" \
                      "queremos disponibilizá-la da forma mais rápida e moderna possível.\n" \
                      "\nRecursos disponíveis: \n" \
                      "- CEP \n" \
                      "- DDD \n" \
                      "- Bank \n" \
                      "- CNPJ \n" \
                      "- Feriados Nacionais \n" \
                      "- Tabela FIPE \n" \
                      "- ISBN \n" \
                      "- Registros de domínio br \n" \
                      "- Taxas \n"

about_banks = "Informações sobre sistema bancário: \n" \
              "* Retorna lista de todos os bancos do Brasil\n"

about_banks_specific = "Busca as informações de um especifico banco a partir de um código\n"

about_stockbrokers = "Retorna lista de todas as corretoras nos arquivos da CVM.\n"

about_stockbroke_specific = "Busca por informacoes de uma corretoras especifica nos arquivos da CVM.\n"

about_cep = "O CEP (Código de Endereçamento Postal) é um sistema de códigos que visa racionalizar \n" \
            "o processo de encaminhamento e entrega de correspondências através da divisão do país \n" \
            "em regiões postais. ... Atualmente, o CEP é composto por oito dígitos, cinco de um lado \n" \
            "e três de outro. Cada algarismo do CEP possui um significado.\n"


about_cnpj = "O Cadastro Nacional da Pessoa Jurídica é um número único que identifica uma pessoa jurídica \n" \
             "e outros tipos de arranjo jurídico sem personalidade jurídica junto à Receita Federal.\n"


about_cptec = "Retorna listagem com todas as cidades junto a seus respectivos códigos presentes nos serviços \n" \
              "da CPTEC. O Código destas cidades será utilizado para os serviços de meteorologia e a \n" \
              "ondas (previsão oceânica) fornecido pelo centro. Leve em consideração que o WebService do CPTEC \n" \
              "as vezes é instável, então se não encontrar uma determinada cidade na listagem completa, tente \n" \
              "buscando por parte de seu nome no endpoint de busca.\n"

about_cptec_cities = "Retorna listagem com todas as cidades correspondentes ao termo pesquisado junto a seus \n" \
                   "respectivos códigos presentes nos serviços da CPTEC. O Código destas cidades será utilizado \n" \
                   "para os serviços de meteorologia e a ondas (previsão oceânica) fornecido pelo centro.\n"

about_cptec_capital = "Condições atuais nas capitais: \n" \
                      "Retorna condições meteorológicas atuais nas capitais do país, com base nas estações de \n" \
                      "solo de seu aeroporto.\n"

about_cptec_airport = "Condições atuais no aeroporto: \n" \
                      "Retorna condições meteorológicas atuais no aeroporto solicitado. Este endpoint \n" \
                      "utiliza o código ICAO (4 dígitos) do aeroporto.\n"

about_cptec_city_meteorology = "Previsão meteorológica para uma cidade: \n" \
                               "Retorna Pervisão meteorológica para 1 dia na cidade informada.\n"

about_cptec_sea_waves = "Previsão oceânica: \n" \
                        "Retorna a previsão oceânica para a cidade informada para 1 dia\n"

about_ddd = "DDD significa Discagem Direta à Distância. É um sistema de ligação telefônica \n" \
            "automática entre diferentes áreas urbanas nacionais. O DDD é um código constituído \n" \
            "por 2 dígitos que identificam as principais cidades do país e devem ser adicionados \n" \
            "ao nº de telefone, juntamente com o código da operadora.\n"

about_holidays = "Lista os feriados nacionais de determinado ano: \n" \
                 "Calcula os feriados móveis baseados na Páscoa e adiciona os feriados fixos\n"

about_fipe_types = "Informações sobre Preço Médio de Veículos fornecido \n" \
                   "pela FIPE (Fundação Instituto de Pesquisas Econômicas) \n\n" \
                   "*Lista as marcas de veículos referente ao tipo de veículo\n" \
                   "   Os tipos suportados são caminhoes, carros e motos. Quando o tipo não é específicado \n" \
                   "são buscada as marcas de todos os tipos de veículos\n"

about_fipe_price = "Consulta o preço do veículo segundo a tabela fipe.(Código fipe do veículo)\n"

about_fipe = "Lista as tabelas de referência existentes\n"

about_isbn = "Informações sobre livros publicados no Brasil (prefixo 65 ou 85) a partir do ISBN, um sistema \n" \
             "internacional de identificação de livros que utiliza números para classificá-los por título, autor, \n" \
             "país, editora e edição.\n\n" \
             "* O código informado pode conter traços (-) e ambos os formatos são aceitos, sendo \n" \
             "eles o obsoleto de 10 dígitos e o atual de 13 dígitos.\n"

about_ncm = "Retorna informações de todos os NCMs:\n\n" \
            "* O NCM representa uma nomenclatura que identifica códigos de oito dígitos para produtos \n" \
            "diversos, que vão desde: produtos de origem animal, como o leite, têxteis e metais.\n"

about_ncm_product = "Pesquisa por NCMs a partir de um código ou descrição.\n"

about_pix = "Retorna informações de todos os participantes do PIX no dia atual ou anterior\n"

about_domain = "Avalia o status de um: (dominio .br)"

about_taxes = "Retorna as taxas de juros e alguns índices oficiais do Brasil\n"

about_specific_taxes = "Busca as informações de uma taxa a partir do seu nome/sigla\n"


