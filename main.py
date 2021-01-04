# Imports
from functools import partial
from tkinter import *
from tkinter import filedialog as fd
import os
import shutil
from PIL import ImageTk, Image
import matplotlib.pyplot as plt
import matplotlib.figure as mplfig
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from pandas import DataFrame
import fileinput
import sys
import getpass

# Global Photo List
photolist = {}  # Global dictionary holding all images names and inventories.


def popup_bonus(photoname):  # Popup when an image is successfully uploaded
    # Initialize popup
    win = Toplevel()
    win.wm_title("Success")
    winx = 400
    winy = 300
    win.minsize(winx, winy)
    win.maxsize(winx, winy)
    win.geometry("400x300+400+200")

    # Title of the popup
    message = Label(win, text="Image Uploaded Successfully", font=('Ariel', 20))
    message.pack(side=TOP, pady=10)

    # Create canvas
    canvas = Canvas(win, width=winx, height=winy)
    canvas.pack(side=LEFT)

    # Create photoname2 which is the img name + how to get to it
    photoname2 = "Images/"
    photoname2 += photoname

    # load the img to show a preview
    load = Image.open(photoname2)
    imgsize = 150
    load = load.resize((imgsize, imgsize), Image.ANTIALIAS)
    render = ImageTk.PhotoImage(load)
    img = Label(win, image=render)
    img.image = render
    img.place(x=((winx/2) - (imgsize/2)), y=((winy/2) - (imgsize/2)))

    # Exit button to close the popup window
    exitpop = Button(win, text="Okay", command=win.destroy, height=2, width=12)
    exitpop.place(x=(winx/2)-55, y=winy-60)


def UpdatePhotoList():  # returns the updated photolist (Set photolist = to it to use it properly)
    fmaster = open("master.txt", "r")  # Open File
    lines = fmaster.readlines()  # Get each line separately
    photolist = {}  # initialize to no images
    for line in lines:
        sepLine = line.split(",")  # Get each line seperated
        photolist[sepLine[0]] = int(sepLine[1])  # Add each line of file to Dictionary
    fmaster.close()  # Close file
    return photolist


def replaceLine(file, search, replace):  # Helper function to update the file (Searches file to find line and replace)
    for line in fileinput.input(file, inplace=1):
        if search in line:
            line = line.replace(search, replace)
        sys.stdout.write(line)


def AddtoFile(photo, inv):  # Update the file by either adding photo to file or updating inventory
    fmaster = open("master.txt", "r+")  # Append to File
    lines = fmaster.readlines()  # Get each line separately
    original = 1  # starts off being original line
    for line in lines:
        sepLine = line.split(",")  # Get each line seperated
        if sepLine[0] == photo:
            replaceLine("master.txt", f"{sepLine[0]},{sepLine[1]}",  f"{sepLine[0]},{int(sepLine[1])+inv}\n")
            original = 0  # photo already in file, not original
    if original:
        fmaster.writelines(f"{photo},{inv}\n")  # write to file only if it is original
    fmaster.close()  # Close file


def DownloadPhoto(photo):  # Open the photo, get the photo name, add the inventory,
    # Copy Image to folder
    username = getpass.getuser()  # Get username of computer
    download_path = "/Users/" + username + "/Downloads/"  # Get download directory from username
    shutil.copyfile(f"Images/{photo}", os.path.join(download_path, photo))


def OpenPhoto():  # Open the photo, get the photo name, add the inventory,
    # Open the photo
    file1 = fd.askopenfile(mode="r")
    fileaddress = file1.name

    # Get the photo name
    filename = ''
    for letter in fileaddress:
        filename += letter
        if letter == '/':
            filename = ''

    # Copy Image to folder
    images_path = os.path.dirname(os.path.realpath("Icons"))  # Find folder
    imgfolder_dir = images_path + "/Images"  # Find images folder
    shutil.copyfile(file1.name, os.path.join(imgfolder_dir, filename))

    # Update inventory of photo and add to master.txt
    AddtoFile(filename, 1)

    # Update screen and open success popup
    ChangeScreen(HomePage, window)
    popup_bonus(filename)


