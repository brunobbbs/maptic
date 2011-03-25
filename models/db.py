# -*- coding: utf-8 -*-

from gluon.utils import hash

#########################################################################
## Preparando o ambiente para GAE ou não
#########################################################################

if request.env.web2py_runtime_gae:            # Caso estiver executando o ambiente GAE
    db = DAL('gae://mynamespace')             # conecta ao Google BigTable
    session.connect(request, response, db = db) # e armazene sessões e tickets aqui

    ### ou use as seguintes linhas para armazenar sessoes no Memcache
    from gluon.contrib.memdb import MEMDB
    from google.appengine.api.memcache import Client
    session.connect(request, response, db = MEMDB(Client()))
else:                                         # senao, use um banco de dados relacional
    db = DAL('sqlite://mapeiatic.sqlite')
    #db = DAL('mysql://dresam:ntesam@mysql.dresam.com.br')

## Caso não precisar mais da sessão
# session.forget()

## Importando as ferramentas adicionais
from gluon.tools import *
mail = Mail()                                  # E-mail
auth = Auth(globals(),db)                      # Autenticacao/Autorizacao
crud = Crud(globals(),db)                      # para helpers CRUD usando Auth
service = Service(globals())                   # para renderizacao json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()                      # Gerencia todos os plugins instalados no sistema

# Dados para envio de emails
mail.settings.server = 'logging' or 'smtp.gmail.com:587'  # seu servidor SMTP
mail.settings.sender = 'ntesamambaia@gmail.com'         # seu email
mail.settings.login = 'ntesamambaia:@ntesam414@'      # suas credenciais ou vazio (caso nao precise de autenticacao)
mail.settings.tls = True


# Antes de mais nada, temos que renomear as tabelas do modulo de autenticacao e controle de acesso
auth.settings.table_user_name = 'usuarios'
auth.settings.table_group_name = 'grupos'
auth.settings.table_membership_name = 'relacionamento'
auth.settings.table_permission_name = 'autorizacao'
auth.settings.table_event_name = 'eventos'

### Personalizando as mensagens do CRUD

crud.messages.delete_label = 'Selecione para deletar'
crud.messages.record_created = 'Registro criado'
crud.messages.record_updated = 'Registro atualizado'
crud.messages.record_deleted = 'Registro deletado'

### Tabela grupos (customizado)
grupos = db.define_table(
    auth.settings.table_group_name,
    Field('role',length=128,default=''),
    Field('description',length=128,default=''))

custom_group_table = grupos
custom_group_table.role.requires = IS_NOT_EMPTY(error_message = T('is_empty'))
custom_group_table.description.requires = IS_NOT_EMPTY(error_message = T('is_empty'))

### Desabilitando a criacao automatica de grupos
auth.settings.create_user_groups = False

### Carga inicial de grupos
### Caso os grupos nao foram cadastrados, sao inseridos automaticamente
papeis = ('Administrador','Escola','Tecnico')

for papel in papeis:
    grupo = db(db.grupos.role == papel).select().first()
    if not grupo:
        db.grupos.insert(role=papel,description='Grupo tipo %s'%papel)


############## Tabela de cadastro das escolas ##############
db.define_table('escola',
                Field('nome'),
                Field('endereco'),
                Field('telefone', 'integer', comment='Digite apenas números, sem o DDD'),
                Field('cod_inep', label='Código INEP'),
                Field('dre', label='DRE'),
                Field('nte', label='NTE'),
                Field('turno', 'list:string', label='Turnos de funcionamento da escola', comment='Segure CTRL para selecionar mais de uma opção'),
                format='%(nome)s')

### Validadores da tabela escola

db.escola.nome.requires=[
                           IS_NOT_EMPTY(error_message=T('is_empty')),
                           IS_NOT_IN_DB(db, 'escola.nome'),
                           IS_UPPER()
                           ]
db.escola.endereco.requires= [
                            IS_NOT_EMPTY(error_message=T('is_empty')),
                            IS_UPPER()
                            ]
db.escola.telefone.requires=[
                             IS_NOT_EMPTY(error_message=T('is_empty')),
                             IS_MATCH('^\d{8}$', error_message=T('formato'))
                             ]
