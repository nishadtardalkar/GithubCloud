from github import Github
import json
import base64
import requests
from requests.auth import HTTPBasicAuth


class GithubHandler:
    
    def login_and_init(self, username, password, max_files):
        self.max_files = max_files
        self.username = username
        self.password = password
        self.github_handle = Github(username, password, timeout=5000)                
        try:
            self.github_handle.get_user().login
        except:
            print('Something went wrong..')
            return False
        self.github_user = self.github_handle.get_user()
        try:
            self.index_repo = self.github_handle.get_repo(username + '/Index')
        except:
            print('Index not found. Creating Index.')
            self.index_repo = self.github_user.create_repo('Index')
            data = {'rep':-1, 'file': max_files}
            self.index_repo.create_file('size', '', json.dumps(data))
            self.index_repo.create_file('index', '', '{}')
        return True

    def get_list_of_posts(self):
        index_raw = self.index_repo.get_contents('index')
        index_data = base64.b64decode(index_raw.content).decode('utf-8')
        index_json = json.loads(index_data)
        return list(index_json.keys())            

    def upload_data(self, string_data):
        size_raw = self.index_repo.get_contents('size')
        size_data = base64.b64decode(size_raw.content).decode('utf-8')
        size_data = json.loads(size_data)
        repo_index = int(size_data['rep'])
        file_index = int(size_data['file']) + 1
        if file_index >= self.max_files:
            repo_index += 1
            file_index = 0
            repo = self.github_user.create_repo('R' + str(repo_index))
        else:
            #repo = self.github_handle.get_repo(self.username + '/R' + str(repo_index))
            repo = self.github_user.get_repo('R' + str(repo_index))
        repo.create_file('D' + str(file_index), '', string_data)

        '''
        url = 'https://api.github.com/repos/' + self.username + '/R' + str(repo_index) + '/contents/D' + str(file_index)
        print(url)
        post_data = '{"message":"", "content":"'+base64.b64encode(string_data.encode('utf-8')).decode('utf-8')+'"'
        res = requests.put(url, data=post_data, auth=(self.username, self.password), timeout=5000)        
        print(res.request.method + ' / HTTP/1.1')
        print('\r\n'.join(': '.join(i) for i in res.request.headers.items()))
        '''

        new_size = {'rep':repo_index, 'file':file_index}
        self.index_repo.update_file('size', '', json.dumps(new_size), size_raw.sha)
        return str(repo_index) + '-' + str(file_index)

    def add_to_index(self, post_name, file_struct, total_size):
        index_raw = self.index_repo.get_contents('index')
        index_data = base64.b64decode(index_raw.content).decode('utf-8')
        index_json = json.loads(index_data)
        if post_name in index_json:
            i = 0
            while (post_name + ':' + i) in index_json:
                i += 1
            post_name += ':' + i
            print('Found duplicate. Saving with name : ' + post_name)
        index_json[post_name] = {}
        for i in file_struct:
            index_json[post_name][i] = file_struct[i]
        index_json[post_name]['_total_size'] = total_size
        self.index_repo.update_file('index', '', json.dumps(index_json), index_raw.sha)
        return

    def get_post_struct(self, post_name):
        index_raw = self.index_repo.get_contents('index')
        index_data = base64.b64decode(index_raw.content).decode('utf-8')
        index_json = json.loads(index_data)
        if post_name not in index_json:
            print('Post not found.')
            return        
        return index_json[post_name]

    def download_data(self, repo_file_name):
        repo_index = int(repo_file_name.split('-')[0])
        file_index = int(repo_file_name.split('-')[1])
        url = 'https://api.github.com/repos/' + self.username + '/R' + str(repo_index) + '/git/trees/master'
        data = requests.get(url=url).json()['tree']
        for i in data:
            if i['path'] == 'D' + str(file_index):
                sha = i['sha']
                break
        url = 'https://api.github.com/repos/' + self.username + '/R' + str(repo_index) + '/git/blobs/' + sha
        data = requests.get(url=url).json()['content']          
        data = base64.b64decode(data).decode('utf-8')
        return data
