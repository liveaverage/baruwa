from django import forms
from django.template.defaultfilters import force_escape
try:
    from django.forms.fields import email_re
except ImportError:
    from django.core.validators import email_re


SALEARN_OPTIONS = (
  ('1', 'Spam'),
  ('2', 'Ham'),
  ('3', 'Forget'),
)

EMPTY_VALUES = (None, '')

class QuarantineProcessForm(forms.Form):
    """
    Generates a quarantine process form,
    it can be used to release, sa learn or
    delete a quarantined message
    """
    salearn = forms.BooleanField(required=False)
    salearn_as = forms.ChoiceField(choices=SALEARN_OPTIONS)
    release = forms.BooleanField(required=False)
    todelete = forms.BooleanField(required=False)
    use_alt = forms.BooleanField(required=False)
    altrecipients = forms.CharField(required=False)
    message_id = forms.CharField(widget=forms.HiddenInput)

    def clean(self):
        """
        Validates the quarantine form
        """
        cleaned_data = self.cleaned_data
        use_alt = cleaned_data.get("use_alt")
        altrecipients = cleaned_data.get("altrecipients")
        salearn = cleaned_data.get("salearn")
        release = cleaned_data.get("release")
        todelete = cleaned_data.get("todelete")
        message_id = cleaned_data.get("message_id")

        if not salearn and not release and not todelete:
            raise forms.ValidationError("Select atleast one action to perform")
        else:
            if altrecipients in EMPTY_VALUES and use_alt and release:
                raise forms.ValidationError("Provide atleast one alternative recipient")
            else:
                if use_alt and release:
                    emails = altrecipients.split(',')
                    for email in emails:
                        if not email_re.match(email.strip()):
                            raise forms.ValidationError('%s is not a valid e-mail address.' % force_escape(email))
        return cleaned_data
