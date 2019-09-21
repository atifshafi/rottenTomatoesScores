import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from numpy import median


def movie_endpoints():
    result = requests.get("https://www.rottentomatoes.com/top/bestofrt/")

    src = result.content

    soup = BeautifulSoup(src, features="html.parser")

    endpoints = []
    names = []

    for link in soup.find_all("table"):
        if link.attrs['class'][0] == 'table':
            for link in link.find_all("a"):
                endpoints.append(link.attrs['href'])
                tmp_list = []
                tmp_list.append(link.text.lstrip())
                names.append(tmp_list)

    return endpoints, names


def scores(endpoints, names):
    for i in range(len(endpoints)):

        result = requests.get("https://www.rottentomatoes.com/" + endpoints[i])
        src = result.content

        soup = BeautifulSoup(src, features="html.parser")

        # Scraping scores from web
        for link in soup.find_all("span"):
            try:
                if link.attrs['class'][0] == 'mop-ratings-wrap__percentage':
                    names[i].append(re.sub("[^0-9]", "", link.text))
            except:
                pass

        # Calculating total score
        names[i].append(int(names[i][1]) + int(names[i][2]))

        # Scraping more info of the film from web
        for link in soup.find_all("div"):
            try:
                if link.attrs['class'][0] == 'meta-value':
                    names[i].append(' '.join(link.text.strip().split()))
            except:
                pass

    # Creating a csv file
    df = pd.DataFrame(names, columns=['movie_name', 'critic_score', 'audiance_score',
                                      'total_score', 'Rating', 'Genre', 'Directed By',
                                      'Written BY', 'In Theaters', 'On Disc/Streaming',
                                      'Box Office', 'Runtime', 'Studio'])
    df.to_csv("output.csv", index=False, header=None)

    # Plotting a scatter diagram
    fig = px.scatter(df, x="critic_score", y="audiance_score", hover_name="movie_name",
                     hover_data=["Rating", "Genre", "Directed By", "Written BY", "In Theaters",
                                 "On Disc/Streaming", "Box Office", "Runtime", "Studio"],
                     color="total_score", color_continuous_scale=px.colors.sequential.Viridis,
                     render_mode="webgl")

    # Adding median to the graph
    median_y = median([int(names[i][1]) for i in range(len(names))])
    median_x = median([int(names[i][2]) for i in range(len(names))])

    low_x = min([int(names[i][1]) for i in range(len(names))])
    low_y = min([int(names[i][2]) for i in range(len(names))])

    fig.add_trace(go.Line(x=[low_x-0.5, 100.5], y=[median_x, median_x]))
    fig.add_trace(go.Line(x=[median_y, median_y], y=[low_y-0.5, 100.5]))

    fig.update_layout(showlegend=False)
    fig.update_traces(marker=dict(size=10,
                                  line=dict(width=1,
                                            color='DarkSlateGrey')),
                      selector=dict(mode='markers'))
    fig.show()


movie_endpoints()
scores(movie_endpoints()[0], movie_endpoints()[1])