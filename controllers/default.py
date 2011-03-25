# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index():
    if session.auth:
        if auth.has_membership('Tecnico'):
            pass
        if auth.has_membership('Administrador'):
            pass
        if auth.has_membership('Escola'):
            redirect(URL('escola', 'index'))

    else:
        redirect(URL('default', 'user', args=['login']))


    return dict()

def sobre():
    response.view = 'default/index.html'
    return dict()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
  
    if request.args(0) == 'register':

        # Permitindo o registro de novos usuários apenas pelo Administrador
        if auth.has_membership('Administrador'):
            form = SQLFORM(db.usuarios, submit_button=T('register'))

            # Se o cadastro foi efetuado com sucesso
            # Vincule ao grupo selecionado
            if form.accepts(request.vars, session):
                # Consulta o usuario registrado a partir do username
                user = db(db.usuarios.username == request.vars.username).select().first()
                id_group = request.vars.grupo

                auth.add_membership(id_group, user.id)

                # Exibe mensagem de sucesso
                response.flash = T('sucesso_login')

                # Redireciona para o login
                redirect(URL('admin','usuarios', args=['lista']))
        else:
            redirect(URL('user', args=['login']))

    elif request.args(0) == 'profile':      # Se esta no perfil do usuario, captura os seus dados para editar caso for necessário.
        # Ocultando os campos ID, PERFIL e SENHA
        db.usuarios.id.readable = False
        db.usuarios.grupo.readable = \
        db.usuarios.grupo.writable = False
        db.usuarios.password.readable = \
        db.usuarios.password.writable = False

        # Capturando os dados do usuario logado
        id_user = session.auth.user.id
        form = SQLFORM(db.usuarios, id_user, submit_button=T('Save'))

        if form.accepts(request.vars, session):
            response.flash = 'Perfil atualizado com sucesso.'

    else:       # Caso nao entrar nos casos acima passa o metodo padrao auth()
        form = auth()

    return dict(form=form)


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()


