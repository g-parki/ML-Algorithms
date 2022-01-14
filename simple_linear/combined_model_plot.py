from bokeh.plotting import figure, ColumnDataSource
from bokeh.embed import components, file_html
from bokeh.resources import CDN
from bokeh.models import Slider, LabelSet
from bokeh.models.callbacks import CustomJS
from bokeh.layouts import column
from bokeh.transform import jitter
from bokeh.io import show
import numpy as np
import json
import pandas as pd

#Load linear model, extract components
with open('simple_linear_regressions.json') as f:
    model = json.load(f)
slope = model['coefficients'][0]
intercept = model['intercept']
corresponding_y = lambda x: intercept + (slope*x)

#Load poly model, extract components
with open('poly_linear_regression.json') as f:
    poly_model = json.load(f)

#Poly
coef_x, coef_x2 = poly_model['coefficients'][0], poly_model['coefficients'][1]
poly_intercept = poly_model['intercept']
poly_corresponding_y = lambda x: poly_intercept + (coef_x*x) + (coef_x2*x*x)

data = pd.read_csv('simple_linear_regressions_data.csv')
source = ColumnDataSource(data=data)

# General plot definition
p = figure(title=f'Annual income vs. percent of adults who report\nconsuming vegetables fewer than once daily.', height=400, sizing_mode= "stretch_width", tools='', toolbar_location=None, x_range=(0,95000))
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
p.outline_line_color = None

# Scatter of original data
jitter_radius = 3000
p.circle(x=jitter('income_val', jitter_radius), y='value', source=source, fill_alpha=0.05, line_alpha=0.05, size=7)

# Line provided by models
max_x = max(data['income_val']) + jitter_radius/2
x = np.linspace(0, max_x, 200)
y = [corresponding_y(_x) for _x in x]
poly_y = [poly_corresponding_y(_x) for _x in x]
line_source = ColumnDataSource({'x': x, 'y': y, 'poly_y': poly_y})
p.line(x='x', y='y', color="purple", source=line_source, legend_label="Linear model")
p.line(x='x', y='poly_y', color="red", source=line_source, legend_label="Polynomial model")

# Slider with indicator circle and customjs callback
initial_x = 42000
initial_y = round(corresponding_y(initial_x), 1)
poly_initial_y = round(poly_corresponding_y(initial_x), 1)
slider_coordinates = ColumnDataSource({'x': [initial_x], 'y': [initial_y], 'poly_y': [poly_initial_y], 'labels': [f'{initial_y}%'], 'poly_labels': [f'{poly_initial_y}%']})
slider_circle = p.circle(x='x', y='y', size=10, source=slider_coordinates, color="purple")
poly_slider_circle = p.circle(x='x', y='poly_y', size=10, source=slider_coordinates, color="red")


slider = Slider(start=0, end=max_x, value=initial_x, step=1000, title="Select Income", format='$ 0,0[.]00', bar_color= "#B3D9FF", margin=[5, 25, 5, 25])
labels = LabelSet(x='x', y='y', text='labels',
              x_offset=5, y_offset=5, source=slider_coordinates, render_mode='canvas', text_color="purple")
poly_labels = LabelSet(x='x', y='poly_y', text='poly_labels',
              x_offset=5, y_offset=-20, source=slider_coordinates, render_mode='canvas', text_color="red")
p.add_layout(labels)
p.add_layout(poly_labels)

callback = CustomJS(
    args={
        'slider_data': slider_coordinates,
        'poly_intercept': poly_intercept,
        'coef_x': coef_x,
        'coef_x2': coef_x2,
        'poly_labels': poly_labels,
        'slope': slope,
        'intercept': intercept,
        'labels': labels,
    },
    code= """

    const x = cb_obj.value;
    const y = intercept + (slope*x);
    const poly_y = poly_intercept + (coef_x*x) + (coef_x2*x*x);

    const text_align = (x > 80000) ? 'right' : 'left';
    if (poly_labels.text_align != text_align) {
        poly_labels.text_align = text_align;
        labels.text_align = text_align;
    }

    poly_labels.y_offset = poly_y > y ? 5 : -20;
    labels.y_offset = poly_y > y ? -20 : 5;

    slider_data.data = {
        x: [x],
        y: [y],
        poly_y: [poly_y],
        labels: [`${y.toFixed(1)}%`],
        poly_labels: [`${poly_y.toFixed(1)}%`],
    };

""")

slider.js_on_change('value', callback)

columns = column([p, slider], sizing_mode='stretch_width')

html = file_html(columns, resources=CDN)
with open('combined_linear.html', 'w') as f:
    f.writelines(html)

script, div = components(columns)
resources = CDN.render()
