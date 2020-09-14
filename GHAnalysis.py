
import json
import os
import argparse

class Data:

    def __init__(self,isfirst:int =0, addr:int=None):
        self.uevent = {}
        self.revent = {}
        self.urevent = {}
        if isfirst == 1:
            if(addr == None):
                raise RuntimeError('error: init failed')
            self.TotalAnalyse(addr)
            self.SaveToLocal()
        # if addr is None: #and not os.path.exists('1.json') and not os.path.exists('2.json') and not os.path.exists(
        # #         '3.json'):
        #     raise RuntimeError('error: init failed')
        else:
            self.localu={}
            self.localr={}
            self.localur={}
            if self.ReadLocal() == False:
                raise RuntimeError("file is not exist")


    def TotalAnalyse(self,addr:str):
        for root, dic, files in os.walk(addr):
            for f in files:
                if f[-5:] == ".json":
                    jpath = f
                    self.JsonAnalyse(addr,jpath)



    def JsonAnalyse(self,addr:str,jpath:str):
        f = open(addr + '\\' + jpath,'r', encoding='utf-8')
        #f=open("data.json",'r',encoding='utf-8').read()
        try:
            while True:
                stmp = f.readline()
                if stmp:
                    dtmp = json.loads(stmp)
                    #print(type(dtmp))
                    #print(dtmp)
                    #print(isinstance(dtmp,dict))
                    if not dtmp["type"] in ['PushEvent','IssueCommentEvent',
                                            'IssuesEvent','PullRequestEvent']:
                        continue
                    if not dtmp["actor"]["login"] in self.uevent.keys():
                        event = {'PushEvent':0,'IssueCommentEvent':0,
                                 'IssuesEvent':0,'PullRequestEvent':0}
                        self.uevent[dtmp["actor"]["login"]] = event

                    if not dtmp["repo"]["name"] in self.revent.keys():
                        event = {'PushEvent':0,'IssueCommentEvent':0,
                                 'IssuesEvent':0,'PullRequestEvent':0}
                        self.revent[dtmp["repo"]["name"]] = event

                    if not dtmp["actor"]["login"]+'&'+dtmp["repo"]["name"] in self.urevent.keys():
                        event = {'PushEvent': 0, 'IssueCommentEvent': 0,
                                 'IssuesEvent': 0, 'PullRequestEvent': 0}
                        self.urevent[dtmp["actor"]["login"]+'&'+dtmp["repo"]["name"]] = event
                    self.uevent[dtmp["actor"]["login"]][dtmp['type']] += 1
                    self.revent[dtmp["repo"]["name"]][dtmp['type']] += 1
                    self.urevent[dtmp["actor"]["login"] +'&'+ dtmp["repo"]["name"]][dtmp['type']] += 1
                else:
                    break
        except:
            pass
        finally:
            f.close()
        #print(self.uevent.items())
       # print(revent.items())

    def ReadLocal(self) -> bool:
        if not os.path.exists('user.json') and not os.path.exists(
                'repo.json') and not os.path.exists('userrepo.json'):
            return False
        x = open('user.json', 'r', encoding='utf-8').read()
        self.localu = json.loads(x)
        x = open('repo.json', 'r', encoding='utf-8').read()
        self.localr = json.loads(x)
        x = open('userepo.json', 'r', encoding='utf-8').read()
        self.localur = json.loads(x)
        return True


    def SaveToLocal(self):
        try:
            with open('user.json', 'w', encoding = 'utf-8') as f:
                json.dump(self.uevent,f)
            with open('repo.json', 'w', encoding = 'utf-8') as f:
                json.dump(self.revent,f)
            with open('userepo.json', 'w', encoding = 'utf-8') as f:
                json.dump(self.urevent,f)
        except:
            raise RuntimeError("save error")
        finally:
            f.close()


    def QueryByUser(self, user:str, event: str):
        if not user in self.localu.keys():
            return 0
        return self.localu[user][event]


    def QueryByRepo(self, repo: str, event: str):
        if not self.localr.get(repo, 0):
            return 0
        return self.localr[repo][event]


    def QueryByUserAndRepo(self, user:str, repo:str, event: str):
        if not self.localur.get(user+'&'+repo,0):
            return 0
        return self.localur[user+'&'+repo][event]


class Run:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.data = None
        self.ArgInit()
        print(self.Analyse())

    def ArgInit(self):
        self.parser.add_argument('-i', '--init')
        self.parser.add_argument('-u', '--user')
        self.parser.add_argument('-r', '--repo')
        self.parser.add_argument('-e', '--event')

    def Analyse(self):
        if self.parser.parse_args().init:
            self.data = Data(1,self.parser.parse_args().init)
            return 0
        else:
            #if self.data is None:
            self.data = Data(0,None)
            if self.parser.parse_args().event:
                if self.parser.parse_args().user:
                    if self.parser.parse_args().repo:
                        res = self.data.QueryByUserAndRepo(
                            self.parser.parse_args().user, self.parser.parse_args().repo,
                            self.parser.parse_args().event)
                    else:
                        res = self.data.QueryByUser(
                            self.parser.parse_args().user, self.parser.parse_args().event)
                elif self.parser.parse_args().repo:
                    res = self.data.QueryByRepo(
                        self.parser.parse_args().repo, self.parser.parse_args().event)
                else:
                    raise RuntimeError('error: argument -l or -c are required')
            else:
                raise RuntimeError('error: argument -e is required')
        return res


if __name__ == '__main__':

    run = Run()