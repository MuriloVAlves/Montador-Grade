import re, copy, time
from math import trunc


#global variables
#Ler arquivo config
with open('./bin/config.txt','r',encoding='utf-8') as arquivo:
    texto = arquivo.read()
    arquivo.close()
texto = texto.split('\n')

#recuperar curso
pttrn = re.compile(r"'(.+?)'")
_cursos = re.findall(pttrn,texto[0])

#recuperar turno
pttrn = re.compile(r'_turno: (Matutino|Noturno|Ambos)')
_turno = re.findall(pttrn,texto[1])[0] #Matutino/Noturno/Ambos

#recuperar campus
pttrn = re.compile(r'_campus: (SA|SB|Ambos)')
_campus = re.findall(pttrn,texto[2])[0] #SA/SB/Ambos

#recuperar dias da semana
pttrn = re.compile(r"'(.+?)'")
_excluirDiaSemana = re.findall(pttrn,texto[3]) #'segunda','terça','quarta','quinta','sexta','sábado','domingo'

#recuperar creditos:
pttrn = re.compile(r'_creditos: (\d+)')
_creditos = int(re.findall(pttrn,texto[4])[0]) #Colocar um valor alto para maximizar os creditos

#recuperar endereço planilha
pttrn = re.compile(r"\./([A-Za-z\. 0-9/]+).txt")
_endereco = './'+re.findall(pttrn,texto[5])[0]+'.txt'

#recuperar materias feitas:
pttrn = re.compile(r"'(.+?)'")
_materiasFeitas = re.findall(pttrn,texto[6])



'''PROGRAMA - NÃO MUDAR'''


'''Funcoes Interface Config'''
def save_file():
    #Limpar configuracoes antigas
    open('./bin/config.txt','w').close()
    #Inserir configuracoes novas
    with open('./bin/config.txt','a',encoding='utf-8') as arquivo:
        arquivo.write('_cursos: '+str(_cursos)+'\n')
        arquivo.write('_turno: '+str(_turno)+'\n')
        arquivo.write('_campus: '+str(_campus)+'\n')
        arquivo.write('_excluirDiaSemana: '+str(_excluirDiaSemana)+'\n')
        arquivo.write('_creditos: '+str(_creditos)+'\n')
        arquivo.write('_endereco: '+str(_endereco)+'\n')
        arquivo.write('_materiasFeitas: '+str(_materiasFeitas))

#Read text
with open(_endereco,'r',encoding='utf-8') as arquivo:
    texto = arquivo.read()
    arquivo.close()

#Find page pattern and split
pttrn = re.compile(r'\d{1,3} / \d{1,3}')
pages = re.split(pttrn,texto)

#Remove header
pttrn = re.compile(r'PRÁTICA 3\n')
pgBody = []
for page in pages:
    if len(re.findall(pttrn,page)) >0:
        pgBody.append(re.split(pttrn,page)[1]) 

#Form full class string
#Save class info
classes = []
#Tipos de classes
#BACHARELADO|ENGENHARIAS|LICENCIATURA
pttrn = re.compile(r'(BACHARELADO EM|ENGENHARIAS|LICENCIATURA EM)')
TPIPttrn = re.compile(r'\d{1,2}-\d{1,2}-\d{1,2}')
concat = ''
for cls in pgBody:
    
    #Split new line char
    #Find pattern in string
    # if found -> Start a new string
    # else -> concat strings
    literalText = cls.split('\n')
    
    for text in literalText:
        if len(re.findall(pttrn,text)):
            if concat != '' and len(re.findall(TPIPttrn,concat)):
                classes.append(concat)
                concat = text
            else:
                concat += text
        else:
            concat += ' '+text
#Para a última matéria
if concat != '' and len(re.findall(TPIPttrn,concat)):
    classes.append(concat)
    concat = text
