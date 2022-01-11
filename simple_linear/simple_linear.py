from bokeh.plotting import figure, ColumnDataSource
from bokeh.embed import components
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
corresponding_y = lambda x: intercept + (slope*x)

data = pd.read_csv('simple_linear_regressions_data.csv')
source = ColumnDataSource(data=data)

p = figure(title='Annual incomve vs. percent of adults who report consuming vegetables less than one time daily', sizing_mode='stretch_width', tools='', toolbar_location=None, x_range=(0,95000))
p.xaxis[0].axis_label = 'Income ($)'
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

jitter_radius = 3000
end_x = max(data['income_val']) + jitter_radius/2
end_y = corresponding_y(end_x)

p.circle(x=jitter('income_val', jitter_radius), y='value', source=source, fill_alpha=0.2, line_alpha=0.2, size=7)
p.line(x=[0, end_x], y=[intercept, end_y])


initial_x = 42000
initial_y = round(corresponding_y(initial_x), 1)
slider_coordinates = ColumnDataSource({'x': [initial_x], 'y': [initial_y], 'label': [f'{initial_y}% no vegetables']})
slider_circle = p.circle(x='x', y='y', size=10, source=slider_coordinates)

slider = Slider(start=0, end=end_x, value=initial_x, step=1000, title="Select Income", margin=[5, 40, 5, 20])
labels = LabelSet(x='x', y='y', text='label',
              x_offset=5, y_offset=5, source=slider_coordinates, render_mode='canvas')
p.add_layout(labels)

callback = CustomJS(args={'slider_data': slider_coordinates, 'intercept': intercept, 'slope': slope}, code= """

    const x = cb_obj.value;
    const y = intercept + (slope*x);
    slider_data.data = {
        x: [x],
        y: [y],
        label: [`${y.toFixed(1)}% no vegetables`],
    };

""")



slider.js_on_change('value', callback)

#show(column([p, slider], sizing_mode='stretch_width'))
script, div = components(column([p, slider], sizing_mode='stretch_width'))

with open('bokeh_script.txt', 'w') as f:
    f.writelines(script)

with open('bokeh_div.txt', 'w') as f:
    f.writelines(div)