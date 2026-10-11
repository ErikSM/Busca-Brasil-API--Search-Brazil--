# Comportamentos conhecidos após a Etapa 02

## Corrigidos nesta etapa

- Busca por CEP aceita oito dígitos com ou sem hífen e consulta com o valor normalizado; busca por DDD exige dois dígitos e feriados exigem ano válido com quatro dígitos. Entradas rejeitadas exibem mensagem e não chamam o cliente HTTP.

- `access.requests.open_dict` não acrescenta barra final quando `page` está vazio; complementos são codificados como um segmento seguro de caminho.
- As requisições usam timeout explícito de 10 segundos e chamam `raise_for_status` antes de decodificar JSON.
- JSON inválido propaga a exceção de decodificação do `requests`, permitindo que o fluxo existente da interface trate a falha.
- Respostas JSON em listas ou dicionários continuam sendo retornadas nos tipos Python correspondentes.

## Ainda existentes e fora do escopo

- O fluxo da interface em `app/App.py` interpreta listas como sequência de itens, mas para dicionários de resposta de complemento apresenta valores superficialmente: listas são expandidas um nível e dicionários aninhados não são percorridos recursivamente.
- Em uma falha na busca com complemento, a interface limpa a lista de resultados e mostra `Erro de acesso`; na busca sem complemento, a exceção é impressa no texto sem inserir essa indicação na lista.
- As outras operações que usam complemento continuam sem validação específica.
