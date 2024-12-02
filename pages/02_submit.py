import streamlit as st
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
import pandas as pd
import numpy as np

## To cytoscape json
#elements = df.apply(lambda x: {"data": dict(x)}, axis=1).tolist()

## Back to pandas
#df = pd.json_normalize(elements).rename(columns=lambda x: x.split("."

st.title('Living Review - Graph')
# st.markdown(':warning: :construction: in progress :warning: :construction:')

# connect to sql database
conn = st.connection("postgresql", "sql")

# Perform query
df_papers = conn.query('select papers.id, papers.name, papers.arxiv from papers')
#df_papers['paper_name'] = df_papers['name'].apply(convert_key_to_paper_name)
df_papers['label'] = 'PAPER'
df_papers['attribute'] = df_papers['arxiv']
df_papers = df_papers.drop(columns=['arxiv'], axis=1)
df_papers['id'] = df_papers['id'].map(lambda x: "p"+str(x))

df_datasets = conn.query('select datasets.id, datasets.name, datasets.modality from datasets')
df_datasets['label'] = 'DATASET'
df_datasets['attribute'] = df_datasets['modality']
df_datasets = df_datasets.drop(columns=['modality'])
df_datasets['id'] = df_datasets['id'].map(lambda x: "d"+str(x))

df_nodes = pd.concat([df_datasets, df_papers])
the_nodes = df_nodes.apply(lambda x: {"data": dict(x)}, axis=1).tolist()

# load data with links
df_dataset_usages = conn.query('select dataset_usages.paper_id, dataset_usages.dataset_id, dataset_usages.id,'
                               'dataset_usages.shortcuts, dataset_usages.labels from dataset_usages')
# rename indices
df_dataset_usages['id'] = np.arange(0, len(df_dataset_usages), 1)
df_dataset_usages['id'] = df_dataset_usages['id'].map(lambda x: "e"+str(x))
df_dataset_usages['source'] = df_dataset_usages['paper_id'].map(lambda x: "p"+str(x))
df_dataset_usages['target'] = df_dataset_usages['dataset_id'].map(lambda x: "d"+str(x))
# get indices for shortcuts or labels
labels_index = df_dataset_usages.index[df_dataset_usages['labels'].notna()].tolist()
shortcuts_index = df_dataset_usages.index[df_dataset_usages['shortcuts'].notna()].tolist()
# combine information into attribute field
df_dataset_usages['attribute'] = [df_dataset_usages['shortcuts'][i] if i in shortcuts_index else df_dataset_usages['labels'][i] for i in range(len(df_dataset_usages))]
# assign posted or follows for labels or shortcuts respectively
df_dataset_usages['label'] = ['SHORTCUT' if i in shortcuts_index else '+LABEL' for i in range(len(df_dataset_usages))]
df_dataset_usages = df_dataset_usages.drop(columns=['dataset_id'], axis=1)
df_dataset_usages = df_dataset_usages.drop(columns=['paper_id'], axis=1)
df_dataset_usages = df_dataset_usages.drop(columns=['shortcuts'], axis=1)
df_dataset_usages = df_dataset_usages.drop(columns=['labels'], axis=1)

the_edges = df_dataset_usages.apply(lambda x: {"data": dict(x)}, axis=1).tolist()

node_styles = [
    NodeStyle(label='DATASET', color='#FF7F3E', caption='name', icon='inventory'),  # DATASETS // PERSON
    NodeStyle(label="PAPER", color="#2A629A", caption="name", icon="description")  # PAPERS  // POST
]

edge_styles = [
    EdgeStyle("+LABEL", color='#e8c2a7', caption='label', directed=True),
    EdgeStyle("SHORTCUT", color='#dcc7e4', caption='label', directed=True),
    #EdgeStyle("QUOTES", caption='label', directed=True),
]

layout = {"name": "fcose", "animate": "end", "nodeDimensionsIncludeLabels": False}

elements = {"nodes": the_nodes, "edges": the_edges}

st_link_analysis(elements, layout, node_styles, edge_styles, key="xyz")

