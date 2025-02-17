import re, copy, time
from math import trunc
'''Modificar apenas aqui'''
#global variables
_cursos = ['BACHARELADO EM ENGENHARIA DE INFORMAÇÃO', 'BACHARELADO EM ENGENHARIA DE INSTRUMENTAÇÃO, AUTOMAÇÃO E ROBÓTICA','BACHARELADO EM ENGENHARIA AEROESPACIAL']
_turno = 'Noturno' #Matutino/Noturno/Ambos
_campus = 'SA' #SA/SB/Ambos
_excluirDiaSemana = ['sábado','domingo'] #'segunda','terça','quarta','quinta','sexta','sábado','domingo'
_creditos = 21 #'Max'

'''PROGRAMA - NÃO MUDAR'''
#Fix credits
if _creditos == 'Max':
    _creditos = 99

#Read text
with open('./planilha.txt','r',encoding='utf-8') as arquivo:
    texto = arquivo.read()

#Find page pattern and split
pttrn = re.compile(r'\d{1,3} / \d{1,3}')
pages = re.split(pttrn,texto)

#Remove header
pttrn = re.compile(r'PRÁTICA 2\n')
pgBody = []
for page in pages:
    if len(re.findall(pttrn,page)) >0:
        pgBody.append(re.split(pttrn,page)[1]) 

#Form full class string
#Save class info
classes = []
#Tipos de classes
#BACHARELADO|ENGENHARIAS|LICENCIATURA
pttrn = re.compile(r'( BACHARELADO| ENGENHARIAS| LICENCIATURA)')
for cls in pgBody:
    
    #Split new line char
    #Find pattern in string
    # if found -> Start a new string
    # else -> concat strings
    literalText = cls.split('\n')
    concat = ''
    
    for text in literalText:
        if len(re.findall(pttrn,text)):
            if concat != '':
                classes.append(concat)
                concat = text
            else:
                concat = text
        else:
            concat += text

#Split classes info
#Patterns to find
TPIPttrn = re.compile(r'\d{1,2}-\d{1,2}-\d{1,2}')
campusPttrn = re.compile(r'\((SA|SB)\)')
codDiscPttrn = re.compile(r'[A-Z0-9]+-\d{2}[A-Z]{2}')
horarioPttrn = re.compile(r'(segunda|terça|quarta|quinta|sexta|sábado|domingo)\sdas\s([0-9]+)[0-9:]+ às ([0-9]+)[0-9:]+, (semanal|quinzenal I| quinzenal II)')#,\s(semanal|quinzenal I| quinzenal II)
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
    parse = txt.split(f'({campus})')[1].split(campus)[0]
    
    for horario in re.findall(horarioPttrn,parse):
        dia,inicio,fim,semana = horario
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
            print(f'\r{len(gradesFinal)} grades encontradas! -> '+'Testando classes... '+f'(delta: {trunc(time.time()-delta)}s)',end='')
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
pass
print('Filtrando grades iguais...')
#Encontrar grades repetidas:
gradesFilter = []
for i in range(len(gradesFinal)):
    print('\r'+str(i)+'/'+str(len(gradesFinal)),end='')
    isEqual = True
    if i != len(gradesFinal)-1:
        for j in range(1,len(gradesFinal)-i):
            grade1 = gradesFinal[i]
            grade2 = gradesFinal[i+j]
            for s in range(2):
                for dia in grade1[f'semana {s+1}'].keys(): #creditos sempre no fim
                    if isEqual:
                        for horario in grade1[f'semana {s+1}'][dia].keys():
                            try:
                                if grade1[f'semana {s+1}'][dia][horario] != grade2[f'semana {s+1}'][dia][horario]:
                                    isEqual = False
                                    break
                            except Exception:
                                isEqual = False
                                break
    if not isEqual:
        # print('Grade distinta encontrada!')
        gradesFilter.append(grade1)
gradesFinal = gradesFilter
    
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


'''Funcoes Interface'''




'''Interface'''
latch = True
while latch:
    print('0. Sair')
    print('1. Grades alternativas')
    print('2. Consultar cursos inseridos')
    inp = input('O que você deseja fazer? ')
    print(' ')
    match inp:
        case '0':
            latch = False
        case '1':
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
        case '2':
            latch2 = True
            n = 0
            print('Cursos selecionados:')
            for curso in _cursos:
                print(f'{n+1} - {curso}')
                n += 1
            print(' ')
            while latch2:
                print('0. Voltar')
                print('1. Consultar cursos')
                print('2. Adicionar curso')
                print('3. Remover curso')
                print('4 Limpar curso')
                pass

#print(classesJSON.keys())