#Split classes info
#Patterns to find
TPIPttrn = re.compile(r'\d{1,2}-\d{1,2}-\d{1,2}')
campusPttrn = re.compile(r'\((SA|SB)\)')
codDiscPttrn = re.compile(r'[A-Z0-9]+-\d{2}[A-Z]{2}')
horarioPttrn = re.compile(r'(segunda|terça|quarta|quinta|sexta|sábado|domingo)\sdas\s([0-9]+)[0-9:]+ às ([0-9]+)[0-9:]+[,;]')#,\s(semanal|quinzenal I| quinzenal II)
semanaPttrn = re.compile(r'(semanal|quinzenal I| quinzenal II)')
profPttrn = re.compile(r'([A-Z]\D+) ')
#Make json class
classesJSON = {}
for txt in classes:
    TPI = re.findall(TPIPttrn,txt)[0]
    credit = int(TPI.split('-')[0])+int(TPI.split('-')[1])
    campus = re.findall(campusPttrn,txt)[0]
    codDisc = re.findall(codDiscPttrn,txt)[0]
    professores = re.findall(profPttrn,txt.split(TPI)[1])
    #Variaveis com split
    curso = txt.split(codDisc)[0].removeprefix(' ').removesuffix(' ')
    materia = txt.split(codDisc)[1].split(f'({campus})')[0]
    semana1 = {}
    semana2 = {}
    parse = txt.split(f'({campus})')[1].split(TPI)[0]
    for horario in range(len(re.findall(horarioPttrn,parse))):
        dia,inicio,fim = re.findall(horarioPttrn,parse)[horario]
        semana = re.findall(semanaPttrn,parse)[horario]
        if 'semanal' in semana:
            semana1[dia] = [float(inicio),float(fim)]
            semana2[dia] = [float(inicio),float(fim)]
        else: #quinzenal
            if semana.count('I') >1:
                semana2[dia] = [float(inicio),float(fim)]
            else:
                semana1[dia] = [float(inicio),float(fim)]
    
    if 'Matutino' in materia: 
        turno = 'Matutino'
    else: 
        turno = 'Noturno'
    #Criar curso JSON
    if curso in classesJSON.keys():
        pass
    else:
        classesJSON[curso] = {}
    
    #Insert class
    classesJSON[curso][materia] = {}
    classesJSON[curso][materia]['nome'] = materia
    classesJSON[curso][materia]['TPI'] = TPI
    classesJSON[curso][materia]['creditos'] = credit
    classesJSON[curso][materia]['campus'] = campus
    classesJSON[curso][materia]['turno'] = turno
    classesJSON[curso][materia]['Cod. Disciplina'] = codDisc
    classesJSON[curso][materia]['professores'] = professores
    classesJSON[curso][materia]['semana 1'] = semana1
    classesJSON[curso][materia]['semana 2'] = semana2

#Cursos de pesquisa
listaAulas = {}
#listar aulas
for curso in _cursos:
    listaAulas.update(classesJSON[curso])
#deletar outro turno
novaLista = listaAulas.copy()
for aula in listaAulas.keys():
    k = ''
    if _turno != 'Ambos':
        if listaAulas[aula]['turno'] != _turno :
            k = novaLista.pop(aula)
    if _campus != 'Ambos':
        if listaAulas[aula]['campus'] != _campus:
            if listaAulas[aula] != k:
                novaLista.pop(aula)
listaAulas = novaLista

#Output
print(f'Encontradas {len(listaAulas.keys())} aulas com os parâmetros inseridos!')

