# -*- coding: utf-8 -*-

"""
Author: David Wong <davidwong.xc@gmail.com>
License: 3 clause BSD license

This module contains form classes that are used in view functions, to render forms in html.

"""

from django import forms

class MessageForm(forms.Form):
    #Used as a Contact form on the Contact page
    name = forms.CharField(max_length=100, required=False, label="Your Name")
    sender_email = forms.EmailField(label="Your E-mail Address")
    message = forms.CharField(label="Your Message", widget=forms.Textarea)
    