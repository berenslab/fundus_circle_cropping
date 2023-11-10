import os

if __name__ == "__main__":
    data_path = "../data/images"
    list_file_names = os.listdir(data_path)
    
    list_file_names_wo_extension = [file.split('.')[0] for file in list_file_names]

    with open("../data/ids.lst", "w") as outfile:
        outfile.write("\n".join(list_file_names_wo_extension))