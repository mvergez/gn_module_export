# inspiration:
# https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/Views
# sqlalchemy-views

import re
from sqlalchemy.schema import DDLElement
from sqlalchemy.ext.compiler import compiles
from flask import current_app

from geonature.utils.env import DB

logger = current_app.logger


class CreateView(DDLElement):
    def __init__(self, name, selectable):
        self.name = name
        self.selectable = selectable


@compiles(CreateView)
def visit_create_view(element, compiler, **kw):
    schema, schema_dot_view = kw.get('schema', None), None
    if hasattr(element.target, 'schema') and element.target.schema:
        schema = element.target.schema
        schema_dot_view = '.'.join([schema, element.name])
    return 'DROP VIEW IF EXISTS %s; CREATE VIEW %s AS %s' % (
        schema_dot_view if schema else element.name,
        schema_dot_view if schema else element.name,
        compiler.sql_compiler.process(element.selectable))


def View(name, metadata, selectable):
    t = DB.table(name)
    if hasattr(metadata, 'schema') and not t.schema:
        t.schema = metadata.schema  # otherwise the view lands in 'public'.
    for c in selectable.c:
        c._make_proxy(t)

    # TODO: if no pk in selection, make all fields pks
    t.primary_key_constraints = {c for c in t.columns
                                 if isinstance(c, DB.PrimaryKeyConstraint)}
    if len(t.primary_key_constraints) == 0:
        t.primary_key_constraints = {c for c in t.columns}

    t.foreign_key_constraints = {c for c in t.columns
                                 if isinstance(c, DB.ForeignKeyConstraint)}
    t._extra_dependencies = set()
    # TODO: view indexes
    # logger.debug('indexes: %s', {c for c in t.columns
    #                              if isinstance(c, DB.Index)})
    # FIXME: deprecated execute_at -> use DB.event
    # DB.event.listen(metadata, 'after_create',
    CreateView(t.name, selectable).execute_at('after-create', metadata)
    return t


def mkView(name, metadata, selectable, base=DB.Model, *mixins):
    slug_name = slugify(name)
    return type(
        slug_name, (base, *mixins), {
            '__table__': View(slug_name, metadata, selectable),
            '__table_args__': {
                'schema': metadata.schema if hasattr(metadata, 'schema') else "gn_exports",  # noqa: E501
                'extend_existing': True,
                'autoload': True,
                'autoload_with': metadata.bind if hasattr(metadata, 'bind') else DB.engine  # noqa: E501
                }  # noqa: E133
            })


def slugify(s):
    # FIXME: slugify impl
    allowed_chars = r'-a-zA-Z0-9_'
    ansi = re.compile(r'\x1b\[[;\d]*[A-Za-z]')
    invalid_view_name = re.compile(r'[^\s\.-a-zA-Z0-9_]')
    m = re.match(invalid_view_name, s)
    if m:
        raise Exception(
            'InvalidViewName: "{}", allowed chars: "{}"'.format(
                s, allowed_chars))
    else:
        text = ansi.sub('', s)
        text = re.sub(r'([\.\sA-Z])', r'_\1', text)
        text = re.sub(r'[\.\s]+', '', text)
        text = re.sub(r'_{2,}', '_', text)
        text = text.strip('_')
        text = text.lower()
        return text
