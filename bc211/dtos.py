from bc211 import validate

class Organization:
    def __init__(self, **kwargs):
        self.id = validate.required_string('id', kwargs)
        self.name = validate.required_string('name', kwargs)
        self.description = validate.optional_string('description', kwargs)
        self.website = validate.optional_string('website', kwargs)
        self.email = validate.optional_string('email', kwargs)
        self.locations = kwargs['locations']


class Location:
    def __init__(self, **kwargs):
        self.id = validate.required_string('id', kwargs)
        self.name = validate.required_string('name', kwargs)
        self.organization_id = validate.required_string('organization_id', kwargs)
        self.description = validate.optional_string('description', kwargs)
        self.spatial_location = validate.optional_object(SpatialLocation, 'spatial_location', kwargs)
        self.services = kwargs['services']

class SpatialLocation:
    def __init__(self, **kwargs):
        self.latitude = validate.required_float('latitude', kwargs)
        self.longitude = validate.required_float('longitude', kwargs)

class Service:
    def __init__(self, **kwargs):
        self.id = validate.required_string('id', kwargs)
        self.name = validate.required_string('name', kwargs)
        self.site_id = validate.required_string('site_id', kwargs)
        self.taxonomy_terms = kwargs['taxonomy_terms']

class TaxonomyTerm:
    def __init__(self, **kwargs):
        self.vocabulary = validate.required_slug('vocabulary', kwargs)
        self.name = validate.required_slug('name', kwargs)
