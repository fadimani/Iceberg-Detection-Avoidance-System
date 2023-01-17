import PySimpleGUI as sg
import os
from PIL import Image, ImageTk
import io
from project import *

# Get the folder containin:g the images from the user
folder = sg.popup_get_folder('Image folder to open', default_path='.')
if not folder:
    sg.popup_cancel('Cancelling')
    raise SystemExit()

# PIL supported image types
img_types = (".png", ".jpg", "jpeg", ".tiff", ".bmp")

# get list of files in folder
flist0 = os.listdir(folder)

# create sub list of image files (no sub folders, no wrong file types)
fnames = [f for f in flist0 if os.path.isfile(os.path.join(folder, f)) and f.lower().endswith(img_types)]

num_files = len(fnames)                # number of images found
if num_files == 0:
    sg.popup('No files in folder')
    raise SystemExit()

del flist0                             # no longer needed



def get_img_data(f, maxsize=(1000, 700), first=False):
    """Generate image data using PIL
    """
    img = Image.open(f)
    img.thumbnail(maxsize)
    if first:
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)
# ------------------------------------------------------------------------------


# make these 2 elements outside the layout as we want to "update" them later
# initialize to the first file in the list
filename = os.path.join(folder, fnames[0])  # name of first file in list
image_elem = sg.Image(data=get_img_data(filename, first=True))
filename_display_elem = sg.Text(filename, size=(80, 3),font="Helvitica 20")
file_num_display_elem = sg.Text('File 1 of {}'.format(num_files), size=(15, 1))

# define layout, show and read the form
col = [
       [image_elem]]

col_files = [[sg.Listbox(values=fnames, change_submits=True, size=(60, 30), key='listbox')],
             [sg.Button('Next', size=(8, 2)), sg.Button('Prev', size=(8, 2)),sg.Button('Analyse', size=(8, 2)), file_num_display_elem]]

layout = [[sg.Text('Iceberg Detection and Avoidance System',justification='center', size=(80, 1),font="Helvitica 30 bold")],[sg.Column(col_files), sg.Column(col)]]

window = sg.Window('Iceberg Detection and Avoidance System', layout,size=(1500, 700),icon=sg.Image('logo.jpg'), return_keyboard_events=True,
                   location=(0, 0), use_default_focus=False,grab_anywhere=True)

# loop reading the user input and displaying image, filename
i = 0
while True:
    # read the form
    event, values = window.read()
    print(event, values)
    # perform button and keyboard operations
    if event == sg.WIN_CLOSED:
        break
    elif event in ('Next', 'MouseWheel:Down', 'Down:40', 'Next:34'):
        i += 1
        if i >= num_files:
            i -= num_files
        filename = os.path.join(folder, fnames[i])
    elif event in ('Prev', 'MouseWheel:Up', 'Up:38', 'Prior:33'):
        i -= 1
        if i < 0:
            i = num_files + i
        filename = os.path.join(folder, fnames[i])
    elif event == 'Analyse':
        filename = os.path.join(folder, fnames[i])
        #print("analysing bybyy:")
        #print(values)
        print(type(filename))
        WIN = pygame.display.set_mode((WIDTH, WIDTH))
        main(WIN, WIDTH,filename)
    elif event == 'listbox':            # something from the listbox
        f = values["listbox"][0]            # selected filename
        filename = os.path.join(folder, f)  # read this file
        i = fnames.index(f)                 # update running index
    else:
        filename = os.path.join(folder, fnames[i])

    # update window with new image
    image_elem.update(data=get_img_data(filename, first=True))
    file_num_display_elem.update('File {} of {}'.format(i+1, num_files))

window.close()