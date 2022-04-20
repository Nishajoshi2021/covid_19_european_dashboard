from django.http import HttpResponse
import datetime
from django.shortcuts import render
from django.http import JsonResponse
import urllib.request, json

import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression

import mysql.connector


def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

def display_map(request):

    return render(request, 'maps.html')
def getcountries(request):
    #countries = {"country_name": "ireland"},{"country_name": "germany"}
    import mysql.connector
    import datetime
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="covid_19"
    )

    countries = []
    mycusor = mydb.cursor()
    mycusor.execute("select distinct country_name from covid_19.covid_19_data;")
    myresult = mycusor.fetchall()
    for x in myresult:
        countries.append({"country_name": x[0]})
    #countries = tuple(countries)
    mydb.close()
    #print(countries)
    return JsonResponse(countries, safe=False)

def getcompareddata(request):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="covid_19"
    )

    country1 = request.GET.get('country1')
    print(country1)
    country2 = request.GET.get('country2')
    print(country2)
    casespermillion= request.GET.get('casespermillion')
    print(casespermillion)
    chartvariable = request.GET.get('chartvariable')
    print(chartvariable)

    country1_data = gettotalcountriesdata(mydb, country1, chartvariable)
    country2_data = gettotalcountriesdata(mydb, country2, chartvariable)
    if casespermillion=="true" and chartvariable!="stringency_index":
        mycusor = mydb.cursor()
        query = """select population_in_millions from covid_19.countries where country_name= %s"""
        mycusor.execute(query, (country1,))
        myresult = mycusor.fetchall()
        country1_population = myresult[0][0]
        mycusor.execute(query, (country2,))
        myresult = mycusor.fetchall()
        country2_population = myresult[0][0]
        for x in country1_data:
            x["total_cases"]= int(x["total_cases"]/country1_population)
        for x in country2_data:
            x["total_cases"]= int(x["total_cases"]/country2_population)
    #country3_data = gettotalcountriesdata(mydb, 'Germany', chartvariable)
    mydb.close()



    #all_data= [country1_data, country2_data, country3_data]
    all_data= [country1_data, country2_data]

    return JsonResponse(all_data, safe=False)


def gettotalcountriesdata(mydb, countryname, chartvariable):
    total_cases = []
    mycusor = mydb.cursor()
    query="""select date, {} from covid_19.covid_19_data where country_name= %s""".format(chartvariable)
    mycusor.execute(query, ( countryname,))
    myresult = mycusor.fetchall()


    for y in myresult:
        total_cases.append({"date": y[0], "total_cases": y[1]})
    return(total_cases)

def total_deaths_linear_regression(request):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="covid_19"
    )
    countryname = request.GET.get('country')

    query = """select date, stringency_index, new_cases, total_death from covid_19.covid_19_data where country_name= %s"""



    df_all=pd.read_sql(query, mydb, params=(countryname,))
    df = df_all[["date", "stringency_index", "new_cases", "total_death"]]
    df = df.replace(np.nan, 0)

    lr_total_deaths_dict={ "date": df_all["date"].tolist()}

    first_date_string = str(df_all.iloc[0]["date"])
    first_date = datetime.datetime.strptime(first_date_string, "%Y-%m-%d")
    date_list = []
    for row in df['date']:
        d1 = datetime.datetime.strptime(str(row), "%Y-%m-%d")
        # print(d1)
        date_list.append((d1 - first_date).days)



    df["date_day"] = pd.DataFrame(date_list)

    lr_total_deaths = df[["date_day", "stringency_index", "new_cases", "total_death"]]

    df_new = lr_total_deaths.iloc[0:550]

    x = df_new[["date_day", "stringency_index"]]
    y = df_new["total_death"]

    model = LinearRegression()
    model.fit(x, y)

    df_test = lr_total_deaths.iloc[477:]

    x_test = df_test[["date_day", "stringency_index"]]
    y_test = df_test["total_death"]

    y_predict_total_deaths_new = model.predict(x_test)
    print(type(y_predict_total_deaths_new))


    lr_total_deaths_dict['actual']= df["total_death"].tolist()

    y_list = y.tolist()
    y_predict_list = y_predict_total_deaths_new.astype(int).tolist()

    total_list_predicted=y_list + y_predict_list

    lr_total_deaths_dict['predicted'] = total_list_predicted

    mydb.close()

    return JsonResponse(lr_total_deaths_dict, safe=False)


