import ipywidgets


class Widget(object):

    def get_widget(self):
        return ipywidgets.HBox([])

    def _ipython_display_(self, **kwargs):
        return self.get_widget()._ipython_display_(**kwargs)