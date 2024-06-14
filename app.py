import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit.components.v1 as components

from app_utils.produce_common_df import produce_common_df
from app_utils.visualization_utils import heatmap_df, generate_pdb_view

st.title('Data Interactive Analysis App')

# Function to load the uploaded files
def load_data(uploaded_file, sep=','):
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, sep=sep)
            return df
        except Exception as e:
            st.error(f"Error loading file: {e}")
            return None
    else:
        return None
    
# Function to filter the DataFrame according to EC level
def filter_according_to_ec(df, ec_level):
    df_filtered = df[df['EC'] == ec_level]
    return df_filtered

# Function to render py3Dmol view in Streamlit
def render_pdb_view(view):
    view_html = view._make_html()
    components.html(view_html, height=600, width=800)

# Upload files
st.sidebar.header('Upload your CSV files')
file1 = st.sidebar.file_uploader('Upload PRANK residue level predictions', type='csv')
file2 = st.sidebar.file_uploader('Upload GASS-WEB predictions', type='csv')

# Load the uploaded files
df_prank = load_data(file1)
df_gass = load_data(file2, sep='\t')

if df_prank is not None and df_gass is not None:
    df_common = produce_common_df(df_prank, df_gass)


    tab1, tab2, tab3,tab4 = st.tabs(['Main' ,'Statistics of Data', 'Heatmap Analysis', 'Visualize Results on PDB'])
    with tab1:
        st.header('First 10 rows of the common DataFrame')
        st.write(df_common.head(10))

        # select one pr multiple columns to filter the dataframe
        st.header('Filter DataFrame')
        filter_columns = st.multiselect('Select columns to filter', df_common.columns)
        filter_values = {}
        for col in filter_columns:
            if col =='FITNESS' or col == 'PROB.POCKET':
                df_common[col] = df_common[col].astype(float)
                min_value = df_common[col].min()
                max_value = df_common[col].max()
                filter_values[col] = st.slider(f'Select values for {col}', min_value, max_value, (min_value, max_value))
            else:
                unique_values = df_common[col].unique()
                filter_values[col] = st.multiselect(f'Select values for {col}', unique_values)

        filtered_df = df_common.copy()
        for col, values in filter_values.items():
            if values:
                if col == 'FITNESS' or col == 'PROB.POCKET':
                    filtered_df = filtered_df[(filtered_df[col] >= values[0]) & (filtered_df[col] <= values[1])]
                else:               
                    filtered_df = filtered_df[filtered_df[col].isin(values)]

        st.write('Filtered DataFrame')
        st.write(filtered_df)

    with tab2:
        st.title('Statistics of Data')
        st.header('Histogram Analysis')
        # select the column to plot the histogram
        column = st.selectbox('Select the column', df_common.columns)
        plt.figure(figsize=(10, 7))
        sns.histplot(df_common[column], kde=True)
        st.pyplot(plt)

        st.header('Scatter Plot Analysis')
        x_col = st.selectbox('Select the X-axis column for scatter plot', df_common.columns)
        y_col = st.selectbox('Select the Y-axis column for scatter plot', df_common.columns)
        plt.figure(figsize=(10, 7))
        sns.scatterplot(x=df_common[x_col], y=df_common[y_col])
        st.pyplot(plt)
    with tab3:
        # Heatmap Analysis
        st.title('Heatmap Analysis')
        st.write('Select the columns to plot the heatmap')
        # list columns except FITNESS and PROB.POCKET
        heatmap_columns = list(set(df_common.columns) - set(['FITNESS', 'PROB.POCKET']))


        index_ = st.selectbox('Select the index column', heatmap_columns, index=0)
        heatmap_columns.remove(index_)
        columns = st.selectbox('Select the columns', heatmap_columns, index=1)
        values = st.selectbox('Select the values column', ['FITNESS', 'PROB.POCKET'])
        # aggfunc = st.selectbox('Select the aggregation function', ['mean', 'sum', 'count'])
        heatmap = heatmap_df(df_common, index_, columns, values)

        st.pyplot(heatmap)
    with tab4:
        st.title('Visualize Results on PDB')
        # upload pdb file for visualization
        st.write('Upload the PDB file to visualize the results')
        file_pdb = st.file_uploader('Upload PDB file', type=['pdb'])
        if file_pdb is not None:
       
            pdb_data = file_pdb.getvalue().decode("utf-8")

            residue_number = st.text_input('Enter the residue number(s) to highlight')
            # if residue_number is comma separated, split it and convert to list
            if ',' in residue_number:
                residue_numbers = residue_number.split(',')
            else:
                residue_numbers = [residue_number]
            chain = st.text_input('Enter the chain(s) to highlight')
            # if chain is comma separated, split it and convert to list
            if ',' in chain:
                chains = chain.split(',')
            else:
                chains = [chain]

            if len(residue_numbers) != len(chains):
                st.error('Number of residue numbers and chains should be the same')
                st.stop()
            color = st.selectbox('Select the color to highlight', ['red', 'blue', 'green'])
            radius = st.slider('Select the radius of the highlighted residue', 0.1, 5.0, 1.0)
            view = generate_pdb_view(pdb_data, residue_numbers, chains, color, radius)
            render_pdb_view(view)
