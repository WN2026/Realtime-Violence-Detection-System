def get_graph_path(model_name):
    return {
        'cmu_640x480': './models/graph/cmu_640x480/graph_opt.pb',
        'cmuq_640x480': './models/graph/cmu_640x480/graph_q.pb',

        'cmu_640x360': './models/graph/cmu_640x360/graph_opt.pb',
        'cmuq_640x360': './models/graph/cmu_640x360/graph_q.pb',

        'mobilenet_thin_432x368': './models/graph/mobilenet_thin_432x368/graph_opt.pb',
    }[model_name]


