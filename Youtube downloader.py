from pytubefix import YouTube,Playlist
import customtkinter as ctk
from PIL import Image, ImageTk
from requests import get
from os import environ
import webbrowser
from threading import Thread
from CTkMessagebox import CTkMessagebox
from logo import path

#khi ta import file logo.py, mặc định code trong file đó sẽ lập tức được chạy
#file logo chứa dữ liệu về ảnh ytdownloaderlogo.ico, và file ảnh sẽ được tạo, viết dữ liệu ra
#file logo ở %temp%
#path chính là đường dẫn tới logo, mục đích import là để dùng cho lệnh iconbitmap ở dưới



class VideoBox(ctk.CTkFrame):
    # Tạo ra frame chứa các thông tin là video, rồi sau đó đặt frame vào dòng thứ 2 của main window - vùng chứa các video

    def __init__(self,master,Video_url):
        super().__init__(master= master, fg_color="#181818", height = 120,bg_color="transparent")# khởi tạo ra frame, cùng các đặc tính như màu, chiều cao...
        self.pack(expand = True, fill = "x",padx =3,pady = 2) # đặt luôn frame đó vào trong dòng dòng thứ 2 của main window
        self.pack_propagate(False) # chống cho frame tự resize
        self.video = YouTube(Video_url) # dùng class Youtube để lấy thông tin video
        self.thumbnail_url = self.video.thumbnail_url # lấy url của thumbnail
        self.title = self.video.title # lấy title video
        self.image = Image.open(get(self.thumbnail_url,stream= True).raw).resize((160,90)) # dùng hàm get của module request để lấy dữ liệu của ảnh thumbnail về, sau đó dùng Image để mở ra
        self.tk_image = ImageTk.PhotoImage(self.image) # bién đối tượng ảnh vừa mở thành ImageTK
        self.image_button = ctk.CTkButton(self, text= "",image = self.tk_image,corner_radius=0,fg_color= "#222222",hover_color= "gray", command= lambda:webbrowser.open(Video_url)) #tạo ra một cái nút, có ảnh là thumbnail của video, và khi ấn vào sẽ mở luôn video đó trên trình duyệt
        self.image_button.pack(side = "left",padx = 10) # đặt cái nút thumbnail xuống
        self.check = ctk.BooleanVar(value=True) # ở trên tool bar của mainwindow, có các nút để áp dụng chức năng 1 loạt, như download 1 loạt hay delete 1 loạt
                                                # việc thêm 1 biến check ở đây, để lưu giá trị việc 1 video có đang được chọn hay không, rồi khi dùng các chức năng của tool bar sẽ kiểm tra biến này
        self.streambox_value = [] # một list để lưu text của stream
        self.resolution = {} # độ phân giải: các stream
        # đây là một từ điển có dạng { <string> : class:stream } mục đích là khi người dùng chọn text từ danh sách các stream thì sẽ lấy ra stream tương ứng với text
        
        
        try: # thử lấy các stream download của video, nếu không thể lấy stream, tức không có quyền truy cập. Trong tình huống đó sẽ biến title của video thành lỗi để hiển thị
            for stream in self.video.streams.filter(file_extension="mp4"): # vì một lý do nào đó, file âm thanh hay video thì sẽ đều có file extension là mp4, nên dùng để lọc luôn
                
                name = str(stream) # biến stream thành dạng text, và add text vào danh sách các lựa chọn
                self.resolution[name] = stream # thêm texta và stream vào dictionary
                self.streambox_value.append(name) # add vào list streambox để đưa vào combo box
        except Exception as e:
            self.title = str(e)
        self.stream = None


        
        self.detail_frame_setup()

    def callback1(self,event): #hàm của combobox: khi chọn 1 stream sẽ đặt lại self.stream và set nút download button từ disable về normal
        self.stream = self.resolution[event]
        self.dowloadbutton.configure(state = ctk.NORMAL)
    
    def detail_frame_setup(self):
        self.detail_frame = ctk.CTkFrame(self,fg_color="transparent")
        self.detail_frame.pack(side = "left",fill = "both",expand = True)
        #bên cạnh hình thumbnail của video, có 1 frame khác để chứa các thông tin như title, combo box và nút tải, xoá
        
        ctk.CTkEntry(self.detail_frame,
                     textvariable=ctk.StringVar(value=self.title),
                     state= "readonly",
                     font=("Arial",20),
                     fg_color="transparent",
                     corner_radius= 0,
                     border_width=0).pack(fill = "x",pady = 10) # set title, dùng entry với state readonly để có thể viết ra các title dài
        self.checkbox = ctk.CTkCheckBox(self.detail_frame,text = "",hover_color= "gray",variable=self.check) # tạo check box
        self.checkbox.pack(side = "left",padx = 7)
        
        
        self.stream_box = ctk.CTkComboBox(self.detail_frame,state="readonly",command=self.callback1) # tạo combo box để chọn stream
        self.stream_box.configure(values = self.streambox_value)
        self.stream_box.pack(side = "right",expand = True, fill = "x",padx = 10)
        self.dowloadbutton = ctk.CTkButton(self.detail_frame,
                                           text= "📥",
                                           fg_color="#222222",
                                           hover_color="gray",
                                           font = ("Arial",16), 
                                           width= 20,state=ctk.DISABLED,
                                           command= lambda: Thread(target = lambda: self.stream.download()).start()) # thêm nút download
        self.deletebutton = ctk.CTkButton(self.detail_frame,text= "❌",fg_color="#222222",hover_color="gray",font = ("Arial",16), width= 20,command= self.destroy) # thêm nút xoá box
        self.dowloadbutton.pack(side = "right")
        self.deletebutton.pack(side = "right")

    def download(self):
        if self.check.get() == True: #kiểm tra xem biến check có đang là True không
            if self.stream != None: # nếu có stream rồi thì download
                Thread(target= self.stream.download).start() 
            else: # nếu chưa có, thì mặc định lấy chất lượng cao nhất và tải
                Thread(target= self.video.streams.get_highest_resolution().download).start()
        
        # tạo một thread riêng biệt và khởi động để khi thread download video, ta vẫn có thể thao tác các việc khác trong app

    def delete(self):
        if self.check.get() == True:
            self.destroy()

class YoutubeDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Youtube Downloader") # đặt title
        self.geometry("900x450") # cài đặt độ rộng cửa sổ
        self.iconbitmap(path) # đặt logo logo
        self.minsize(900,450) # đặt độ rộng cửa sổ min
        #cài đặt số dòng
        self.rowconfigure(0,weight=1,uniform="a") # dòng 1 nhỏ ở trên cùng - thanh công cụ
        self.rowconfigure(1,weight=5,uniform="a") # dòng 2 là frame to ở dưới, nơi chứa các videos

        # cài đặt số cột - 1 cột duy nhất
        self.columnconfigure(0,weight=1,uniform="a")
    
    def toolframe(self):
        self.tool_frame = ctk.CTkFrame(self,fg_color="#222222",corner_radius=0) # tạo ra một frame, đặt ở dòng đầu tiên của main window
        self.tool_frame.grid(row = 0,sticky = "news")                           # grid frame vừa tạo
        self.download_button = ctk.CTkButton(self.tool_frame,
                                             text= "📥",
                                             fg_color="#222222",
                                             hover_color="gray",
                                             font = ("Arial",28), 
                                             width= 40,height=40,
                                             border_color="gray",
                                             border_width=2,
                                             corner_radius=0,
                                             command=self.download_func)        # tạo nút download
        self.download_button.pack(side = "left",padx = 15)                      # đặt nút download
        self.delete_button = ctk.CTkButton(self.tool_frame,
                                           text= "❌",
                                           fg_color="#222222",
                                           hover_color="gray",
                                           font = ("Arial",28), 
                                           width= 40,
                                           height=40,
                                           border_color="gray",
                                           border_width=2,
                                           corner_radius=0,
                                           command=self.delete_func)            # tạo nút delete
        self.delete_button.pack(side = "left",padx = 15)                        # đặt nút delete
        self.add_button = ctk.CTkButton(self.tool_frame,
                                        text= "➕",
                                        fg_color="#222222",
                                        hover_color="gray",
                                        font = ("Arial",28), 
                                        width= 40,height=40,
                                        border_color="gray",
                                        border_width=2,
                                        corner_radius=0
                                        ,command= AddURL)                       # tạo nút để thêm video
        self.add_button.pack(side = "left",padx = 15)                           # đặt nút thêm video

        self.multilink = ctk.CTkButton(self.tool_frame,
                                       text= "📃",
                                       fg_color="#222222",
                                       hover_color="gray",
                                       font = ("Arial",28), 
                                       width= 40,
                                       height=40,
                                       border_color="gray",
                                       border_width=2,
                                       corner_radius=0,
                                       command= MultiLink)                      # tạo nút thêm nhiều video một lúc
        self.multilink.pack(side = "left",padx = 15)                            # đặt nút
    
    def delete_func(self):
        for box in self.list_frame.winfo_children():
            box.delete()
    
    def download_func(self):
        for box in self.list_frame.winfo_children():
            box.download()
    
    def listframe(self):
        self.list_frame = ctk.CTkScrollableFrame(self,fg_color="transparent")
        self.list_frame.grid(row = 1,sticky = "news")
        
    
    def addvideo(self,url):
        Thread(target= lambda: VideoBox(self.list_frame,url)).start()
    
    def run(self):
        # chạy lần lượt các mục tool frame, list frame và sau đó bật mainloop

        self.toolframe() # hàm này chứa code cho các đối tượng ở tool bar
        self.listframe() # hàm này chứa code cho các đối tượng ở list các videos
        # thuật toán chính:
        # khi bấm nút addvideo và đưa url vào, hàm addvideo() sẽ được chạy, với tham số là url
        # sau đó thì tham số url sẽ được đưa vào class VideoBox
        
        
        self.mainloop()