def trends_data_analysis(request):
    countryname = request.GET.get('country')

    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        database="covid_19"
        # auth_plugin = 'root'
    )

    todays_date = datetime.datetime.today()
    old_date = datetime.timedelta(days=10)
    last_7_days = todays_date - old_date
    last_7_days.strftime('%Y-%m-%d')

    mycursor = mydb.cursor()
    sql = "select date, new_cases, new_death, new_vaccinations from covid_19.covid_19_data where country_name=%s and (date > %s)"
    val = (countryname, last_7_days)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    mydb.close()

    print(myresult)

    new_cases_7_days_list = []
    new_deaths_7_days_list = []
    new_vaccinations_7_days_list = []

    trends_data = {"date_7_days": [], "new_cases_trends": {}, "new_deaths_trends": {}, "new_vaccinations_trends": {}}
    for i in range(7):
        row = myresult[i]
        trends_data["date_7_days"].append(row[0].strftime('%Y-%m-%d'))
        new_cases_7_days_list.append(row[1])
        new_deaths_7_days_list.append(row[2])
        new_vaccinations_7_days_list.append(row[3])


    trends_data["new_cases_trends"]["7_days_data"] = new_cases_7_days_list
    trends_data["new_deaths_trends"]["7_days_data"] = new_deaths_7_days_list
    trends_data["new_vaccinations_trends"]["7_days_data"] = new_vaccinations_7_days_list

    # 7_day_average
    trends_data["new_cases_trends"]["7_days_average"] = int(sum(new_cases_7_days_list) / 7)
    trends_data["new_deaths_trends"]["7_days_average"] = int(sum(new_deaths_7_days_list) / 7)
    trends_data["new_vaccinations_trends"]["7_days_average"] = int(sum(new_vaccinations_7_days_list) / 7)

    # Yesterday_data
    trends_data["new_cases_trends"]["yesterdays_data"] = myresult[7][1]
    trends_data["new_deaths_trends"]["yesterdays_data"] = myresult[7][2]
    trends_data["new_vaccinations_trends"]["yesterdays_data"] = myresult[7][3]

    # more or less
    if trends_data["new_cases_trends"]["yesterdays_data"] > trends_data["new_cases_trends"]["7_days_average"]:
        trends_data["new_cases_trends"]["increase"] = "more"
    else:
        trends_data["new_cases_trends"]["increase"] = "less"

    if trends_data["new_deaths_trends"]["yesterdays_data"] > trends_data["new_deaths_trends"]["7_days_average"]:
        trends_data["new_deaths_trends"]["increase"] = "more"
    else:
        trends_data["new_deaths_trends"]["increase"] = "less"

    if trends_data["new_vaccinations_trends"]["yesterdays_data"] > trends_data["new_vaccinations_trends"][
        "7_days_average"]:
        trends_data["new_vaccinations_trends"]["increase"] = "more"
    else:
        trends_data["new_vaccinations_trends"]["increase"] = "less"

    # %
    try:
        trends_data["new_cases_trends"]["percentage_change_data"] = int((abs((myresult[7][1]) - trends_data["new_cases_trends"][
        "7_days_average"]) * 100) / (trends_data["new_cases_trends"]["7_days_average"]))
    except:
        trends_data["new_cases_trends"]["increase"] = "N/A"

    try:
        trends_data["new_deaths_trends"]["percentage_change_data"] = int((abs((myresult[7][2]) -
                                                                      trends_data["new_deaths_trends"][
                                                                          "7_days_average"]) * 100) / (
                                                                 trends_data["new_deaths_trends"]["7_days_average"]))
    except:
        trends_data["new_deaths_trends"]["increase"] ="N/A"

    try:
        trends_data["new_vaccinations_trends"]["percentage_change_data"] = int((abs((myresult[7][3]) -
                                                                            trends_data["new_vaccinations_trends"][
                                                                                "7_days_average"]) * 100) / (
                                                                       trends_data["new_vaccinations_trends"][
                                                                           "7_days_average"]))
    except:
        trends_data["new_vaccinations_trends"]["increase"] = "N/A"

    return JsonResponse(trends_data, safe=False)



def countries_map_data(request):
    full_map_data={}
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        database="covid_19"
        # auth_plugin = 'root'
    )

    mycursor = mydb.cursor()
    sql = "SELECT covid_19_data.country_name, max(total_cases) as total_cases, max(total_death) as total_deaths, latitude, longitude from countries,covid_19_data  where covid_19_data.country_name=countries.country_name group by country_name;"
    mycursor.execute(sql,)
    myresult = mycursor.fetchall()
    mydb.close()

    for row in myresult:
        country_map_data={}
        country_map_data["total_cases"] = row[1]
        country_map_data["total_deaths"] = row[2]
        country_map_data["coords"] = {"lat": row[3], "lng": row[4]}
        full_map_data[row[0]]= country_map_data

    return JsonResponse(full_map_data, safe=False)

def about_covid(request):
    return render(request, 'about.html')