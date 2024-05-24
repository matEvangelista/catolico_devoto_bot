# Bem-vindo ao repositório do Bot Católico

<p align="center">
    <img style="max-width: 300px; margin: auto" src="exemplo.gif" alt="Exemplo de uso"/> 
</p>

Com este bot, você pode ter acesso aos mistérios do terço do dia corrente (horário de Brasília),
ter acesso ao folheto da Missa dominical disponibilizada pela Arquidiocese do Rio de Janeiro,
saber um pouco sobre um dos santos do dia e acessar versículos da Bíblia.

Há planos para adicionar uma função que retonar parágrafos do catecismo.

## Comandos básicos

### Mistérios do terço
Comando `if else` básicos para a seleção. Os mistérios do dia são listados como descrição (caption) de um conjunto de
imagens que os representam. Além disso, o bot também envia um link para um vídeo do Padre Paulo Ricardo rezando o terço
com os mistérios do dia.

### Santo do dia
Dados obtidos a partir do scraping feito a partir do site da Canção Nova: [Santo do Dia](https://santo.cancaonova.com/). Devido ao limite de 1024
caracteres que o telegram impõe ao texto que acompanha imagens, foi possível enviar apenas o nome do santo e sua oração.

### Folheto
Em primeiro lugar, é feito o scraping da [página de folhetos da ArqRio](https://arqrio.org.br/folhetos). A partir disso,
é selecionada a `</div>` cujo elemento `</h3>` tem a data do domingo mais próximo. Se o usuário executar este comando num
domingo, ele terá o folheto da missa do mesmo dia.

### Bíblia
Os versículos da bíblia são retirados desta api: [biblia-api-flas](https://github.com/matEvangelista/biblia-api-flask)
com requisições no formato `https://biblia-api-flask.onrender.com/sigla_livro/cap/ver1_ver2` ou
`https://biblia-api-flask.onrender.com/sigla_livro/cap/ver1_ver2`

## Próximos Passos
1. Retornar parágrafos do catecismo como se faz com versículos da bíblia
2. Lembrete para dias de guarda