def clearMasterTxt(photolist):  # Code to clear the master.txt (Clear all Images in repository)
    for photo in photolist:
        # Delete from folder
        dir_path = "Images/"
        dir_path += photo
        os.remove(dir_path)
        # Delete from file/photolist
        deleteLine(photo, photolist[photo])
    ChangeScreen(HomePage, window) # Update window


def ChangeScreen(screen, frame):  # Change screen by destroying all widgets then rebuilding
    for widget in frame.winfo_children():
        widget.destroy()
    screen(window)


def deleteLine(search, searchInv):  # Delete a line in master.txt for changeInv function
    mfile = open("master.txt", "r")
    lines = mfile.readlines()
    mfile.close()

    search += f",{searchInv}\n"
    lines.remove(search)

    new_mfile = open("master.txt", "w+")
    for line in lines:
        new_mfile.write(line)
    new_mfile.close()


def changeInv(photo, screen, frame, operator, photolist):  # Change the inventory
    AddtoFile(photo, operator)
    photolist[photo] += operator
    # Delete from photolist
    if photolist[photo] < 1:
        deleteLine(photo, photolist[photo])
        # del photolist[photo]
        # DELETE FROM FOLDER
        # find the old directory of the image
        dir_path = "Images/"
        dir_path += photo
        os.remove(dir_path)
        ChangeScreen(screen, frame)
    else:
        ChangeScreen(screen, frame)
        # invlabel.config(text=f"Inventory: {photolist[photo]}")  # SUPER SAD. MAYBE FIGURE THIS OUT


def captureUserInput(win, userfield, photo):  # Capture user input (Helper for rename function)
    photolist = UpdatePhotoList()

    # Store the user input in new name
    newname = userfield.get()
    photoname = "Images/"
    photoname += photo

    # find the old directory of the image
    dir_path = os.path.dirname(os.path.realpath(photoname))
    dir_path += "/"
    dir_path += photo

    # create the new directory of the image
    newdir_path = dir_path[:-(len(photo))]
    newdir_path += newname
    os.rename(dir_path, newdir_path)

    # Update master.txt with new image name
    replaceLine("master.txt", f"{photo},{photolist[photo]}\n", f"{newname},{photolist[photo]}\n")

    # Update the tkinter window
    ChangeScreen(HomePage, window)

    win.destroy()

    # Some global variables
    global changephotolist
    changephotolist = newname


def renamephoto(photo):  # Rename function
    # Create temp window for user input
    win = Toplevel()
    win.wm_title("Rename Photo")
    winx = 400
    winy = 200
    win.minsize(winx, winy)
    win.maxsize(winx, winy)
    win.geometry("400x300+400+200")
    message = Label(win, text="Please Enter The New Name:", font=('Ariel', 20))
    message.pack(side=TOP, pady=10)

    # User Input field
    userfield = Entry(win)
    userfield.place(x=100, y=100)
    userfield.focus_set()

    # Button to close temp window
    exitpop = Button(win, text="Okay", command=lambda: captureUserInput(win, userfield, photo), height=2, width=12)
    exitpop.place(x=(winx / 2) - 55, y=winy - 60)


