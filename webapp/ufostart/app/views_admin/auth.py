from hnc.forms.formfields import EmailField, REQUIRED, PasswordField, GRID_BS3
from pyramid.security import has_permission
from ufostart.lib.baseviews import BaseForm
from hnc.forms.handlers import FormHandler
from ufostart.models.auth import UserModel


USER_TOKEN = "ADMIN_USER_TOKEN"

def canEdit(self): return has_permission('edit', self, self.request)
def getUser(self):
    return self.request.session.get(USER_TOKEN) or AdminUserModel()
def setUserF(self, user):
    self.request.session[USER_TOKEN] = user
    self.user = user

def isAdminUser(request):
    user = request.session.get(USER_TOKEN)
    return not user.isAnon() if user else False




class AdminUserModel(UserModel):
    UserGroups = ["AdminUser"]

class LoginForm(BaseForm):
    label = "Admin Login"
    id="login"
    grid = GRID_BS3
    fields=[
        EmailField("email", "Email", REQUIRED)
        , PasswordField("pwd", "Password", REQUIRED)
    ]
    @classmethod
    def on_success(cls, request, values):

        if values == request.context.settings.login:
            request.context.setUser(AdminUserModel(token = 'ADMIN', **values))
            return {'success':True, 'redirect': request.rld_url()}

        return {'success':False, "errors":{"email": "Unknown email or password."}}



class AuthenticationHandler(FormHandler):
    form = LoginForm

