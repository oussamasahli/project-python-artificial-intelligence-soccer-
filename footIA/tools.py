from soccersimulator import Vector2D, SoccerState, SoccerAction
from soccersimulator import SoccerTeam, Strategy, Player, Ball
from soccersimulator.settings import *

import math

class ProxyObj(object):
    def __init__(self,state):
        self._obj = state
    def __getattr__(self,attr):
        return getattr(self._obj,attr)

class ToolBox(ProxyObj):
    
    def __init__(self, state, id_team, id_player):

        super(ToolBox,self).__init__(state)
        self.id_team = id_team
        self.id_player = id_player
    @property
    def myTeam(self):
        return self.id_team
    @property
    def oppTeam(self):
        return 3-self.id_team
    @property
    def myId(self):
        return self.id_player

#vitesses courantes

    @property
    def ballSpeed(self):
        return self.ball.vitesse
    @property
    def pos_mil(self):
        return Vector2D(GAME_WIDTH/2,GAME_HEIGHT/2)
    @property
    def mySpeed(self):
        return self.player_state(self.id_team, self.id_player).vitesse
    def playerSpeed(self, player):
        return player.self.mySpeed

#Vecteurs utiles

    @property        
    def playerPos(self):
        return self.player_state(self.id_team, self.id_player).position
    @property
    def playerSpeed(self):
        return self.player_state(self.id_team, self.id_player).vitesse
    @property     
    def ballPos(self):
        return self.ball.position
    @property
    def vecMyGoal(self):
        target = 0 if self.id_team == 1 else 1
        return Vector2D((target)*GAME_WIDTH, GAME_HEIGHT/2)
    @property
    def pos_def(self):
        if self.id_team == 1:
           return Vector2D(GAME_WIDTH/4,GAME_HEIGHT/2)
        else:
           return Vector2D(GAME_WIDTH*3/4,GAME_HEIGHT/2)
    @property
    def pos_att(self):
        if self.id_team == 1:
           return Vector2D(GAME_WIDTH/2+15,GAME_HEIGHT/2)
        else:
           return Vector2D(GAME_WIDTH/2-15,GAME_HEIGHT/2)
    @property
    def vecOppGoal(self):
        target = 0 if self.id_team == 2 else 1
        return Vector2D((target)*GAME_WIDTH, GAME_HEIGHT/2)
    @property
    def vecTheirGoal(self):
        target = 0 if self.id_team == 2 else 1
        return Vector2D((target)*GAME_WIDTH, GAME_HEIGHT/2)

#DONNEES DU TERRAIN

    @property
    def width(self):
        return GAME_WIDTH
    @property
    def height(self):
        return GAME_HEIGHT
    @property
    def middleSpot(self):
        return Vector2D(self.width/2, self.height/2)



    @property
    def get_opponent(self):
        opp = [self.player_state(idteam, idplayer).position for idteam, idplayer in self.players if idteam != self.id_team]
        return opp
    @property
    def nb_mateplayer(self):
        return len(self.get_mate)+1
    @property
    def get_mate(self):
        mate = [self.player_state(idteam,idplayer).position for idteam,idplayer in self.players if (idteam == self.id_team and idplayer!=self.id_player)]
        return mate

    def mostCloseMate(self, coop):

        mates=coop
        numDistMin = None
        distMin = GAME_WIDTH
        i=0
        for mate in mates:
            if self.distMe_Players(mate)<distMin:
                distMin=self.distMe_Players(mate)
                numDistMin=i
            i=i+1
        if (numDistMin==None):
            return
        return mates[numDistMin]

    def mostCloseOpp(self, opponents):
        """
        Retourne le vecteur position du joueur adverse le plus proche
        """
        opps=opponents
        distMin = self.width
        numDistMin = None
        i=0
        for opp in opps:
            if self.distMe_Players(opp)<distMin:
                distMin=self.distMe_Players(opp)
                numDistMin=i
            i=i+1

        if (numDistMin==None):
            return
        return opps[numDistMin]

    def mostCloseOppforward(self, opponents):
        """
        Retourne le vecteur position du joueur adverse le plus proche
        """
        opps=opponents
        distMin = self.width
        numDistMin = None
        i=0
        for opp in opps:
            if self.distMe_Players(opp)<distMin and self.forward(opp):
                distMin=self.distMe_Players(opp)
                numDistMin=i
            i=i+1

        if (numDistMin==None):
            return None

        return opps[numDistMin]

    def mostCloseOppToball(self, opponents):
        """
        Retourne l'adversaire le plus proche de la balle
        """
        opps=opponents
        distMin = self.width
        numDistMin = None
        i=0
        for opp in opps:
            if self.distPlayers(opp, self.ballPos)<distMin:
                distMin=self.distPlayers(opp, self.ballPos)
                numDistMin=i
            i=i+1

        if (numDistMin==None):
            return None
        return opps[numDistMin]

    def mostCloseMateToball(self, coop):
        return self.mostCloseOppToball(coop)

    def defenderbehindopp(self, opponents, coop):
       
        opp=self.mostCloseOppToball(opponents)
        mate=self.mostCloseMateToball(coop)
        print(not(self.specificForward(mate,opp)))
        return not(self.specificForward(mate,opp))

