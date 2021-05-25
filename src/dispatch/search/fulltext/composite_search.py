"""
CompositeSearch provides search across multiple tables
with the connection objects.


Base usage::

    s = CompositeSearch(session, [User, Comment, Blog])
    q = s.build_query('star wars', sort=True).limit(10)
    s.search(query=q)


Adding other objects::

    class RatingSearch(CompositeSearch):

        def extend_search_objects(self, model_class, objects):
            part = Rating.query.filter(
                Rating.author_id == request.user_id,
                Rating.target.is_type(model_class),
                Rating.target_id.in_(objects.keys()))
            part = {x.target_id: x for x in part}
            for k, v in objects.items():
                objects[k] = (v, part.get(k))
            return objects

        def map_result(self, search_row, object):
            content, rating = object
            obj = {'type': search_row.type, 'content': content}
            return {'object': obj, 'rating': rating}

    s = RatingSearch(session, [User, Comment, Blog])
    q = s.build_query('star wars', sort=True).limit(10)
    s.search(query=q)

"""
from collections import defaultdict
from sqlalchemy.sql.expression import literal

from . import inspect_search_vectors, search


class CompositeSearch(object):
    def __init__(self, session, model_classes):
        self.session = session
        self.model_classes = model_classes

    def union_query(self):
        qs = None
        for model_class in self.model_classes:
            search_vectors = inspect_search_vectors(model_class)
            vector = search_vectors[0]
            q = self.session.query(
                model_class.id.label("id"),
                vector.label("vector"),
                literal(model_class.__name__).label("type"),
            )
            if qs is None:
                qs = q
            else:
                qs = qs.union(q)
        return qs

    def build_query(self, search_query, vector=None, regconfig=None, sort=False):
        qs = self.union_query()
        return search(qs, search_query, vector, regconfig, sort)

    def split_filter(self, model_class, obj):
        return obj.type == model_class.__name__

    def split_search_result(self, search_result):
        objects_by_model = {x: [] for x in self.model_classes}
        for x in search_result:
            for model_class in self.model_classes:
                if self.split_filter(model_class, x):
                    objects_by_model[model_class].append(x)
        return objects_by_model

    def extend_search_objects(self, model_class, objects):
        return objects

    def load_search_objects(self, objects_by_model):
        objects_by_type = {x.__name__: [] for x in self.model_classes}
        for model_class, objects in objects_by_model.items():
            if objects:
                objects = {
                    x.id: x
                    for x in self.session.query(model_class).filter(
                        model_class.id.in_([x.id for x in objects])
                    )
                }
                objects = self.extend_search_objects(model_class, objects)
            objects_by_type[model_class.__name__] = objects
        return objects_by_type

    def map_result(self, search_row, object):
        return {"type": search_row.type, "content": object}

    def search(self, query, by_type=True):
        search_result = list(query)
        objects_by_model = self.split_search_result(search_result)
        objects_by_type = self.load_search_objects(objects_by_model)

        # mapping all to search result
        objects = defaultdict(list)
        if by_type:
            for x in search_result:
                if x.type in objects_by_type:
                    objects[x.type].append(objects_by_type[x.type][x.id])
        return objects
