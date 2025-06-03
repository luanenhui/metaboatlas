import re
import os
import json
import time
from flask import request, Blueprint, render_template
from werkzeug.utils import secure_filename
from sqlalchemy import and_, or_
from flask_login import login_required
from flask_mail import Message

from metaboatlas import db, celery, mail
from metaboatlas.models import Compound, Spectra, User
from metaboatlas.forms import SimilarityForm, MgfForm, LargeMgfForm, MultipleMgfForm

html_bp = Blueprint('html', __name__)

# 设置上传文件存放目录
UPLOAD_FOLDER = "F:/uploads"

@html_bp.route('/email', methods=['GET'])
def email():
    message = Message(subject='test', recipients=['ehluan@aptbiotech.com'])
    mail.send(message)
    time.sleep(10)
    return "OK"

@html_bp.route('/help', methods=['GET'])
def help():
    return render_template('README.html')

@html_bp.route('/', methods=['GET',"POST"])
def index():

    # 读写图片到数据库
    # with open("F:/metaboAtlasData/struct/4.png", "rb") as f:
    #     img_buffer = f.read()
    # print(img_buffer)
    # message = Message(id=2, Struct=img_buffer)
    # db.session.add(message)
    # db.session.commit()
    # print("success")
    # print(current_user)
    # print(login_user)

    maidNum = Compound.query.with_entities(Compound.MAID).distinct().count()
    spectraNum = Spectra.query.with_entities(Spectra.SpectraID).distinct().count()

    species = Compound.query.with_entities(Compound.Species).distinct().all()
    species = [i[0] for i in species]
    species = "|".join(species).split("|")
    species = list(set(species))
    species.sort()
    speciesNum = len(species)

    stat = {"maidNum":maidNum, "spectraNum":spectraNum, "speciesNum":speciesNum, "species":species}
    # return render_template("chart.html", data={"n1":1,"n2":2,"n3":10,"n4":4,"n5":5})
    return render_template("index.html", form=SimilarityForm(), mgfForm=MgfForm(), largeMgfForm=LargeMgfForm(), multipleMgfForm=MultipleMgfForm(), stat=stat)
 
@html_bp.route('/search/metabolite/detail', methods=['GET'])
def detail():
    # ---- search metabolite ---- #
    name = request.args.get('name')  # MA000002
    print(name)
    # result = Message.query.all()
    result = Compound.query.filter(Compound.MAID.ilike('%s%'.replace("s",name))).all()

    keys = dir(Compound)
    keys = [i for i in keys if not re.match("_",i)]
    keys = [i for i in keys if i not in ["metadata","query","query_class"]]

    resultJson = [{key:i.__dict__[key] for key in keys} for i in result]

    # ---- search spectra ---- # 
    compoundID = name
    # result = Message.query.all()
    result = Spectra.query.filter(Spectra.CompoundID.ilike('%s%'.replace("s",compoundID))).all()

    keys = dir(Spectra)
    keys = [i for i in keys if not re.match("_",i)]
    keys = [i for i in keys if i not in ["metadata","query","query_class"]]

    resultJson2 = [{key:i.__dict__[key] for key in keys} for i in result]

    result={"metabo":resultJson[0], "spectra":resultJson2}
    return render_template('detail.html', result=result)

@html_bp.route('/search/metabolite', methods=['GET', "POST"])
def searchName():
    if request.method == "GET":
        name = request.args.get('name')
    
    if request.method == "POST":
        name = request.form.get("name")

    name = name.replace("%","\%")    # 防止sql注入攻击

    result = Compound.query.filter(or_(
        Compound.MAID.ilike('%s%'.replace("s",name)),
        Compound.NAME.ilike('%s%'.replace("s",name)),
        Compound.INCHIKEY.ilike('%s%'.replace("s",name)),
        Compound.SMILES.ilike('%s%'.replace("s",name)),
        Compound.FORMULA.ilike('%s%'.replace("s",name)),
        Compound.Cas.ilike('%s%'.replace("s",name)),
        Compound.PUBCHEM.ilike('%s%'.replace("s",name))
    )).all()

    keys = dir(Compound)
    keys = [i for i in keys if not re.match("_",i)]
    keys = [i for i in keys if i not in ["metadata","query","query_class"]]

    resultJson = [{key:i.__dict__[key] for key in keys} for i in result]

    # return render_template("table.html", name=name)  # for tableVue.html
    return render_template("table.html", resultJson=resultJson)

@html_bp.route('/search/pathway', methods=['GET', "POST"])
def searchPathway():
    if request.method == "GET":
        name = request.args.get('pathway')
    
    if request.method == "POST":
        name = request.form.get("pathway")
    
    name = name.replace("%","\%")    # 防止sql注入攻击

    # result = Message.query.all()
    result = Compound.query.filter(or_(
        Compound.Pathway.ilike('%s%'.replace("s",name)),
        Compound.KEGG.ilike('%s%'.replace("s",name)),
        Compound.Reaction.ilike('%s%'.replace("s",name))
    )).all()

    keys = dir(Compound)
    keys = [i for i in keys if not re.match("_",i)]
    keys = [i for i in keys if i not in ["metadata","query","query_class"]]

    resultJson = [{key:i.__dict__[key] for key in keys} for i in result]

    # return({"data":resultJson})
    return render_template('table.html', resultJson=resultJson)

