# -*- coding: utf-8 -*-

@auth.requires_membership('Administrador')
def escolas():
    if not request.args(0):
        redirect(URL('admin', 'escolas', args=['lista']))

    if request.args(0) == 'nova':
        nova_escola = SQLFORM(db.escola, submit_button='Salvar')

        editar_escola = \
            escolas = None

        if nova_escola.accepts(request.vars, session):
            session.flash = 'Escola cadastrada com sucesso'
            redirect(URL('admin', 'escolas', args=['lista']))

        return dict(nova_escola=nova_escola, escolas=escolas, editar_escola=editar_escola)

    if request.args(0) == 'lista':
        escolas = db(db.escola.id>1).select()
        editar_escola = \
        nova_escola = None
        return dict(escolas=escolas, editar_escola=editar_escola, nova_escola=nova_escola)

    if request.args(0) == 'editar':
        escola_id = request.args(1) or redirect(URL('escolas', args=['lista']))

        escolas = \
        nova_escola = None

        db.escola.id.readable = \
            db.escola.id.writable = False

        editar_escola = SQLFORM(db.escola, escola_id, deletable=True, submit_button='Salvar')

        if editar_escola.accepts(request.vars, session):
            session.flash = 'Escola editada com sucesso!'
            redirect(URL('admin', 'escolas', args=['lista']))

        return dict(editar_escola=editar_escola, escolas=escolas, nova_escola=nova_escola)

@auth.requires_membership('Administrador')
def usuarios():
    pagina = request.args(0) or redirect(URL('usuarios', args=['lista']))
    
    if pagina == 'lista':
        todos = db(db.usuarios.id>1).select()
        usuario = None
        return dict(todos = todos, usuario = usuario)

    if pagina == 'editar':
        # Captura o argumento passado com o id do usuário a ser editado.
        user_id = request.args(1) or redirect(URL('usuarios', args=['lista']))

        # Oculta o campo ID da edição
        db.usuarios.id.readable = \
            db.usuarios.id.writable = False

        # Cria o formulário de edição de usuários
        usuario = SQLFORM(db.usuarios, user_id, deletable=True, submit_button='Salvar')

        # Retorna vazio a variável todos para evitar conflitos com a página lista
        todos = None

        if usuario.accepts(request.vars, session):
            session.flash = 'Usuário editado com sucesso!'
            redirect(URL('usuarios', args=['lista']))

        return dict(usuario=usuario, todos = todos)