#Criação de filtragem de matérias já feitas
latch = True
while latch:
    inp = input('Deseja filtrar as matérias já cursadas? [Y/n] ')
    if inp == 'n':
        latch = False
    if inp == 'Y':
        #Listar todas as matérias e numerar
        #Separar somente o nome da matéria
        pttrn = re.compile(r'([A-Z][0-9]?-|[A-Z]Noturno)')
        listaCursos = {}
        for aula in listaAulas.keys():
            padr = re.findall(pttrn,str(aula))
            #Populate dict
            listaCursos[aula.split(padr[0])[0]] = 0
        print(' ')
        n = 1
        for aula in listaCursos.keys():
            print(f'{n} - '+str(aula))
            n += 1
        print(' ')
        print('Matérias cursadas (serão removidas da grade final): ',_materiasFeitas)
        latch2 = True
        while latch2:
            inp = int(input('Selecione as matérias já cursadas (0 para sair / -1 para limpar preferências): '))
            print(' ')
            if inp == 0:
                inp = input('Salvar mudanças? [Y/n] ')
                if inp == 'Y':
                    save_file()
                latch2 = False
            elif inp == -1:
                _materiasFeitas = []
                print('As preferências foram apagadas!')
                print('Matérias cursadas: ',_materiasFeitas)

            else:
                if list(listaCursos.keys())[inp-1] not in _materiasFeitas:
                    _materiasFeitas.append(list(listaCursos.keys())[inp-1])
                print('Matérias cursadas: ',_materiasFeitas)

#Limpar matérias já cursadas
novaLista = copy.deepcopy(listaAulas)
for cursada in _materiasFeitas:
    for mat in listaAulas:
        #Caso a matéria já tenha sido cursada:
        if cursada in mat:
            #Pop
            pop = novaLista.pop(mat)
#Retornar a lista para as aulas
listaAulas = novaLista

print(' ')
print(f'Total de {len(listaAulas.keys())} turmas com aulas não cursadas!')
print('Gerando grades...')

#Iniciar a criação da grade
#Funcionalidade recursiva
#Ideias - O dict pode ser passado com a mesma matéria, já que essa não encaixará na grade duas vezes
#Será contabilizada a quantidade de créditos - Não colocar matéria quando o crédito já for maior que o ideal
#Recursividade irá inserir cada vez mais matéria
#Será feita um loop entre todas as matérias para diversificar o início da grade e possibilitar outras montagens
#Cada vez será colocada uma nova grade para nova interação
#Iniciar criando a grade
#Funcao para criar nova grade
def criar_grade():
    grade = {'semana 1':{},'semana 2':{}}
    #Dias da semana
    for dia in ['segunda','terça','quarta','quinta','sexta','sábado','domingo']:
        if dia not in _excluirDiaSemana:
            grade['semana 1'][dia] = {}
            grade['semana 2'][dia] = {}
    grade['creditos'] = 0
    return grade

