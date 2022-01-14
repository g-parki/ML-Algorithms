from bokeh.plotting import figure, ColumnDataSource
from bokeh.embed import components, file_html
from bokeh.resources import CDN
from bokeh.models import Slider, LabelSet
from bokeh.models.callbacks import CustomJS
from bokeh.layouts import column
from bokeh.transform import jitter
from bokeh.io import show
import json
import pandas as pd

with open('simple_linear_regressions.json') as f:
    model = json.load(f)

slope = model['coefficients'][0]
intercept = model['intercept']
score = round(model['score'], 2)
corresponding_y = lambda x: intercept + (slope*x)

data = pd.read_csv('simple_linear_regressions_data.csv')
source = ColumnDataSource(data=data)

p = figure(title=f'Annual income vs. percent of adults who report\nconsuming vegetables fewer than once daily.\nR2: {score}', height=400, sizing_mode= "stretch_width", tools='', toolbar_location=None, x_range=(0,95000))
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
p.outline_line_color = None

jitter_radius = 3000
end_x = max(data['income_val']) + jitter_radius/2
end_y = corresponding_y(end_x)

p.circle(x=jitter('income_val', jitter_radius), y='value', source=source, fill_alpha=0.05, line_alpha=0.05, size=7)
p.line(x=[0, end_x], y=[intercept, end_y], color="red")


initial_x = 42000
initial_y = round(corresponding_y(initial_x), 1)
slider_coordinates = ColumnDataSource({'x': [initial_x], 'y': [initial_y], 'label': [f'{initial_y}%']})
slider_circle = p.circle(x='x', y='y', size=10, source=slider_coordinates, color="red")

slider = Slider(start=0, end=end_x, value=initial_x, step=1000, title="Select Income", format='$ 0,0[.]00', bar_color= "#B3D9FF", margin=[5, 25, 5, 25])
labels = LabelSet(x='x', y='y', text='label',
              x_offset=5, y_offset=5, source=slider_coordinates, render_mode='canvas')
p.add_layout(labels)

callback = CustomJS(args={'slider_data': slider_coordinates, 'intercept': intercept, 'slope': slope, 'label': labels}, code= """

    const x = cb_obj.value;
    const y = intercept + (slope*x);

    label.text_align = (x > 80000) ? 'right' : 'left';

    slider_data.data = {
        x: [x],
        y: [y],
        label: [`${y.toFixed(1)}%`],
    };

""")

slider.js_on_change('value', callback)

columns = column([p, slider], sizing_mode='stretch_width')

html = file_html(columns, resources=CDN)
# with open('simple_linear.html', 'w') as f:
#     f.writelines(html)

script, div = components(columns)
resources = CDN.render()
