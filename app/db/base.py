from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from app.models import user
from app.models import cv
from app.models import recommendation
from app.models import feedback