#A funcao deve inserir a proxima materia da grade e contar os creditos
delta = 0
def montar_grade(_aulas:dict,_grade:dict,nested = 1):
    #Caso os creditos passem do limite
    if _grade['creditos'] > _creditos:
        if not _grade in gradesFinal:
            gradesFinal.append(_grade.copy())
        return
        #return _grade
    #Caso não passe
    #Tentar inserir aula na grade
    # if len(_recoverGrid) < nested:
    #     recoverGrid = _recoverGrid + [_grade.copy()]
    # for rec in _recoverGrid:
    #     print(hex(id(rec)))
    #     print(rec)
    # print(_recoverGrid)
    # grades = []
    hitCount = 0
    delta2 = 0
    for aula in _aulas.keys():
        if time.time()-delta2>0.5:
            print(f'\r{len(gradesFinal)} grades encontradas! -> '+'Testando classes... '+f'(tempo: {trunc(time.time()-delta)}s)'+f' [Nível: {nested}]',end='')
            delta2 = time.time()
        # print('----------')
        # print('nested:',nested)
        # for rec in _recoverGrid:
        #     print(hex(id(rec)))
        #     print(rec)
        # #print(_recoverGrid)
        # print(_grade)
        dias1 = list(_aulas[aula]['semana 1'].keys())
        dias2 = list(_aulas[aula]['semana 2'].keys())
        grade1 = list(_grade['semana 1'].keys())
        grade2 = list(_grade['semana 2'].keys())
        possivel = True
        #Verificar grade
        for i in range(2):
            dia = [dias1,dias2][i]
            grade = [grade1,grade2][i]
            for d in dia:
                if d not in grade:
                    possivel = False
                    break

        if possivel:
            #Checar se é possível inserir a materia
            aplicavel = True
            for s in range(2):
                dias = [dias1,dias2][s]
                for dia in dias:
                    if aplicavel == False:
                        break
                    #Criar horários
                    h = _aulas[aula][f'semana {str(s+1)}'][dia]
                    #Criar horarios disponiveis
                    hora = []
                    for i in range(int(h[0]),int(h[1])):
                        hora.append(str(i))
                    #Verificar o horario do dia está disponível
                    for div in hora:
                        if div in list(_grade[f'semana {str(s+1)}'][dia].keys()):
                            aplicavel = False
                            break
            if aplicavel:
                hitCount += 1
                #Duplicar a grade
                novaGrade = copy.deepcopy(_grade)
                nomeDisc = str(_aulas[aula]['nome'])
                codDisc = '('+str(_aulas[aula]['Cod. Disciplina'])+')'
                #Inserir os horarios na tabela
                for s in range(2):
                    dias = [dias1,dias2][s]
                    for dia in dias:
                        #Criar horários
                        h = _aulas[aula][f'semana {str(s+1)}'][dia]
                        #Inserir os horários na tabela
                        for i in range(int(h[0]),int(h[1])):
                            novaGrade[f'semana {str(s+1)}'][dia][str(i)] = nomeDisc+ codDisc
                novaGrade['creditos'] += _aulas[aula]['creditos']
                #for al in range(len(_aulas.keys())):
                    #print(len(_aulas),_grade['creditos'],_idx)
                _recoverGrid[nested] = copy.deepcopy(novaGrade)
                recover = montar_grade(_aulas,_recoverGrid[nested],nested+1)
                # print('nested:',nested)
                _grade = copy.deepcopy(_recoverGrid[nested-1])
                # print(_grade)
                # if type(novaIterGrade) != list: 
                #     if not novaIterGrade in grades:
                #         grades.append(novaIterGrade)
                # else:
                #     grades += novaIterGrade
    if hitCount == 0:
        #Fim da grade
        #Salvar caso seja uma grade nova
        if not _grade in gradesFinal:
            print('\r                                                                                                                                                                \n')
            print('////////////////////////////////////////////////////')
            dictMaterias = {}
            for semana in _grade.keys():
                if semana != 'creditos':
                    for dia in _grade[semana].keys():
                        for hora in _grade[semana][dia].keys():
                            dictMaterias[_grade[semana][dia][hora]] = 0
            for mat in list(dictMaterias.keys()):
                print(mat)
            print("////////////////////////////////////////////////////")
            print('')
            gradesFinal.append(copy.deepcopy(_grade))
            return _recoverGrid
        else:
            #Retornar grade com creditos para  primeira contagem
            return _recoverGrid
    else:
        return _recoverGrid
                

#Loop para fazer a grade:
gradesFinal = []
# for aula in range(len(listaAulas.keys())):
_recoverGrid = []
for i in range(len(listaAulas)):
    _recoverGrid.append(criar_grade())
delta = time.time()
grade = montar_grade(listaAulas,criar_grade())
    #gradesFinal += grade
    # for grd in grade:
    #     print(f'Grade gerada: '+str(grd['creditos'])+' créditos!')
    # pass
