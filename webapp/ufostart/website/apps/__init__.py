from operator import methodcaller
from hnc.tools.routing import ClassRoute, FunctionRoute, route_factory, App, JSON_FORM_ATTRS

from . import contexts, index, auth, company, expert
import simplejson
from ufostart.website.apps.social.angellist import AngelListSettings
from ufostart.website.apps.social.facebook import FacebookSettings
from ufostart.website.apps.social.linkedin import LinkedinSettings
from ufostart.website.apps.social.twitter import TwitterSettings
from ufostart.website.apps.social.xing import XingSettings


__author__ = 'Martin'

ROUTE_LIST = [
    FunctionRoute  ("website_index"                        , "/", contexts.WebsiteRootContext                                                , index.index, "index.html")
    , FunctionRoute('website_template_basic'               , '/project/template', contexts.WebsiteRootContext                                , index.template.basics, "template/basic.html")
    , FunctionRoute('website_template_details'             , '/project/:template', contexts.WebsiteRootContext                               , index.template.details, "template/details.html")
    , FunctionRoute('website_template_signup'              , '/project/signup/:network/:action', contexts.WebsiteRootContext                 , index.template.login, "template/signup.html")

    , FunctionRoute('website_social_login'                 , '/social/:network/:action', contexts.WebsiteRootContext                         , auth.social.login, None)

    , ClassRoute   ("website_company_basic"                , "/company/setup", contexts.WebsiteRootContext                                   , company.general.SetupCompanyHandler, "company/setup.html", view_attrs = JSON_FORM_ATTRS)
    , ClassRoute   ("website_company_invite"               , "/c/:slug/invite", contexts.WebsiteCompanyContext                               , company.invite.InviteCompanyHandler, "company/invite.html", view_attrs = JSON_FORM_ATTRS)
    , FunctionRoute('website_company'                      , '/c/:slug', contexts.WebsiteCompanyContext                                      , company.general.index, None)
    , FunctionRoute('website_company_round_create'         , '/c/:slug/create/round', contexts.WebsiteCompanyContext                         , company.general.create_round, None)


    , FunctionRoute("website_company_customers"            , "/c/:slug/customers", contexts.WebsiteCompanyContext                            , company.customers.index, None)
    , FunctionRoute("website_company_import"               , "/company/import/:network", contexts.WebsiteAuthedContext                       , company.customers.company_import, "company/customers/list.html")
    , FunctionRoute("website_company_import_list"          , "/c/:slug/import/:network/:user_id/:token", contexts.WebsiteCompanyContext      , company.customers.company_import_list, "company/customers/list.html")
    , FunctionRoute("website_company_import_confirm"       , "/c/:slug/confirm/:network/:company_id/:token", contexts.WebsiteCompanyContext  , company.customers.company_import_confirm, None)

    , FunctionRoute("website_company_pledge_decide"        , "/c/:slug/pledge", contexts.WebsiteCompanyContext                               , company.customers.pledge_decide, "company/customers/pledge_decide.html")
    , FunctionRoute('website_login_to_pledge'              , '/c/:slug/pledge/:network/:action', contexts.WebsiteCompanyContext              , company.customers.login, None)


    , FunctionRoute('website_company_round_view'           , '/c/:slug/tasks', contexts.WebsiteCompanyContext                                , company.tasks.index, "company/tasks/index.html")


    , FunctionRoute("website_expert_dashboard"             , '/expert/dashboard', contexts.WebsiteAuthedContext                              , expert.index.index, "expert/index.html")
    , ClassRoute   ("website_expert_taskcreate"            , '/task/create', contexts.WebsiteAuthedContext                                   , expert.index.TaskCreateHandler, "expert/task_create.html", view_attrs = JSON_FORM_ATTRS)

    , FunctionRoute('website_logout'                       , '/user/logout', contexts.WebsiteRootContext, index.logout, None)

    , FunctionRoute("website_invite_answer"                , '/invite/:token', contexts.WebsiteRootContext                                   , company.invite.answer, "company/invite_confirm.html")
    , FunctionRoute("website_invite_confirm"               , '/invite/:token/confirm', contexts.WebsiteAuthedContext                         , company.invite.confirm, "company/invite_confirm.html")
    , FunctionRoute('website_invite_login'                 , '/invite/login/:network/:action/:token', contexts.WebsiteRootContext            , company.invite.login, None)

]



SOCIAL_CONNECTORS_MAP = {'angellist': AngelListSettings, 'facebook': FacebookSettings, 'linkedin': LinkedinSettings, 'xing':XingSettings, 'twitter':TwitterSettings}

class WebsiteSettings(object):
    key = "website"
    networks = {}

    def __init__(self, settings):
        self.clientToken = settings['apiToken']
        socials = map(methodcaller("strip"), settings['social_networks'].split(","))
        for network in socials:
            SettingsCls = SOCIAL_CONNECTORS_MAP[network]
            self.networks[network] = SettingsCls(type=network, **settings[network])

    def toPublicJSON(self, stringify = True):
        result = {k:v.toPublicJSON(False) for k,v in self.networks.items()}
        return simplejson.dumps(result) if stringify else result


ROUTE_MAP = {r.name:r for r in ROUTE_LIST}

def includeme(config):
    settings = config.registry.settings
    settings['g'].setSettings(WebsiteSettings, settings)
    route_factory('ufostart', ROUTE_LIST, App("website"), config, template_path_prefix = 'website')

