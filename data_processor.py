import os
import binascii

class DataProcessor:

    def preprocess(self, dir_path):
        file_list = []
        open_list = [os.path.join(dir_path, i) for i in os.listdir(dir_path)]
        i = 0
        while i < len(open_list):
            if os.path.isdir(open_list[i]):
                for j in os.listdir(open_list[i]):
                    open_list.append(os.path.join(open_list[i], j))
            else:
                file_list.append(open_list[i])
            i += 1
        return file_list

    def open_read_data_stream(self, file_path, chunk_size):
        if hasattr(self, 'open_file') and not self.open_file.closed:
            self.open_file.close()
        self.open_file = open(file_path, 'rb')
        self.chunk_size = chunk_size

    def close_read_data_stream(self):
        if hasattr(self, 'open_file') and not self.open_file.closed:
            self.open_file.close()        
    
    def get_file_chunk(self):
        chunk = self.open_file.read(self.chunk_size)
        if chunk:
            chunk = binascii.hexlify(chunk).decode('utf-8')
            return chunk        
        return

    def open_write_data_stream(self, dir_path, file_name):
        if hasattr(self, 'open_file') and not self.open_file.closed:
            self.open_file.close()
        self.open_file = open(os.path.join(dir_path, file_name), 'wb')

    def write_data(self, chunk):
        data = binascii.unhexlify(chunk.encode('utf-8'))
        self.open_file.write(data)

    def close_write_data_stream(self):
        if hasattr(self, 'open_file') and not self.open_file.closed:
            self.open_file.close()
        
        
