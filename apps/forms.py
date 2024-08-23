from django.forms import ModelForm

from apps.models import Order


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = 'full_name', 'phone_number',

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        return re.sub('\D', '', phone_number)  # noqa

