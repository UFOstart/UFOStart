from hnc.forms.formfields import BaseForm


class RoundSetupForm(BaseForm):
    fields = []

    @classmethod
    def on_success(cls, request, values):
        return {'success': True}