class AddURL(ctk.CTkToplevel): # tạo một cửa sổ để nhập và thêm video
    def __init__(self):
        super().__init__()
        # self.attributes("-toolwindow",True)
        self.iconbitmap(path)
        self.after(200,lambda: self.iconbitmap(path))
        self.geometry("300x100")
        self.attributes("-topmost",True)
        self.title("Add video")
        self.minsize(300,100)
        ctk.CTkLabel(self,text="Enter video link or playlist link").pack()
        self.entry = ctk.CTkEntry(self)
        self.entry.pack(fill = "x",padx = 10, expand = True)
        button = ctk.CTkButton(self,text="add",fg_color="#222222",hover_color="gray",command=self.add,border_width=2)
        button.pack(expand = True)
    def add(self):
        url = self.entry.get()
        try: # dùng cấu trúc này để thử xem có phải url của video youtube không
            YouTube(url) # dòng này sẽ raise error nếu url không hợp lệ
            app.addvideo(url)
            self.destroy()
            return
        except: # nếu không phải thì thử tiếp qua playlist
            pass  
        try:
            playlist =  Playlist(url) # dòng này sẽ raise error nếu url không hợp lệ
            for video in playlist.videos:
                app.addvideo(video.watch_url)
            self.destroy()         
        except: # vẫn không phải, thì sẽ đưa ra msg box báo lỗi
            CTkMessagebox(title="Error",icon="cancel",message="Invalid URL")
            self.destroy()
            return       

class MultiLink(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.iconbitmap(path)
        self.after(200,lambda: self.iconbitmap(path))
        # self.attributes("-toolwindow",True)
        self.geometry("600x400")
        self.attributes("-topmost",True)
        self.title("Add video")
        self.minsize(600,400)
        self.text = ctk.CTkTextbox(self)
        self.text.pack(expand = True,fill = "both")
        button = ctk.CTkButton(self,text="add",fg_color="#222222",hover_color="gray",command=self.add,border_width=2)
        button.pack()
    
    def add(self):
        url = self.text.get("1.0",ctk.END)
        url = url.split("\n")
        for i in url:
            try:
                YouTube(i)
                app.addvideo(i)
            except:
                pass
        self.destroy()       

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = YoutubeDownloader()
    app.run()
