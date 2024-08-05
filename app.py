import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit.components.v1 as components
import subprocess

from app_utils.produce_common_df import produce_common_df
from app_utils.visualization_utils import heatmap_df, generate_pdb_view


# Custom CSS for styling
st.markdown("""
    <style>
    .title {
        font-size: 3em;
        color: #4CAF50;
        text-align: center;
        margin-top: 20px;
    }
    .intro-text {
        font-size: 1.2em;
        line-height: 1.6;
        margin: 20px;
    }
    .how-to-use {
        font-size: 1.5em;
        margin-top: 30px;
        margin-bottom: 10px;
        color: #4CAF50;
    }
    .step {
        font-size: 1.2em;
        margin: 10px 0;
    }
    .enjoy {
        font-size: 1.3em;
        color: #4CAF50;
        margin-top: 20px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="title">Identify and Analyze Catalytic Sites in Proteins</h1>', unsafe_allow_html=True)

# Introduction and instructions
st.markdown("""
    <div class="intro-text">
    Welcome to this interactive data analysis app designed to help you identify and analyze catalytic sites in proteins. 
    This tool allows you to:
    <ul>
        <li>Upload your own CSV files to analyze residue-level predictions and visualize them.</li>
        <li>Upload a PDB file to visualize 3D structures and run PRANK predictions.</li>
        <li>Explore and filter the data using various plots and visualizations.</li>
    </ul>
    </div>
    
    <div class="how-to-use"> How to Use the App:</div>
    <div class="step">1. <strong>Upload Files:</strong></div>
    <div class="intro-text">
        <ul>
            <li>Choose to upload either a PDB file or CSV files using the options in the sidebar.</li>
            <li>Follow the prompts to upload your files.</li>
        </ul>
    </div>
    
    <div class="step">2. <strong>Analyze Data:</strong></div>
    <div class="intro-text">
        <ul>
            <li>If you upload a PDB file, the app will run PRANK predictions and allow you to visualize the results.</li>
            <li>If you upload CSV files, you can filter the data and create various plots to explore the results.</li>
        </ul>
    </div>
    
    <div class="step">3. <strong>Visualize Results:</strong></div>
    <div class="intro-text">
        <ul>
            <li>Use the tabs to navigate through different analysis options, including viewing data statistics, creating heatmaps, and visualizing results on 3D structures.</li>
        </ul>
    </div>
    
    <div class="enjoy">Enjoy exploring and analyzing your protein data!</div>
""", unsafe_allow_html=True)

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

def run_prank(path2pdb):
    command = f'p2rank/distro/prank predict -f {path2pdb} -o data/prank_outputs'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout, stderr

def tabs(df_common):
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


# Radio button for user choice
st.sidebar.header('Choose an option')
option = st.sidebar.radio(
    'Select what you want to upload:',
    ('Upload PDB file', 'Upload CSV files')
)



# If user selects to upload PDB file
if option == 'Upload PDB file':
    st.sidebar.header('Upload your PDB file')
    file_pdb = st.sidebar.file_uploader('Upload PDB file', type=['pdb'], key='pdb_uploader')
    pdb_file_name = file_pdb.name if file_pdb is not None else None
    #st.write(f"Uploaded file: {pdb_file_name}")

    # Save and process the uploaded PDB file if available
    if file_pdb is not None:
        path2pdb = f'data/pdbs/{pdb_file_name}'
        with open(path2pdb, 'wb') as f:
            f.write(file_pdb.getvalue())

        # Run PRANK prediction on the uploaded PDB file
        with st.spinner('Progress...'):
            stdout, stderr = run_prank(path2pdb)
        st.success('PRANK prediction completed successfully!')

        # Load the uploaded CSV files
        file_prank = f'data/prank_outputs/{pdb_file_name}_residues.csv'
        df_prank = load_data(file_prank)

        file_gass = st.sidebar.file_uploader('Upload GASS-WEB predictions', type='csv', key='gass_uploader1')
        df_gass = load_data(file_gass, sep='\t')
        
        
        if df_prank is not None and df_gass is not None:
            
            df_common = produce_common_df(df_prank, df_gass) 
            tabs(df_common)

# If user selects to upload CSV files
elif option == 'Upload CSV files':
    st.sidebar.header('Upload your CSV files')
    file1 = st.sidebar.file_uploader('Upload PRANK residue level predictions', type='csv', key='prank_uploader')
    file2 = st.sidebar.file_uploader('Upload GASS-WEB predictions', type='csv', key='gass_uploader2')

    # Load the uploaded CSV files
    df_prank = load_data(file1)
    df_gass = load_data(file2, sep='\t')

    # Process the data if both CSV files are uploaded
    if df_prank is not None and df_gass is not None:
        df_common = produce_common_df(df_prank, df_gass)
        tabs(df_common)

