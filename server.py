'''
This is the core of the server's functionality, that handles the webpage requests, and
responds appropriately. It also handles the data submission for building games on
the website.

@AUTHORS	Thomas Pryor, Taylor Hall, Curtis Duval, Joshua Wilkins, Nathan Wilkins
@DATE		April 7, 2019
@INFO		CODEFEST 2019 COMPETITION CODE
'''


import smtplib
import json
from flask import Flask, redirect, url_for, request, render_template, send_from_directory



# This creates the web application object, for handling all client communication
app = Flask(__name__)



# create the server response for gameplay, loading the text, and the choices
@app.route('/game/')
def load_game_page():
	params =  request.args.to_dict()
	f = open(params['gamename'])
	data = json.load(f)
	f.close()
	choices = [] # list of dicts, with the dicts holding the text and the link
	# loop through all the choices ascociated with the current scenario,
	# and format them to submit to the template file for rendering
	if (len(data[params['scenarioname']]['choices']) > 0):
		for choice in data[params['scenarioname']]['choices']:
			linkaddr = "/game/?gamename=" + params['gamename'] + "&scenarioname=" + data[choice]['destinationScenario']
			tempdict = {data[choice]['content']:linkaddr}
			choices.append(tempdict)
		print (choices)
	return render_template('/game.html', scene = data[params['scenarioname']]['image'], scenario = data[params['scenarioname']]['content'],choices = choices,gamename = params['gamename'])



# render a webpage with a list of available games
@app.route('/gameslist')
def load_games_list_page():
	f = open('gameslist.json')
	data = json.load(f)
	f.close()
	games = []
	# loop through the list of games, removing the ".json", and listing
	# them with the link to the initial page
	for game in data['games']:
		for name, link in game.items():
			games.append({name[:-5]:link})
	return render_template('/gameslist.html', games=games)



# respond to requests for the build game form, and adding content to a game
@app.route('/make_game', methods=["POST", "GET"])
@app.route('/form', methods=["POST", "GET"])
def game_form():
	# This is the initial request for the making game page
	if (request.method == "GET"):
		return render_template("/form.html")
	# they have submitted some data, so store it and move them
	# to the appropriate page depending on if they pressed submit
	# or end.
	elif(request.method == "POST"):
		gamename = request.form['Game name']+'.json'
		gamename2 = request.form['Game name']
		# load all the submission data into easily addressable variables
		scenarioname = request.form['Scenario name']
		scenariocontent = request.form['Scenario']
		choice1content = request.form['Choice 1']
		choice1destination = request.form['Choice 1 Destination']
		choice2content = request.form['Choice 2']
		choice2destination = request.form['Choice 2 Destination']
		choice3content = request.form['Choice 3']
		choice3destination = request.form['Choice 3 Destination']
		scenario1 = ""
		# check to see if the game that is being created has a name that already exists
		f = open('gameslist.json','r')
		data = json.load(f)
		f.close()
		gamenames = []
		for game in data['games']:
			for key, value in game.items():
				gamenames.append(key)
		if gamename in gamenames:
			return render_template("/taken.html")
		try: # If successful, the file already exists. Add the new game data to existing game data
			f = open(gamename,'r')
			f.close()
			f = open(gamename)
			data = json.load(f)
			f.close()
			scenario1 = data['game']['scenarios'][0]
			print('The file already existed')
			if (len(scenarioname)>0):
				if (len(scenariocontent)>0):
					choices = []
					if (len(choice1content)>0 and len(choice1destination)>0):
						choice1 = {'content':choice1content, 'destinationScenario':choice1destination}
						choices.append('choice1_' + scenarioname)
						data.update({'choice1_' + scenarioname : choice1})
					if (len(choice2content)>0 and len(choice2destination)>0):
						choice2 = {'content':choice2content, 'destinationScenario':choice2destination}
						choices.append('choice2_' + scenarioname)
						data.update({'choice2_' + scenarioname : choice2})
					if (len(choice3content)>0 and len(choice3destination)>0):
						choice3 = {'content':choice3content, 'destinationScenario':choice3destination}
						choices.append('choice3_' + scenarioname)
						data.update({'choice3_' + scenarioname : choice3})
					scenario = {'content' : scenariocontent, 'image' : "" ,'choices' : choices}
					data.update({scenarioname:scenario})
					data['game']['scenarios'].append(scenarioname)
			f = open(gamename,'w')
			json.dump(data,f)
			f.close()
		except FileNotFoundError: # Else the file is not found. Save the data to a new file, identified by the game name.
			print('Had to create the file')
			data = {}
			scenarios = [scenarioname]
			data.update({'game':{'scenarios':scenarios}})
			scenario1 = scenarioname
			if (len(scenarioname)>0):
				if (len(scenariocontent)>0):
					choices = []
					if (len(choice1content)>0 and len(choice1destination)>0):
						choice1 = {'content':choice1content, 'destinationScenario':choice1destination}
						choices.append('choice1_' + scenarioname)
						data.update({'choice1_' + scenarioname : choice1})
					if (len(choice2content)>0 and len(choice2destination)>0):
						choice2 = {'content':choice2content, 'destinationScenario':choice2destination}
						choices.append('choice2_' + scenarioname)
						data.update({'choice2_' + scenarioname : choice2})
					if (len(choice3content)>0 and len(choice3destination)>0):
						choice3 = {'content':choice3content, 'destinationScenario':choice3destination}
						choices.append('choice3_' + scenarioname)
						data.update({'choice3_' + scenarioname : choice3})
					scenario = {'content' : scenariocontent, 'image' : "" ,'choices' : choices}
					data.update({scenarioname:scenario})
			f = open(gamename, 'w')
			json.dump(data,f)
			f.close()
		# respond based on if the user pressed the submit button,
		# or the end button, the latter of which finalizes the
		# writing of the game.
		if 'end' in request.form:
			f = open('gameslist.json')
			data = json.load(f)
			f.close()
			data['games'].append({gamename:"/game/?gamename=" + gamename + "&scenarioname=" + scenario1})
			f = open('gameslist.json','w')
			json.dump(data, f)
			f.close()
			return render_template("/index.html")
		else:
			return render_template("/form.html", game_name = gamename2)



# send static data to the client
@app.route('/static/<path:path>')
def send_static(path):
	return send_from_directory('static', path)



# send the website icon to the client
@app.route('/favicon.ico')
def send_icon():
	return send_from_directory('/','favicon.ico')



# send the index page to the client
@app.route('/index')
@app.route('/')
def index_click():
	return render_template("/index.html")

@app.route('/send_email', methods=["POST", "GET"])
def send_mail():
	if (request.method == "GET"):
		return render_template("/index.html")
	# they have submitted some data, so store it and move them
	# to the appropriate page depending on if they pressed submit
	# or end.
	elif(request.method == "POST"):
		SUBJECT = 'Come and Experience the Choices!'
		TEXT = 'There is a brand new make your own adventure game!\nThe Choices We Make is now LIVE! Come play it in the following link http://192.168.193.243:5000'
		content = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
		mail = smtplib.SMTP('smtp.gmail.com', 587)
		mail.ehlo()

		mail.starttls()
		#mail.login('email','password')
		mail.login('TheChoicesWeMakeGame@gmail.com','WhereDidYouGoSempai123')

		mail.sendmail('TheChoicesWeMakeGame@gmail.com', request.form['destination mail'] , content)
		mail.close()
		return render_template("/index.html")
	
if __name__ == '__main__':
	app.run('0.0.0.0', debug=True)
