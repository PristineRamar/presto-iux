"""
API Description

ApiId	Name	Description	Arguments	Usage	Returns
"""
import pandas as pd

pd.options.mode.chained_assignment = None


def _reduce(df):
    api_desc = pd.DataFrame()
    for api_id in df.ApiId.unique():
        api_items = df[df.ApiId == api_id]
        usage = api_items.Usage.tolist()
        first_row = api_items.head(1)
        first_row.loc[:, "Usage"] = "\n".join(usage)
        api_desc = pd.concat([api_desc, first_row])

    api_desc = api_desc.reset_index(drop=True)
    return api_desc


def resolve_optional_args(args):
    text = []
    for iarg in [a.strip() for a in args.split(",") if a.strip()]:
        wo_opt = iarg.replace("[optional]", "").strip()
        if "[optional]" in iarg:
            text.append(f"{wo_opt} are optional arguments")
        else:
            text.append(wo_opt)
        if "/" in wo_opt:
            alt_args = ", ".join(wo_opt.split("/"))
            text.append(f"{alt_args} are different representations of the same entity")

    return text


def resolve_choices(args):
    for i, a in enumerate(args):
        if "product_level" in a and "/" in a:
            args.insert(i + 1, "product_level belongs to the range [1, 8]")
        if "location_level" in a and "/" in a:
            args.insert(
                i + 1, "location_level is represented by an integer in [1, 5, 6]"
            )

    return args


def _flatten(api_row):
    fargs = api_row["Arguments"]
    # _args = "\n".join([a.strip() for a in _args.split(",")])
    fargs = resolve_optional_args(fargs)
    fargs = resolve_choices(fargs)
    return f"""
{api_row["Name"]}
============
{api_row["Description"]}

Arguments:
{fargs}

Returns:
{api_row["Returns"]}

Usage:
{api_row["Usage"]}
"""


def prepare_context(rows):
    df = pd.DataFrame(rows[1:], columns=rows[0])
    df = _reduce(df)
    contexts = []
    for api_id in df.ApiId.unique():
        row = df[df.ApiId == api_id].to_dict("records")[0]
        api_desc = _flatten(row)
        contexts.append(api_desc)

    return contexts
