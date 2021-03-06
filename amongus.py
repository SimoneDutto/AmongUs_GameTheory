import random, functools
import sys, os
from termcolor import colored
from collections import defaultdict 
import matplotlib.pyplot as plt


# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

KILL_SUSPECT=1
WIN_POINT=5
NUM_IMP=1
NUM_SPACE=4
PPL_LIVE=3

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
  score=0
  # State
  dead=0
  mutate=1

  def __init__(self, impostor, id):
    self.id=id
    self.impostor=impostor
    if impostor == 0:
      self.pr_attack=random.randrange(0,10,1)
      self.pr_defend=random.randrange(0,10,1)
      self.th_voting=random.randrange(0,10,1)
    else:
      self.pr_attack=5
      self.pr_defend=5
      self.th_voting=5

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
  
  def mutatet(self):
    # reset counters
    self.dead = 0
    self.turns = 0
    self.turn_votes=0
    self.kills = 0
    self.suspect = 0
    self.mutate = 1
    # mutate variables
    rand = random.randrange(1, 30, 1)
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

  def reset(self, rand=1):
    # reset counters
    self.dead = 0
    self.turns = 0
    self.turn_votes=0
    self.kills = 0
    self.suspect = 0
    self.mutate = 0
    # random attributes
    if rand:
      self.pr_attack=random.randrange(0,10,1)
      self.pr_defend=random.randrange(0,10,1)
      self.th_voting=random.randrange(0,10,1)
  
  def win(self):
    self.score = self.kills + self.turns + WIN_POINT
  
  def loose(self):
    self.score = self.kills + self.turns
    

class Game:
  players=list()
  def __init__(self,players):
    self.players = players
  
  def __get_impostors(self):
    filtered = filter(lambda x: x.impostor == 1, self.__get_players())
    return list(filtered)
  
  def __get_spacemen(self):
    filtered = filter(lambda x: x.impostor != 1, self.__get_players())
    return list(filtered)

  def __get_players(self):
    filtered = filter(lambda x: x.dead == 0, self.players)
    return list(filtered)
  
  def __most_sus(self, id, imp=0):
    if imp == 1:
      players = self.__get_spacemen() 
    else: 
      players = self.__get_players()
    
    random.shuffle(players) #avoid taking always the first when all equals
    players = list(filter(lambda x: x.id != id, players))
    sus = functools.reduce(lambda a,b: a if a.suspect > b.suspect else b, players)
    return sus
  
  def __most_voted(self):
    vot = functools.reduce(lambda a,b: a if a.turn_votes > b.turn_votes else b, self.__get_players())
    return vot

  def kill_spaceman(self):
    spaceman = random.choices(self.__get_spacemen())
    spaceman = spaceman[0]
    spaceman.dead = 1
    for imp in self.__get_impostors():
      imp.kill()
    print(colored("Player "+str(spaceman.id)+" was killed",'red'))

  def discussing(self):
    players = self.__get_players()
    random.shuffle(players) # shuffle to starting always with the same player
    for player in players:
      rand = random.randrange(0,10,1) # attack prob
      if rand >= player.pr_attack:
        if player.impostor == 1:
          sus = self.__most_sus(player.id, 1) # get most sus from spacemen
        else:
          sus = self.__most_sus(player.id) # get most sus from all
        rand = random.randrange(0,10,1) # prob of giving a good defence
        # defence was bad
        print(colored("Player "+str(player.id)+" attacked "+str(sus.id),'yellow'))
        if rand > sus.pr_defend+1:
          sus.sus(rand-sus.pr_defend)
          print("Suspected "+str(sus.id)+" defended bad")
        # defence was good, if very good the sus is on the attacker
        elif rand < sus.pr_defend-1:
          player.sus(rand-sus.pr_defend)
          print("Suspected "+str(sus.id)+" defended good")
  
  def voting(self):
    for player in self.__get_players():
      if player.impostor:
          sus = self.__most_sus(player.id, 1) # get most sus from spacemen
      else:
        sus = self.__most_sus(player.id) # get most sus from all
      if sus.suspect >= player.th_voting:
        sus.vote()
    
  def evaluate_turn(self):
    vot = self.__most_voted()
    if vot.turn_votes > 0:
      vot.dead=1
      print(colored("Player "+str(vot.id)+" was voted out", 'red'))
      if vot.impostor == 0:
        for imp in self.__get_impostors():
          imp.kill(susp=0) # kill point without being sus
        
    for player in self.__get_players():
      player.turn()
  
  def evaluate_game(self):
    imp = self.__get_impostors()
    if len(imp)==0:
      print("-----------------------------")
      print("Game won by spacemen")
      print("-----------------------------")
      for player in self.__get_spacemen():
        player.win()
      for player in self.__get_impostors():
        player.loose()
      return 1
    spacemen=self.__get_spacemen()
    if len(spacemen)==0:
      for player in self.__get_impostors():
        player.win()
      for player in self.__get_spacemen():
        player.loose()
      print("-----------------------------")
      print("Game won by imposter")
      print("-----------------------------")
      return 0

    return -1

  def best_players(self):
    #discard one impostor
    # imposters=self.players[:NUM_IMP]
    # vot = functools.reduce(lambda a,b: a if a.turns < b.turns else b, imposters)
    # vot.mutate = 0

    # spacemen=self.players[NUM_IMP:]
    # vot = functools.reduce(lambda a,b: a if a.turns < b.turns else b, spacemen)
    # vot.mutate=0
    players = self.players
    players.sort(key=lambda p: p.score)
    for i in range(NUM_IMP+NUM_SPACE):
      if i < PPL_LIVE:
        players[i].mutate=1
      else:
        players[i].mutate=0
    
    return self.players

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
    if player.impostor == 0:
      if player.mutate == 1:
        player.mutatet()
      else:
          player.reset()
    else:
      player.reset(rand=0)

  return players

