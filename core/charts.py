# -*- coding: utf-8 -*-
import json
import os


def plotly_available():
    return os.path.isfile(_plotly_js_path())


def _plotly_js_path():
    root = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(root, 'vendor', 'js', 'plotly.min.js')


def write_plotlyjs_html(output_html_path, title, traces, layout, config=None, inline_plotly=True):
    if config is None:
        config = {'responsive': True}
    elif 'responsive' not in config:
        config = dict(config)
        config['responsive'] = True

    plotly_js = ''
    if inline_plotly:
        js_path = _plotly_js_path()
        if not os.path.isfile(js_path):
            raise FileNotFoundError('Plotly.js not found at {}'.format(js_path))
        with open(js_path, 'r', encoding='utf-8') as handle:
            plotly_js = handle.read()
        plotly_tag = '<script>{}</script>'.format(plotly_js)
    else:
        js_rel = os.path.relpath(_plotly_js_path(), os.path.dirname(output_html_path))
        plotly_tag = '<script src="{}"></script>'.format(js_rel.replace(os.sep, '/'))

    html = [
        '<!doctype html>',
        '<html>',
        '<head>',
        '<meta charset="utf-8">',
        '<title>{}</title>'.format(title),
        '<style>',
        'html, body { margin: 0; padding: 0; width: 100%; height: 100%; }',
        '#chart { width: 100%; height: 100vh; }',
        '</style>',
        '</head>',
        '<body>',
        '<div id="chart"></div>',
        plotly_tag,
        '<script>',
        'const traces = {};'.format(json.dumps(traces, ensure_ascii=False)),
        'const layout = {};'.format(json.dumps(layout, ensure_ascii=False)),
        'const config = {};'.format(json.dumps(config, ensure_ascii=False)),
        "Plotly.newPlot('chart', traces, layout, config);",
        "window.onresize = () => Plotly.Plots.resize('chart');",
        '</script>',
        '</body>',
        '</html>',
    ]
    with open(output_html_path, 'w', encoding='utf-8') as handle:
        handle.write('\n'.join(html))


def _class_label(class_id, label):
    label = label or ''
    if label:
        return '{} - {}'.format(class_id, label)
    return str(class_id)


def _axis_label(unit_label):
    if unit_label == 'pixels':
        return 'Pixels'
    if unit_label == 'm2':
        return 'Area (m2)'
    if unit_label == 'km2':
        return 'Area (km2)'
    return unit_label


def _write_plot_html(html_path, title, traces, layout, config=None):
    try:
        write_plotlyjs_html(html_path, title, traces, layout, config=config, inline_plotly=True)
    except FileNotFoundError as exc:
        return False, str(exc)
    return True, None


def _ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def export_area_by_class(rows, output_dir, unit_label):
    if not plotly_available():
        return False, 'Plotly.js not available.'
    _ensure_dir(output_dir)
    years = sorted({row[0] for row in rows})
    classes = sorted({row[1] for row in rows})
    labels = {row[1]: row[2] for row in rows}
    area_map = {(row[1], row[0]): float(row[4]) for row in rows}

    traces = []
    for class_id in classes:
        y = [area_map.get((class_id, year), 0.0) for year in years]
        traces.append({
            'type': 'scatter',
            'mode': 'lines+markers',
            'x': years,
            'y': y,
            'name': _class_label(class_id, labels.get(class_id, '')),
        })

    layout = {
        'title': 'Area by Class',
        'xaxis': {'title': 'Year'},
        'yaxis': {'title': _axis_label(unit_label)},
        'legend': {'title': {'text': 'Class'}},
    }
    html_path = os.path.join(output_dir, 'area_by_class.html')
    ok, err = _write_plot_html(html_path, 'Area by Class', traces, layout)
    return ok, err


