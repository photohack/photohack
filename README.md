# foo() photo

![](https://ballzbeatz.com/wp-content/uploads/2018/01/Foo-Fighters-Flashy-Logo-Vinyl-Decal-Sticker.jpg)

Project for PhotoHack MSK 2019 by team "foo() Fighters"
=============

REQUERIMENTS:
- Python 3.6 (https://www.python.org/downloads/) and pip
- Go (https://golang.org/doc/install)
- Windows (to install packages from .bat; or just copy commands from it in Linux)

If you want to local run foo(photo), you should save the repo on your desktop and then install all necessary packages. Go to cmd and type:

> cd path/to/git/photohack
> install_requirements.bat

<abbr title="Hyper Text Markup Language">Python packages will be installed to your global python directory</abbr>

Then run app and local server for result:
> python app.py
> python -m http.server 7000

Information about usage you can find in section "Описание"

### Performance

| Cores  | Description  | Time |
| :------------ |:---------------:| -----:|
| 4  (local)    | 2 img 800*800 (400 iters)| 45 sec |
| 12 (server AWS/GCP)     | 2 img 800*800 (400 iters)       |   12 sec |
| 4 (local) | 4 img  800*800 (400 iters)   |    97 sec |
| 12 (server AWS/GCP)| 4 img  800*800 (400 iters)   |    26 sec |

Examples:
![](https://github.com/photohack/photohack/blob/master/static/img/gif1.gif)
![](https://github.com/photohack/photohack/blob/master/static/img/gif2.gif)

Screenshots:
![](https://github.com/photohack/photohack/blob/master/static/img/sc1.jpg)
![](https://github.com/photohack/photohack/blob/master/static/img/sc2.jpg)

### End