def printHomeImgs(bottomframe):  # Helper for the HomePage window to print all photos
    photolist = UpdatePhotoList()  # Update Imgs in photolist from master.txt

    icon_path = os.path.dirname(os.path.realpath("Icons"))  # Find Icon Path

    # Photo initialization for Inventory Icons
    plusicon_dir = icon_path + "/Icons/plusPS.png"
    plusicon = PhotoImage(file=plusicon_dir)
    plusiconformat = plusicon.subsample(15, 15)
    panelplus = Label(bottomframe, image=plusiconformat)
    panelplus.photo = plusiconformat
    minusicon_dir = icon_path + "/Icons/minusPS.png"
    minusicon = PhotoImage(file=minusicon_dir)
    minusiconformat = minusicon.subsample(15, 15)
    panelminus = Label(bottomframe, image=minusiconformat)
    panelminus.photo = minusiconformat

    col = -2  # As col increment by 2 at beginning, set to -2
    rowinv = 0  # Start in row 1 (0)

    # Huge FOR loop for each photo on dashboard
    for photo in photolist:
        col += 2  # Increment cols by 2 (some widgets take up 2 columns)

        # Determine the name of the photo (Accounts for lengthy names)
        global photolabel
        if len(photo) > 18:
            photolabel = Label(bottomframe, text=photo[0:18], font=('Ariel', 14, 'bold'))
        else:
            photolabel = Label(bottomframe, text=photo, font=('Ariel', 14, 'bold'))
        photolabel.grid(column=col, row=1+rowinv, pady=1, columnspan=2)

        # Rename Button Functionality
        rename = Button(bottomframe, text="Rename", command=lambda photo=photo: renamephoto(photo))
        rename.grid(column=col, row=5+rowinv, sticky=W, padx=2)

        # Load + resize the image
        photoname = "Images/"
        photoname += photo
        load = Image.open(photoname)
        imgsize = 150
        load = load.resize((imgsize, imgsize), Image.ANTIALIAS)
        render = ImageTk.PhotoImage(load)
        img = Label(bottomframe, image=render)
        img.image = render
        img.grid(column=col, row=3+rowinv, padx=5, pady=5, columnspan=2)  # Rowinv changes once 6 images are in 1st row

        # Display the inventory on dashboard
        global invlabel
        invlabel = Label(bottomframe, text=f"Inventory: {photolist[photo]}", font=('Ariel', 14, 'bold'))
        invlabel.grid(column=col, row=4+rowinv)

        # Increase inventory button
        invup = Button(bottomframe, image=panelplus.photo, relief="flat", border=1, bd=0, highlightthickness=0,
                       command=lambda photo=photo: changeInv(photo, HomePage, window, 1, photolist))
        invup.grid(column=col+1, row=4+rowinv, sticky=E)

        # Decrease inventory button
        invdown = Button(bottomframe, image=panelminus.photo,
                         command=lambda photo=photo: changeInv(photo, HomePage, window, -1, photolist))
        invdown.grid(column=col + 1, row=5+rowinv, sticky=E, padx=2)

        # Download button
        download = Button(bottomframe, text="Download",
                         command=lambda photo=photo: DownloadPhoto(photo))
        download.grid(column=col, row=6 + rowinv, sticky=W, padx=2)

        # If there are more than 6 photos, start printing on second row
        if col > 8 and rowinv == 0:
            col = -2
            rowinv = 6


