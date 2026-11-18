import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

def map(topo, filename):
    # COMPATIBILITY PATCH (UCC-2021 snapshot): Basemap is optional.
    from mpl_toolkits.basemap import Basemap as Basemap

    if not filename:
        filename="simulation"

    lon = [value[0] for x,value in nx.get_node_attributes(topo, 'pos').items()]
    lat = [value[1] for x,value in nx.get_node_attributes(topo, 'pos').items()]

    m = Basemap(
        projection='merc',
        llcrnrlon=min(lon)-(max(lon)-min(lon))*0.1,
        llcrnrlat=min(lat)-(max(lat)-min(lat))*0.1,
        urcrnrlon=max(lon)+(max(lon)-min(lon))*0.1,
        urcrnrlat=max(lat)+(max(lat)-min(lat))*0.1,
        lat_ts=0,
        resolution='i',
        suppress_ticks=True)

    subgraph = nx.subgraph(topo, [x for x,value in nx.get_node_attributes(topo, 'type').items() if value == "netabs" ])

    subgraph_simple_edges = nx.DiGraph()
    for n, data in subgraph.nodes(data=True):
        subgraph_simple_edges.add_node(n, **data)
    for u,v,data in subgraph.edges(data=True):
        if not (subgraph_simple_edges.has_edge(u,v) or subgraph_simple_edges.has_edge(v,u)):
            subgraph_simple_edges.add_edge(u, v, **data)
    
    pos = { x:m(value[0], value[1]) for x,value in nx.get_node_attributes(subgraph_simple_edges, 'pos').items()}
    #size = [10+len(value)*5 for x,value in nx.get_node_attributes(topo, 'containers').items()]
    #color = [1 if value == "chost" else 100 for x,value in nx.get_node_attributes(subgraph, 'type').items()]    

    figsize = abs(int((max(lon)-min(lon))%100)), abs(int((max(lat)-min(lat))%100))
    
    fig = plt.figure(figsize=figsize)

    m.drawcountries(linewidth=0.5)
    m.drawcoastlines(linewidth=0.5)
    m.fillcontinents(color='lightgrey')
    m.drawmapboundary()

    nx.draw_networkx_nodes(subgraph_simple_edges, pos=pos, node_size=2000,cmap=plt.cm.get_cmap("plasma"))
    nx.draw_networkx_edges(subgraph_simple_edges, pos=pos, arrowstyle="-", arrowsize=100, connectionstyle="arc3,rad=0.1")
    nx.draw_networkx_labels(subgraph_simple_edges, pos, labels={x:value for x,value in nx.get_node_attributes(subgraph_simple_edges, 'name').items()}, font_weight="bold", font_color="white", font_size=18)
    plt.plot()
    
    fig.savefig("images/"+filename+"-map.png", dpi=200)

def container_instantiantion_time(messages, filename):
    if not filename:
        filename="simulation"

    messages_plot = {}

    for message in messages:
        if not message.name in messages_plot.keys():
            messages_plot[message.name] = []

        messages_plot[message.name].append(
            (round(message.finish_time-message.start_time, 2),
            round(message.start_time-message.arrival_time, 2)))

    name_array = []
    container_len = [ len(x) for n,x in messages_plot.items()]
    message_matrix_1 = [ [] for i in range(0,max(container_len)) ]
    message_matrix_2 = [ [] for i in range(0,max(container_len)) ]

    for name, values in sorted(messages_plot.items()):
        name_array.append(name)
        for i, message in enumerate(sorted(values, key=lambda x: x[0]+x[1])):
            message_matrix_1[i].append(message[1])
            message_matrix_2[i].append(message[0])

    barWidth = 0.1
    
    r = []
    for i in range(0, len(message_matrix_1)):
        if i == 0:
            r.append(np.arange(len(message_matrix_1[0])*1.2, step=1.2).tolist())
        else:
            r.append([round(x + barWidth,2) for x in r[i-1]])
   
    fig = plt.figure(figsize=(max(len(name_array),12), 8))

    for i in range(0, len(message_matrix_1)):
        plt.bar(r[i], message_matrix_1[i], color='lightgrey', width=barWidth, edgecolor='white')
        plt.bar(r[i], message_matrix_2[i], color='grey', width=barWidth, edgecolor='white', bottom=message_matrix_1[i])

    # Add xticks on the middle of the group bars
    plt.xlabel('Applications', fontweight='bold', labelpad=10)
    plt.xticks([r*1.2 + barWidth*5 for r in range(0,len(name_array))], name_array)
 
     # Create legend & Show graphic
    legend_elements = [Patch(facecolor='grey', 
                         label='Download Time'),
                         Patch(facecolor='lightgrey', 
                         label='Waiting Time')]
    plt.legend(handles=legend_elements, fontsize=8)
    plt.plot()
    fig.tight_layout()

    fig.savefig("images/"+filename+"-containerInstTime.png", dpi=200)

def container_instantiantion_maxmin_time(messages, filename):
    
    if not filename:
        filename="simulation"

    messages_plot = {}

    for message in messages:
        if not message.name in messages_plot.keys():
            messages_plot[message.name] = []

        messages_plot[message.name].append(
            (round(message.finish_time-message.start_time, 2),
            round(message.start_time-message.arrival_time, 2)))

    name_array = []
    message_matrix_1 = [ [] , [] ]
    message_matrix_2 = [ [] , [] ]
    
    for name, values in messages_plot.items():
        name_array.append(name)
        sum_array = [ x[0]+x[1] for x in values ]


        message_matrix_1[0].append(values[sum_array.index(min(sum_array))][1])
        message_matrix_1[1].append(values[sum_array.index(max(sum_array))][1])
        message_matrix_2[0].append(values[sum_array.index(min(sum_array))][0])
        message_matrix_2[1].append(values[sum_array.index(max(sum_array))][0])

    barWidth = 0.2
    
    r = []
    for i in range(0, len(message_matrix_1)):
        if i == 0:
            r.append(np.arange(len(message_matrix_1[0])*0.5, step=0.5))
        else:
            r.append([round(x + barWidth,2) for x in r[i-1]])
    
    fig = plt.figure(figsize=(max(len(name_array)*0.5,12), 8))

    for i in range(0, len(message_matrix_1)):
        plt.bar(r[i], message_matrix_1[i], color='lightgrey', width=barWidth, edgecolor='white')
        plt.bar(r[i], message_matrix_2[i], color='grey', width=barWidth, edgecolor='white', bottom=message_matrix_1[i])

    # Add xticks on the middle of the group bars
    plt.xlabel('Applications', fontweight='bold', labelpad=10)
    plt.xticks([r*0.5 + barWidth/2 for r in range(0,len(name_array))], name_array, fontsize=8, rotation=90)
    
    # Create legend & Show graphic
    legend_elements = [Patch(facecolor='grey', 
                         label='Download Time'),
                         Patch(facecolor='lightgrey', 
                         label='Waiting Time')]
    plt.legend(handles=legend_elements, fontsize=8)
    plt.plot()
    fig.tight_layout()
    
    fig.savefig("images/"+filename+"-containerMaxMinInstTime.png", dpi=200)