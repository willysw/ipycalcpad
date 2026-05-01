
from typing import Mapping


def name_to_tex(raw_name: str, special_names: Mapping[str, str] = None) -> str:
    """
    Process a raw name by splitting it into parts and formatting it for LaTeX.

    Examples:

    - ``name_to_tex('my_var')`` returns ``'my_{var}'``
    - ``name_to_tex('my_var_foo')`` returns ``'my_{var,foo}'``
    - ``name_to_tex('my_var_foo_bar')`` returns ``'my_{var,foo,bar}'``
    - ``name_to_tex('var',{'var':'MyVar'})`` returns ``'MyVar'``
    - ``name_to_tex('my_var',{'var':'MyVar'})`` returns ``'my_{MyVar}'``
    """
    parts = raw_name.split('_')

    if special_names:
        for i, part_i in enumerate(parts):
            if part_i in special_names:
                parts[i] = special_names[part_i]

    if len(parts) > 1:
        return f'{parts[0]}_{{{','.join(parts[1:])}}}'
    else:
        return parts[0]