def PrintMenuBar(topframe, color1):  # Helper function to print the Menu Bar
    photolist = UpdatePhotoList()

    icon_path = os.path.dirname(os.path.realpath("Icons"))  # Find Icon Path

    # Print the title
    title = Label(topframe, text="Image Repository", font=('Ariel', 30, 'bold'), bg=color1)
    title.place(x=380, y=5)

    # Initialize Photo for Home Button
    homeicon_dir = icon_path + "/Icons/home-icon.png"
    photohome = PhotoImage(file=homeicon_dir)
    photoimagehome = photohome.subsample(12, 12)
    panelhome = Label(topframe, image=photoimagehome)
    panelhome.photo = photoimagehome

    # Create button for Home Button
    homepage = Button(topframe, image=panelhome.photo, command=lambda: ChangeScreen(HomePage, window),
                      relief="flat", bg=color1, border=1, bd=0, highlightthickness=0)
    homepage.place(x=0, y=0)

    # Initialize Photo for Info Page Button
    infoicon_dir = icon_path + "/Icons/bar-icon.png"
    photobar = PhotoImage(file=infoicon_dir)
    photoimagebar = photobar.subsample(12, 12)
    panelbar = Label(topframe, image=photoimagebar)
    panelbar.photo = photoimagebar

    # Create button for InfoPage Button
    infopage = Button(topframe, image=panelbar.photo, command=lambda: ChangeScreen(InfoPage, window),
                      relief="flat", bg=color1, border=1, bd=0, highlightthickness=0)
    infopage.place(x=60, y=0)

    # Initialize Photo for Upload Button
    uploadicon_dir = icon_path + "/Icons/upload_icon.png"
    photoupload = PhotoImage(file=uploadicon_dir)
    photoimageupload = photoupload.subsample(11, 11)
    panelupload = Label(topframe, image=photoimageupload)
    panelupload.photo = photoimageupload

    # Create button for Upload Button
    upload1 = Button(window, image=panelupload.photo, command=OpenPhoto,
                     relief="flat", bg=color1, border=1, bd=0, highlightthickness=0)
    upload1.place(x=120, y=0)

    # Create button for clear master.txt Button
    clc = Button(window, text="Clear All", command=lambda: clearMasterTxt(photolist),
                      relief="flat", bg=color1, border=1, bd=0, highlightthickness=0)
    clc.place(x=180, y=20)


def sizeOfImg(filename):  # Find the size of an Img
    st = os.stat(filename)
    size = -999999
    suffex = ""
    if st.st_size < 1000000:
        size = float(st.st_size/1000)
        size = round(size, 2)
        suffex = " KB"
    else:
        size = float(st.st_size/1000000)
        size = round(size, 2)
        suffex = " MB"
    size = str(size)
    size += suffex
    return size


def truncate_keys(a, length):  # Truncate all of the keys for a dictionary
    return dict((k[:length], v) for k, v in a.items())


def SearchInventory(userfield):
    photolist = UpdatePhotoList()
    string = userfield.get()
    global searchedlist
    searchedlist = {}

    for photo in photolist:
        if string in photo:
            searchedlist[photo] = photolist[photo]

    ChangeScreen(InfoPage, window)


