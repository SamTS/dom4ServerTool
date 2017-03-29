from subprocess import call
from subprocess import check_output as cliGet
import shlex, subprocess
import re
import random
import math
import copy

#TODO test

#Functions for various parts of the process

#helper function for checking if user wants yes or no, defaults to no
def pYesNo(text):
	print("\n")
	answer = raw_input(text+" (Y/N): ")
	return answer.upper() == "Y" or answer.upper() == "YES"


#processes CSVs gotten from raw input turns numbers from strings to ints and takes out spaces
def proccessCSVs(text, validationValues=[], isInts=False):
	print("\n")
	inputValues = raw_input(text)
	outputList = []
	#turn values into ints and strip out white space, otherwise just strip out white space
	if isInts:
		outputList = [int(x.strip()) for x in  inputValues.split(",") if x.strip() != ""]
	else:
		outputList = [x.strip() for x in inputValues.split(",") if x.strip != ""]

	#check if values exist in validationValues list, unless list is empty
	if validationValues != []:
		outputList = [x for x in outputList if x in validationValues ]

	return outputList
	

#this function allows a user to choose AI
#current properties are [dom4 path,era]
def chooseAi(props):
	dom4 = props[0]
	era = props[1]


	#run cli command to get list of all nations 
	nationRaw = cliGet([dom4, "--listnations"])

	#find all of the nations of a certain type
	nations = re.findall('-----\sEra\s'+era+'\s-----[^-]*' ,nationRaw)

	eraNations = " ".join(nations)

	#make regex object, this makes a list with tuples withere the first gropu is first touple value (nation number) and second is nation naem
	nationList = re.findall('(\d+)\s*([^-\n]*)\n',eraNations)

	#nation list also keeps track of civiliations that CAN be added (so as civiliations get added they get revmoved from nationList
	nationList = [ [int(n[0]), n[1]]  for n in nationList]

	nationTotalList = copy.copy(nationList)
	
	#difficulty List
	diffList = ["easyai","normai","diffai","mightyai","masterai","impai"]

	#generate dictioanry that has ta list of all the ais that will be at each difficulty level
	aiDict = {aiLvl : [] for aiLvl in diffList}

	#loop through to find out how many of each type of AI we want for the game, also whether random or choosen

	loopMe = pYesNo("Would you like to add some AI?")
	while loopMe:
		print "\nChoose an AI Level (in order of difficulty)"
		for i in range(len(diffList)):
			print str(i+1) + " " + diffList[i]	
	
		#find ai level from list
		aiLvl = diffList[int(raw_input("choose level: "))-1]

		#list of ais for this dificults level
		aiList = []
		rAi = pYesNo("Would you like to assign AI civs  at random?")

		#if random add a nation at random
		if rAi:
			aiNumber = int(raw_input("choose number of AI at this level: ").strip())
			for i in range(aiNumber):
				aiNum = int(math.floor(random.random()*len(nationList)))	
				aiList.append(nationList.pop(aiNum)[0])	
		else:
			print "choose from the AI Below:"
			for nation in nationList:
				print str(nation[0]) +" "+ nation[1]

					
			#get list of ai choices from user
			aiList = proccessCSVs( "Enter a comma seperated list of AI: " ,[int(n[0]) for n in nationList],True)
			
			#remove choosen nations from nation list
			nationList = [n for n in nationList if n[0] not in aiList]

		print "\n"+aiLvl+" will have these civilizaitons added:"
		for nation in nationTotalList:
			if nation[0] in aiList:
				print str(nation[0]) +" "+nation[1]

		stayAi = pYesNo("Are these nations acceptable, no lets you reselect them." )
	

		#assuming most time a user wants to not add ai they want to add more again
		if stayAi:
			aiDict[aiLvl] = aiDict[aiLvl] + aiList			
			loopMe = pYesNo("Would you like to add more AI?")

 	#finally put the ai civs in the proper CLI command format eg : --normai 9 --diffai 86	
	aiMegaCmd = ""
	for aiType, aiCivs in aiDict.iteritems():
	#list thing should take each civ for each ai level and append it's ai type to it then turns the whole thing into a string it appends to aiMegaLIst
		aiMegaCmd += " "+" ".join(["--"+aiType+" "+str(civ) for civ in aiCivs ])

	return aiMegaCmd
	