db.escola.cod_inep.requires=IS_NOT_EMPTY(error_message=T('is_empty'))
db.escola.dre.requires=[
                        IS_NOT_EMPTY(error_message=T('is_empty')),
                        IS_UPPER()
                        ]
db.escola.nte.requires=[
                        IS_NOT_EMPTY(error_message=T('is_empty')),
                        IS_UPPER()
                        ]
db.escola.turno.requires=IS_IN_SET(('Matutino', 'Vespertino', 'Noturno'), multiple=True)

### Carga inicial da escola genérica (para uso do administrador)

school  = {
    'name':'Administrador',
    'endereco':'n/a',
    'inep':'n/a',
    'dre':'n/a',
    'nte':'n/a',
    'turno':'n/a'
}

# Caso nao existir
school_admin = db(db.escola.nome == school['name']).select().first()
if not school_admin:
    id_user = db.escola.insert(
        nome = school['name'],
        endereco = school['endereco'],
        cod_inep = school['inep'],
        dre = school['dre'],
        nte = school['nte'],
        turno = school['turno']
    )
    db.commit()

### Tabela usuarios (customizado)

usuarios = db.define_table(
    auth.settings.table_user_name,
    Field('first_name', db.escola),
    Field('username', length = 128, default = '', unique = True),
    Field('email', length=128, default=''),
    Field('password', 'password', length=512,
          readable=False, label='Password'),
    Field('grupo', db.grupos, notnull = True),
    Field('registration_key', length=512,
          writable=False, readable=False, default=''),
    Field('reset_password_key', length=512,
          writable=False, readable=False, default=''),
    Field('registration_id', length=512,
          writable=False, readable=False, default=''),
    format=lambda n: n.first_name.nome)

# Validacao dos campos
custom_auth_table = usuarios
#custom_auth_table.first_name.requires = IS_IN_DB(db(db.escola.id != 1), 'escola.id', zero = '-- Selecione --',
                                           # error_message='Esta escola não está cadastrada')
                                            
#custom_auth_table.first_name.widget = SQLFORM.widgets.autocomplete(request, db.escola.nome, limitby=(0,10), min_length=2)
custom_auth_table.username.requires = [
            IS_NOT_EMPTY(error_message = T('is_empty')),
            IS_NOT_IN_DB(db, custom_auth_table.username, T('login_already'))]
"""
custom_auth_table.password.requires = [
            # Especifica a complexidade da senha
            # minimo = 6
            # caracteres especiais = 0 (nenhum)
            # caracteres em maiusculo = 0 (nenhum)
            IS_STRONG(min = 6, special = 0, upper = 0, invalid=' "', error_message = 'Senha inválida'),CRYPT()]
"""
custom_auth_table.password.requires = CRYPT()
custom_auth_table.email.requires = [IS_EMAIL(error_message=auth.messages.invalid_email)]

# Rotulo dos campos
custom_auth_table.first_name.label = 'Escola'
custom_auth_table.username.label = 'Login'
custom_auth_table.email.label = 'Email'
custom_auth_table.password.label = T('Password')
custom_auth_table.grupo.label = T('Perfil')

auth.define_tables()                           # cria todas as tabelas necessarias para o modulo Auth
auth.settings.hmac_key = 'sha512:1d718a94-81cf-4274-8ac1-42207b203246'   # antes de define_tables()
auth.settings.mailer = mail                    # para verificação de email

# Habilitando verificacao de senha e desabilitando aprovacao de cadastro
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False

# Traduzindo o rotulo do campo Submit
auth.messages.submit_button = T('Submit')

### Carga inicial para criacao do Administrador
admin  = {
    'username':'admin',
    'password':'admin123',
    'email':'admin@mail.com',
    'grupo':'1',    # ID do grupo Administrador (caso for outro, altere)
}

