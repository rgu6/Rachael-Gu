import gradio as gr
import pandas as pd
import numpy as np

import requests
import json

import ast
import re

import matplotlib.pyplot as plt

# create home page
def home_page():
    return """
    <h1>Home</h1>
    <h2>Welcome to the College Enrollment Dashboard</h2>
    <p>This interactive dashboard allows users to ask questions in a chatbox about student enrollment at UIUC and other colleges, including data on majors, gender, ethnicity, and comparisons to national and state data.</p>
    <p>Here is a list of the sources that were used:</p>
    <ul>
        <li><a href="https://dmi.illinois.edu/stuenr/">UIUC Student Enrollment</a></li>
        <li><a href="https://www.census.gov/data/tables/time-series/demo/popest/2020s-national-detail.html">National Census</a></li>
        <li><a href="https://www.census.gov/library/stories/state-by-state.html">State-by-State Census</a></li>
    </ul>
    """

home = gr.HTML(home_page())

# function to send query to Mixtral LLM
def send(query):
    try:
        url = "https://mixtral.k8s-gosha.atlas.illinois.edu/completion"  # for mixtral (better version)

        myobj = {
            "prompt": "<s>[INST]" + query + "[/INST]",
            "n_predict": -1  # -1 for no limit of tokens for output
        }

        headers = {
            "Content-Type": "application/json",
            # "Authorization": "Basic YXRsYXNhaXRlYW06anhAVTJXUzhCR1Nxd3U="
        }

        response = requests.post(url, data=json.dumps(myobj), headers=headers,
                                 auth=('atlasaiteam', 'jx@U2WS8BGSqwu'), timeout=1000)
        return response.json()['content']

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
# load data
UIUC = pd.read_excel("fall_enroll_2004-23.xlsx")
UIUC = UIUC.dropna(how='all')

national = pd.read_excel("national population 2020-2023.xlsx")
national = national.rename(columns={'table with row headers in column A and column headers in rows 3 through 4. (leading dots indicate sub-parts)': 'Sex, Race, and Hispanic Origin Population Numbers', 
                                    'Unnamed: 1': 'April 2020',
                                    'Unnamed: 2': 'July 2020',
                                    'Unnamed: 3': 'July 2021',
                                    'Unnamed: 4': 'July 2022',
                                    'Unnamed: 5': 'July 2023'})
national = national.drop(index=0).reset_index(drop=True)

Illinois_ethnicity = pd.read_csv('Illinois (Ethnicity).csv')
Illinois_ethnicity = Illinois_ethnicity.rename(columns={'Label (Grouping)': 'Ethnicity Groupings'})

# create visualization for total UIUC students over the years categorized by ethnicity
def UIUC_fall_enroll():
    # read the data from the Excel file
    fall_enroll_race = pd.read_excel("fall_enroll_2004-23.xlsx")
    campus_total = fall_enroll_race[fall_enroll_race['Level'] == '***Campus total*** ']

    # list of ethnicities
    ethnicities = ['Caucasian', 'Asian American', 'African American', 'Hispanic', 'Native American', 'Hawaiian/Pacific Isl']

    plt.figure(figsize=(10, 10))
    
    # create a subplot for each ethnicity
    for i, ethnicity in enumerate(ethnicities, start=1):
        year = []
        students = []
        for _, row in campus_total.iterrows():
            year.append(int(row['Year']))
            students.append(row[ethnicity])
        
        df = pd.DataFrame({"Year": year, "Number of Students": students})

        # create a subplot
        plt.subplot(len(ethnicities), 1, i)
        plt.plot(df['Year'], df['Number of Students'], marker='o', linestyle='-')
        plt.title(ethnicity)
        plt.xlabel('Year')
        plt.ylabel('Number of Students')
        plt.xticks(year)

    plt.tight_layout()
    plt.savefig("UIUC_fall_enrollment.png")
    plt.close()
    
    return "UIUC_fall_enrollment.png"

# create visualizations for national gender breakdown over time
def national_gender_breakdown():
    df = pd.DataFrame({'Date': national.columns.values[1:6],
                   'Male': national.iloc[42][1:6],
                   'Female': national.iloc[84][1:6]})
    
    num_pies = len(df)
    num_cols = 3  
    num_rows = 2

    # create a figure with subplots
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(10, 10))
    axes = axes.flatten()  # Flatten the 2D array of axes to 1D

    # create pie charts
    for index, (i, row) in enumerate(df.iterrows()):
        sizes = [row['Male'], row['Female']]
        labels = ['Male', 'Female']
        
        axes[index].pie(sizes, labels=labels, autopct='%.2f%%', colors=['#66b3ff', '#ff9999'])
        axes[index].set_title(row["Date"])

    # remove any unused subplots
    for ax in axes[num_pies:]:
        ax.axis('off')

    plt.tight_layout()
    plt.savefig('national_gender_breakdown.png')
    plt.close()

    return 'national_gender_breakdown.png'

