# -*- coding: utf-8 -*-

@auth.requires_membership('Escola')
def index():
    """
    Essa é a página inicial dos usuários com perfil: Escola
        Aqui é possível preencher/atualizar os formulários para mapear as TICs nas escolas.
    """

    # Consultando o status do formulário para escola (preenchido ou à preencher)
    status = db(db.questionario.escola==session.auth.user.first_name).select()

    # Se a escola não estiver na tabela questionario, insere ela lá.
    if not status:
        db.questionario.insert(
                            escola=session.auth.user.first_name,
                            infrati=False,
                            infraescola=False,
                            outrastics=False)
        db.commit()

    return dict(status=status)

@auth.requires_membership('Escola')
def ajuda():
    return dict()

@auth.requires_membership('Escola')
def formulario():
    """
    Essa função contém os formulários de mapeamento das TICs para inserir/atualizar

    Ex. URL:
        /formulario/infrati -> inserir
        /formulario/infrati/atualizar -> atualizar
    """
    # Verificando se foram passados os argumentos corretos
    formulario = request.args(0) or redirect(URL('escola', 'index'))

    # Verifica qual ação está sendo realizada
    acao = request.args(1) or None
    idescola = session.auth.user.first_name

    # Formulário Infraestrutura de Tecnologia
    if formulario == 'infrati':

        # Verifica se a chamada é para atualizar o formulário
        if acao == 'atualizar':
            # Consulta o ID do formulário infrati para o caso de atualização
            consulta = db(db.infrati.id_escola==idescola).select()

            # Ocultando o campo ID
            db.infrati.writable = \
                db.infrati.readable = False

            # Formulário infrati para atualização
            form = SQLFORM(db.infrati, consulta[0].id, formstyle='table2cols')

            # Pre-populando o campo id_escola com o id da escola que está atualizando o formulário.
            form.vars.id_escola = idescola

        # Se variável acao for vazia, retorna o formulário para ser preenchido
        if acao == None:
            form = SQLFORM(db.infrati, formstyle='table2cols')
            form.vars.id_escola = idescola

        # Valida os campos do formulário e atualiza a tabela questionario, informando que este formulário foi preenchido
        if form.accepts(request.vars, session):
            db(db.questionario.escola==idescola).update(infrati=True)
            db.commit()
            session.flash = 'Questionário de Infraestrutura de Tecnologia atualizado com sucesso'
            redirect(URL('escola', 'index'))

    if formulario == 'infraescola':

        # Verifica se a chamada é para atualizar o formulário
        if acao == 'atualizar':
            # Consulta o ID do formulário infraescola para o caso de atualização
            consulta = db(db.infraescola.id_escola==idescola).select()

            # Ocultando o campo ID
            db.infraescola.writable = \
                db.infraescola.readable = False

            # Formulário infraescola para atualização
            form = SQLFORM(db.infraescola, consulta[0].id, formstyle='table2cols')

            # Pre-populando o campo id_escola com o id da escola que está atualizando o formulário.
            form.vars.id_escola = idescola

        # Se variável acao for vazia, retorna o formulário para ser preenchido
        if acao == None:
            form = SQLFORM(db.infraescola, formstyle='table2cols')
            form.vars.id_escola = idescola

        # Valida os campos do formulário e atualiza a tabela questionario, informando que este formulário foi preenchido
        if form.accepts(request.vars, session):
            db(db.questionario.escola==idescola).update(infraescola=True)
            db.commit()
            session.flash = 'Questionário da Infraestrutura da Escola atualizado com sucesso'
            redirect(URL('escola', 'index'))

    if formulario == 'outrastics':

        # Verifica se a chamada é para atualizar o formulário
        if acao == 'atualizar':
            # Consulta o ID do formulário outrastics para o caso de atualização
            consulta = db(db.outrastics.id_escola==idescola).select()

            # Ocultando o campo ID
            db.outrastics.writable = \
                db.outrastics.readable = False

            # Formulário infraescola para atualização
            form = SQLFORM(db.outrastics, consulta[0].id, formstyle='table2cols')

            # Pre-populando o campo id_escola com o id da escola que está atualizando o formulário.
            form.vars.id_escola = idescola

        # Se variável acao for vazia, retorna o formulário para ser preenchido
        if acao == None:
            form = SQLFORM(db.outrastics, formstyle='table2cols')
            form.vars.id_escola = idescola

        # Valida os campos do formulário e atualiza a tabela questionario, informando que este formulário foi preenchido
        if form.accepts(request.vars, session):
            db(db.questionario.escola==idescola).update(outrastics=True)
            db.commit()
            session.flash = 'Questionário de TICs atualizado com sucesso'
            redirect(URL('escola', 'index'))

    return dict(form=form)