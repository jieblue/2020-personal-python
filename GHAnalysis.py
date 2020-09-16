
import json
import os
import re
import argparse
from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing.pool import ThreadPool


class Data:

    def __init__(self, isFirst:int =0, addr:int=None):
        self.uEvent = {}
        self.rEvent = {}
        self.urEvent = {}
        if isFirst == 1:##第一次初始化
            if(addr == None):
                raise RuntimeError('error: init failed')
            self.TotalAnalyse(addr)
            self.SaveToLocal()

        else:
            self.localU={}
            self.localR={}
            self.localUR={}
            if self.ReadLocal() == False:
                raise RuntimeError("file is not exist")

    def TotalAnalyse(self,addr:str):#解析文件夹中的所有json
        for root, dic, files in os.walk(addr):
            for f in files:
                if f[-5:] == ".json":
                    jPath = f
                    self.JsonAnalyse(addr,jPath)

    def JsonAnalyse(self, addr:str,jPath:str):#单个json解析函数
        f = open(addr + '\\' + jPath, 'r', encoding='utf-8')
        try:
            while True:
                stmp = f.readline()
                if stmp:
                    pattern = re.compile('"login":".*?",')##以下3段采用正则表达式
                    res=pattern.search(stmp).group(0)
                    rLogin = res[9:-2]

                    pattern = re.compile('"name":".*?",')
                    res = pattern.search(stmp).group(0)
                    rName = res[8:-2]

                    pattern = re.compile('"type":".*?",')
                    res = pattern.search(stmp).group(0)
                    rEvent = res[8:-2]

                    if not rEvent in ['PushEvent', 'IssueCommentEvent',
                                            'IssuesEvent','PullRequestEvent']:
                        continue
                    if not rLogin in self.uEvent.keys():##没有即跳过
                        event = {'PushEvent':0,'IssueCommentEvent':0,
                                 'IssuesEvent':0,'PullRequestEvent':0}
                        self.uEvent[rLogin] = event

                    if not rName in self.rEvent.keys():##初始化
                        event = {'PushEvent':0,'IssueCommentEvent':0,
                                 'IssuesEvent':0,'PullRequestEvent':0}
                        self.rEvent[rName] = event

                    if not rLogin + '&' + rName in self.urEvent.keys():
                        event = {'PushEvent': 0, 'IssueCommentEvent': 0,
                                 'IssuesEvent': 0, 'PullRequestEvent': 0}
                        self.urEvent[rLogin + '&' + rName] = event
                        ##更新
                    self.uEvent[rLogin][rEvent] += 1
                    self.rEvent[rName][rEvent] += 1
                    self.urEvent[rLogin + '&' + rName][rEvent] += 1
                else:
                    break
        except:
            pass
        finally:
            f.close()

    def ReadLocal(self) -> bool:#判断数据是否成功存在本地
        if not os.path.exists('user.json') and not os.path.exists(
                'repo.json') and not os.path.exists('userrepo.json'):
            return False
        x = open('user.json', 'r', encoding='utf-8').read()
        self.localU = json.loads(x)
        x = open('repo.json', 'r', encoding='utf-8').read()
        self.localR = json.loads(x)
        x = open('userepo.json', 'r', encoding='utf-8').read()
        self.localUR = json.loads(x)
        return True

    def SaveToLocal(self):##保存在本地
        try:
            with open('user.json', 'w', encoding = 'utf-8') as f:
                json.dump(self.uEvent, f)
            with open('repo.json', 'w', encoding = 'utf-8') as f:
                json.dump(self.rEvent, f)
            with open('userepo.json', 'w', encoding = 'utf-8') as f:
                json.dump(self.urEvent, f)
        except:
            raise RuntimeError("save error")
        finally:
            f.close()

    def QueryByUser(self, user:str, event: str):
        if not user in self.localU.keys():
            return 0
        return self.localU[user][event]

    def QueryByRepo(self, repo: str, event: str):
        if not self.localR.get(repo, 0):
            return 0
        return self.localR[repo][event]

    def QueryByUserAndRepo(self, user:str, repo:str, event: str):
        if not self.localUR.get(user + '&' + repo, 0):
            return 0
        return self.localUR[user + '&' + repo][event]


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