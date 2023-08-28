"""
书写针对用户表的form代码
"""
from django import forms
from app01 import models


class MyRegForm(forms.Form):
    username = forms.CharField(label='用户名', min_length=3, max_length=8,
                               error_messages={
                                   'required': '用户名不能为空',
                                   'min_length': '用户名最少3位',
                                   'max_length': '用户名最大8位',
                               },
                               widget=forms.widgets.TextInput(attrs={'class': 'form-control'})
                               )
    password = forms.CharField(label='密码', min_length=6, max_length=12,
                               error_messages={
                                   'required': '密码不能为空',
                                   'min_length': '密码最少6位',
                                   'max_length': '密码最大12位',
                               },
                               widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'})
                               )
    confirm_password = forms.CharField(label='确认密码', min_length=6, max_length=12,
                                       error_messages={
                                           'required': '确认密码不能为空',
                                           'min_length': '确认密码最少6位',
                                           'max_length': '确认密码最大12位',
                                       },
                                       widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'})
                                       )
    email = forms.EmailField(label='邮箱',
                             error_messages={
                                 'required': '邮箱不能为空',
                                 'invalid': '邮箱格式不正确',
                             },
                             widget=forms.widgets.EmailInput(attrs={'class': 'form-control'})
                             )

    def clean_username(self):
        """
        校验用户名是否已经存在
        :return:
        """
        username = self.cleaned_data.get('username')
        is_exist = models.UserInfo.objects.filter(username=username)
        if is_exist:
            self.add_error('username', '用户名已经存在')
        return username

    def clean(self):
        """
        校验两次密码是否一致
        :return:
        """
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if not password == confirm_password:
            self.add_error('confirm_password', '两次密码不一致')
        return self.cleaned_data
