from pandas import DataFrame, Series, Index

from ...utility import name_to_tex
from ..format import Format

from ...config import Configuration
_C = Configuration()


class PDDataFrameFormat(Format):
    types_to_format = (DataFrame,)

    @classmethod
    def format(cls, value: DataFrame, format_spec:str=None) -> str:
        formatted_df = cls._format_dataframe(value, format_spec)
        return f'{formatted_df.to_markdown(stralign="right")}'

    @staticmethod
    def _format_dataframe(df: DataFrame, format_spec:str=None) -> DataFrame:
        index_out = Index([f'${name_to_tex(i)}$' for i in df.index])
        df_out = DataFrame(index=index_out)

        for col, col_name in ((df[col], col) for col in df.columns):
            formated_col = col.map(lambda x: f'${_C.format_object(x, format_spec)}$')
            formated_col.index = index_out
            formated_col_name = f'${name_to_tex(col_name)}$'
            df_out[formated_col_name] = formated_col

        return df_out


class PDSeriesFormat(Format):
    types_to_format = (Series,)

    @classmethod
    def format(cls, value: Series, format_spec:str=None) -> str:
        if format_spec is None:
            format_spec = '.3g~L'

        table_str = value.map(lambda x: f'${x:{format_spec}}$').to_markdown()
        return f'{table_str}'


__all__ = ['PDDataFrameFormat', 'PDSeriesFormat']
