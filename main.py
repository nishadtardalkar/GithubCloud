from github_handler import GithubHandler
from data_processor import DataProcessor
import os

# HARD CODED INPUTS
MAX_FILE_SIZE = 25 * 1000 * 1000
NO_OF_FILES_IN_A_REPO = 40

# INIT
github = GithubHandler()
processor = DataProcessor()

# LOGIN INPUTS
username = input('Username : ')
password = input('Password : ')

# DO LOGIN
if not github.login_and_init(username, password, NO_OF_FILES_IN_A_REPO):
    exit(0)

# TYPE OF SESSION
session_type = input('R/W/L : ').upper()

# LIST SESSION
if session_type == 'L':
    posts = github.get_list_of_posts()
    for i in posts:
        print(i)

# READ SESSION
elif session_type == 'R':

    # SESSION BASED INPUTS
    input_name = input('Name of the post : ')
    output_dir_path = input('Directory path to save at : ')

    # PROCESS    
    post_struct = github.get_post_struct(input_name)
    if not post_struct:
        exit(0)
    total_size_to_download = int(post_struct['_total_size'])
    total_size_downloaded = 0
    del post_struct['_total_size']
    for i in post_struct:
        processor.open_write_data_stream(output_dir_path, i)
        for j in post_struct[i]:
            chunk = github.download_data(j)
            total_size_downloaded += len(chunk)/2
            print("{0:.2f}%".format(total_size_downloaded * 100 / total_size_to_download))
            processor.write_data(chunk)
    processor.close_write_data_stream()
    
# WRITE SESSION
elif session_type == 'W':
    
    # SESSION BASED INPUTS
    input_name = input('Name for this post : ')
    input_dir_path = input('Directory path to upload : ')

    # PROCESS
    total_post_size = 0
    total_size_uploaded = 0
    file_list = processor.preprocess(input_dir_path)
    file_struct = {}
    for i in file_list:
        total_post_size += os.path.getsize(i)
    for i in file_list:
        file_path_from_base = i[len(input_dir_path)+1:]
        processor.open_read_data_stream(i, int(MAX_FILE_SIZE/2))
        chunk = processor.get_file_chunk()
        while chunk:
            total_size_uploaded += len(chunk)/2
            file_id = github.upload_data(chunk)
            print("{0:.2f}%".format(total_size_uploaded * 100 / total_post_size))
            if file_path_from_base in file_struct:            
                file_struct[file_path_from_base].append(file_id)
            else:
                file_struct[file_path_from_base] = [file_id]
            chunk = processor.get_file_chunk()
    github.add_to_index(input_name, file_struct, total_post_size)
    processor.close_read_data_stream()
