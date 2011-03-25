#-*- coding: utf-8 -*-

@auth.requires_membership('Administrador')
def index():
    """
    Essa é a página inicial do menu relatórios, Ela faz uma consulta ao banco de escolas cadastradas
    e retorna um dropdown para selecionar a escola que deseja gerar o relatório.
    """
    escola = db(db.escola.id>1).select()
    return dict(escola=escola)

@auth.requires_membership('Administrador')
def escola():
    """
    Essa função lista os relatórios disponíveis de cada escola.
    """
    
    valida = request.vars or redirect(URL('relatorios', 'index'))

    escola = db(db.questionario.escola==request.vars['escola']).select()

    return dict(escola=escola)

@auth.requires_membership('Administrador')
def gerar():
    """
    Função para gerar os relatórios de InfraTI, InfraEscola, OutrasTICS e Geral de cada escola
    Plugin utilizado: Appreport by Lucas D'Avilla
    """

    formulario = request.args(0) or redirect(URL('relatorios', 'index'))

    if formulario == 'infrati':
        e = request.vars['escola']
        e = int(e)
        maptic = db(db.infrati.id_escola==e).select()
        escola = db(db.escola.id==e).select()
        email_escola = db(db.usuarios.first_name==e).select()
        html = response.render('relatorios/infrati.html', dict(maptic = maptic, escola = escola, email_escola = email_escola))
        return plugin_appreport.REPORT(html = html)
        
    elif formulario == 'infraescola':
        e = request.vars['escola']
        e = int(e)
        maptic = db(db.infraescola.id_escola==e).select()
        escola = db(db.escola.id==e).select()
        email_escola = db(db.usuarios.first_name==e).select()
        html = response.render('relatorios/infraescola.html', dict(maptic = maptic, escola = escola, email_escola = email_escola))
        return plugin_appreport.REPORT(html = html)

    elif formulario == 'outrastics':
        e = request.vars['escola']
        e = int(e)
        maptic = db(db.outrastics.id_escola==e).select()
        escola = db(db.escola.id==e).select()
        email_escola = db(db.usuarios.first_name==e).select()
        html = response.render('relatorios/outrastics.html', dict(maptic = maptic, escola = escola, email_escola = email_escola))
        return plugin_appreport.REPORT(html = html)

    elif formulario == 'geral':
        e = request.vars['escola']
        e = int(e)
        infrati = db(db.infrati.id_escola==e).select()
        infraescola = db(db.infraescola.id_escola==e).select()
        outrastics = db(db.outrastics.id_escola==e).select()
        escola = db(db.escola.id==e).select()
        email_escola = db(db.usuarios.first_name==e).select()
        html = response.render('relatorios/geral.html', dict(infrati = infrati,
                                                                infraescola = infraescola, outrastics = outrastics,
                                                                escola = escola, email_escola = email_escola))
        return plugin_appreport.REPORT(html = html)
    
    else:
        redirect(URL('relatorios', 'index'))