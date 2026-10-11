# Comportamentos conhecidos para etapas futuras

Registro separado dos testes de contrato. Estes itens descrevem o comportamento
encontrado no código original; não foram alterados nesta etapa.

1. `access.requests.open_dict` concatena sempre `/{page}` à URL. Uma chamada sem
   complemento termina em `/`, mesmo quando o endpoint já poderia ser usado sem
   barra final. O comportamento pode depender do servidor.
2. A função não chama `raise_for_status` nem trata erros HTTP. Respostas de erro
   que contenham JSON válido são decodificadas e retornadas como se fossem
   respostas normais; JSON inválido propaga a exceção do decodificador.
3. O fluxo da interface em `app/App.py` interpreta listas como sequência de
   itens, mas para dicionários de resposta de complemento apresenta valores
   superficialmente: listas são expandidas um nível e dicionários aninhados não
   são percorridos recursivamente.
4. Em uma falha na busca com complemento, a interface limpa a lista de
   resultados e mostra `Erro de acesso`; na busca sem complemento, a exceção é
   impressa no texto sem inserir essa indicação na lista.

Esses registros são observações estáticas do fluxo atual, não requisitos de
correção nem testes de regressão aprovados para a próxima etapa.