def export_net_gross(rows, year0, year1, unit_label, area_factor, output_dir):
    if not plotly_available():
        return False, 'Plotly.js not available.'
    _ensure_dir(output_dir)
    labels = []
    gains = []
    losses = []
    for row in rows:
        class_id = row[0]
        label = row[1]
        gain_px = row[2]
        loss_px = row[3]
        labels.append(_class_label(class_id, label))
        gains.append(gain_px * area_factor)
        losses.append(loss_px * area_factor)

    traces = [
        {'type': 'bar', 'x': labels, 'y': gains, 'name': 'Gain', 'marker': {'color': '#2ca02c'}},
        {'type': 'bar', 'x': labels, 'y': [-val for val in losses], 'name': 'Loss', 'marker': {'color': '#d62728'}},
    ]
    layout = {
        'title': 'Net/Gross Change {}-{}'.format(year0, year1),
        'barmode': 'relative',
        'xaxis': {'title': 'Class'},
        'yaxis': {'title': _axis_label(unit_label)},
    }
    fname = 'net_gross_change_{}_{}'.format(year0, year1)
    html_path = os.path.join(output_dir, '{}.html'.format(fname))
    ok, err = _write_plot_html(html_path, 'Net/Gross Change {}-{}'.format(year0, year1), traces, layout)
    return ok, err


def export_net_gross_combined(interval_rows, legend_map, output_dir):
    if not plotly_available():
        return False, 'Plotly.js not available.'
    _ensure_dir(output_dir)

    if not interval_rows:
        return False, 'No interval data for combined chart.'

    class_ids = [row[0] for row in interval_rows[0]['rows']]
    class_labels = [_class_label(class_id, legend_map.get(class_id, '')) for class_id in class_ids]
    palette = [
        'rgba(31, 119, 180, 0.85)',
        'rgba(255, 127, 14, 0.85)',
        'rgba(44, 160, 44, 0.85)',
        'rgba(214, 39, 40, 0.85)',
        'rgba(148, 103, 189, 0.85)',
        'rgba(140, 86, 75, 0.85)',
        'rgba(227, 119, 194, 0.85)',
        'rgba(127, 127, 127, 0.85)',
        'rgba(188, 189, 34, 0.85)',
        'rgba(23, 190, 207, 0.85)',
    ]

    traces = []
    unit_label = interval_rows[0]['unit_label']
    for idx, interval in enumerate(interval_rows):
        label = interval['label']
        rows = interval['rows']
        area_factor = interval['area_factor']
        gains = []
        losses = []
        for row in rows:
            gain_px = row[2]
            loss_px = row[3]
            gains.append(-gain_px * area_factor)
            losses.append(loss_px * area_factor)
        color = palette[idx % len(palette)]
        traces.append({
            'type': 'bar',
            'y': class_labels,
            'x': gains,
            'orientation': 'h',
            'name': '{} Gain'.format(label),
            'marker': {'color': color},
            'offsetgroup': label,
            'legendgroup': label,
            'showlegend': True,
        })
        traces.append({
            'type': 'bar',
            'y': class_labels,
            'x': losses,
            'orientation': 'h',
            'name': '{} Loss'.format(label),
            'marker': {'color': color.replace('0.85', '0.45')},
            'offsetgroup': label,
            'legendgroup': label,
            'showlegend': True,
        })

    layout = {
        'title': 'Net/Gross Change (All Intervals)',
        'barmode': 'group',
        'xaxis': {'title': _axis_label(unit_label)},
        'yaxis': {'title': 'Class'},
    }
    html_path = os.path.join(output_dir, 'net_gross_change_all_intervals.html')
    ok, err = _write_plot_html(html_path, 'Net/Gross Change (All Intervals)', traces, layout)
    return ok, err


def export_transition_matrix(matrix, classes, labels, year0, year1, output_dir, unit_label):
    if not plotly_available():
        return False, 'Plotly.js not available.'
    _ensure_dir(output_dir)
    class_labels = [_class_label(c, labels.get(c, '')) for c in classes]
    matrix_list = matrix.tolist() if hasattr(matrix, 'tolist') else matrix
    traces = [{
        'type': 'heatmap',
        'z': matrix_list,
        'x': class_labels,
        'y': class_labels,
        'colorscale': 'Blues',
        'colorbar': {'title': {'text': _axis_label(unit_label)}},
    }]
    layout = {
        'title': 'Transition Matrix {}-{}'.format(year0, year1),
        'xaxis': {'title': 'To class'},
        'yaxis': {'title': 'From class'},
    }
    fname = 'transition_matrix_{}_{}'.format(year0, year1)
    html_path = os.path.join(output_dir, '{}.html'.format(fname))
    ok, err = _write_plot_html(html_path, 'Transition Matrix {}-{}'.format(year0, year1), traces, layout)
    return ok, err


