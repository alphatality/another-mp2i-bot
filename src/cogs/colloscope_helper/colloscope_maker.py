import csv
import datetime
import os

from fpdf import FPDF

ANNEE_SCOLAIRE = 2023  # année de la rentrée
COLLOSCOPE_PATH = "./data/colloscope.csv"  # path to the colloscope csv file


class ColleData:
    # This class contains the information of a single colle
    def __init__(self, groupe: str, matiere: str, prof: str, semaine: str, jourSemaine: str, heure: str, salle: str):
        self.groupe = groupe

        self.matiere = matiere
        self.prof = prof
        self.semaine = semaine
        self.jourSemaine = jourSemaine.lower()
        self.heure = heure
        self.salle = salle

        self.date = self.formatDate()
        self.dateLetters = self.formatDateLetters()

    def __str__(self):  # what this class return whene printed
        return f"Le {self.date}, passe le groupe {self.groupe} en {self.salle} avec {self.prof} à {self.heure}"

    def formatDate(self):
        jourSemaines = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]

        jourInt, moisInt = map(
            int, self.semaine.split("-")[0].split("/")
        )  # get the day and month of the first day of the week

        if int(moisInt) > 8:
            annee = ANNEE_SCOLAIRE
        else:
            annee = ANNEE_SCOLAIRE + 1

        jour = datetime.date(annee, moisInt, jourInt)

        delta_jour = datetime.timedelta(days=0)

        for j in enumerate(jourSemaines):
            if j[1] == self.jourSemaine:
                delta_jour = datetime.timedelta(days=j[0])
                break

        return (jour + delta_jour).strftime("%d/%m/%Y")

    def formatDateLetters(self):
        monthName = [
            "janvier",
            "fevrier",
            "mars",
            "avril",
            "mai",
            "juin",
            "juillet",
            "aout",
            "septembre",
            "octobre",
            "novembre",
            "decembre",
        ]
        date = self.date.split("/")

        return f" {self.jourSemaine} {date[0]} {monthName[ int(date[1])-1 ]}"  # date en toute lettre


def sortColles(ColleDatas, sortType="temps"):
    # sort the colleDatas by time
    def SortByTime(colleDatas):
        # return a score based on how far from the beginning of the year the colle is
        def getTimeValue(colle):
            return datetime.datetime.strptime(colle.date, "%d/%m/%Y").timestamp()

        return sorted(colleDatas, key=getTimeValue)

    def SortByProf(ColleDatas):
        def getProfValues(colle):
            return colle.prof

        return sorted(ColleDatas, key=getProfValues)

    def SortByGroupe(ColleDatas):
        return sorted(ColleDatas, key=lambda colle: colle.groupe)

    match sortType:
        case "temps":
            return SortByTime(ColleDatas)

        case "prof":
            return SortByProf(ColleDatas)

        case "groupe":
            return SortByGroupe(ColleDatas)

    Exception("Invalid sort type")


def getAllColles(filename):
    # returns a list of all the collesDatas by reading the csv file
    colles = []  # list of collesDatas

    with open(filename, encoding="utf-8", errors="ignore") as f:  # open file
        CsvReader = csv.reader(f, delimiter=",")  # CSV reader

        header = []  # header
        dataMatrix = []  # array of all the csv data | dataMatrix[y][x] to get the data
        for RowIndex, row in enumerate(CsvReader):  # iterate over each row
            if RowIndex == 0:  # get the first row
                header = row
            dataMatrix.append(row)

    for y in range(1, len(dataMatrix)):  # iterate over each colles rows
        matiere = dataMatrix[y][0]
        professeur = dataMatrix[y][1]
        jour = dataMatrix[y][2]
        heure = dataMatrix[y][3]
        salle = dataMatrix[y][4]

        for x in range(5, len(header)):  # iterate over each colles columns
            groupe = dataMatrix[y][x]
            semaine = dataMatrix[0][x]
            if groupe != "":
                colles.append(ColleData(groupe, matiere, professeur, semaine, jour, heure, salle))

    return colles


def getVacances(filename):
    """#### renvoie les dates de chaques vacances"""
    with open(filename, encoding="utf-8", errors="ignore") as Cfile:  # open file
        csvReader = csv.reader(Cfile, delimiter=",")  # CSV reader

        vacances = []  #
        for RowIndex, row in enumerate(csvReader):  # iterate over each row
            if RowIndex == 0:  # get the first row
                for i, week in enumerate(row):  # iterate over each column
                    if week.lower() == "vacances":
                        if row[i - 1] is None:
                            continue  # skip empty rows
                        semaine = ColleData("", "", "", row[i - 1], "lundi", "", "").formatDate()  # format date
                        vacances.append(addOneWeek(semaine))  # add vacances to list

    return vacances


