# voronoi_project
Project for Algorithm midterm.

原本預計在UbuntuOS以**Python-kivy**套件實做Voronoi diagram， 無奈在打包成.exe時發生套件缺失而無法順利進行測試，只能轉用Python內建的**tkinter**進行實做。
I was started by using **Python-kivy** in UbuntuOS to do this Voronoi diagram project, since that the relevant kit doesn't support packaging into ".exe" with WindowsOS, I switched to Python's built-in **tkinter**.

相關心得詳見Blog:
https://yctseng1227.github.io//2019/12/08/20191208-voronoi-diagram-project/

.
+-- .vscode
+-- pic                     # 存放報告用相關圖片檔
+-- voronoi_kivy            # 原本使用的Python圖形套件
|   +-- image.png           # example image
|   +-- main.kv
|   +-- main.py
|   +-- result.txt          # Output file
|   +-- simple.txt          # Input file
+-- voronoi_tkinter
|   +-- .gitgnore
|   +-- canvas.py           # main implement
|   +-- final_merge.py      # merge by all source code
|   +-- hard_testcase.txt   # Input file
|   +-- main2.exe           # run in WindowsOS
|   +-- main2.py            # main interface
|   +-- result.txt          # Output file
|   +-- simple_testcase.txt # Input file (my testcase)
+-- .gitgnore
+-- README.md
+-- requirements.txt        # environments setting