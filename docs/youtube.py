from docutils import nodes
from docutils.parsers.rst import Directive, directives

YOUTUBE_TEMPLATE = """
<div style="position: relative; padding-bottom: {aspect}%; height: 0; overflow: hidden; max-width: 100%; height: auto;">
  <iframe src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen
    style="position: absolute; top: 0; left: 0; width: {width}; height: {height};"></iframe>
</div>
"""

class Youtube(Directive):
    required_arguments = 1  # The YouTube video ID
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'width': directives.unchanged,
        'height': directives.unchanged,
        'caption': directives.unchanged,
    }

    def run(self):
        video_id = self.arguments[0]
        width = self.options.get('width', '100%')
        height = self.options.get('height', '100%')
        caption = self.options.get('caption', None)
        # Calculate aspect ratio for responsive embed (default 56.25% for 16:9)
        aspect = 56.25
        if width.endswith('%') and height.endswith('%'):
            aspect = 56.25  # default 16:9
        elif width.isdigit() and height.isdigit():
            aspect = 100 * int(height) / int(width)
        html = YOUTUBE_TEMPLATE.format(
            video_id=video_id,
            width=width,
            height=height,
            aspect=aspect
        )
        raw_node = nodes.raw('', html, format='html')
        if caption:
            fig = nodes.figure()
            fig += raw_node
            fig += nodes.caption(text=caption)
            return [fig]
        else:
            return [raw_node]

def setup(app):
    app.add_directive("youtube", Youtube)
