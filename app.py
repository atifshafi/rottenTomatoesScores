import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from numpy import median


def verify_year(year):
    while True:
        if year.isdigit() is True:
            return year
        else:
            print("Please enter numeric values of the year and"
                  " don't use any spaces\n")
            year = input("\n")


def set_year():
    start_year = verify_year(input("Beginning Year?\n"))
    end_year = verify_year(input("Ending Year?\n"))
    while True:
        if start_year > end_year:
            print("Ending year can't be earlier than beginning year")
            end_year = verify_year(input("Ending Year?\n"))
        else:
            break

    return int(start_year), int(end_year)


def movie_endpoints(start_year, end_year):
    endpoints = []
    names = []
    for year in range(end_year-start_year + 1):
        print(year)
        result = requests.get("https://www.rottentomatoes.com/top/bestofrt/?year=" +
                              str(start_year + year))

        src = result.content

        soup = BeautifulSoup(src, features="html.parser")

        for link in soup.find_all("table"):
            if link.attrs['class'][0] == 'table':
                for link in link.find_all("a"):
                    endpoints.append(link.attrs['href'])
                    tmp_list = []
                    tmp_list.append(link.text.lstrip())
                    names.append(tmp_list)

        print(names)
    return endpoints, names


def scores(endpoints, names):
    for i in range(len(endpoints)):
        result = requests.get("https://www.rottentomatoes.com/" +
                              endpoints[i])
        src = result.content
        soup = BeautifulSoup(src, features="html.parser")

        # Scraping scores from web
        for link in soup.find_all("span"):
            try:
                if link.attrs['class'][0] == 'mop-ratings-wrap__percentage':
                    #print(link.text)
                    names[i].append(re.sub("[^0-9]", "", link.text))
            except:
                pass

        # Removing any movie from the list which doesn't have any audiance score
        try:
            if len(names[i]) < 3:
                del names[i]
                continue
        except:
            break

        # Calculating total score
        names[i].append(int(names[i][1]) + int(names[i][2]))
        print(names[i])
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


start, end = set_year()
scores(movie_endpoints(start, end)[0],
       movie_endpoints(start, end)[1])