# Caso nao existir
user_admin = db(db.usuarios.username == admin['username']).select().first()
user_school = db(db.escola.nome == 'Administrador').select().first()
if not user_admin:
    id_user = db.usuarios.insert(
        first_name = user_school,
        username = admin['username'],
        email = admin['email'],
        password = hash(admin['password'], 'md5'), # Convertendo a senha no formado MD5
        grupo = admin['grupo']
    )
    db.commit()
    db.relacionamento.insert(user_id = id_user,group_id = 1)
    db.commit()


### Se o usuario for Administrador, ele pode querer adicionar outro Administrador.
### Com isso tem que verificar se o usuario logado tem permissoes para isso, ou seja
### participa do grupo Administrador
if 'auth' in globals():
    if session.auth:
        if auth.has_membership('Administrador'):
            custom_auth_table.grupo.requires = IS_IN_DB(db,'grupos.id', 'grupos.role',
                zero=T('escolha_grupo'), error_message=T('is_choose'))
    else:
        query = db.grupos.role != 'Administrador'
        # query = (db.grupos.role != 'Administrador') & (db.grupos.role != 'Participante')
        custom_auth_table.grupo.requires = IS_IN_DB(db(query),
            'grupos.id', 'grupos.role', zero=T('escolha_grupo'), error_message=T('is_choose'))

### Desativando o registro pela página principal
auth.settings.actions_disabled.append('register')


"""
############################################
##
##           Tabelas do Sistema
##
############################################
"""

############## Tabela da Infra Estrutura de TI ##############
infrati = db.define_table('infrati',
                Field('id_escola', 'integer'),
                Field('labinfo', label='Possui laboratório de informática?', widget=SQLFORM.widgets.radio.widget),
                Field('e_novo', label='Recebeu equipamentos novos em 2009/2010?', widget=SQLFORM.widgets.radio.widget),
                Field('num_comp', 'integer', label='Quantidade de computadores no(s) laboratório(s) de informática'),
                Field('origem', label='Origem dos equipamentos do laboratório de informática'),
                Field('ano_imp', 'integer', label='Ano de implementação do laboratório de informática'),
                Field('qtd_func', 'integer', label='Quantidade de computadores funcionando'),
                Field('so', 'list:string', label='Sistema Operacional', widget=SQLFORM.widgets.checkboxes.widget),
                Field('config', 'text', label='Configuração predominante nos computadores', 
                      comment='Informe as configurações gerais da maioria dos computadores, como: Processador, memória, placa de vídeo...'),
                Field('qtd_pc_professor', 'integer', label='Quantidade de computadores na sala dos professores'),
                Field('qtd_pc_secretaria', 'integer', label='Quantidade de computadores na secretaria'),
                Field('rede_logica_lab', label='Rede lógica no laboratório', widget=SQLFORM.widgets.radio.widget),
                Field('ponto_rede_lab', 'integer', label='Nº de Pontos'),
                Field('rede_logica_prof', label='Rede lógica na sala dos professores', widget=SQLFORM.widgets.radio.widget),
                Field('ponto_rede_prof', 'integer', label='Nº de Pontos'),
                Field('rede_logica_sec', label='Rede lógica na secretaria', widget=SQLFORM.widgets.radio.widget),
                Field('ponto_rede_sec', 'integer', label='Nº de Pontos'),
                Field('internet', widget=SQLFORM.widgets.radio.widget),
                Field('internet_outro', label='Outro serviço'),
                Field('local_internet', 'text', label='Em quais locais da escola há acesso à internet?'),
                Field('wifi', label='Possui rede wireless?', widget=SQLFORM.widgets.radio.widget),
                Field('condicao_lab', label='Condição de funcionamento do laboratório', widget=SQLFORM.widgets.radio.widget),
                Field('tel_lab', label='Possui linha telefônica para o laboratório?', widget=SQLFORM.widgets.radio.widget))



# Validadores da tabela formulario

db.infrati.id_escola.requires=[IS_IN_DB(db, 'escola.id', zero='-- Selecione --', error_message=T('is_empty'))]
db.infrati.labinfo.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.infrati.e_novo.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.infrati.num_comp.requires=IS_INT_IN_RANGE(0,101, error_message=T('out_lab'))
db.infrati.origem.requires=IS_NOT_EMPTY(error_message=T('is_empty'))
db.infrati.ano_imp.requires=IS_IN_SET([x for x in range(2011,1980,-1)], error_message='Informe um ano válido no formato AAAA. ex: 2008, 2010...',
                                         zero='-- Selecione --')
