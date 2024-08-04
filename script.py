import requests
from bs4 import BeautifulSoup
import csv
import re
import sys

teamName = input("What is the team Name ? \n")
Seasons = input("Which season matches do you want ? example(2023-24 2022-23) \n")

teamName = teamName.lower().strip().replace(' ' , '-')

seasonDate = Seasons.strip().split(' ')
numSeason = len(seasonDate)

# to use in the dictionary 
teamNameUsed = teamName.split('-')
teamNameUsed = [x.title() for x in teamNameUsed]
teamNameUsed = ' '.join(teamNameUsed)

outputFile = []


def scoresNameTime(text) :
    if text : 
        global finalPlayerNames 
        global finalMinutesGoals 
        timeGoals = []
        namesGoals = []
        results = []
        lines = text.split('\n')
        for line in lines:
            if line :

            # Extract the name
                playerName = re.match(r"([\w\sÀ-ÖØ-öø-ÿ]+)\s\(", line, re.UNICODE)
                playerName = playerName.group(1).strip() if playerName else ""
                            
                # getting the minutes
                minGoal = re.findall(r"\d+'?\d*(?:th|st|nd|rd)", line)
                cleaned_numbers = [re.sub(r'(th|st|nd|rd)', '', number.split("'")[1]) for number in minGoal]
                            
                # adding the names and minutes in the list
                namesGoals.append(f'({playerName})')
                timeGoals.extend(cleaned_numbers)

                # Format the final result
                result = f"[{playerName} ({'-'.join(cleaned_numbers)})]"
                results.append(result)

    # Join all results into a single line
        final_output = ' '.join(results).strip()
        finalPlayerNames = ' '.join(namesGoals)
        finalMinutesGoals = ' '.join(timeGoals)

        return final_output


