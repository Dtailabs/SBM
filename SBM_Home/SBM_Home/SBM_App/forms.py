from django import forms
from posts.models import Users

class NameForm(forms.Form):
   class Meta:
   		model=Users
   		fields="__all__"