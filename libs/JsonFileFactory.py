import json
import os

class JsonFileFactory:
    def write_data(self, arr_data, filename):
        """
        Converts a list of objects OR dicts to JSON and writes it to the specified file.
        """
        try:
            new_list = []
            for item in arr_data:
                if isinstance(item, dict):
                    # Nếu item là dict, ta giữ nguyên
                    new_list.append(item)
                else:
                    # Nếu item là object, ta dùng item.__dict__
                    new_list.append(item.__dict__)

            json_string = json.dumps(
                new_list,
                default=str,
                indent=4,
                ensure_ascii=False
            )
            with open(filename, 'w', encoding='utf-8') as json_file:
                json_file.write(json_string)
            return True
        except Exception as e:
            print("Error writing data to JSON:", e)
            return False

    def read_data(self, filename, ClassName):
        """
        Reads a JSON string from a file and reconstructs objects of type ClassName
        or returns list of dict if ClassName == dict.
        """
        if not os.path.isfile(filename):
            return []
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)  # data thường là list

            if not isinstance(data, list):
                return []

            # Nếu ta yêu cầu đọc dict, trả về list[dict] luôn
            if ClassName is dict:
                return data

            arr_data = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                try:
                    obj = ClassName(**item)
                    arr_data.append(obj)
                except TypeError as e:
                    print(f"Error constructing {ClassName.__name__} from item:", item, "->", e)

            return arr_data
        except Exception as e:
            print("Error reading data from JSON:", e)
            return []
