from sqlalchemy import nulls_last

def sort_and_paginate(page, per_page, sort, sort_fields, query):
    if page < 1:
        raise ValueError("page must be >= 1")

    if per_page < 1:
        raise ValueError("per_page must be >= 1")

    per_page = min(per_page, 100)
    offset = (page - 1) * per_page

    if sort not in sort_fields:
        raise ValueError("invalid sort input")

    column = sort_fields[sort] # it accepts sort because sort_fields is a dict

    if sort == "old":
        query = query.order_by(nulls_last(column.asc()))
    else:
        query = query.order_by(nulls_last(column.desc()))

    query = query.offset(offset).limit(per_page)

    return query