def compareDates(date1, date2):
    """### takes in two dates of format dd/mm/yyyy
    #### True if date1 > date2 else False
    """
    date1 = list(map(int, date1.split("/")))
    date2 = list(map(int, date2.split("/")))
    convert1 = datetime.datetime(date1[2], date1[1], date1[0])
    convert2 = datetime.datetime(date2[2], date2[1], date2[0])
    return convert1 > convert2


def addOneWeek(time):
    """### Add one week
    #### Args :
        time : string dd/mm/yyyy
    """
    date1 = list(map(int, time.split("/")))
    convert1 = datetime.datetime(date1[2], date1[1], date1[0])
    convert1 = convert1 + datetime.timedelta(days=7)
    return convert1.strftime("%d/%m/%Y")


def convertHour(time):
    """Convertie l'heure francaises en heures anglaise
    Ex: 10h00 -> 10:00 AM
        18h00 -> 6:00 PM

    Args:
        heure (string): Ex: 18h00
    """

    temps = time.split("h")

    temps[1] = "00" if temps[1] == "" else temps[1]

    heure = int(temps[0])
    if heure >= 12:
        heure = heure - 12
        return str(heure) + f":{temps[1]} PM"
    else:
        return str(heure) + f":{temps[1]} AM"


def addOneHour(time):
    """Ajoute une heure à l'heure donnée (pas de colle a minuit donc flemme)

    Args:
        time (string): Ex: 10:00 AM
    """

    temps = time.split(":")
    heure = int(temps[0])
    if heure == 12:
        return f"1:{temps[1].split(' ')[0]} PM"
    else:
        return str(heure + 1) + f":{temps[1]}"


