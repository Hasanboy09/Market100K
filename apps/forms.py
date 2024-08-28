import re

from django.forms import ModelForm

from apps.models import Order, User, Stream


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = 'full_name', 'phone_number', 'product', 'region'

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        return re.sub('\D', '', phone_number)  # noqa


class ProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'email')


class StreamForm(ModelForm):
    class Meta:
        model = Stream
        fields = 'product', 'name', 'discount', 'owner'



