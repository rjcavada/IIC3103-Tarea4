import requests
import gspread
import xml.etree.ElementTree as ET

countries = {"JAM": "Jamaica", "FRA": "France", "AUS": "Australia",
            "ISL":"Iceland", "DEU": "Germany", "CHL": "Chile"}

gc = gspread.service_account(filename='client-secret.json')

gho = ["Number of deaths", "Number of infant deaths", "Number of under-five deaths", "Mortality rate for 5-14 year-olds (probability of dying per 1000 children aged 5-14 years)", 
    "Adult mortality rate (probability of dying between 15 and 60 years per 1000 population)", "Estimates of number of homicides", "Crude suicide rates (per 100 000 population)", "Mortality rate attributed to unintentional poisoning (per 100 000 population)",
    "Number of deaths attributed to non-communicable diseases, by type of disease and sex", "Estimated road traffic death rate (per 100 000 population)", "Estimated number of road traffic deaths",
    "Mean BMI (kg/m&#xb2;) (crude estimate)", "Mean BMI (kg/m&#xb2;) (age-standardized estimate)", "Prevalence of obesity among adults, BMI &GreaterEqual; 30 (age-standardized estimate) (%)",
    "Prevalence of obesity among children and adolescents, BMI > +2 standard deviations above the median (crude estimate) (%)",
    "Prevalence of overweight among adults, BMI &GreaterEqual; 25 (age-standardized estimate) (%)",
    "Prevalence of overweight among children and adolescents, BMI > +1 standard deviations above the median (crude estimate) (%)",
    "Prevalence of underweight among adults, BMI < 18.5 (age-standardized estimate) (%)",
    "Prevalence of thinness among children and adolescents, BMI < -2 standard deviations below the median (crude estimate) (%)",
    "Alcohol, recorded per capita (15+) consumption (in litres of pure alcohol)", "Estimate of daily cigarette smoking prevalence (%)",
    "Estimate of daily tobacco smoking prevalence (%)", "Estimate of current cigarette smoking prevalence (%)", "Estimate of current tobacco smoking prevalence (%)",
    "Mean systolic blood pressure (crude estimate)", "Mean fasting blood glucose (mmol/l) (crude estimate)", "Mean Total Cholesterol (crude estimate)"]
traffic = ["Estimated number of road traffic deaths", "Estimated road traffic death rate (per 100 000 population)", "Mortality rate attributed to unintentional poisoning (per 100 000 population)", "Crude suicide rates (per 100 000 population)"]
indicadores = ["AGEGROUP", "COUNTRY", "GHECAUSES", "GHO", "SEX", "YEAR", "Display", "Numeric", "High", "Low"]
wks = gc.open("IIC3103-Tarea4").worksheet("Datos")
wks.format('A1:J1', {'textFormat': {'bold': True}})
for i in range(0,len(indicadores)):
    wks.update_cell(1,i+1,indicadores[i])
inicio = '2'
for country in countries:
    file = requests.get(f"http://tarea-4.2021-1.tallerdeintegracion.cl/gho_{country}.xml")
    root = ET.fromstring(file.text)
    guardar = []
    pob_list_rate = {}
    pob_list = {}
    poison = {}
    suicide = {}
    for child in root:
        for node in child:
            if node.tag == "GHO":
                if node.text in gho:
                    if node.text in traffic:
                        for tipo in child:
                            if tipo.tag == "YEAR":
                                año = tipo.text
                            if tipo.tag == "SEX":
                                sex = tipo.text
                            if tipo.tag == "Numeric":
                                valor = tipo.text
                        if node.text == "Estimated number of road traffic deaths":
                            pob_list[(año,sex)] = valor
                        if node.text == "Estimated road traffic death rate (per 100 000 population)":
                            pob_list_rate[(año,sex)] = valor
                        if node.text == "Mortality rate attributed to unintentional poisoning (per 100 000 population)":
                            poison[(año,sex)] = valor
                        if node.text == "Crude suicide rates (per 100 000 population)":
                            suicide[(año,sex)] = valor
                    fila = []
                    for parte in child:
                        if parte.tag in indicadores:
                            if parte.tag in ["Numeric", "High", "Low"]:
                                fila.append(float(parte.text))
                            else:
                                fila.append(parte.text)
                    guardar.append(fila)
    for keys in pob_list:
        divisor = float(pob_list_rate[keys])
        pob = (float(pob_list[keys]) * 100000)/divisor
        suicidios = (float(suicide[keys]) * pob)/100000
        venenos = (float(poison[keys]) * pob)/100000
        guardar.append(["", countries[country],"","Numero de suicidos",keys[1],keys[0],"",suicidios,"",""])
        guardar.append(["", countries[country],"","Numero de muertes por veneno",keys[1],keys[0],"",venenos,"",""])

    final = str(int(inicio) + len(guardar) - 1)
    rango = 'A' + inicio+ ':J' + final
    inicio = str(int(final) + 1)
    wks.update(rango,guardar)
