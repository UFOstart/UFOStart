import formencode
from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import BaseForm, EmailField, PasswordField, REQUIRED, StringField, HtmlAttrs, CheckboxPostField
from hnc.forms.messages import GenericSuccessMessage
from ufostart.website.apps.models.auth import WebLoginEmailProc, WebSignupEmailProc, ResendRequestProc, PasswordRequestProc, UpdatePasswordProc


class SignupForm(BaseForm):
    id="signup"
    label = "Signup"
    action_label = "Signup"
    fields = [
        StringField("name", "Name", REQUIRED)
        , EmailField("email", "Email", HtmlAttrs(required = True, data_validation_url = '/signup/checkemail'))
        , PasswordField("pwd", "Password", REQUIRED)
        , PasswordField("pwdconfirm", "Confirm password", REQUIRED)
        , CheckboxPostField("agreeTOS", 'I accept the <a class="link" target="_blank" href="/terms">terms of use</a>', REQUIRED)
    ]
    chained_validators = [formencode.validators.FieldsMatch('pwd', 'pwdconfirm')]

    @classmethod
    def on_success(cls, request, values):
        try:
            user = WebSignupEmailProc(request, values)
        except DBNotification, e:
            if e.message == 'EMAIL_TAKEN':
                return {'success':False, 'errors':{'email': "Email already registered!"}}
            else:
                return {'success':False, 'errors':{'email': e.message}}
        return {'success':True, 'redirect':request.fwd_url("website_index")}



class LoginForm(BaseForm):
    id="login"
    label = "Login"
    action_label = "Login"
    fields = [
        EmailField("email", "Email Address", REQUIRED)
        , PasswordField("pwd", "Password", REQUIRED)
    ]

    @classmethod
    def on_success(cls, request, values):
        values['network'] = 'email'
        try:
            user = WebLoginEmailProc(request, values)
        except DBNotification, e:
            return {"success":False, 'errors':{'email':"Unknown email or password"}}
        request.root.setUser(user)
        return {'success':True, 'redirect':request.furl}


class PasswordForgotForm(BaseForm):
    id="password"
    label = "Password forgot"
    fields = [
        EmailField("email", "Email Address", REQUIRED)
    ]

    @classmethod
    def on_success(cls, request, values):
        email = values['email']
        try:
            if values['isResend']:
                ResendRequestProc(request, {'email':email})
            else:
                PasswordRequestProc(request, {'email':email})
        except DBNotification, e:
            if e.message in ['NO_USER', 'NO_USER_WITH_THIS_EMAIL', 'NO_OWNER_WITH_THIS_EMAIL']:
                errors = {"email": "Unknown email address."}
                return {'values' : values, 'errors':errors}
            elif e.message == "TOKEN_SET_IN_LAST_24_HOURS":
                values['isResend'] = True
                return {'values' : values, 'errors':{'email': "Email has been sent in last 24 hours!"}}
            else:
                raise e
        return {"success":True, "message":"An email with your new password has been sent to {email}.".format(email = email)}



class PasswordResetForm(BaseForm):
    id = 'pwdreset'
    fields = [
        PasswordField("pwd", "New Password", REQUIRED)
        , PasswordField("pwdconfirm", "Confirm New Password", REQUIRED)
    ]
    chained_validators = [formencode.validators.FieldsMatch('pwd', 'pwdconfirm')]

    def on_success(self, request, values):
        try:
            UpdatePasswordProc(request, {'token':request._user.token, 'pwd':values['pwd']})
        except DBNotification:
            raise # HORROR HAPPENED
        request.session.flash(GenericSuccessMessage("Your password has been changed. You can now log in using your new password.", "generic_messages"))
        request.fwd("website_index")
        
