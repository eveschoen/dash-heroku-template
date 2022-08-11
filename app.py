#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 13:15:18 2022

@author: eveschoenrock
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

markdown_txt = """
**GSS Description:** https://www.gss.norc.org/About-The-GSS
The General Social Survey (GSS) has been taking place for the last 50 years. It is a nationally representative survey of adults in the United States that monitors American opinions, attitudes, and behaviors by collecting information on participant demographics, behavior, attitudes, and opinions on special interest topics. Extensive research has been done to ensure that the GSS is of the highest quality, accurately representing the people of the United States. The GSS is extremely beneficial to researchers because it enables them to examine American society more closely, using data.
**Article 1:** https://www.forbes.com/sites/hollycorbett/2022/03/14/what-equal-pay-day-2022-data-is-and-is-not-telling-us/?sh=475ddd1b332b
Equal Pay Day, the day that marks how far into the new year a woman must work to earn what her male counterpart earned in the previous year, for 2022 fell on March 15, 8 days sooner than previous years. Although this looks like progress, there is a troubling story behind this perceived "closing" of the gender wage gap. 1.1 million women dropped from the labor force after the start of the COVID-19 pandemic, many of whom were low-paid workers that could not afford childcare during those trying times, ultimately causing the median earnings for women to rise. When these women are considered, the gender wage gap widens significantly - to almost 73 cents per every dollar a man earns. The gap is even wider for women of color. Over a lifetime of working, women can lose over a million dollars to the gender wage gap. This makes it harder for women to retire, forcing females into a state of dependency on the state or on men.
**Article 2:** https://www.census.gov/library/stories/2022/03/what-is-the-gender-wage-gap-in-your-state.html#:~:text=In%202020%2C%20women%20earned%2083,gap%20is%20narrowing%20but%20continues
"""

##table
tab = gss_clean.groupby('sex').agg({'income':'mean',
                                    'job_prestige':'mean',
                                    'socioeconomic_index':'mean',
                                    'education':'mean'}).round(2).reset_index()
tab_display = tab.rename({'sex':'Gender',
                          'income':'Income',
                          'job_prestige':'Job Prestige',
                          'socioeconomic_index':'Socioeconomic Status',
                          'education':'Years of Education'}, axis=1)
table = ff.create_table(tab_display)

##fig_bar
gss_clean['male_breadwinner'] = gss_clean['male_breadwinner'].astype('category')
gss_clean['male_breadwinner'] = gss_clean['male_breadwinner'].cat.reorder_categories(['strongly agree', 'agree', 'disagree', 'strongly disagree'])

tab = pd.crosstab(gss_clean.sex, gss_clean.male_breadwinner).reset_index()
tab = pd.melt(tab, id_vars='sex')

fig_bar = px.bar(tab, x='male_breadwinner', y='value', color='sex',
            labels={'value':'Count', 'male_breadwinner':'It is better for the man of the house to be the primary achiever.'},
            hover_data = ['value'],
            barmode = 'group')
fig_bar.update_layout(showlegend=True)
fig_bar.update(layout=dict(title=dict(x=0.5)))

##fig_scatter
fig_scatter = px.scatter(gss_clean, x='job_prestige', y='income', 
                 color = 'sex',
                 trendline = 'ols',
                 height=600, width=600,
                 labels={'job_prestige':'Job Prestige', 
                        'income':'Income ($)'},
                 hover_data=['education', 'socioeconomic_index'])
fig_scatter.update(layout=dict(title=dict(x=0.5)))

##fig_boxincome
fig_boxincome = px.box(gss_clean, x='income', y = 'sex', color = 'sex',
                   labels={'income':'Income ($)', 'sex':'Gender'})
fig_boxincome.update(layout=dict(title=dict(x=0.5)))
fig_boxincome.update_layout(showlegend=False)

##fig_boxprestige
fig_boxprestige = px.box(gss_clean, x='job_prestige', y = 'sex', color = 'sex',
                   labels={'job_prestige':'Job Prestige', 'sex':'Gender'})
fig_boxprestige.update(layout=dict(title=dict(x=0.5)))
fig_boxprestige.update_layout(showlegend=False)

gss_new = gss_clean[['income', 'sex', 'job_prestige']]

mi = min(gss_new['job_prestige'])
ma = max(gss_new['job_prestige'])

bi = (ma - mi)/6
bi1 = mi
bi2 = mi + bi * 1
bi3 = mi + bi * 2
bi4 = mi + bi * 3
bi5 = mi + bi * 4
bi6 = mi + bi * 5

gss_new['prestige_cut'] = pd.cut(gss_new['job_prestige'],
                        [bi1, bi2, bi3, bi4, bi5, bi6, 1000],
                        labels = [1, 2, 3, 4, 5, 6],
                        right=False)
gss_new = gss_new.dropna()

##fig_facet
fig_facet = px.box(gss_new, x='income', y = 'sex', color = 'sex',
             facet_col='prestige_cut',
             facet_col_wrap=2,
             color_discrete_map = {'male':'blue', 'female':'red'},
             labels={'income':'Income', 'sex':'Gender'},
             category_orders={'prestige_cut': [1,2,3,4,5,6]})
fig_facet.update(layout=dict(title=dict(x=0.5)))
fig_facet.for_each_annotation(lambda a: a.update(text=a.text.replace("prestige_cut=", "Prestige Category ")))

##dashboard
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = JupyterDash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.H1("Exploring the Gender Wage Gap"),
        dcc.Markdown(children = markdown_txt),
        
        html.H3("Comparing Men and Women in Society"),
        dcc.Graph(figure=table),
        
        html.H3("Preferring Male Breadwinners by Gender"),
        dcc.Graph(figure=fig_bar),
        
        html.H3("Income vs. Job Prestige by Gender"),
        dcc.Graph(figure=fig_scatter),
        
        html.Div([
            html.H4("Income by Gender"),
            dcc.Graph(figure=fig_boxincome)
        ], style = {'width':'48%', 'float':'left'}),
        
        html.Div([
            html.H4("Job Prestige by Gender"),
            dcc.Graph(figure=fig_boxprestige)
        ], style = {'width':'48%', 'float':'right'}),
        
        html.H3("Income by Sex across Job Prestige Category"),
        dcc.Graph(figure=fig_facet)
    ]
)

if __name__ == '__main__':
    app.run_server(mode='inline', debug=True, port=8055)
