##
##      CODIGO PARA IMG AUGMENTATION + LABELS
##      USAR COM O VENV DE PYTHON 3.8
##
##

import imgaug as ia
import imgaug.augmenters as iaa
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage
import cv2, os, shutil, random


ia.seed(4)

##  Paths ------------
_lab_in = "labels"#input("Qual a pasta de labels?\n")
_img_in = "images"#input("Qual a pasta de imgs?\n")
cwd = os.getcwd()
_path_labels = os.path.join(cwd, _lab_in)
img_path = os.path.join(cwd, _img_in)
_path_save_labels = os.path.join(cwd, "AUG_lbls")
_path_save_imgs = os.path.join(cwd, "AUG_imgs")
_path_save_imgs_debug = os.path.join(cwd, "AUG_debug")

if not os.path.exists(_path_save_labels):
    os.makedirs(_path_save_labels, exist_ok=True)

if not os.path.exists(_path_save_imgs):
    os.makedirs(_path_save_imgs, exist_ok=True)

if not os.path.exists(_path_save_imgs_debug):
    os.makedirs(_path_save_imgs_debug, exist_ok=True)

## -----------------


### FUNÇÕES AUXILIARES ------
def wh2xy(x_center,y_center,w,h):
    x1, y1 = x_center-w/2, y_center-h/2 #Gera os pontos no topo a esquerda
    x2, y2 = x_center+w/2, y_center+h/2 #Gera os pontos na parte de baixo a direita
    return x1, y1, x2, y2

def coordinadasXtamanho(x1,y1,x2,y2,iw,ih):
    x1_, y1_, x2_, y2_ = iw*x1, ih*y1, iw*x2, ih*y2
    return [x1_, y1_, x2_, y2_]

#ERRO TA AQUI
def xy2wh_scaledown(z, ih, iw, cls):
    center_x = (z.x1 +z.x2)/2
    center_y = (z.y1 +z.y2)/2
    width_bb = z.x2 - z.x1
    height_bb = z.y2 - z.y1
    x, y = center_x/iw, center_y/ih
    w, h = width_bb/iw, height_bb/ih
    return [cls, x, y, w, h]


def get_bbs(path_txts):
    lista_completa = []
    for i_txt in sorted(os.listdir(path_txts)):
        _i_txt = os.path.join(path_txts, i_txt)
        with open(_i_txt) as t:
            lista_bbs = []
            bbs = [line.rstrip().split(' ') for line in t]
            for xx in bbs:
                x = [float(l) for l in xx]
                x1, y1, x2, y2 = wh2xy(x[1],x[2],x[3],x[4])
                x[1] = x1
                x[2] = y1
                x[3] = x2
                x[4] = y2
                lista_bbs.append(x)
        idtup = (i_txt.rsplit('.',1)[0], lista_bbs)
        lista_completa.append(idtup)
    return lista_completa
    
#   ESTRUTURA DA LISTA DE LABELS
#   labels_lista[x] = cada imagem
#   labels_lista[x][y] = y: 0 -> nome do arquivo de img; y: 1 -> lista com labels
#   labels_lista[x][y][z] = z -> lista do Bounding Box z encontrado na img: [classe, x, y, x2, y2]
#   


## ------------------------



### MAIN  -------------------------


#classe = input("Classe trabalhada em index?\n")
img_list = []

aug_num = int(input("Quantos augumentations por imagem?:\n"))
porcent_imgs = 100#int(input("Qual a porcentagem de imagens que devem ter data augmenation?\n"))
print('')


load_bbs = get_bbs(_path_labels)


aag = iaa.SomeOf((1,3), [
    ##Sequencia de augmentations 1
    iaa.Multiply((0.5, 1.2)),                          # Multiplicação do brilho da imagem
    iaa.SaltAndPepper(0.02),                            # Ruido Sal e Pimenta
    iaa.JpegCompression(compression=(5, 25)),           # Compresão JPEG
    iaa.MotionBlur(k=4),                                # Blur de movimento (Simula uma imagem tremida ou tirada as pressas)
    iaa.GaussianBlur(sigma=(0.75, 1.25)),                 # Blur Gaussiano
    #iaa.Add((-40,15)),                                 # Adição do nivel de brilho da imagem
    #iaa.GammaContrast((0.85, 1.15))                     # Mudança do contraste
], random_order=True)

