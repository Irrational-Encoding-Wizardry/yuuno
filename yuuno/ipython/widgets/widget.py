import ipywidgets
from jinja2 import Template

from yuuno.util import get_data_file


class Widget(object):

    def get_widget(self):
        return ipywidgets.HBox([])

    def _ipython_display_(self, **kwargs):
        return self.get_widget()._ipython_display_(**kwargs)


class Jinja2Mixin(object):

    @staticmethod
    def get_template_by_name(name):
        with open(get_data_file('widgets/' + name), "r") as f:
            return f.read()

    @staticmethod
    def render(name, context):
        template = Template(Jinja2Mixin.get_template_by_name(name))
        return template.render(**context)        

    def get_html(self, context, name=None):
        if name is None:
            name = self.template_name
        return self.render(name, context)
