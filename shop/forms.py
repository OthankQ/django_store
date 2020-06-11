from django import forms


class UploadImageForm(forms.Form):
    item_id = forms.CharField(max_length=50)
    image = forms.ImageField()
