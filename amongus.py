import random, functools
import sys, os

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

KILL_SUSPECT=1
WIN_POINT=5

class Player:
  id=0
  suspect=0 # suspectfullness
  # Strategy
  pr_attack=0 # probability of attacking
  pr_defend=0 # probability of giving a good defense
  # Voting
  th_voting=0 # suspect threshold to vote
  turn_votes=0
  # Class
  impostor=0
  # Scoring
  kills=0
  turns=0
  def __init__(self, impostor, id):
    self.id=id
    self.pr_attack=random.randrange(0,10,1)
    self.pr_defend=random.randrange(0,10,1)
    self.th_voting=random.randrange(0,10,1)
    self.impostor=impostor
  
  def sus(self, susness):
    self.suspect += susness
  
  def vote(self):
    self.turn_votes+=1
  
  def turn(self):
    self.turn_votes=0
    self.turns+=1
  
  def kill(self, susp=1):
    self.kills+=1
    if susp == 1:
      self.suspect+=KILL_SUSPECT
  
  def mutate(self):
    rand = random.randrange(1, 6, 1)
    if rand==1:
      self.pr_attack += 1
    elif rand ==2:
      self.pr_attack -= 1
    elif rand==3:
      self.pr_defend += 1
    elif rand ==4:
      self.pr_defend -= 1
    elif rand ==5:
      self.th_voting += 1
    elif rand ==6:
      self.th_voting -= 1




class Game:
  players=list()
  def __init__(self,players):
    self.players = players
  
  def __get_impostors(self):
    filtered = filter(lambda x: x.impostor == 1, self.players)
    return list(filtered)
  
  def __get_spacemen(self):
    filtered = filter(lambda x: x.impostor != 1, self.players)
    return list(filtered)
  
  def __most_sus(self, imp=0):
    if imp == 1:
      players = self.__get_spacemen() 
    else:
      players = self.players 
    
    random.shuffle(players) #avoid taking always the first when all equals
    sus = functools.reduce(lambda a,b: a if a.suspect > b.suspect else b, players)
    return sus
  
  def __most_voted(self):
    vot = functools.reduce(lambda a,b: a if a.turn_votes > b.turn_votes else b, self.players)
    return vot

  def kill_spaceman(self):
    spaceman = random.choices(self.__get_spacemen())
    spaceman = spaceman[0]
    self.players.remove(spaceman)
    for imp in self.__get_impostors():
      imp.kill()
    print("Player "+str(spaceman.id)+" was killed")

  
  def discussing(self):
    players = self.players
    random.shuffle(players) # shuffle to starting always with the same player
    for player in players:
      rand = random.randrange(0,10,1) # attack prob
      if rand >= player.pr_attack:
        if player.impostor == 1:
          sus = self.__most_sus(1) # get most sus from spacemen
        else:
          sus = self.__most_sus() # get most sus from all
        rand = random.randrange(0,10,1) # prob of giving a good defence
        # defence was bad
        print("Player "+str(player.id)+" attacked "+str(sus.id))
        if rand > sus.pr_defend+1:
          sus.sus(rand-sus.pr_defend)
          print("Suspected "+str(sus.id)+" defended bad")
        # defence was good, if very good the sus is on the attacker
        elif rand < sus.pr_defend-1:
          player.sus(sus.pr_defend-rand)
          print("Suspected "+str(sus.id)+" defended good")
  
  def voting(self):
    for player in self.players:
      if player.impostor:
          sus = self.__most_sus(1) # get most sus from spacemen
      else:
        sus = self.__most_sus() # get most sus from all
      if sus.suspect >= player.th_voting:
        sus.vote()
    
  def evaluate_turn(self):
    vot = self.__most_voted()
    if vot.turn_votes > 0:
      self.players.remove(vot)
      print("Player "+str(vot.id)+" was voted out")
      if vot.impostor == 0:
        for imp in self.__get_impostors():
          imp.kill(susp=0) # kill point without being sus
        
    for player in self.players:
      player.turn()
  
  def evaluate_game(self):
    imp = self.__get_impostors()
    if len(imp)==0:
      print("Game won by spacemen")
      return 1
    spacemen=self.__get_spacemen()
    if len(spacemen)==0:
      print("Game won by imposter")
      return 0

    return -1

  def best_players(self):
    #discard one impostor
    imposters=self.__get_impostors()
    if (imposters[0].kills+imposters[0].turns) > (imposters[1].kills+imposters[1].turns):
      impostor = imposters[0]
    else:
      impostor = imposters[1]
    # discard one spacemen
    spacemen=self.__get_spacemen()
    vot = functools.reduce(lambda a,b: a if a.turns < b.turns else b, spacemen)
    spacemen.remove(vot)

    return impostor+spacemen

def play_game(game):
  result = -1
  while result == -1:
    game.kill_spaceman()
    result = game.evaluate_game()
    if result != -1: break
    game.discussing()
    game.voting()
    game.evaluate_turn()
    result = game.evaluate_game()

  return result

def mutation_player(players):
  for player in players:
    player.mutate()
  
  imp = Player(1,2) # random imp
  players.insert(1,imp)
  spacemen = Player(1,-1)
  players.append(spacemen)
  return players


# initialization
imp_win=0
sp_win=0
old_players= list()
for i in range(10):
  if (i<2):
    player = Player(1,i)
  else:
    player = Player(0,i)
  old_players.append(player)

  

#simulation
for i in range(100):
  new_players = mutation_player(old_players)
  game = Game(players=new_players)
  blockPrint()
  res = play_game(game)
  enablePrint()
  if res == 1:
    sp_win+=1
  else:
    imp_win+=1
  
  old_player=game.best_players()
  


print("Impostor win: "+str(imp_win))
print("Spacemen win: "+str(sp_win))