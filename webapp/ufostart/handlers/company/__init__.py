from . import product, general, need, setup, funding, invite
from ufostart.handlers.company.__resources__ import TemplatesRootContext, TemplateContext, CompanyContext, RoundContext, ProductContext, FundingContext, NeedContext, ApplicationContext


def includeme(config):
    config.add_view(setup.basics                 , context = TemplatesRootContext                        , renderer = "ufostart:templates/company/templates/list.html")
    config.add_view(setup.details                , context = TemplateContext                             , renderer = "ufostart:templates/company/templates/details.html")


    config.add_view(setup.CreateProjectHandler   , context = TemplateContext   , name = 'startcompany'   , renderer = "ufostart:templates/company/company/create.html", permission = 'create')
    config.add_view(general.CompanyIndexHandler  , context = CompanyContext                              , renderer = "ufostart:templates/company/company/index.html")
    config.add_view(setup.EditProjectHandler     , context = CompanyContext    , name='edit'             , renderer = "ufostart:templates/company/company/edit.html", permission = 'edit')


    config.add_view(general.RoundDashboardHandler, context = RoundContext                               , renderer = "ufostart:templates/company/round.html")
    config.add_view(general.AddMentorHandler     , context = RoundContext      , name='mentor'           , renderer = "ufostart:templates/company/addmentor.html")
    config.add_view(general.add_top_mentor       , context = RoundContext      , name='topmentor'        , permission='edit')
    config.add_view(general.publish_round        , context = RoundContext      , name='approve'          , permission='approve')
    config.add_view(general.reject_round         , context = RoundContext      , name='reject'           , permission='approve')
    config.add_view(general.ask_for_approval     , context = RoundContext      , name='askforapproval'   , permission='edit')


    config.add_view(product.ProductCreateHandler , context = RoundContext      , name='productsetup'     , renderer = "ufostart:templates/company/product/create.html", permission="edit")
    config.add_view(product.ProductOfferHandler  , context = ProductContext                              , renderer = "ufostart:templates/company/product/index.html")
    config.add_view(product.ProductEditHandler   , context = ProductContext    , name='edit'             , renderer = "ufostart:templates/company/product/create.html", permission="edit")
    config.add_view(product.remove_offer         , context = ProductContext    , name='delete'           , renderer = "json", permission="edit")


    config.add_view(funding.FundingCreateHandler , context = RoundContext      , name='fundingsetup'     , renderer = "ufostart:templates/company/funding/create.html", permission="edit")
    config.add_view(funding.InvestmentHandler    , context = FundingContext                              , renderer = "ufostart:templates/company/funding/index.html")
    config.add_view(funding.FundingEditHandler   , context = FundingContext    , name='edit'             , renderer = "ufostart:templates/company/funding/edit.html", permission='edit')


    config.add_view(need.NeedCreateHandler       , context = RoundContext      , name='new'              , renderer = "ufostart:templates/company/need/create.html", permission='edit')
    config.add_view(need.NeedIndexHandler        , context = NeedContext                                 , renderer = "ufostart:templates/company/need/index.html")
    config.add_view(need.ApplicationHandler      , context = NeedContext       , name = 'apply'          , renderer = "ufostart:templates/company/need/apply.html", permission='apply')
    config.add_view(need.accept_application      , context = ApplicationContext, name = 'accept')
    config.add_view(need.NeedEditHandler         , context = NeedContext       , name = 'edit'           , renderer = "ufostart:templates/company/need/edit.html", permission='edit')


    config.add_view(invite.invite_landing        , context = invite.InviteContext                          , renderer = "ufostart:templates/company/invite_confirm.html"     , permission='join')
    config.add_view(invite.confirm               , context = invite.InviteContext, name = 'confirm'        , permission='join')
    config.add_view(invite.reject                , context = invite.InviteContext, name = 'reject'         , permission='join')

    config.add_view(invite.invite_landing        , context = invite.InviteNeedContext                      , renderer = "ufostart:templates/company/invite_need_confirm.html", permission='join')
    config.add_view(invite.confirm               , context = invite.InviteNeedContext, name = 'confirm'    , permission='join')
    config.add_view(invite.reject                , context = invite.InviteNeedContext, name = 'reject'     , permission='join')