class InfoPage:
    def __init__(self, master):
        photolist = UpdatePhotoList()  # Update Imgs in photolist from master.txt

        master.geometry("1000x600+100+50")  # Initialize size of window
        # Control the Menu Bar
        color1 = "#4d95d4"  # Colour of background
        topframe = Frame(master, height=60, width=1000, bg=color1)
        topframe.pack(side=TOP)

        PrintMenuBar(topframe, color1)  # Helper function to print Menu Bar

        # Bottom frame is broken up into left and right
        bottomframe = Frame(master, height=540, width=1000)
        bottomframe.pack(anchor=SW)
        # Left
        leftframe = Frame(bottomframe, height=540, width=500)
        leftframe.place(x=0, y=0)
        # Right
        rightframe = Frame(bottomframe, height=540, width=500)
        rightframe.place(x=500, y=0)

        # Header on left frame (Search Inventory)
        infolabel = Label(leftframe, text="Search Inventory:", font=('Ariel', 20, 'bold'))
        infolabel.place(x=50, y=5)

        # User Input field
        userfield = Entry(leftframe)
        userfield.place(x=50, y=35)
        userfield.focus_set()

        # Button to close temp window
        searchbutton = Button(leftframe, text="Search", command=lambda: SearchInventory(userfield), height=1, width=6)
        searchbutton.place(x=250, y=40)

        # Print off all photos in photolist for Img Stats
        yinc = -20  # Start at y=0 (increments 20 at beginning)

        for photo in searchedlist:
            yinc += 25  # Increment the y pos of the next photo
            photoname = f"Images/{photo}"
            infolabel = Label(leftframe, text=f"{photo} (Inventory: {photolist[photo]}, {sizeOfImg(photoname)})\n",
                              font=('Ariel', 15))
            infolabel.place(x=50, y=60+yinc)

        # Split right frame in Top/Bottom frames
        # Top Frame (Top Inventories)
        rightup = Frame(rightframe, height=200, width=500)
        rightup.place(x=0, y=0)
        # Bottom Frame (Graph)
        rightdown = Frame(rightframe, height=300, width=500)
        rightdown.place(x=0, y=200)

        # Sort top inventories for top frame and print them
        sortedphotolist = dict(sorted(photolist.items(), key=lambda item: item[1]))  # sort
        toplabel = Label(rightup, text="Top Inventories", font=('Ariel', 20, 'bold'))  # header
        toplabel.place(x=50, y=5)
        counterorder = 0  # numbering initialization
        yinc = -20  # Start at y=0 (increments 20 at beginning)
        totalInv = 0  # Total amount of Inventory
        totalPhoto = 0  # Total amount of photos
        for photo in reversed(sortedphotolist):  # print biggest five inventories
            yinc += 25  # Increment the y pos of the next photo
            if counterorder > 4:
                break
            counterorder += 1
            infolabel = Label(rightup, text=f"{counterorder}. {photo} -> Inventory: {photolist[photo]}\n",
                              font=('Ariel', 15))
            infolabel.place(x=50, y=40+yinc)
            totalInv += photolist[photo]  # Increment total inventory
            totalPhoto += 1  # Increment total # of photos

        # Print total inventory
        numInventory = Label(leftframe, text=f"Total Inventory: {totalInv}", font=('Ariel', 15))
        numInventory.place(x=40, y=500)

        # Print total inventory
        numPhoto = Label(leftframe, text=f"Number of Photos: {totalPhoto}", font=('Ariel', 15))
        numPhoto.place(x=300, y=500)

        # Graph in bottom right frame
        trunc_photolist = truncate_keys(photolist, 8)
        data1 = {'Photo': (trunc_photolist.keys()),
                 'Inventory': (photolist.values())}
        # Put inventories and photo names into dataframe
        df1 = DataFrame(data1, columns=['Photo', 'Inventory'])
        figure1 = plt.Figure(figsize=(3, 3), dpi=100)  # Figure size
        ax1 = figure1.add_subplot(111)  # Add plot data
        bar1 = FigureCanvasTkAgg(figure1, rightdown)  # Create figure
        bar1.get_tk_widget().place(x=75, y=5)  # Place figure
        df1 = df1[['Photo', 'Inventory']].groupby('Photo').sum()  # Order data
        df1.plot(kind='bar', legend=False, ax=ax1)  # Type of graph + misc
        ax1.set_title('Photo w/ Inventory')  # Title of graph
        figure1.tight_layout()
        for tick in ax1.get_xticklabels():  # Axis ticks
            tick.set_rotation(45)


class HomePage:
    def __init__(self, master):
        global searchedlist
        searchedlist = photolist  # _---------------------------------------
        master.geometry("1000x600+100+50")  # Initialize size of window
        # Control the Menu Bar
        color1 = "#4d95d4"  # Colour of background
        # Split window into top(Menu Bar) and bottom(Image Dashboard) frame
        topframe = Frame(master, height=60, width=1000, bg=color1)
        topframe.pack(side=TOP)
        bottomframe = Frame(master, height=540, width=1000)
        bottomframe.pack(anchor=SW)

        # Print HomePage
        PrintMenuBar(topframe, color1)  # Helper function to print menu bar
        printHomeImgs(bottomframe)  # Helper function to print all images


def main():  # Main function
    global window  # Window is a global variable

    # intialize the tkinter window
    window = Tk()
    window.wm_title("Image Repository")
    HomePage(window)

    # Set size of the window to not change.
    windowx = 1000
    windowy = 600
    window.minsize(windowx, windowy)
    window.maxsize(windowx, windowy)

    # Start the mainloop
    window.mainloop()


main()