def export_top_transitions(rows, year0, year1, output_dir, unit_label, max_items=20):
    if not plotly_available():
        return False, 'Plotly.js not available.'
    _ensure_dir(output_dir)
    ranked = sorted(rows, key=lambda r: r[5], reverse=True)[:max_items]
    labels = ['{} -> {}'.format(_class_label(r[0], r[1]), _class_label(r[2], r[3])) for r in ranked]
    areas = [r[5] for r in ranked]

    traces = [{
        'type': 'bar',
        'y': labels,
        'x': areas,
        'orientation': 'h',
        'marker': {'color': '#1f77b4'},
    }]
    layout = {
        'title': 'Top Transitions {}-{}'.format(year0, year1),
        'xaxis': {'title': _axis_label(unit_label)},
        'yaxis': {'title': 'Transition'},
    }
    fname = 'top_transitions_{}_{}'.format(year0, year1)
    html_path = os.path.join(output_dir, '{}.html'.format(fname))
    ok, err = _write_plot_html(html_path, 'Top Transitions {}-{}'.format(year0, year1), traces, layout)
    return ok, err


def export_intensity(rows, output_dir):
    if not plotly_available():
        return False, 'Plotly.js not available.'
    _ensure_dir(output_dir)
    labels = ['{}-{}'.format(row[0], row[1]) for row in rows]
    annualized = [row[6] for row in rows]
    interval = [row[5] for row in rows]

    traces = [
        {'type': 'scatter', 'mode': 'lines+markers', 'x': labels, 'y': interval, 'name': 'Interval'},
        {'type': 'scatter', 'mode': 'lines+markers', 'x': labels, 'y': annualized, 'name': 'Annualized'},
    ]
    layout = {
        'title': 'Change Intensity',
        'xaxis': {'title': 'Interval'},
        'yaxis': {'title': 'Intensity'},
    }
    html_path = os.path.join(output_dir, 'change_intensity.html')
    ok, err = _write_plot_html(html_path, 'Change Intensity', traces, layout)
    return ok, err


def export_sankey(intervals, legend_map, output_dir, max_links=5000):
    if not plotly_available():
        return False, 'Plotly.js not available.'
    _ensure_dir(output_dir)

    nodes = []
    node_index = {}
    links = {'source': [], 'target': [], 'value': []}

    def get_node(year, class_id):
        key = (year, class_id)
        if key in node_index:
            return node_index[key]
        label = _class_label(class_id, legend_map.get(class_id, ''))
        node_label = '{} | {}'.format(year, label)
        node_index[key] = len(nodes)
        nodes.append(node_label)
        return node_index[key]

    total_links = 0
    unit_label = 'pixels'
    for interval in intervals:
        year0 = interval['year0']
        year1 = interval['year1']
        matrix = interval['matrix']
        nodata_class = interval.get('nodata_class')
        unit_label = interval.get('unit_label', unit_label)
        area_factor = interval.get('area_factor', 1.0)
        if nodata_class is not None and 0 <= nodata_class < matrix.shape[0]:
            matrix = matrix.copy()
            matrix[nodata_class, :] = 0
            matrix[:, nodata_class] = 0
        rows, cols = (matrix > 0).nonzero()
        for i, j in zip(rows.tolist(), cols.tolist()):
            value = matrix[i, j]
            if unit_label != 'pixels':
                value = float(value) * area_factor
            else:
                value = int(value)
            if value <= 0:
                continue
            links['source'].append(get_node(year0, i))
            links['target'].append(get_node(year1, j))
            links['value'].append(value)
            total_links += 1
            if total_links >= max_links:
                break
        if total_links >= max_links:
            break

    traces = [{
        'type': 'sankey',
        'arrangement': 'snap',
        'node': {'label': nodes, 'pad': 12, 'thickness': 14},
        'link': {'source': links['source'], 'target': links['target'], 'value': links['value']},
    }]
    layout = {
        'title': 'Class Transitions (All Intervals)',
        'font': {'size': 12},
    }
    html_path = os.path.join(output_dir, 'class_flow_sankey.html')
    ok, err = _write_plot_html(html_path, 'Class Transitions (All Intervals)', traces, layout)
    return ok, err
