import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from annotated_text import annotated_text
import re


# Function to separate the numbers and alphabets from the given string
# from paper key to paper name
def convert_key_to_paper_name(str):
    numbers = re.findall(r'[0-9]+', str)
    numbers = ''.join(numbers)
    alphabets = re.findall(r'[a-zA-Z]+', str)
    alphabets = ''.join(alphabets)  # convert list to string
    paper_name = alphabets[0].upper() + alphabets[1:] + ' et al. ' + numbers
    return paper_name


st.set_page_config(layout="wide")

col4, col5 = st.columns(2)

with col4:
    # Add a title and intro text
    st.title('Dataset Explorer :dizzy:')
    st.text('This is a web app to allow exploration of medical imaging datasets')

    st.image("overview.png", width=600)

conn = st.connection("postgresql", "sql")




# Perform query.
df_datasets = conn.query('SELECT * FROM datasets', ttl="10m")

with col5:
    st.text("")
    st.text("")
    st.text("")
    st.text("")
    st.text("")
    selected_modality = st.selectbox('Select modality', options=df_datasets.modality.unique())
    df_datasets_filtered = df_datasets.loc[df_datasets['modality'] == selected_modality]
    st.text("")
    selected_dataset = st.selectbox('Select dataset', options=df_datasets_filtered.name)
    #selected_dataset = st.selectbox('Select dataset', options=df_datasets.name)

#df_data = conn.query('SELECT * FROM datasets where name = :thename', ttl="10m", params={"thename": selected_dataset})

df = conn.query('select papers.name, papers.arxiv, dataset_usages.shortcuts, dataset_usages.labels from papers '
                'left join dataset_usages on papers.id = dataset_usages.paper_id '
                'left join datasets on datasets.id = dataset_usages.dataset_id '
                'where datasets.name ilike :thename', params={"thename": selected_dataset})

df['paper_name'] = df['name'].apply(convert_key_to_paper_name)
df_shortcuts = df[['name', 'paper_name', 'arxiv', 'shortcuts']].dropna()
df_labels = df[['name', 'paper_name', 'arxiv', 'labels']].dropna()

st.header("Exploring...")
st.subheader(selected_dataset + " dataset")
#st.header(selected_dataset)
if not df.empty:
    #annotated_text("Jiménez-Sánchez et al. 2023 [link](https://arxiv.org/abs/2402.06353) ", ("chest drains", "shortcuts"))
    #df_shortcuts.apply(lambda x: st.markdown("check out this [link](%s)" % x.arxiv), axis=1)
    df_shortcuts.apply(lambda x: annotated_text(x.paper_name, ' [ref](%s) ' % x.arxiv, (x.shortcuts, 'shortcuts', "#faa")), axis=1)
    df_labels.apply(lambda x: annotated_text(x.paper_name, ' [ref](%s) ' % x.arxiv, (x.labels, 'labels', '#9cf')), axis=1)

col1, col2, col3 = st.columns(3)

with col1:
   st.header("Shortcuts")
   st.image("shortcuts.png")
   df_shortcuts.apply(
       lambda x: annotated_text(x.paper_name, ' [ref](%s) ' % x.arxiv, (x.shortcuts, '', "#faa")), axis=1)
   #st.dataframe(df_shortcuts.set_index(df_shortcuts.columns[0]))

with col2:
   st.header("Additional labels")
   st.image("labels.png")
   df_labels.apply(lambda x: annotated_text(x.paper_name, ' [ref](%s) ' % x.arxiv, (x.labels, '', '#9cf')), axis=1)

with col3:
   st.header("Additional resources")
   st.image("embedding.png")