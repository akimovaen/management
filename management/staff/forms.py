from django.forms import ModelChoiceField, ModelForm

from .models import TimeSheet, Salary

class TimesheetForm(ModelForm):
    name = ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].queryset = Salary.objects.filter(fire_date=None)
    
    class Meta:
        model = TimeSheet
        fields = ['name', 'hours', 'shop', 'date']


