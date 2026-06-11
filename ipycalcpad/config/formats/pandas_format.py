from pandas import DataFrame, Series, Index

from ...utility import name_to_tex
from ..format import Format

from ...config import Configuration
_C = Configuration()


class PDDataFrameFormat(Format):
    types_to_format = (DataFrame,)

    @classmethod
    def format(cls, value: DataFrame, format_spec:str|None=None) -> str:
        formatted_df = cls._format_dataframe(value, format_spec)
        return f'{formatted_df.to_markdown(stralign="right")}'

    @staticmethod
    def _format_dataframe(df: DataFrame, format_spec:str|None=None) -> DataFrame:
        index_out = PDDataFrameFormat._format_index(df, format_spec)
        df_out = DataFrame(index=index_out)

        for col, col_name in ((df[col], col) for col in df.columns):
            formated_col = col.map(lambda x: f'${_C.format_object(x, format_spec)}$')
            formated_col.index = index_out
            formated_col_name = f'${name_to_tex(col_name)}$'
            df_out[formated_col_name] = formated_col

        return df_out

    @staticmethod
    def _format_index(df: DataFrame, format_spec: str|None = None) -> Index:
        out = []
        for i, itype in zip(df.index, (type(j) for j in df.index)):
            if isinstance(itype, str):
                out.append(f'${name_to_tex(i)}$')
            elif isinstance(itype, (int, float)):
                out.append(f'${_C.format_object(i, format_spec)}$')
            else:
                out.append(str(i))
        return Index(out)


class PDSeriesFormat(Format):
    types_to_format = (Series,)

    @classmethod
    def format(cls, value: Series, format_spec: str|None = None) -> str:
        if format_spec is None:
            format_spec = '.3g~L'

        table_str = value.map(lambda x: f'${x:{format_spec}}$').to_markdown()
        return f'{table_str}'


__all__ = ['PDDataFrameFormat', 'PDSeriesFormat']
