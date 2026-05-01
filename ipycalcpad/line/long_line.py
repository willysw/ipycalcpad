
from ..tree import Assign

from .line import Line


class LongLine(Line):
    def get_markdown(self):
        if self.expressions:
            expr = self.expressions[0]

            if self.comment:
                comment_text = f'{self.comment}\n\n'
            else:
                comment_text = ''

            if isinstance(expr, Assign) and expr.target:
                desc_text = f'${expr.target.get_tex(subs=False)}$\n\n'
            else:
                desc_text = ''

            return ('\n\n' +
                    comment_text +
                    desc_text +
                    expr.get_tex_result() +
                    '\n\n')

        return ""


__all__ = ['LongLine']
