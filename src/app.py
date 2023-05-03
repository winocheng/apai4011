from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
from course import *

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

COURSES = course_list()

app.layout = html.Div([
    html.Div([
        html.H3("Select Your Course(s):"),
        dcc.Dropdown(
            COURSES,
            [COURSES[0]],
            id = "course-input",
            multi=True,
            placeholder="Select a course"
        ),
        html.Br(),
        html.Button('Submit', id='submit-course', style={
            "color": "#2186f4", 
            "border-style": "solid",
            "border-width": "1px",
            "border-color": "#2186f4",
            "border-radius": "10px",
            "background-color": "white",
            "text-transform": "uppercase"}),
        dcc.Loading(children=html.Div(id='course-output'))
    ], style= {'width': '40%', 'float':'left', 'margin-right':"10px"}),
    html.Div(id='jobs-output',style={'width': '40%', 'float':'left'})
])


@app.callback(
    Output('course-output', 'children'),
    Output('submit-course', 'disabled'),
    Input('course-input', 'value')
)
def update_course_out(value):
    outlist = [html.H4("Skills from your course:")]
    if value:
        disabled = False
        skills, _ = skill_list(value)
        skills.sort()
        if skills:
            for skill in skills:
                outlist.append(html.P(skill))
    else:
        disabled = True
    return html.Div(outlist), disabled


@app.callback(
    Output('jobs-output', 'children'),
    Input('submit-course', 'n_clicks'),
    State('course-input', 'value')
)
def update_jobs_out(click, value):
    children = list()
    
    _, ids = skill_list(value)
    job_cat = predict_job(ids)
    children.append(html.H3("Job Category Predicted:"))
    children.append(html.H4(job_cat[0][1], style={
        "color": "#2186f4",
        "font-family": "Arial, Helvetica, sans-serif"}))
    children.append(html.H3("Top 10 jobs from category:"))
    
    jobs = get_job_list(ids, job_cat[0][1])
    children.append(dash_table.DataTable([{"id":i, "Job Title": title} for i, title in jobs.items()], id='tbl'))
    children.append(html.Div(id='tbl_out'))
    
    return dcc.Loading(children=children)

@app.callback(
    Output('tbl_out', 'children'), 
    Input('tbl', 'active_cell'),
    State('tbl', 'data')
)
def update_job_skills(active_cell, data):
    if active_cell:
        skills, title = get_job_skills(active_cell['row_id'])
        outlist = [html.H4(f"Skills from {title} (id: {active_cell['row_id']}): ")]
        skills.sort()
        if skills:
            for name in skills:
                outlist.append(html.P(name))
        return outlist 
    else: 
        return "Click the table"


if __name__ == '__main__':
    app.run_server(debug=True)