def exportColles(typeExport, collesDatas: ColleData, groupe: int, vacances: list):
    pathExport = f"./exports/groupe{groupe}"

    if os.path.exists(pathExport) == False:
        os.mkdir(pathExport)

    def simpleCSV(collesDatas: [ColleData]):
        # write the sorted data into a csv file
        with open(os.path.join(pathExport, f"ColloscopeGroupe{groupe}.csv"), "w", newline="") as Ofile:
            writer = csv.writer(Ofile, delimiter=",")
            writer.writerow(["date", "heure", "prof", "salle", "matière"])

            for colle in collesDatas:  # écris les données de colles dans un fichier
                data = [colle.date, colle.heure, colle.prof, colle.salle, colle.matiere]
                writer.writerow(data)

        return os.path.join(pathExport, f"ColloscopeGroupe{groupe}.csv")

    def agenda(collesDatas: [ColleData]):
        AgendaColle = []
        for colle in collesDatas:
            AgendaColle.append(
                {
                    "Subject": f"{colle.matiere} {colle.prof} {colle.salle}",
                    "Start Date": colle.date,
                    "Start Time": convertHour(colle.heure),
                    "End Date": colle.date,
                    "End Time": addOneHour(convertHour(colle.heure)),
                    "All Day Event": False,
                    "Description": f"Colle de {colle.matiere} avec {colle.prof} en {colle.salle} a {colle.heure}",
                    "Location": colle.salle,
                }
            )

        with open(os.path.join(pathExport, f"AgendaGroupe{groupe}.csv"), "w", newline="") as csvfile:
            fieldnames = [
                "Subject",
                "Start Date",
                "Start Time",
                "End Date",
                "End Time",
                "All Day Event",
                "Description",
                "Location",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for colle in AgendaColle:
                writer.writerow(colle)

    def todoist(collesDatas: [ColleData]):
        type, priority = "task", 2
        todoistColle = []
        for colle in collesDatas:
            todoistColle.append(
                {
                    "TYPE": type,
                    "CONTENT": f"Colle de {colle.matiere} avec {colle.prof}",
                    "DESCRIPTION": f"Salle {colle.salle}",
                    "PRIORITY": priority,
                    "INDENT": "",
                    "AUTHOR": "",
                    "RESPONSIBLE": "",
                    "DATE": colle.date + " " + colle.heure,
                    "DATE_LANG": "fr",
                    "TIMEZONE": "Europe/Paris",
                }
            )

        with open(os.path.join(pathExport, f"todoistGroupe{groupe}.csv"), "w", newline="") as csvfile:
            fieldnames = [
                "TYPE",
                "CONTENT",
                "DESCRIPTION",
                "PRIORITY",
                "INDENT",
                "AUTHOR",
                "RESPONSIBLE",
                "DATE",
                "DATE_LANG",
                "TIMEZONE",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for colle in todoistColle:
                writer.writerow(colle)

        return os.path.join(pathExport, f"todoistGroupe{groupe}.csv")

    def pdfExport(collesDatas: [ColleData], vacances: [str]):
        vacanceIndex = 0
        pdf = FPDF()
        pdf.add_page()
        page_width = pdf.w - 2 * pdf.l_margin

        pdf.set_font("Arial", "U", 14.0)
        pdf.cell(page_width, 0.0, f"Colloscope groupe {groupe}", align="C")
        pdf.ln(10)

        pdf.set_font("Arial", "", 11)

        col_width = page_width / 4

        pdf.ln(1)

        th = pdf.font_size + 2

        pdf.set_font("Arial", "B", 11.0)
        pdf.cell(10, th, txt="Id", border=1, align="C")
        pdf.cell(40, th, "Date", border=1, align="C")
        pdf.cell(20, th, "Heure", border=1, align="C")
        pdf.cell(col_width * 0.75, th, "Prof", border=1, align="C")
        pdf.cell(30, th, "Salle", border=1, align="C")
        pdf.cell(col_width, th, "Matiere", border=1, align="C")
        pdf.set_font("Arial", "", 11)
        pdf.ln(th)

        for i, colle in enumerate(collesDatas, 1):
            if vacanceIndex < len(vacances):  # fait un saut de ligne à chaque vacances
                if compareDates(colle.date, vacances[vacanceIndex]):
                    pdf.ln(th * 0.5)
                    pdf.set_font("Arial", "B", 14.0)
                    pdf.cell(90 + 2 * col_width, th, f"Vacances", align="C")
                    pdf.set_font("Arial", "", 11)
                    pdf.ln(th * 1.5)
                    vacanceIndex += 1
            pdf.cell(10, th, str(i), border=1, align="C")
            pdf.set_font("Arial", "", 9)
            pdf.cell(40, th, colle.dateLetters, border=1, align="C")
            pdf.set_font("Arial", "", 11)
            pdf.cell(20, th, colle.heure, border=1, align="C")
            pdf.cell(col_width * 0.75, th, colle.prof, border=1, align="C")
            pdf.cell(30, th, colle.salle, border=1, align="C")
            pdf.cell(col_width, th, colle.matiere, border=1, align="C")
            pdf.ln(th)

        pdf.ln(10)

        pdf.set_font("Times", "", 10.0)

        pdf.output(os.path.join(pathExport, f"ColloscopeGroupe{groupe}.pdf"), "F")

        return os.path.join(pathExport, f"ColloscopeGroupe{groupe}.pdf")

    match typeExport:
        case "csv":
            return simpleCSV(collesDatas)

        case "agenda":
            return agenda(collesDatas)

        case "pdf":
            return pdfExport(collesDatas, vacances)

        case "todoist":
            return todoist(collesDatas)

    Exception("Invalid sort type")


def getGroupRecentColleData(groupe):
    if groupe == "":
        return []

    colles = getAllColles(COLLOSCOPE_PATH)  # list of ColleData objects
    colles = sortColles(colles, sortType="temps")  # sort by time
    sortedColles = []
    currentDate = datetime.datetime.now() + datetime.timedelta(days=-1)  # date de la veille
    currentDate = currentDate.strftime("%d/%m/%Y")

    for data in colles:
        if data.groupe == groupe and compareDates(data.date, currentDate):
            sortedColles.append(data)
    return sortedColles


def main(userGroupe, typeExport="pdf"):
    colles = getAllColles(COLLOSCOPE_PATH)  # list of ColleData objects
    vacances = getVacances(COLLOSCOPE_PATH)
    colles = sortColles(colles, sortType="temps")  # sort by time

    sortedColles = []

    for data in colles:
        if data.groupe == userGroupe:
            sortedColles.append(data)

    try:
        groupe = sortedColles[0].groupe
    except IndexError:
        return "Aucune colle n'a été trouvé pour ce groupe"

    return exportColles(typeExport, sortedColles, groupe, vacances)