#Some players and ball currents distances

    def distMe_Players(self, player):
        """
        Ma distance courrante par rapport a un autre joueur allie ou adverse
        """
        return self.playerPos.distance(player)

    def distPlayers(self, object1, object2):
        return object1.distance(object2)

    @property
    def myGoalBall_distance(self):
        return self.ballPos.distance(self.vecMyGoal)
    @property
    def playerBall_distance(self):
        return self.ballPos.distance(self.playerPos)

    @property    
    def mateMostCloseDistance(self):
        mates= self.get_mate
        DistMin = GAME_WIDTH
        for mate in mates:
                if self.distPlayers(mate)<DistMin:
                    DistMin=self.distPlayers(mate)
        return DistMin

    @property 
    def oppMostCloseDistance(self):
        opps= self.get_opponent
        DistMin = GAME_WIDTH
        for opp in opps:
                if self.distPlayers(opp)<DistMin:
                    DistMin=self.distPlayers(opp)
        return DistMin
        

########################################################################################################
# Boolean Condition
########################################################################################################
 
    @property
    def canShoot(self):
        return self.ballPos.distance(self.playerPos) < PLAYER_RADIUS + BALL_RADIUS
    
    @property
    def isInGoal(self):
        """
        Retourn true si le joueur courrant est dans les cages
        """
        coordx= self.playerPos.x
        coordy= self.playerPos.y
        target = 0 if self.id_team == 1 else 1

        if((((target == 0)and (coordx<=5))|
        ((target == 1) and(coordx>145))) 
        and (coordy<=50 and coordy>=40)):
            return True
        else:
            return False   

    @property       
    def inCamp(self):
        """
        Retourne true si je suis dans mon camp
        """
        return (((self.myTeam==1) and (self.ballPos.x <= self.width/2))
            | ((self.myTeam==2) and (self.ballPos.x >= self.width/2)))

    @property
    def mateHaveBall(self):
        
        mate= self.get_mate
        for players in mate :
            if (players.distance(self.ballPos)<=10):
                return True
        return False
    @property
    def iHaveBall(self):
        
        if (self.playerPos.distance(self.ballPos)<=10) and self.mateHaveBall:
            return True
        return False
    @property
    def inCorner(self):
       
        if (self.myTeam == 0):
            if ((self.playerPos.distance(Vector2D(GAME_WIDHT,0))<=10) | (self.playerPos().distance(Vector2D(GAME_WIDTH,GAME_HEIGHT))<=10)):
                return True
            else:
                return False
        else:
            if ((self.playerPos.distance(Vector2D(0,0))<=10) | (self.playerPos().distance(Vector2D(0,GAME_HEIGHT))<=10)):
                return True
            else:
                return False
    @property
    def isInAera(self):
       
        opp = self.get_opponent
        for players in opp:
            if (players.distance(self.playerPos)<10):
                return True
        return False

    def specificForward(self, mate, opp):
        
        if(self.myTeam==1):
            return opp.x > mate.x
        else:
            return opp.x < mate.x

    def forwardOpp(self):
       
        opp = self.get_opponent
        for player in opp:
            if (player.distance(self.playerPos)<20)and(self.forward(player)):
                return True
        return False

    def forward(self, player):
       
        if(self.myTeam==1):
            return player.x > self.playerPos.x
        else:
            return player.x < self.playerPos.x

###################################################################
#COMPORTEMENTS
###################################################################

class Comportement(ProxyObj):
    def __init__(self,obj):
        super(Comportement,self).__init__(obj)
    def run(self,p):
        raise(NotImplementedError)
    def go(self,p):
        raise(NotImplementedError)
    def shoot(self):
        raise(NotImplementedError)
    def degage(self):
        raise(NotImplementedError)
    def drible(self):
        raise(NotImplementedError)
    def VecBallPredicted(self):
        raise(NotImplementedError)
    def returnToGial(self):
        raise(NotImplementedError)
    def returnToCamp(self):
        raise(NotImplementedError)
    def passToMostCloseMate(self):
        raise(NotImplementedError)
    def bigshoot(self):
    	raise(NotImplementedError)

def get_random_vec():
    return Vector2D.create_random(-1,1)

def get_random_SoccerAction():
    return SoccerAction(get_random_vec(),get_random_vec())