print(' ')
# print('Filtrando grades iguais...')
# #Encontrar grades repetidas:
# gradesFilter = []
# for i in range(len(gradesFinal)):
#     print('\r'+str(i)+'/'+str(len(gradesFinal)),end='')
#     isEqual = True
#     if i != len(gradesFinal)-1:
#         for j in range(1,len(gradesFinal)-i):
#             grade1 = gradesFinal[i]
#             grade2 = gradesFinal[i+j]
#             for s in range(2):
#                 for dia in grade1[f'semana {s+1}'].keys(): #creditos sempre no fim
#                     if isEqual:
#                         for horario in grade1[f'semana {s+1}'][dia].keys():
#                             try:
#                                 if grade1[f'semana {s+1}'][dia][horario] != grade2[f'semana {s+1}'][dia][horario]:
#                                     isEqual = False
#                                     break
#                             except Exception:
#                                 isEqual = False
#                                 break
#     if not isEqual:
#         # print('Grade distinta encontrada!')
#         gradesFilter.append(grade1)
# gradesFinal = gradesFilter
    
#Encontrar quantidade de grades e créditos e listar
contagemCreditosGrade = {}
for grade in gradesFinal:
    if str(grade['creditos']) in list(contagemCreditosGrade.keys()):
        contagemCreditosGrade[str(grade['creditos'])] += 1
    else:
        contagemCreditosGrade[str(grade['creditos'])] = 1

#Output
print(f'Foram criadas {len(gradesFinal)} grades de acordo com as matérias encontradas!')
print('Exibindo resultados...')
print('----------------------------')
#Print de grades e créditos
for cred in contagemCreditosGrade.keys():
    print(f'Encontradas {contagemCreditosGrade[cred]} grade(s) com {cred} créditos...')
print('----------------------------')
print('Procurando grades ideais...')
print('----------------------------')
print(' ')
#Calcular as melhores grades
gradeIdeal = False
gradesIdeais = []
n = 0
while not gradeIdeal:
    gradesAlternativas = []
    for grade in gradesFinal:
        if abs(grade['creditos']-_creditos) == n:
            gradeIdeal = True
            gradesIdeais.append(grade)
        else:
            gradesAlternativas.append(grade)
    n += 1

#Output Grades
print('************** GRADES IDEAIS **************')
#Grades ideais:
if len(gradesIdeais)>4:
    for g in range(5):
        print(f'----------- Grade {g+1} -----------')
        materiasOutput = {}
        for s in range(2):
            grade1 = gradesIdeais[g]
            for dia in grade1[f'semana {s+1}'].keys(): #creditos sempre no fim
                for horario in grade1[f'semana {s+1}'][dia].keys():
                    if str(grade1[f'semana {s+1}'][dia][horario]) in list(materiasOutput.keys()):
                        pass
                        materiasOutput[str(grade1[f'semana {s+1}'][dia][horario])] += 1
                    else:
                        print(grade1[f'semana {s+1}'][dia][horario])
                        materiasOutput[str(grade1[f'semana {s+1}'][dia][horario])] = 1
        print('*Créditos totais: '+str(grade1['creditos']))
        print(' ')
    print('----------------------------')
    print(f'Existem mais {len(gradesIdeais)-5} grades ideias! (insira "1" para saber mais)')
    print('----------------------------')
    print(' ')
else:
    for g in range(len(gradesIdeais)):
        print(f'----------- Grade {g+1} -----------')
        materiasOutput = {}
        for s in range(2):
            grade1 = gradesIdeais[g]
            for dia in grade1[f'semana {s+1}'].keys(): #creditos sempre no fim
                for horario in grade1[f'semana {s+1}'][dia].keys():
                    if str(grade1[f'semana {s+1}'][dia][horario]) in list(materiasOutput.keys()):
                        pass
                        materiasOutput[str(grade1[f'semana {s+1}'][dia][horario])] += 1
                    else:
                        print(grade1[f'semana {s+1}'][dia][horario])
                        materiasOutput[str(grade1[f'semana {s+1}'][dia][horario])] = 1
        print('*Créditos totais: '+str(grade1['creditos']))
        print(' ')
        



