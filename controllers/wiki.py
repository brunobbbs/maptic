#-*- coding: utf-8 -*-

@auth.requires_login()
def index():
    artigos = db().select(db.wiki.ALL, orderby=db.wiki.titulo)
    return dict(artigos=artigos)

@auth.requires_login()
def ver():
    id_artigo = request.args(0) or redirect(URL('wiki', 'index'))
    detalhes = db(db.wiki.id==id_artigo).select()
    return dict(detalhes=detalhes)

@auth.requires_membership('Administrador')
def adicionar():
    form = crud.create(db.wiki, next=URL('index'))
    response.view = 'wiki/artigo.html'
    return dict(form=form)

@auth.requires_membership('Administrador')
def deletar():
    id_artigo = request.args(0) or redirect(URL('wiki', 'index'))
    crud.delete(db.wiki, id_artigo, next=URL('wiki', 'index'))
    return dict()

@auth.requires_membership('Administrador')
def editar():
    id_artigo = request.args(0) or redirect(URL('wiki', 'index'))
    form = crud.update(db.wiki, id_artigo, next=URL('wiki', 'ver', args=[id_artigo]))
    response.view = 'wiki/artigo.html'
    return dict(form=form)