#chooses all mods
#current properties are [dom4 path]
def chooseMods(props):
	modDir = "/home/ubuntu/dominions4/mods"

	chooseMod = pYesNo("Do you want to add any mod?")
	if not chooseMod:
		return ""
		
	mods = cliGet(["ls",modDir])
	modList = shlex.split(mods)
	modList = [x for x  in modList if x != "ExpandedMods"]

	loopMe = True
	while loopMe:
		print "\nChoose Mods to use"
		for i in range(len(modList)):
			print str(i+1) +" "+modList[i]
	
		#make sure choose a value in length of modList and turns it into integers
		modChoice = proccessCSVs("Choose mod number in comma seperated list: ",range(1,len(modList)+1),True)
	
		selectedMods = [modList[sm-1] for sm in modChoice]

		print "Selected Mods are: "+" ".join(selectedMods)

		loopMe = not pYesNo("Are you satisfied with choosen mods?")


	modMegaCmd = " ".join(["--enablemod "+mod for mod in selectedMods])
	return modMegaCmd
	

#For chooinsg a made map or creating a random map
def chooseMap(props):
	fileMap = pYesNo("Would you like to select a map from file??")
	mapCmd = ""
	if not fileMap:
		advanced = pYesNo("do you want advanced map setup?")
		if advanced:
			loopMe = True
			while loopMe:
				waterPart = proccessCSVs("Enter River amount and sea level height, dfeault is 50,30: ",[],True)
				wpCmds = ["seapart","mountpart"]
				#set defaults
				if len(waterPart) != len(wpCmds):
					waterPart  = [50,30]
			
				percentPart = proccessCSVs("Enter percent of map that is mountains (20), forests (20), farm lands (15), wastes(10), swamps(10), caves(3): ",[],True)
				ppCmds = ["mountpart","forestpart","farmpart","wastepart","swamppart","cavepart"]
				#set defaults
				if len(percentPart) != len(ppCmds):
					percentPart = [20,20,15,10,10,3]
				
				NSwrapping =  pYesNo("Do you want north/south wrapping?") 
				EWwrapping = pYesNo("Do you want east/west wrapping?")
			
				#create map command as it is so far
				parts = waterPart + percentPart
				typeCmds = wpCmds + ppCmds
				cmds = []
				for i in range(len(typeCmds)):
					cmds.append("--" + typeCmds[i] + " " + str(parts[i]))
				
				mapCmd = " ".join(cmds)
				
				if NSwrapping:
					mapCmd += " --vwrap "
				if not EWwrapping:
					mapCmd += " --nohwrap " 			

	
				tPP =  pYesNo("Do you want to choose tiles per person? (No chooses total tiles)")
			
				if tPP:
					regionsPP = raw_input("choose how many tiles per player, (10,15,20): ")
					mapCmd += " --randmap "+regionsPP
				else:
					regions = raw_input("choose how many tiles for the entire map, recomended 10-20 per player: ")
					mapCmd += " --mapprov "+regions
				print "Current map settings are : "+ mapCmd
				loopMe = not pYesNo("Are you happy with these settings?")
		else:			
			regionsPP = raw_input("choose how many tiles per player, (10,15,20)")
			mapCmd = "--randmap "+regionsPP
	else:
		#finds all the maps in main and custom map directories and lists them and lets you choose one
		mainMapsDir = "/home/ubuntu/.local/share/Steam/steamapps/common/Dominions4/maps"
		customMapDir = "/home/ubuntu/dominions4/maps"
		mainMaps = shlex.split(cliGet(["ls",mainMapsDir]))
		customMaps = shlex.split(cliGet(["ls",customMapDir]))
		allMaps = mainMaps + customMaps
		
		loopMe = True
		while loopMe:
			print "\nChoose Map to use:"
			for i in range(len(allMaps)):
				print str(i+1) + " " + allMaps[i]

			mapChoice = int(raw_input("Choose Map Number to Use: ")) - 1
			
			loopMe = not pYesNo("You choose: "+allMaps[mapChoice]+" Is this correct?")


		mapCmd =  "--mapfile " + allMaps[mapChoice]

	return mapCmd



		
		


#define the dom 4 location
dom4= "/home/ubuntu/.local/share/Steam/steamapps/common/Dominions4/dom4.sh"


#get era

era = raw_input("what era do you want?  ")

ai = chooseAi([dom4,era])

mods = chooseMods([dom4])

domMap = chooseMap([dom4])

portNumber = raw_input("what port number? (1024-5000-ish) ")

gameName = raw_input("what do you want the game called? ")


rawCmd = dom4+" -S -T -n "+ ai+" "+mods+" "+domMap+" --port "+portNumber+" --era "+era+" "+gameName

#this slipts up the command into an array so it can be used by python call command
call(shlex.split(rawCmd))