@html_bp.route('/search/spectra', methods=['GET'])
def searchSpectra():
    ID = request.args.get('ID', default="%")
    instrument = request.args.get('instrument', default="%")
    ionMode = request.args.get('ionMode', default="%")
    compoundID = request.args.get('compoundID', default="%")
    # result = Message.query.all()
    result = Spectra.query.filter(and_(
        Spectra.SpectraID.like('%s%'.replace("s",ID)),
        Spectra.InstrumentType2.like('%s%'.replace("s",instrument)),
        Spectra.IonMode.like('%s%'.replace("s",ionMode)),
        Spectra.CompoundID.like('%s%'.replace("s",compoundID)),
    )).all()

    keys = dir(Spectra)
    keys = [i for i in keys if not re.match("_",i)]
    keys = [i for i in keys if i not in ["metadata","query","query_class"]]

    resultJson = [{key:i.__dict__[key] for key in keys} for i in result]

    return({"data":resultJson})

@html_bp.route('/similarity', methods=['GET',"POST"])
# @login_required
def similarity():
    if request.method == "GET":
        return render_template('similarity.html', form=SimilarityForm())

    if request.method == "POST":
        mz = request.form.get("mz")
        ionMode = request.form.get("ionMode")
        cutoff = request.form.get("cutoff")
        tol = request.form.get("tol")

        f = request.files['file']
        dest = UPLOAD_FOLDER + "/" + secure_filename(f.filename)
        f.save(dest)

        with open(dest, "r") as f:
            result = f.read()

        result = os.popen("Rscript scripts/score.r -e %s --mz %s --mode %s --cutoff %s --tol %s" %(dest, mz, ionMode, cutoff, tol)).read()
        resultDict = result.split(";")
        resultDict = [i.split("&") for i in resultDict]
        resultDict = [{
            "SpectraID":i[0],
            "score":i[1],
            "precursorMZ":i[2],
            "precursorType":i[3],
            "Instrument": i[4],
            "CE": i[5],
            "CompoundID":i[6],
            "Name": i[7],
            "Formula": i[8],
            "Pubchem": i[9],
            "MZ": i[10],
            "Intensity": i[11]
        } for i in resultDict]

        return render_template("similarityResult.html", resultJson=resultDict)

# mgf文件内的MS2互相比较
@html_bp.route('/mgfsimilarity', methods=['GET',"POST"])
def mgfsimilarity():
    if request.method == "GET":
        return render_template('similarity.html', form=SimilarityForm())

    if request.method == "POST":
        mz = request.form.get("mz")
        ionMode = request.form.get("ionMode")
        cutoff = request.form.get("cutoff")
        tol = request.form.get("tol")

        f = request.files['file']
        dest = UPLOAD_FOLDER + "/" + secure_filename(f.filename)
        f.save(dest)

        with open(dest, "r") as f:
            result = f.read()

        result = os.popen("Rscript scripts/mgfScore.r -f %s --cutoff %s --tol %s" %(dest, cutoff, tol)).read()
        resultDict = result.split(";")
        resultDict = [i.split("&") for i in resultDict]
        resultDict = [{
            "P1":i[0],
            "P2":i[1],
            "Score":i[2],
            "P1_MZ":i[3],
            "P1_RT": i[4],
            "P2_MZ": i[5],
            "P2_RT":i[6],
        } for i in resultDict]

        return render_template("mgfResult.html", resultJson=resultDict)
        # return {"data":resultDict}

# mgf文件与数据库比较
@html_bp.route('/mgfdb', methods=['GET',"POST"])
def mgfdb():
    if request.method == "POST":
        pimTol = request.form.get("pimTol")
        mzTol = request.form.get("mzTol")
        ionMode = request.form.get("ionMode")
        cutoff = request.form.get("cutoff")

        f = request.files['file']
        dest = UPLOAD_FOLDER + "/" + secure_filename(f.filename)
        f.save(dest)

        with open(dest, "r") as f:
            result = f.read()

        result = os.popen("Rscript scripts/mgfDbScore.r -f %s --cutoff %s --pimtol %s --mztol %s --mode %s" %(dest, cutoff, pimTol, mzTol, ionMode)).read()
        resultDict = result.split(";")
        resultDict = [i.split("&") for i in resultDict]
        resultDict = [{
            "Query":i[0],
            "SpectraID":i[1],
            "Similarity":i[2],
            "Query_PreMZ":i[3],
            "Query_RT":i[4],
            "Spectra_PreMZ":i[5],
            "precursorType":i[6],
            "Instrument":i[7],
            "CE":i[8],
            "CompoundID":i[9],
            "Name":i[10],
            "Formula":i[11],
            "Pubchem":i[12],
            "Spectra_MZ":i[13],
            "Spectra_Intensity":i[14]
        } for i in resultDict]
        return render_template("mgfDbResult.html", resultJson=resultDict)
   