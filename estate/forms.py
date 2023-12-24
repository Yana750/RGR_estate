from django import forms

from .models import Rent


class RentCreateForm(forms.ModelForm):
    """
    Форма добавления объявлений на сайте
    """
    class Meta:
        model = Rent
        fields = ('thumbnail', 'title', 'slug', 'category', 'city', 'location', 'floor', 'room', 'area', 'price', 'full_description', 'status')

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы под Bootstrap
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

class RentUpdateForm(RentCreateForm):
    """
    Форма обновления объявлений на сайте
    """
    class Meta:
        model = Rent
        fields = RentCreateForm.Meta.fields + ('updater', 'fixed')

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы под Bootstrap
        """
        super().__init__(*args, **kwargs)

        self.fields['fixed'].widget.attrs.update({
                'class': 'form-check-input'
        })