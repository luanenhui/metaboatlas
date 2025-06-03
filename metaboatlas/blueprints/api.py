from metaboatlas import db
from metaboatlas.models import Compound, Spectra
from flask import request, Blueprint, jsonify
import re
from sqlalchemy import and_, or_

api_bp = Blueprint('api', __name__)

@api_bp.route('/', methods=['GET'])
def index():
    return '<h1>success.</h1>'

@api_bp.route('/search/metabolite', methods=['GET', "POST"])
def searchName():
    if request.method == "GET":
        name = request.args.get('name')
    
    if request.method == "POST":
        name = request.form.get("name")

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
    return jsonify(resultJson)

@api_bp.route('/search/pathway', methods=['GET'])
def searchPathway():
    name = request.args.get('pathway')
    print(name)
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

    return({"data":resultJson})

@api_bp.route('/search/spectra', methods=['GET'])
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

@api_bp.route('/similarity', methods=['GET',"POST"])
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

        # return render_template("similarityResult.html", resultJson=resultDict)
        return {"data": resultDict}

@api_bp.route('/mgfsimilarity', methods=['GET',"POST"])
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

        # return render_template("mgfResult.html", resultJson=resultDict)
        return {"data":resultDict}

# @api_bp.route('/getSpectra', methods=['GET','POST'])
# def getSpectra():
#     if request.method == "GET":
#         instrument = request.args.get("instrument")
#         ionMode = request.args.get("ionMode")
#         species = request.args.get("species")

#     if request.method == "POST":
#         instrument = request.form.get("instrument")
#         ionMode = request.form.get("ionMode")
#         species = request.form.get("species")
    
#     compoundID = Compound.query.filter(Compound.Species.ilike('%s%'.replace("s",species))).with_entities(Compound.MAID).all()
#     compoundID = [i[0] for i in compoundID]

#     result = Spectra.query.filter(and_(
#         Spectra.InstrumentType2.like('%s%'.replace("s",instrument)),
#         Spectra.IonMode.like('%s%'.replace("s",ionMode)),
#         Spectra.CompoundID.in_(compoundID)
#     )).all()

#     keys = dir(Spectra)
#     keys = [i for i in keys if not re.match("_",i)]
#     keys = [i for i in keys if i not in ["metadata","query","query_class"]]

#     resultJson = [{key:i.__dict__[key] for key in keys} for i in result]

#     return({"data":resultJson})

@api_bp.route('/getSpectra', methods=['GET','POST'])
def getSpectra():
    if request.method == "GET":
        instrument = request.args.get("instrument")
        ionMode = request.args.get("ionMode")
    
    if request.method == "POST":
        instrument = request.form.get("instrument")
        ionMode = request.form.get("ionMode")
    
    result = Spectra.query.filter(and_(
        # Spectra.InstrumentType2.like('%s%'.replace("s",instrument)),
        Spectra.IonMode.like('%s%'.replace("s",ionMode))
    )).with_entities(Spectra.SpectraID, Spectra.Name, Spectra.PrecursorMZ, Spectra.PrecursorType,Spectra.MZ, Spectra.Intensity, Spectra.HMDB, Spectra.KEGG, Spectra.Species, Spectra.Cas, Spectra.PUBCHEM, Spectra.Class, Spectra.Biospecimen).all()

    resultJson = [{
        "SpectraID":i[0],
        "Name":i[1],
        "PrecursorMZ":i[2],
        "Precursor_Type":i[3],
        "MZ":i[4],
        "Intensity":i[5],
        "HMDB":i[6],
        "KEGG":i[7],
        "Species":i[8],
        "Cas":i[9],
        "Pubchem":i[10],
        "Class":i[11],
        "Biospecimen":i[12]
    } for i in result]

    return({"data":resultJson})