for season in range(numSeason) : 
    try : 
        websiteContent = requests.get(f'https://www.skysports.com/{teamName}-results/{seasonDate[season]}').content 
    except ConnectionError : 
        print("There is a connection Error")
        
    soup = BeautifulSoup(websiteContent , 'lxml')

    def main(page) : 
        counter = 0 
        mainContent = page.find('div' , {'class' : 'site-wrapper'}).find('div' , {'class' : 'grid'}).find('div' , {'class' : 'site-layout-primary__col1'}).find('div' , {'class' : 'site-layout-secondary'}).find('div' , {'class' : 'grid__col site-layout-secondary__col1'})
        try :
            fixersBody = mainContent.find('div' , {'class' : 'fixres'}).find('div' , {'class' : 'fixres__body'})
        except AttributeError : 
            print('Wrong Input team name or the season')
            sys.exit()
        # print(mainContent)

        dateMatches = fixersBody.find_all('h4' , {'class' : 'fixres__header2'})
        championeName = fixersBody.find_all('h5' , {'class' : 'fixres__header3'})
        matcheDeatils = fixersBody.find_all('div' , {'class' : 'fixres__item'})

        matchNum = len(dateMatches)
        for match in range(matchNum -1, -1 , -1) : 
            ## match deatils : 
            #getting the link of the match info 
            linkDetails = matcheDeatils[match].find('a')['href']
            # Getting the info of the match date stadium attendance goals and all of that using its link
            try : 
                infoMatch = requests.get(f'{linkDetails}').content
            except EnvironmentError : 
                print("There is an error getting the info of match")
            
            #soup Match All Deatils 
            soupMatch = BeautifulSoup(infoMatch , 'lxml')
            allDeatilsContent = soupMatch.find('div' , {'class' : 'sdc-site-match-header'}).find('div' , {'class' : 'sdc-site-match-header__wrapper'}).find('div' , {'class' : 'sdc-site-match-header__body'})
            
            #match Status like Full time or live 
            matchStatus = allDeatilsContent.find('div' , {'class' : 'sdc-site-match-header__status'}).find('span' , {'class' : 'sdc-site-match-header__match-status--ft'}).find_all('span')[1].text
            
            # match details like who is playing and time and attende number
            matchPTHA = allDeatilsContent.find('div' , {'class' : 'sdc-site-match-header__detail'})

            #match header 
            matchHeader = matchPTHA.find('p' , {'class' : 'sdc-site-match-header__detail-fixture'}).text
            matchHeaderPlay = matchHeader.split('.')[1].strip()

            #match Date and Time
            matchDateTime = allDeatilsContent.find_all('p')[1].text.strip().split(', ')
            matchTime = matchDateTime[0]
            matchDate = matchDateTime[1]

            # stadium name and number of attendes
            matchStadiumAttnede = allDeatilsContent.find_all('p')[3].find_all('span')

            if not matchStadiumAttnede : 
                allDeatilsContent.find_all('p')[2].find_all('span')
            matchStadium = matchStadiumAttnede[0].text
            try : 
                matchAttnede = matchStadiumAttnede[1].text.split('Attendance')[2].split('.')[0]
            except IndexError:
                matchAttnede = '0'

            #Match Teams and Score 
            HomeTeam = matcheDeatils[match].find('a' , {'class' : 'matches__item'}).find('span' , {'class' : 'matches__participant--side1'}).get_text().strip()
            matchScoreContent = matcheDeatils[match].find('a' , {'class' : 'matches__item'}).find('span' , {'class' : 'matches__status'}).find('span' , {'class' : 'matches__teamscores'}).find_all('span' , {'class' : 'matches__teamscores-side'})
            AwayTeam = matcheDeatils[match].find('a' , {'class' : 'matches__item'}).find('span' , {'class' : 'matches__participant--side2'}).get_text().strip()
            goalNumHomeTeam = matchScoreContent[0].contents[0].get_text().strip()
            goalNumAwayTeam = matchScoreContent[1].contents[0].get_text().strip()
            matchScore = f"{goalNumHomeTeam}-{goalNumAwayTeam}"
            MainTeamPlace = "Home" if HomeTeam == teamNameUsed else "Away"

            print(HomeTeam , teamNameUsed)
            #match goals time and How scores it :
            matchGoalsTime = allDeatilsContent.find('div' , {'class' : 'sdc-site-match-header__content'}).find('div' , {'class' : 'sdc-site-match-header__content-inner'}).find('div' , {'class' : 'sdc-site-match-header__teams'}).find_all('ul' , {'class' : 'sdc-site-match-header__team-synopsis'})

            #defineing main global variables
            HomeGoalsText , AwayGoalsText  , HomeTimesText , AwayTimesText= 'No Goals' , 'No Goals' , 'No Goals' , 'No Goals'

            #teams text to use it in the function 
            HomeScoresTime = matchGoalsTime[0].get_text().replace('minute' , '').strip('')

            AwayScoresTime = matchGoalsTime[1].get_text().replace('minute' , '').strip('')

            #home score name and times
            HomeGoalsTimeNames = scoresNameTime(HomeScoresTime) 
            if HomeGoalsTimeNames : 
                HomeGoalsText = finalPlayerNames
                HomeTimesText = finalMinutesGoals

            if not HomeGoalsTimeNames : 
                HomeGoalsTimeNames = 'No Goals'

            #away score name and times
            AwayGoalsTimeNames = scoresNameTime(AwayScoresTime)
            if AwayGoalsTimeNames :
                AwayGoalsText = finalPlayerNames
                AwayTimesText = finalMinutesGoals

            if not HomeGoalsTimeNames : 
                AwayGoalsTimeNames = 'No Goals'

            # outfile info 
            outputFile.append({
                "Match Header" : matchHeaderPlay , 
                "Match Time" : matchTime , 
                "Match Date" : matchDate , 
                "Stadium Name" : matchStadium , 
                "Number of Attendences" : matchAttnede ,
                "Season Number" : seasonDate[season] ,
                "Match Date" : dateMatches[match].get_text() ,
                "Champion Name" : championeName[match].get_text() , 
                "Home Team" : HomeTeam ,
                "Away Team" : AwayTeam , 
                "Score" : matchScore ,
                "For Team" : MainTeamPlace ,
                "Match Status" : matchStatus ,
                "Main Team Player Names With Time" : HomeGoalsTimeNames if MainTeamPlace == 'Home' else AwayGoalsTimeNames ,
                "Main Team Player Scored" : HomeGoalsText if MainTeamPlace == 'Home' else AwayGoalsText,
                "Main Team Goals Minutes" : HomeTimesText if MainTeamPlace == 'Home' else AwayGoalsText,
                "Opponet Team Player Names with Time" : AwayGoalsTimeNames if MainTeamPlace == 'Home' else HomeGoalsTimeNames ,
                "Opponet Team Player Scored" : AwayGoalsText if MainTeamPlace == 'Home' else HomeGoalsText,
                "opponet Team Goals MInutes" : AwayTimesText if MainTeamPlace == 'Home' else HomeTimesText 
            })

    main(soup)

keys = outputFile[0].keys()

filepath = 'E:\engenrring Hema\Data Engineeing\python\web scraping\skysportsMatches\matcheDeatilsAllSeasons.csv'
with open( filepath, 'w') as outFile : 
    dictWriter = csv.DictWriter(outFile , keys)
    dictWriter.writerows(outputFile)
    print("file Created")


