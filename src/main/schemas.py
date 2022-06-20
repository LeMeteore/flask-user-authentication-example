from src.main import ma
from src.main import models


class DataSchema(ma.SQLAlchemyAutoSchema):  # type:ignore
    class Meta:
        model = models.Data


data_schema = DataSchema()
datas_schema = DataSchema(many=True)
