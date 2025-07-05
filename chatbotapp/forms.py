from django import forms
from chatbotapp.forms import ChatForm


class ChatForm(forms.Form):
    message = forms.CharField(
        max_length=500,
        label="Your Message",
        widget=forms.TextInput(attrs={
            'placeholder': 'Type your message...',
            'class': 'form-control'
        })
    )