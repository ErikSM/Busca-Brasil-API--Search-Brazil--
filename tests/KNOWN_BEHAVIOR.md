# Comportamentos conhecidos após a Etapa 02

## Corrigidos nesta etapa

- Busca por CNPJ aceita os 12 primeiros caracteres alfanuméricos ASCII e dois dígitos finais, remove pontos, barras e hífens e converte letras para maiúsculas; ISBN aceita ISBN-10 ou ISBN-13 com ou sem hífens, converte `x` final para `X` e consulta com o valor sem hífens; código bancário aceita de um a três dígitos ASCII e preserva zeros à esquerda. Os validadores são associados aos nomes existentes das operações. Entradas rejeitadas não chamam o cliente HTTP. Não há cálculo de dígitos verificadores.
- Busca por CEP aceita oito dígitos com ou sem hífen e consulta com o valor normalizado; busca por DDD exige dois dígitos e feriados exigem ano válido com quatro dígitos. Entradas rejeitadas exibem mensagem e não chamam o cliente HTTP.
- Corretoras por CNPJ reutiliza a validação existente de CNPJ, incluindo remoção de pontuação permitida e conversão para maiúsculas. Busca por Dominio BR remove espaços externos, converte para minúsculas e exige um nome DNS terminado em `.br`; aceita letras Unicode em rótulos internacionalizados e não acrescenta `.br`. A validação verifica apenas o formato, sem conversão IDNA, limite de bytes DNS ou consulta de registro/disponibilidade, que cabe à BrasilAPI. URLs, caminhos, parâmetros, rótulos vazios e caracteres fora do formato são rejeitados antes do cliente HTTP.

- `access.requests.open_dict` não acrescenta barra final quando `page` está vazio; complementos são codificados como um segmento seguro de caminho.
- As requisições usam timeout explícito de 10 segundos e chamam `raise_for_status` antes de decodificar JSON.
- JSON inválido propaga a exceção de decodificação do `requests`, permitindo que o fluxo existente da interface trate a falha.
- Respostas JSON em listas ou dicionários continuam sendo retornadas nos tipos Python correspondentes.

## Ainda existentes e fora do escopo

- O fluxo da interface em `app/App.py` interpreta listas como sequência de itens, mas para dicionários de resposta de complemento apresenta valores superficialmente: listas são expandidas um nível e dicionários aninhados não são percorridos recursivamente.
- Em uma falha na busca com complemento, a interface limpa a lista de resultados e mostra `Erro de acesso`; na busca sem complemento, a exceção é impressa no texto sem inserir essa indicação na lista.
- As outras operações que usam complemento continuam sem validação específica.
