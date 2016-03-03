# -*- coding: utf-8 -*-
#
# PBAutoJoin For Urban Terror plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2015 PtitBigorneau - www.ptitbigorneau.fr
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

__author__  = 'PtitBigorneau www.ptitbigorneau.fr'
__version__ = '1.4'

import b3, time, threading, thread
import b3.plugin
import b3.events
from b3 import clients

class PbautojoinPlugin(b3.plugin.Plugin):
    
    _adminPlugin = None
    _test = 'ok'
    _cronTab = None

    _pbautojoinlevel = 100
    _autojoinminlevel = 40
    _nowarnminlevel = 20
	
    def onLoadConfig(self):

        self._pbautojoinlevel = self.getSetting('settings', 'pbautojoinlevel', b3.LEVEL, self._pbautojoinlevel)
        self._autojoinminlevel = self.getSetting('settings', 'autojoinminlevel', b3.LEVEL, self._autojoinminlevel)
        self._nowarnminlevel = self.getSetting('settings', 'nowarnminlevel', b3.LEVEL, self._nowarnminlevel)

    def onStartup(self):
        
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            raise AttributeError('could not find admin plugin')

        self.registerEvent('EVT_CLIENT_TEAM_CHANGE', self.onClientTeamChange)
        self.registerEvent('EVT_GAME_MAP_CHANGE', self.onGameMapChange)
        self.registerEvent('EVT_GAME_ROUND_START', self.onGameRoundStart)
    
    def onGameMapChange(self, event):

        try:
            swaproles = self.console.getCvar('g_swaproles').getInt()
        except:        
            swaproles = 0
        gametype = self.console.getCvar('g_gametype').getInt()

        if gametype == 0 or gametype == 1 or gametype == 9 or gametype == 11:
            return False            

        self._test = None

        thread.start_new_thread(self.wait, (30,))

    def onGameRoundStart(self, event):

        try:
            swaproles = self.console.getCvar('g_swaproles').getInt()
        except:        
            swaproles = 0
        gametype = self.console.getCvar('g_gametype').getInt()
			
        if gametype == 0 or gametype == 1 or gametype == 9 or gametype == 11:
            return False        

        if swaproles == 1:

            self._test = None

            thread.start_new_thread(self.wait, (10,))     

    def onClientTeamChange(self, event):
        
        try:
            swaproles = self.console.getCvar('g_swaproles').getInt()
        except:        
            swaproles = 0
        gametype = self.console.getCvar('g_gametype').getInt()

        if gametype == 0 or gametype == 1 or gametype == 9 or gametype == 11:
            return False
        
        sclient = event.client
        sclientteam = sclient.team
            
        if sclient.guid[:3] == 'BOT':
            return False

        if self._test == None:
            return False

        if sclient.maxLevel >= self._autojoinminlevel:
            return False

        scores = self.console.getTeamScores()
        redscore = scores[0]
        bluescore = scores[1]
        teamred = 0
        teamblue = 0
        oldteamred = 0
        oldteamblue = 0

        if sclientteam not in (2, 3):
            return
                
        for x in self.console.clients.getList():
            if x.team == 2:
                teamred +=1
            if x.team == 3:
                teamblue +=1
                    
        if sclientteam == 2:

            oldteamred = teamred - 1
            oldteamblue = teamblue

        if sclientteam == 3:

            oldteamred = teamred
            oldteamblue = teamblue - 1

        if gametype != 0:

            if oldteamred == oldteamblue:
                        
                if int(redscore) == int(bluescore):
                            
                    if gametype != 8:
                        team = 0

                    if gametype == 8:
                        team = 3

                if int(redscore) > int(bluescore):
                    team = 3
                if int(redscore) < int(bluescore):
                    team = 2

            if oldteamred > oldteamblue:
                team = 3
            
            if oldteamred < oldteamblue:
                team = 2

            if team != 0 and sclientteam != team:

                if team == 2:
                    dteam = 'red'
                if team == 3:
                    dteam = 'blue'

                self.console.write('forceteam %s %s' %(sclient.cid, dteam))
                self.console.say('%s ^3Change Team No Respect Autojoin'%(sclient.exactName))
                self.debug('PBAutojoin change team : %s %s - red %s %s - blue %s %s'%(sclient.name, sclientteam, oldteamred, redscore, oldteamblue, bluescore))
                       
                if oldteamred != 0 or oldteamblue != 0:
                                          
                    if sclient.maxLevel < self._nowarnminlevel: 
                        self._adminPlugin.warnClient(sclient, '^3No Respect Autojoin', None, False, '', 60)
                        self.debug('PBAutojoin warn : %s %s - red %s %s - blue %s %s'%(sclient.name, sclientteam, oldteamred, redscore, oldteamblue, bluescore))

    def wait(self, temps):

        time.sleep(temps)
        self._test = 'ok'
        self.debug('PBAutojoin wait : %s '%(temps))
