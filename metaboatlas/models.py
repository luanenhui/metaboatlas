from datetime import datetime
from metaboatlas import db

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    body = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    Struct = db.Column(db.Binary)

class Compound(db.Model):
    __tablename__ = "compound"
    MAID = db.Column(db.Text, primary_key=True)
    NAME = db.Column(db.Text) 
    FORMULA = db.Column(db.Text)
    Ontology = db.Column(db.Text)
    INCHIKEY = db.Column(db.Text)
    SMILES = db.Column(db.Text)
    INSTRUMENTTYPE = db.Column(db.Text)
    ExactMass = db.Column(db.Text)
    PUBCHEM = db.Column(db.Text)
    Num_Spectra = db.Column(db.Text)
    Species = db.Column(db.Text)
    Cas = db.Column(db.Text)
    KEGG = db.Column(db.Text)
    Reaction = db.Column(db.Text)
    Pathway = db.Column(db.Text)
    Biospecimen = db.Column(db.Text)
    Healthcondition = db.Column(db.Text)

# class Spectra(db.Model):
#     __tablename__ = "spectra"
#     SpectraID = db.Column(db.Text, primary_key=True)
#     PrecursorMZ = db.Column(db.Float)
#     PrecursorType = db.Column(db.Text)
#     IonMode = db.Column(db.Text)
#     InstrumentType = db.Column(db.Text)
#     InstrumentType2 = db.Column(db.Text)
#     Level = db.Column(db.Text)
#     CollisionEnergy = db.Column(db.Text)
#     ExactMass = db.Column(db.Float)
#     Resource = db.Column(db.Text)
#     MZ = db.Column(db.Text)
#     Intensity = db.Column(db.Text) 
#     # CompoundID = db.Column(db.Text, db.ForeignKey(Compound.MAID))
#     CompoundID = db.Column(db.Text)

class Spectra(db.Model):
    __tablename__ = "liutaiyi"
    SpectraID = db.Column(db.Text, primary_key=True)
    PrecursorMZ = db.Column(db.Float)
    PrecursorType = db.Column(db.Text)


class Spectra(db.Model):
    __tablename__ = "spectra"
    SpectraID = db.Column(db.Text, primary_key=True)
    Name = db.Column(db.Text)
    PrecursorMZ = db.Column(db.Text)
    PrecursorType = db.Column(db.Text)
    Formula = db.Column(db.Text)
    Class = db.Column(db.Text)
    INCHIKEY = db.Column(db.Text)
    SMILES = db.Column(db.Text)
    IonMode = db.Column(db.Text)
    InstrumentType = db.Column(db.Text)
    InstrumentType2 = db.Column(db.Text)
    Level = db.Column(db.Text)
    CollisionEnergy = db.Column(db.Text)
    ExactMass = db.Column(db.Text)
    Resource = db.Column(db.Text)
    PUBCHEM = db.Column(db.Text)
    Species = db.Column(db.Text)
    Cas = db.Column(db.Text)
    KEGG = db.Column(db.Text)
    Reaction = db.Column(db.Text)
    Pathway = db.Column(db.Text)
    Biospecimen = db.Column(db.Text)
    Healthcondition = db.Column(db.Text)
    HMDB = db.Column(db.Text)
    SuperClass = db.Column(db.Text)
    KNApSAcK = db.Column(db.Text)
    Synonyms = db.Column(db.Text)
    sndGNDV = db.Column(db.Text)
    sndName = db.Column(db.Text)
    MZ = db.Column(db.Text)
    Intensity = db.Column(db.Text)


    

# 登录基于用户，需要定义User类，User类必须实现 is_authenticated, is_active, is_anonymous三个属性和get_id()方法，下例中这些属性和方法继承自UserMixin
# https://www.jianshu.com/p/01384ee741b6
class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    UserName = db.Column(db.String(20))
    PasswordHash = db.Column(db.String(128))
    # Tel = db.Column(db.String(12))
    Email = db.Column(db.String(50))

    def set_password(self, password):
        self.PasswordHash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.PasswordHash, password)

    