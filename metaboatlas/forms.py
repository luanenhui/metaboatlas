#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   forms.py
@Time    :   2020/11/18 16:18:27
@Author  :   Luan Enhui 
@Version :   1.0
@Contact :   luanenhui2009@gmail.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA
@Desc    :   None
'''

# here put the import lib

from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, ValidationError, HiddenField, \
    BooleanField, PasswordField, FileField, MultipleFileField, IntegerField, FloatField
from wtforms.validators import DataRequired, Email, Length, Optional, URL, EqualTo
from wtforms import simple, validators, widgets

class SimilarityForm(FlaskForm):
    mz = FloatField('M/Z', validators=[DataRequired()], render_kw={'class':"form-control"})
    ionMode = SelectField('Ion Mode', choices=[(1,"Positive"),(2,"Negative"),(3,"None")], render_kw={'class':"form-control"})
    cutoff = FloatField('cut off', render_kw={'class':"form-control"})
    tol = IntegerField('tolerance (Da)', render_kw={'class':"form-control"})
    text = TextAreaField('MS/MS Peak List (m/z & Intensity)', render_kw={'class':"form-control",
    'placeholder':"Enter one mass (m/z) and intensity corresponding to one peak per line",
    'rows':12})
    file = FileField("请上传csv文件", render_kw={'class':"form-control-file"})
    submit = SubmitField(render_kw={'class':"btn btn-primary"})

class MgfForm(FlaskForm):
    cutoff = FloatField('cut off', render_kw={'class':"form-control"})
    tol = IntegerField('tolerance (Da)', render_kw={'class':"form-control"})
    file = FileField("请上传mgf文件,只比较前50张谱图", render_kw={'class':"form-control-file"})
    submit = SubmitField(render_kw={'class':"btn btn-primary"})

class LargeMgfForm(FlaskForm):

    ionMode = SelectField('Ion Mode', choices=[(1,"Positive"),(2,"Negative"),(3,"None")], render_kw={'class':"form-control"})
    cutoff = FloatField('similarity cut off', render_kw={'class':"form-control"}, default=0.5)
    pimTol = FloatField('Parent Ion Mass Tolerance: (Da)', render_kw={'class':"form-control"}, default=0.02)
    mzTol = FloatField('Mass/Charge(m/z) Tolerance: (Da)', render_kw={'class':"form-control"}, default=0.02)
    file = FileField("请上传mgf文件", render_kw={'class':"form-control-file"})
    submit = SubmitField(render_kw={'class':"btn btn-primary"})

class MultipleMgfForm(FlaskForm):

    ionMode = SelectField('Ion Mode', choices=[(1,"Positive"),(2,"Negative"),(3,"None")], render_kw={'class':"form-control"})
    cutoff = FloatField('similarity cut off', render_kw={'class':"form-control"}, default=0.5)
    pimTol = FloatField('Parent Ion Mass Tolerance: (Da)', render_kw={'class':"form-control"}, default=0.02)
    mzTol = FloatField('Mass/Charge(m/z) Tolerance: (Da)', render_kw={'class':"form-control"}, default=0.02)
    file = MultipleFileField("请上传mgf文件", render_kw={'class':"form-control-file"})
    submit = SubmitField(render_kw={'class':"btn btn-primary"})