from import_export import resources
from userauth.models import Account


class AccountResource(resources.ModelResource):
    class Meta:
        model = Account
        fields = ('lrn', 'fname', 'lname', 'birthday', 'age', 'email')
        import_id_fields = ('lrn',)