db.infrati.qtd_func.requires=IS_INT_IN_RANGE(0,101, error_message=T('out_lab'))
db.infrati.so.requires=IS_IN_SET(['Windows', 'Linux'], multiple=True, error_message=T('is_empty'))
db.infrati.qtd_pc_professor.requires=IS_IN_SET([x for x in range(0,11)], multiple=False, error_message='Informe um valor válido', zero='-- Selecione --')
db.infrati.qtd_pc_secretaria.requires=IS_IN_SET([x for x in range(0,20)], multiple=False, error_message='Informe um valor válido', zero='-- Selecione --')
db.infrati.rede_logica_lab.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.infrati.ponto_rede_lab.requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0,500, error_message=T('out_range')))
db.infrati.rede_logica_prof.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.infrati.ponto_rede_prof.requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0,500, error_message=T('out_range')))
db.infrati.rede_logica_sec.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.infrati.ponto_rede_sec.requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0,500, error_message=T('out_range')))
db.infrati.internet.requires=IS_IN_SET(['BLE/MEC', 'ADSL', 'Antena GESAC', 'Conexão Discada', 'Não possui'],
                                          multiple=False, error_message=T('is_empty'))
db.infrati.wifi.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.infrati.condicao_lab.requires=IS_IN_SET(['Ótima', 'Boa', 'Regular', 'Ruim', 'Em montagem'], multiple=False, error_message=T('is_empty'))
db.infrati.tel_lab.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))

db.infrati.id_escola.writable = \
    db.infrati.id_escola.readable = False

############## Tabela Infra Estrutura Escola ##############

infraescola = db.define_table('infraescola',
                Field('id_escola', 'integer'),
                Field('sala_montagem', label='Possui sala para montagem do laboratório?', widget=SQLFORM.widgets.radio.widget),
                Field('rede_eletrica', label='Rede elétrica', widget=SQLFORM.widgets.radio.widget),
                Field('para_raio', label='Pára-raios', widget=SQLFORM.widgets.radio.widget),
                Field('aterramento', widget=SQLFORM.widgets.radio.widget),
                Field('tomada_tripolar', label='Tomadas tripolares no laboratório de informática', widget=SQLFORM.widgets.radio.widget),
                Field('fiacao', label='Fiação no laboratório de informática', widget=SQLFORM.widgets.radio.widget),
                Field('grades', label='Grades de proteção do laboratório', widget=SQLFORM.widgets.radio.widget),
                Field('ar_cond', label='Ar condicionado nos laboratórios', widget=SQLFORM.widgets.radio.widget),
                Field('disjuntor_ar', label='Disjuntor para o Ar condicionado nos laboratórios', widget=SQLFORM.widgets.radio.widget),
                Field('quadro_branco', label='Quadro Branco no laboratório de informática', widget=SQLFORM.widgets.radio.widget),
                Field('armario', widget=SQLFORM.widgets.radio.widget),
                Field('mesa_cadeira', label='Mesa/Cadeira adaptada para o laboratório de infomrática', widget=SQLFORM.widgets.radio.widget),
                Field('bancada', widget=SQLFORM.widgets.radio.widget),
                Field('cadeira', widget=SQLFORM.widgets.radio.widget),
                Field('qtd_cadeira', 'integer', label='Quantidade')) 


# Validadores da tabela Infra Estrutura Escola

db.infraescola.sala_montagem.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.infraescola.rede_eletrica.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.infraescola.para_raio.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.infraescola.aterramento.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.infraescola.tomada_tripolar.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.infraescola.fiacao.requires=IS_IN_SET(['Embutida', 'Externa (em canaletas)'], multiple=False, error_message=T('is_empty'))
db.infraescola.grades.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.infraescola.ar_cond.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.infraescola.disjuntor_ar.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.infraescola.quadro_branco.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.infraescola.armario.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.infraescola.mesa_cadeira.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.infraescola.bancada.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.infraescola.cadeira.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))

