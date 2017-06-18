from typing import Dict, Any as TAny

from traitlets import Integer, HasTraits, observe
from traitlets import Any

from jinja2 import Template

from yuuno import Yuuno
from yuuno.utils import get_data_file


class Jinja2Mixin:
    """
    Mixin for Jinja2 template based widgets.
    """

    def render(self, name: str, context: Dict[str, TAny]) -> str:
        """
        Renders a jinja2 template

        :param name:         The name of the template
        :param environment:  The environment
        :return: The rendered template
        """
        path = get_data_file("html") / name
        with open(path, "r") as f:
            data = f.read()

        return Template(data).render(**context)


class InitialFrameMixin(HasTraits):

    frame_number: int = Integer(default_value=0)


class ClipWrapperMixin(HasTraits):

    clip: object = Any()
    _clip: object = Any()

    @observe("clip")
    def _wrap_clip(self, proposal):
        self._clip = Yuuno.instance().registry.wrap(proposal.new)