bbg = iaa.SomeOf((2,4), [
    ##Sequencia de augmentations 2
    #iaa.Cutout(fill_mode="constant", cval=(0, 255)),   # Adiciona blocos para "obstruir" a imagem
    #iaa.Affine(rotate=(135, 135)),                       # Rotaciona a imagem
    #iaa.PerspectiveTransform(scale=(0.05, 0.15)),       # Transforma a perspectiva adicionando uma rotação no eixo Z
    #iaa.Fliplr(1),                                      # Espelha a imagem horizontalmente, 1 = todas as imagens que passar
    #iaa.Flipud(1)                                       # Espelha a imagem verticalmente, 1 = todas as imagens que passar
    #iaa.Multiply((0.5, 1.2)),                          # Multiplicação do brilho da imagem
    iaa.SaltAndPepper(0.02),                            # Ruido Sal e Pimenta
    iaa.JpegCompression(compression=(10, 40)),           # Compresão JPEG
    iaa.MotionBlur(k=4),                                # Blur de movimento (Simula uma imagem tremida ou tirada as pressas)
    iaa.GaussianBlur(sigma=(0.65, 1.35)),                 # Blur Gaussiano
    iaa.Add((-50,30)),                                 # Adição do nivel de brilho da imagem
    
],random_order=True)

#aug1 = iaa.Sequential([aag, iaa.Affine(scale=0.85),bbg, iaa.EdgeDetect(alpha=(1))])




bb_count = 0
#rodar img por img
for img in os.listdir(img_path):    
    classe = []
    load_bbs2 = load_bbs
    key = 0
    print(str(bb_count) + " / " + str(len(load_bbs2)))
    img_cv2 = cv2.imread(os.path.join(img_path, img),1)
    img_nm = img.rsplit('.',1)[0]
    bbs_l = []
    for t in load_bbs2:
        if img_nm == t[0]:
            bb_count = bb_count + 1
            if len(t[1]) == 0:
                key = 1
            for x in t[1]:
                classe.append(int(x[0]))
                z = coordinadasXtamanho(x[1], x[2], x[3], x[4], img_cv2.shape[1], img_cv2.shape[0])
                bbs_l.append(BoundingBox(x1=z[0], y1=z[1], x2=z[2], y2=z[3], label=int(x[0])))
            break
    bbs = BoundingBoxesOnImage(bbs_l, shape=img_cv2.shape)
    load_bbs2.remove(t)
    n_vezes = 0
    for rng in range(0,aug_num+1):
        n_vezes = n_vezes + 1
        rotVal = int(45 * n_vezes) 
        aug = iaa.Sequential([iaa.Affine(scale=0.85), aag, iaa.Affine(rotate=rotVal)])
        if n_vezes > aug_num:
            rotVal = int(45 * (n_vezes - aug_num)) 
            aug == iaa.Sequential([iaa.Affine(scale=0.85), bbg, iaa.Affine(rotate=rotVal)])
        if key == 1:
            image_aug = aug(image=img_cv2)
            cv2.imwrite(os.path.join(_path_save_imgs, (str(rng)+"_AUG_"+img)), image_aug)
        else:
            image_aug, bbs_aug = aug(image=img_cv2, bounding_boxes=bbs)
            bbs_aug = bbs_aug.remove_out_of_image().clip_out_of_image()
            img_nova = bbs_aug.draw_on_image(image_aug, size=2, color=[0, 0, 255])
            cv2.imwrite(os.path.join(_path_save_imgs, (str(rng)+"_AUG_"+img)), image_aug)
            cv2.imwrite(os.path.join(_path_save_imgs_debug, (str(rng)+"_AUG-DB_"+img)), img_nova)
            final_labls = []
            for iddex,i in enumerate(bbs_aug):
                z = xy2wh_scaledown(i,image_aug.shape[0],image_aug.shape[1], classe[iddex])
                final_labls.append(z)
            with open(os.path.join(_path_save_labels,(str(rng)+"_AUG_"+img_nm+".txt")), "w") as f:
                for i in final_labls:
                    f.write("{} {} {} {} {}\n".format(str(int(i[0])), str(i[1]), str(i[2]), str(i[3]), str(i[4])))
              

## -------------------------------------------

## Essa parte é so para mover os arquivos criados para a pasta do dataset, não é essencial
mov_op = "s"#input("Mover os aquivos para as suas pasta originais? (S/N)\n")
if mov_op.lower() == "s":
    idox = 0
    max_im = len(os.listdir(_path_save_imgs))
    for img in os.listdir(_path_save_imgs):
        print("{} / {}".format(idox, max_im))
        _img = os.path.join(_path_save_imgs, img)
        shutil.move(_img, os.path.join(img_path, img))
        idox = idox + 1
    idox = 0
    for txt in os.listdir(_path_save_labels):
        print("{} / {}".format(idox, max_im))
        _txt = os.path.join(_path_save_labels, txt)
        shutil.move(_txt, os.path.join(_path_labels, txt))
        idox = idox + 1

print("Pronto!")


### FINAL