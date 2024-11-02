import os.path


class Banner:
    def __init__(self, content=None, path='./'):
        if not content:
            content = Banner.load(path)
        self.content = content

    @staticmethod
    def load(path='./'):
        """
        加载banner文件
        Args:
            path: 如果是一个文件，则读取文件中的内容，否则扫描path目录下的banner作为扩展名的文件，读取第一个.banner文件

        Returns:
            加载的banner文件内容或者错误信息
        """
        if os.path.exists(path):
            if os.path.isfile(path):  # 检查path是否为文件
                with open(path, 'r') as file:
                    return file.read()
            elif os.path.isdir(path):  # 检查path是否为目录
                for entry in os.listdir(path):
                    full_path = os.path.join(path, entry)
                    if entry.endswith('.banner') and os.path.isfile(full_path):
                        with open(full_path, 'r') as file:
                            return file.read()
                return "No .banner file found in the directory."
        else:
            return "The specified path does not exist."

    def show(self):
        print(self.content)
