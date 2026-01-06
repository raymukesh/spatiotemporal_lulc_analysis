# -*- coding: utf-8 -*-

def classFactory(iface):
    from .main_plugin import LandChangeAccountingPlugin
    return LandChangeAccountingPlugin(iface)
