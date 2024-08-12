import os
import shutil
from progress.bar import Bar

def IncorporaDataset(folder_path, output_folder):
    folder_name_para_barra = folder_path.rsplit("\\", 1)[1]
    folder_path = os.path.join(folder_path, "labels")

    txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    bar = Bar('Processando {}:'.format(folder_name_para_barra), max=len(txt_files))

    for txt_file in txt_files:
        file_path = os.path.join(folder_path, txt_file)
        bar.next()

        with open(file_path, 'r') as file:
            first_chars_set = set(line[0] for line in file.readlines())
            
            first_chars = list(first_chars_set)

        if len(first_chars) == 1:
            folder_name = first_chars[0]
            output_folder_path_lbl = os.path.join(output_folder, folder_name + "/labels")
            output_folder_path_img = os.path.join(output_folder, folder_name + "/images")
        elif len(first_chars) > 1:
            folder_name = "MultiClass"
            output_folder_path_lbl = os.path.join(output_folder, folder_name + "/labels")
            output_folder_path_img = os.path.join(output_folder, folder_name + "/images")
        else:
            folder_name = "Empty"
            output_folder_path_lbl = os.path.join(output_folder, folder_name + "/labels")
            output_folder_path_img = os.path.join(output_folder, folder_name + "/images")

        os.makedirs(output_folder_path_lbl, exist_ok=True)
        os.makedirs(output_folder_path_img, exist_ok=True)

        img_file = txt_file.rsplit(".",1)[0] + ".jpg"
        file_path_img = file_path.rsplit("\\", 2)[0] + "/images2/" + img_file

        #Checar se existe o arquivo com mesmo nome no dataset ja
        nome_final_output_image = safeSeExistePasta(img_file, output_folder_path_img)
        nome_final_output_label = safeSeExistePasta(txt_file, output_folder_path_lbl)

        # Confirma se os nomes finais estão iguais ou existe alguma inconsistencia(nao existe 1 dos dois)
        if nome_final_output_image.rsplit(".",1)[0] == nome_final_output_label.rsplit(".",1)[0]:
            output_file_path_lbl = os.path.join(output_folder_path_lbl, nome_final_output_label)
            output_file_path_img = os.path.join(output_folder_path_img, nome_final_output_image)
            #print(output_file_path_img)
            shutil.copy(file_path, output_file_path_lbl)
            shutil.copy(file_path_img, output_file_path_img)
        else:
            print("Erro de inconsistencia de arquivos no: {}".format(img_file.rsplit(".",1)[0]))
            print("label: {} ||| image: {} \n -----------".format(nome_final_output_label, nome_final_output_image))
    bar.finish()

def safeSeExistePasta(arquivo, path):
    if arquivo in [x for x in os.listdir(path)]:
        novo_nome = arquivo.rsplit(".",1)[0] + "_novo."
        arquivo = novo_nome + arquivo.rsplit(".",1)[1]
        return arquivo
    else:
        return arquivo
    