# create visualizations page
def visualizations_page(table_name):
    if table_name == 'UIUC':
        return UIUC_fall_enroll()
    if table_name == 'national':
        return national_gender_breakdown()

visualizations = gr.Interface(fn=visualizations_page, 
                              title="Visualizations", 
                              inputs=gr.Radio(choices=['UIUC', 'national'], label="Select Data"), 
                              outputs=[gr.Image()])

# create view data page
def viewdata_page(table_name):
    table_list = {
        "UIUC": UIUC,
        "national": national,
        "Illinois_ethnicity": Illinois_ethnicity
    }
    return table_list[table_name]

viewdata = gr.Interface(fn=viewdata_page,
                        title='View Data',
                        inputs=gr.Radio(choices=['national', "Illinois_ethnicity"], label="Select Table"),
                        outputs=gr.DataFrame())

# data dictionary used to determine which datasets are relevant to the query
dict = {
  "UIUC": "The dataset contains student enrollment numbers at UIUC from 2004 to 2023 for total campus enrollment, undergraduate, graduate, and professional students. The columns include counts based on gender and ethnicity.",
  "national": "The dataset contains annual estimates of the national resident population by sex, race, and Hispanic origin for the United States from April 1, 2020 to July 1, 2023.",
  "Illinois_ethnicity": "The dataset contains Illinois population numbers in 2020 for different ethnicities, ranging from individuals identifying with one race to those identifying with six races."
}

# dictionary of tables
table_list = {
  "UIUC": UIUC,
  "national": national,
  "Illinois_ethnicity": Illinois_ethnicity
}

# find data relevant to query
def relevant_data(query, datasets):
    formatted_query = f"<s>[INST]{query}\n\nSelect all the table names that are most relevant to the query based on the description of each table. Only return an array list of table names using square brackets in a comma-delimited format! Do not include any explanation!\n{json.dumps(datasets)}[/INST]>"
    
    # find the list of column names inside square brackets within the LLM response
    match = re.search(r'\[(.*?)\]', send(formatted_query))
    
    if match:
        return ast.literal_eval(match.group(0))
    else: # LLM did not return a list of column names
      return []

# find columns relevant to query for each dataset
def relevant_columns(query, df):
    col_names = list(df.columns)
    formatted_query = f"<s>[INST]{query}\n\nSelect the columns that are most relevant to the query and only return an array list of column names. Do not include any explanation.\n{col_names}[/INST]>"

    num_reruns = 0
    while num_reruns < 10:
        try:
            # Send the query to the LLM and parse the response
            relevant_cols = ast.literal_eval(send(formatted_query))

            # make sure column names exist and list is not empty
            if set(relevant_cols).issubset(set(col_names)) and not []:
                return relevant_cols
            # if the columns do not exist in the table, explicitly tell the LLM to give the correct names
            elif not set(relevant_cols).issubset(set(col_names)):
                formatted_query = f"<s>[INST] The columns that were returned ({relevant_cols}) have incorrect names from the table. {query}\n\nPlease select the columns that are most relevant to the query and only return an array list of column names. Do not include any explanation and give me the correct spelling of the columns: {col_names} [/INST]>"
        
        except SyntaxError:
            pass  # ignore the syntax error and continue rerunning
        
        num_reruns += 1

    return []

# create questions page
def questions_page(query):
    # combine all steps to query data
    formatted_query = f"<s>[INST]{query}"

    # Step 1: find relevant datasets
    table_names = relevant_data(query, dict)

    # Step 2: find relevant columns for each dataset
    for x in table_names:
        df = table_list[x]
        cols = relevant_columns(query, df)
        formatted_query = formatted_query + f"\n\n{x}:\n{df[cols].to_json(orient='records')}"

    # Step 3: send query
    formatted_query = formatted_query + f"[/INST]>"
    response = send(formatted_query)

    return response
    
questions = gr.Interface(fn=questions_page,
                        title='Questions',
                        inputs=gr.Textbox(label="Ask a question about student enrollment:"),
                        outputs=gr.Textbox(label='Answer:'))

# combine all tabs
with gr.Blocks(theme=gr.themes.Soft(), css=".gradio-container {background-color: lightblue}") as app:
    gr.TabbedInterface([home, visualizations, viewdata, questions],
                    tab_names=["Home", "Visualizations", "View Data", "Questions"])
    
app.launch(share=True)
