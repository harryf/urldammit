# -*- coding: utf-8 -*-
import web
import config

render = web.template.render('templates/', cache=config.cache_templates)

def tools(**k):
    return render.tools()

def addurl(**k):
    return render.addurl()

def checkurl(**k):
    return render.checkurl()

def badrequest(**k):
    return render.badrequest(**k)

web.template.Template.globals.update(dict(
  datestr = web.datestr,
  render = render
))