'''Interface'''
latch = True
while latch:
    #Interface principal
    print('0. Sair')
    print('1. Selecionar grades por matérias')
    print('2. Grades alternativas')
    print('3. Configurar cursos')
    print('4. Configurar campus')
    print('5. Configurar período')
    print('6. Configurar créditos')
    print('7. Excluir dia da semana da grade')
    inp = input('O que você deseja fazer? ')
    print(' ')
    match inp:
        case '0':
            save_file()
            latch = False
        case '1':
            _preferencias = []
            latch2 = True
            while latch2:
                print(' ')
                n = 1
                for aula in listaAulas.keys():
                    print(f'{n} - '+str(aula))
                    n += 1
                print(' ')
                inp = int(input('Selecione matérias para conter nas grades (0 para voltar / -1 para limpar preferências): '))
                print(' ')
                if inp == 0:
                    latch2 = False
                elif inp == -1:
                    _preferencias = []
                    print('As preferências foram apagadas!')
                else:
                    _preferencias.append(list(listaAulas.keys())[inp-1])
                    print('Preferências: ',_preferencias)
                    for g in range(len(gradesIdeais)):
                        #Separar materias da grade
                        materiasOutput = {}
                        for s in range(2):
                            grade1 = gradesIdeais[g]
                            for dia in grade1[f'semana {s+1}'].keys(): #creditos sempre no fim
                                for horario in grade1[f'semana {s+1}'][dia].keys():
                                    if str(grade1[f'semana {s+1}'][dia][horario]) in list(materiasOutput.keys()):
                                        materiasOutput[str(grade1[f'semana {s+1}'][dia][horario])] += 1
                                    else:
                                        materiasOutput[str(grade1[f'semana {s+1}'][dia][horario])] = 1
                        #Checar se todas as preferencias estão contidas na grade
                        contido = 0
                        for pref in _preferencias:
                            for materia in list(materiasOutput.keys()):
                                if pref in materia:
                                    contido += 1
                                    break
                        #Caso verdadeiro
                        if contido == len(_preferencias):
                            #Print da grade
                            print(f'----------- Grade {g+1} -----------')
                            materiasOutput = {}
                            for s in range(2):
                                grade1 = gradesIdeais[g]
                                for dia in grade1[f'semana {s+1}'].keys(): #creditos sempre no fim
                                    for horario in grade1[f'semana {s+1}'][dia].keys():
                                        if str(grade1[f'semana {s+1}'][dia][horario]) in list(materiasOutput.keys()):
                                            pass
                                            materiasOutput[str(grade1[f'semana {s+1}'][dia][horario])] += 1
                                        else:
                                            print(grade1[f'semana {s+1}'][dia][horario])
                                            materiasOutput[str(grade1[f'semana {s+1}'][dia][horario])] = 1
                            print('*Créditos totais: '+str(grade1['creditos']))
                            print(' ')       
        case '2':
            print('************** GRADES ALTERNATIVAS **************')
            #Grades alternativas
            for g in range(len(gradesAlternativas)):
                print(f'----------- Grade {g+1} -----------')
                materiasOutput = {}
                for s in range(2):
                    grade1 = gradesAlternativas[g]
                    for dia in grade1[f'semana {s+1}'].keys(): #creditos sempre no fim
                        for horario in grade1[f'semana {s+1}'][dia].keys():
                            if str(grade1[f'semana {s+1}'][dia][horario]) in list(materiasOutput.keys()):
                                pass
                                materiasOutput[str(grade1[f'semana {s+1}'][dia][horario])] += 1
                            else:
                                print(grade1[f'semana {s+1}'][dia][horario])
                                materiasOutput[str(grade1[f'semana {s+1}'][dia][horario])] = 1
                print('*Créditos totais: '+str(grade1['creditos']))
                print(' ')
        case '3':
            n = 0
            print('Cursos selecionados:')
            for curso in _cursos:
                print(f'{n+1} - {curso}')
                n += 1
            latch2 = True
            print(' ')
            while latch2:
                print(' ')
                print('0. Voltar')
                print('1. Consultar cursos selecionados')
                print('2. Adicionar curso')
                print('3. Remover curso')
                print('4 Limpar cursos')
                print('5. Salvar mudanças')
                inp = input('O que você deseja fazer? ')
                print(' ')
                match inp:
                    case '0':
                        latch2 = False
                    case '1':
                        n = 0
                        print('Cursos selecionados:')
                        for curso in _cursos:
                            print(f'{n+1} - {curso}')
                            n += 1
                    case '2':
                        latch3 = True
                        while latch3:
                            n=1
                            for curso in classesJSON.keys():
                                print(f'{n} - '+str(curso))
                                n+=1
                            inp = int(input('Selecione os cursos que deseja adicionar (0 para voltar): '))
                            print(' ')
                            if inp == 0:
                                latch3 = False
                            else:
                                if list(classesJSON.keys())[inp-1] not in _cursos:
                                    _cursos.append(list(classesJSON.keys())[inp-1])
                                    print(str(list(classesJSON.keys())[inp-1])+' foi adicionado!')
                                else:
                                    print('O curso já estava selecionado! (sem mudanças)')
                    case '3':
                        latch3 = True
                        while latch3:
                            n = 0
                            print('Cursos selecionados:')
                            for curso in _cursos:
                                print(f'{n+1} - {curso}')
                                n += 1
                            inp = int(input('Selecione os cursos que deseja remover (0 para voltar): '))
                            print(' ')
                            if inp == 0:
                                latch3 = False
                            else:
                                pop = _cursos.pop(inp-1)
                                print(str(pop)+' removido!')
                    case '4':
                        _cursos = []
                    
                    case '5':
                        print('Mudanças salvas!')
                        save_file()
        case '4':
            print('1 - SA')
            print('2 - SB')
            print('3 - Ambos')
            print(f'Atual: {_campus}')
            print(' ')
            inp = input('Selecione o campus: ')
            match inp:
                case '1':
                    _campus = 'SA'
                case '2':
                    _campus = 'SB'
                case '3':
                    _campus = 'Ambos'                   
            print(f'Selecionado: {_campus}')
            save_file()
            print('Retornando ao menu anterior...')
            print(' ')
        case '5':
            print('1 - Matutino')
            print('2 - Noturno')
            print('3 - Ambos')
            print(f'Atual: {_turno}')
            print(' ')
            inp = input('Selecione o período: ')
            match inp:
                case '1':
                    _turno = 'Matutino'
                case '2':
                    _turno = 'Noturno'
                case '3':
                    _turno = 'Ambos'                   
            print(f'Selecionado: {_turno}')
            save_file()
            print('Retornando ao menu anterior...')
            print(' ')
        case '6':
            print(f'Número de créditos atuais: {_creditos}')
            print(' ')
            inp = int(input('Insira o número de créditos alvo (insira número alto para maximizar os créditos): '))
            _creditos = inp
            print(f'Créditos atuais modificados para: {_creditos}')
            save_file()
            print('Retornando ao menu anterior...')
            print(' ')
        case '7':
            latch2 = True
            while latch2:
                print(f'Dias da semana excluídos: {_excluirDiaSemana}')
                diasSemana = ['segunda','terça','quarta','quinta','sexta','sábado','domingo']
                for n in range(len(diasSemana)):
                    print(f'{n+1} - {diasSemana[n]}')
                print(' ')
                inp = int(input('Selecione os dias da semana para excluir da grade (0 para voltar/-1 para limpar a lista):'))
                if inp == 0:
                    save_file()
                    latch2 = False
                    print(' ')
                elif inp == -1:
                    _excluirDiaSemana = []
                elif inp <= len(diasSemana):
                    if diasSemana[inp-1] not in _excluirDiaSemana:
                        _excluirDiaSemana.append(diasSemana[inp-1])
                    
