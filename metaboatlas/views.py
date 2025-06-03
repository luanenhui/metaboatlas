# from metaboatlas import app,db
# from metaboatlas.models import Compound, Spectra
# from flask import request
# import re
# from sqlalchemy import and_, or_

# @app.route('/', methods=['GET'])
# def index():
#     return '<h1>success.</h1>'

# @app.route('/search/metabolite', methods=['GET'])
# def searchName():
#     name = request.args.get('name')
#     print(name)
#     # result = Message.query.all()
#     result = Compound.query.filter(or_(
#         Compound.MAID.like('%s%'.replace("s",name)),
#         Compound.NAME.like('%s%'.replace("s",name)),
#         Compound.INCHIKEY.like('%s%'.replace("s",name)),
#         Compound.SMILES.like('%s%'.replace("s",name)),
#         Compound.FORMULA.like('%s%'.replace("s",name)),
#         Compound.Cas.like('%s%'.replace("s",name)),
#         Compound.PUBCHEM.like('%s%'.replace("s",name))
#     )).all()

#     keys = dir(Compound)
#     keys = [i for i in keys if not re.match("_",i)]
#     keys = [i for i in keys if i not in ["metadata","query","query_class"]]

#     resultJson = [{key:i.__dict__[key] for key in keys} for i in result]

#     return({"data":resultJson})

# @app.route('/search/pathway', methods=['GET'])
# def searchPathway():
#     name = request.args.get('pathway')
#     print(name)
#     # result = Message.query.all()
#     result = Compound.query.filter(or_(
#         Compound.Pathway.like('%s%'.replace("s",name)),
#         Compound.KEGG.like('%s%'.replace("s",name)),
#         Compound.Reaction.like('%s%'.replace("s",name))
#     )).all()

#     keys = dir(Compound)
#     keys = [i for i in keys if not re.match("_",i)]
#     keys = [i for i in keys if i not in ["metadata","query","query_class"]]

#     resultJson = [{key:i.__dict__[key] for key in keys} for i in result]

#     return({"data":resultJson})

# @app.route('/search/spectra', methods=['GET'])
# def searchSpectra():
#     ID = request.args.get('ID', default="%")
#     instrument = request.args.get('instrument', default="%")
#     ionMode = request.args.get('ionMode', default="%")
#     compoundID = request.args.get('compoundID', default="%")
#     # result = Message.query.all()
#     result = Spectra.query.filter(and_(
#         Spectra.SpectraID.like('%s%'.replace("s",ID)),
#         Spectra.InstrumentType2.like('%s%'.replace("s",instrument)),
#         Spectra.IonMode.like('%s%'.replace("s",ionMode)),
#         Spectra.CompoundID.like('%s%'.replace("s",compoundID)),
#     )).all()

#     keys = dir(Spectra)
#     keys = [i for i in keys if not re.match("_",i)]
#     keys = [i for i in keys if i not in ["metadata","query","query_class"]]

#     resultJson = [{key:i.__dict__[key] for key in keys} for i in result]

#     return({"data":resultJson})