def calculate_stats(players):
  impostors = players[:NUM_IMP]
  #impostors = list(filter(lambda x: x.mutate == 1, impostors))
  spacemen = players[NUM_IMP:]
  #spacemen = list(filter(lambda x: x.mutate == 1, spacemen))
  avg_attk =  sum(imp.pr_attack for imp in impostors)/NUM_IMP
  avg_def = sum(imp.pr_defend for imp in impostors)/NUM_IMP
  avg_thr = sum(imp.th_voting for imp in impostors)/NUM_IMP
  attack_prs[0].append(avg_attk)
  defend_prs[0].append(avg_def)
  vot_thrs[0].append(avg_thr)

  avg_attk =  sum(sp.pr_attack for sp in spacemen)/NUM_SPACE
  avg_def = sum(sp.pr_defend for sp in spacemen)/NUM_SPACE
  avg_thr = sum(sp.th_voting for sp in spacemen)/NUM_SPACE
  attack_prs[1].append(avg_attk)
  defend_prs[1].append(avg_def)
  vot_thrs[1].append(avg_thr)

# initialization
imp_win=0
sp_win=0
old_players= list()
for i in range(NUM_IMP+NUM_SPACE):
  if (i<NUM_IMP):
    player = Player(1,i)
  else:
    player = Player(0,i)
  old_players.append(player)
# stats
attack_prs = defaultdict(list) 
defend_prs = defaultdict(list)
vot_thrs = defaultdict(list)
wins = list()
consec = 0
#simulation
for i in range(1000):
  new_players = mutation_player(old_players)
  game = Game(players=new_players)
  blockPrint()
  res = play_game(game)
  enablePrint()
  if res == 1:
    sp_win+=1
    wins.append(1)
    consec = 0
  else:
    imp_win+=1
    wins.append(0)
    consec += 1

  if consec >= 10000:
    print(f"20 Consecutive victory from impostor at {i}")
    break
  old_players=game.best_players()
  calculate_stats(old_players)
  
print("Impostor win: "+str(imp_win))
print("Spacemen win: "+str(sp_win))

fig, axs = plt.subplots(2, 3,figsize=(30,40))
axs[0,0].plot(attack_prs[0],'r')
axs[0,0].set_title("Attack Impostor")
axs[0,1].plot(defend_prs[0], 'y')
axs[0,1].set_title("Defense Impostor")
axs[0,2].plot(vot_thrs[0], 'g')
axs[0,2].set_title("Attack Threshold Impostor")
axs[1,0].plot(attack_prs[1],'r')
axs[1,0].set_title("Spacemen Attack")
axs[1,1].plot(defend_prs[1],'y')
axs[1,1].set_title("Spacemen Defend")
axs[1,2].plot(vot_thrs[1],'g')
axs[1,2].set_title("Spacemen Threshold")
plt.figure()
plt.plot(wins,'o')
plt.show()