db.infraescola.id_escola.requires=[IS_IN_DB(db, 'escola.id', zero='-- Selecione --', error_message=T('is_empty'))]
db.infraescola.id_escola.writable = \
    db.infraescola.id_escola.readable = False

############## Tabela Outras TICs ##############

outrastics = db.define_table('outrastics',
                Field('id_escola', 'integer'),
                Field('parabolica', label='Antena parabólica ou digital', widget=SQLFORM.widgets.radio.widget),
                Field('qtd_parabolica', 'integer', label='Quantidade'),
                Field('dvd', label='Aparelho DVD', widget=SQLFORM.widgets.radio.widget),
                Field('qtd_dvd', 'integer', label='Quantidade'),
                Field('dvdescola1', label='Caixa 1 do DVD escola (50 mídias)', widget=SQLFORM.widgets.radio.widget),
                Field('dvdescola2', label='Caixa 2 do DVD escola (50 mídias)', widget=SQLFORM.widgets.radio.widget),
                Field('dvdescola3', label='Caixa 3 do DVD escola (60 mídias)', widget=SQLFORM.widgets.radio.widget),
                Field('filmadora', label='Câmera filmadora digital', widget=SQLFORM.widgets.radio.widget),
                Field('qtd_filmadora', 'integer', label='Quantidade'),
                Field('fotografica', label='Máquina fotográfica digital', widget=SQLFORM.widgets.radio.widget),
                Field('qtd_fotografica', 'integer', label='Quantidade'),
                Field('lousa', label='Lousa digital', widget=SQLFORM.widgets.radio.widget),
                Field('qtd_lousa', 'integer', label='Quantidade'),
                Field('projetor', label='Projetor multimídia', widget=SQLFORM.widgets.radio.widget),
                Field('qtd_projetor', 'integer', label='Quantidade'),
                Field('som', label='Aparelho de som', widget=SQLFORM.widgets.radio.widget),
                Field('qtd_som', 'integer', label='Quantidade'),
                Field('tv', label='Aparelho de TV', widget=SQLFORM.widgets.radio.widget),
                Field('qtd_tv', 'integer', label='Quantidade'),
                Field('radio_r', label='Equipamento de rádio (recepção)', widget=SQLFORM.widgets.radio.widget),
                Field('radio_t', label='Equipamento de rádio (transmissão)', widget=SQLFORM.widgets.radio.widget),
                Field('observacoes', 'text'))

# Validadores da tabela Outras TICs

db.outrastics.parabolica.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.outrastics.dvd.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.outrastics.dvdescola1.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.outrastics.dvdescola2.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.outrastics.dvdescola3.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.outrastics.filmadora.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.outrastics.fotografica.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.outrastics.lousa.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.outrastics.projetor.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.outrastics.som.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.outrastics.tv.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.outrastics.radio_r.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))
db.outrastics.radio_t.requires=IS_IN_SET(['Sim', 'Não'], multiple=False, error_message=T('is_empty'))

db.outrastics.id_escola.requires=[IS_IN_DB(db, 'escola.id', zero='-- Selecione --', error_message=T('is_empty'))]
db.outrastics.id_escola.writable = \
    db.outrastics.id_escola.readable = False

############## Tabela de Status do Questionário por escola ##############

db.define_table('questionario',
                Field('escola', db.escola),
                Field('infrati', 'boolean', default=False),
                Field('infraescola', 'boolean', default=False),
                Field('outrastics', 'boolean', default=False))

db.questionario.escola.requires = IS_IN_DB(db, db.escola.id, '%(nome)s')

db.questionario.escola.writable = \
    db.questionario.escola.readable = False


############## Tabela para Wiki ##############

db.define_table('wiki',
            Field('titulo'),
            Field('conteudo', 'text'),
            format='%(titulo)s')

db.wiki.titulo.requires = IS_NOT_IN_DB(db, 'wiki.titulo', error_message='Título em branco ou já cadastrado')
db.wiki.conteudo.requires = IS_NOT_EMPTY(error_message='Esse campo não pode ser vazio')




crud.settings.auth = None                      # força autorizacao no CRUD