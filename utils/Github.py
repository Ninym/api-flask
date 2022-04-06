import requests as r
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import json
import flask

ReleaseBase = 'https://api.github.com/repos/'
domain = 'dev.api.ninym.top'

def ghParser(operation, author, repo, ContentType):
    operations = ['release']
    Error404 = {
        'code': 404,
        'msg': 'Invalid path gh/{}'.format(operation)
    }
    Error501 = {
        'code': 501,
        'msg': 'It seems that this repo has no any release'.format(operation)
    }
    if operation not in operations: return json.dump(Error404)
    if operation == 'release':
        release = Release(author,repo,ContentType)
        if release.isEmpty:
            return json.dumps(Error501)
        return release.Draw()

class Release():
    def __init__(self, author, repo, ContentType):
        self.author = author
        self.repo = repo
        self.info = json.loads(r.get(ReleaseBase+self.author+'/'+self.repo+'/releases').text)
        self.ContentType = ContentType
        if len(self.info) == 0: self.isEmpty = True
        else: self.isEmpty = False

    def getInfo(self):  # For debugging
        return self.info

    def makeDimensionList(self):
        self.ReleaseLabel = []
        self.ReleaseDownloads = []
        for i in self.info:
            Downloads = 0
            TagName = i['tag_name']
            assets = i['assets']
            if len(assets) == 0:
                self.ReleaseLabel = None
                self.ReleaseDownloads = None
            else:
                for j in assets:
                    Downloads += j['download_count']
                self.ReleaseLabel.append(TagName)
                self.ReleaseDownloads.append(Downloads)


    def Draw(self): 
        self.makeDimensionList()
        plt.figure(figsize=(10,10)) # Make the circle to be a formal one
        matplotlib.rcParams.update({'font.size': 20})   # Change the font size of title
        if self.ReleaseDownloads == None and self.ReleaseLabel == None:
            values = [100]
            plt.title('No Any Downloadable Asset from {}/{}'.format(self.author,self.repo))
            r = np.linspace(106,142,1,dtype=np.uint8)
            g = np.linspace(103,140,1,dtype=np.uint8)
            b = np.linspace(232,216,1,dtype=np.uint8)
            colors = ['#'+'{:0>2}{:0>2}{:0>2}'.format(str(hex(r[i])),str(hex(g[i])),str(hex(b[i]))).replace('0x','') for i in range(len(r))]            
            plt.pie(values,colors=colors)
            plt.savefig('./cache/{}-{}.png'.format(self.author,self.repo))
            if self.ContentType == 'pic': return flask.send_from_directory('./cache/', '{}-{}.png'.format(self.author,self.repo), as_attachment=False, download_name='{} - {}.png'.format(self.author, self.repo))
            else:
                dt = {
                    'author': self.author,
                    'repo': self.repo,
                    'labels': self.ReleaseLabel,
                    'downloads': self.ReleaseDownloads,
                    'pic': 'https://{}/cache/{}-{}.png'.format(domain,self.author,self.repo),
                    'remark': 'The access to the pic will be removed when the service is redeployed or by the operation of administrator'
                }
                return json.dumps(dt)
        explode = [0.01] * len(self.ReleaseLabel)
        r = np.linspace(106,142,len(self.ReleaseDownloads),dtype=np.uint8)
        g = np.linspace(103,140,len(self.ReleaseDownloads),dtype=np.uint8)
        b = np.linspace(232,216,len(self.ReleaseDownloads),dtype=np.uint8)
        colors = ['#'+'{:0>2}{:0>2}{:0>2}'.format(str(hex(r[i])),str(hex(g[i])),str(hex(b[i]))).replace('0x','') for i in range(len(r))]
        plt.pie(self.ReleaseDownloads,explode=explode,labels=self.ReleaseLabel,autopct='%1.1f%%',colors=colors)
        plt.title('Downloads of {}/{}'.format(self.author,self.repo))
        plt.savefig('./cache/{}-{}.png'.format(self.author,self.repo))
        if self.ContentType == 'pic': return flask.send_from_directory('./cache/', '{}-{}.png'.format(self.author,self.repo), as_attachment=False, download_name='{} - {}.png'.format(self.author, self.repo))
        else:
            dt = {
                'author': self.author,
                'repo': self.repo,
                'labels': self.ReleaseLabel,
                'downloads': self.ReleaseDownloads,
                'pic': 'https://{}/cache/{}-{}.png'.format(domain,self.author,self.repo),
                'remark': 'The access to the pic will be removed when the service is redeployed or by the operation of administrator'
            }
            return json.dumps(dt)

