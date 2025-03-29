Para a utilização do programa 
1 - Copiar a grade contendo as matérias da UFABC (Programa feito com base no sistema de cópia do Chrome Versão 133.0.6943.98 (Versão oficial) 64 bits)
2 - Rodar o programa pela primeira vez - Ignorar a primeira filtragem de matérias feitas (inserir "n")
3 - Configurar curso, campus, período e número de créditos utilizando a interface
4 - Reiniciar o programa
5 - Selecionar (e salvar) matérias já cursadas

Obs.:
- O programa pode demorar para rodar porque ele possui uma função recursiva montada para garantir que sejam criadas todas as grades possíveis
- É recomendado inserir algumas matérias como feitas para reduzir o tempo de processamento do algoritmo
- Caso não seja salva a modificação na variável de matérias cursadas, as modificações serão aplicadas somente à instância do programa - Isso pode ser útil para filtrar matérias que não serão cursadas no momento
- Caso um número muito alto seja inserido como número de créditos (recomendado: 99), o programa irá procurar as grades com maior quantidade de créditos 
- Todas as funções possuem uma interface pelo terminal, não é recomendado alterar o documento config.txt manualmente
- A informação [Nível: <n>] se refere à quantidade de instâncias de recursividade que estão sendo calculadas
- Apesar do aplicativo ser criado para calcualar a grade inteira, os filtros permitem limitar a pesquisa a até um dia

Melhorias futuras:
Criar formas de distinguir as exceções de dia por semana 1 ou 2
Criar a possibilidade de excluir horários especificos, e não dias inteiros
Melhorar as filtragens atualmente implementadas
