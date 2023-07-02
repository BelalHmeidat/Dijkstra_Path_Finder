import os

import customtkinter as ctk
from customtkinter import filedialog, CTkImage
from PIL import Image, ImageTk
import dijkstra2
import tkinter as tk
import re
from CTkMessagebox import CTkMessagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
app = ctk.CTk()

width = 1680
height = 900
app.title("Dijkstra Path Finder")
app.geometry(f"{width}x{height}")
app.resizable(False, False)

main_frame = ctk.CTkFrame(master=app)
main_frame.pack(side=ctk.LEFT, padx=5, pady=5, anchor="center")

path_frame = ctk.CTkFrame(master=app)
path_frame.pack(side=ctk.LEFT, padx=10, pady=5, fill="both", expand=True)

path_lb = ctk.CTkLabel(master=path_frame, text="")
path_lb.pack(side=ctk.TOP, padx=10, pady=5, fill="both", expand=True)

file_frame = ctk.CTkFrame(master=main_frame)
file_frame.pack(side=ctk.TOP, padx=10, pady=5, fill="x")

data_file_lb = ctk.CTkLabel(master=file_frame, text="Data: ")
data_file_lb.pack(side=ctk.LEFT, padx=10, pady=5)

data_file_field = ctk.CTkEntry(master=file_frame, state="readonly")
data_file_field.pack(side=ctk.LEFT, padx=2, pady=5, fill="x")

data_file_bt = ctk.CTkButton(master=file_frame, text="Browse", width=70)
data_file_bt.pack(side=ctk.LEFT, padx=10, pady=5)

image_lb = ctk.CTkLabel(master=file_frame, text="Image: ")
image_lb.pack(side=ctk.LEFT, padx=10, pady=5)

image_field = ctk.CTkEntry(master=file_frame, state="readonly")
image_field.pack(side=ctk.LEFT, padx=2, pady=5, fill="x")

operational_frame = ctk.CTkFrame(master=file_frame)
operational_frame.pack(side=ctk.LEFT, padx=10, pady=5)

search_lb = ctk.CTkLabel(master=operational_frame, text="Search: ")
search_lb.pack(side=ctk.LEFT, padx=10, pady=5)

search_field = ctk.CTkEntry(master=operational_frame, state="normal")
search_field.pack(side=ctk.LEFT, padx=2, pady=5, fill="x", ipadx=30)

show_graph_bt = ctk.CTkButton(master=operational_frame, text="Show Graph", state="disabled")
show_graph_bt.pack(side=ctk.LEFT, padx=10, pady=5)

map_canvas = tk.Canvas(master=main_frame, width=1200, height=800)
map_canvas.pack(side=ctk.TOP, padx=10, pady=10, anchor="center")


def read_file(filename):
    file = open(filename)
    file_content = file.read()

    def process_file_content():
        file_content_arr = file_content.split("\n")

        def remove_spacing():
            lines_to_remove = []
            for i, line in enumerate(file_content_arr):
                if line.strip() == "":
                    lines_to_remove.append(i)
            new_content = []
            for i in range(len(file_content_arr)):
                if i in lines_to_remove:
                    continue
                else:
                    new_content.append(file_content_arr[i])

            return new_content

        file_content_arr = remove_spacing()

        # for i in file_content_arr:
        #     print(i)
        return file_content_arr

    return process_file_content()


x_factor = 1
y_factor = 1

graph = None
vertex_radius = 5
vertices = []
# vertex_node_mapping = {}
# node_vertex_mapping = {}
vertex_coords = {}

labels = []
filtered_labels = []

beginning_item_id = None
end_item_id = None

path = []
lines = []
edge_labels = []
# vertex_labels = []

animate_flag = True
djk = None
return_key_item_id = None


def draw_edges():
    global animate_flag
    animate_flag = True
    lines_coor = []
    path_items = []
    path_dists = []
    for entry1, entry2 in zip(path, path[1:]):
        # item1_id = node_vertex_mapping[entry1.node.name]
        item1_id = map_canvas.find_withtag(entry1.node.name)[0]
        path_items.append(item1_id)
        item2_id = map_canvas.find_withtag(entry2.node.name)[0]
        # item2_id = node_vertex_mapping[entry2.node.name]
        x0, y0, x1, y1 = map_canvas.coords(item1_id)
        if item1_id == beginning_item_id[0]:
            x0 = x0 + vertex_radius + 5
            y0 = y0 + vertex_radius + 5
            start = (x0, y0)
        else:
            x0 = x0 + vertex_radius
            y0 = y0 + vertex_radius
            start = (x0, y0)
        if item2_id == end_item_id[0]:
            path_items.append(item2_id)
            x0, y0, x1, y1 = map_canvas.coords(item2_id)
            x0 = x0 + vertex_radius + 5
            y0 = y0 + vertex_radius + 5
            lines_coor.append((start, (x0, y0)))
        else:
            x0, y0, x1, y1 = map_canvas.coords(item2_id)
            x0 = x0 + vertex_radius
            y0 = y0 + vertex_radius
            lines_coor.append((start, (x0, y0)))
        path_dists.append(entry2.total_dist - entry1.total_dist)

    def animate_line(canvas, lines_coor, index=0, steps=100):
        if index >= len(lines_coor):
            return
        start = lines_coor[index][0]
        end = lines_coor[index][1]
        x1, y1 = start
        x2, y2 = end
        center_line_x = (x1 + x2) / 2
        center_line_y = (y1 + y2) / 2

        dx = (x2 - x1) / steps
        dy = (y2 - y1) / steps

        line = canvas.create_line(x1, y1, x1, y1, fill="red", width=5)  # Initial line with no length
        lines.append(line)
        item_id = path_items[index]
        map_canvas.tag_raise(item_id)
        if path_items[index + 1] == path_items[-1]:
            map_canvas.tag_raise(path_items[-1])
        if index > 0:
            item_id = path_items[index]
            map_canvas.coords(item_id, x1 - 10, y1 - 10, x1 + 10, y1 + 10)

        def update_line(step):
            nonlocal x1, y1
            x1 += dx
            y1 += dy
            canvas.coords(line, start[0], start[1], x1, y1)
            if step < steps and animate_flag:
                canvas.after(1, update_line, step + 1)  # Update every 1 millisecond (not stable)
            elif animate_flag:
                animate_line(canvas, lines_coor, index + 1)
                edge_labels.append(
                    map_canvas.create_text(center_line_x, center_line_y, text=str(path_dists[index]), fill="yellow",
                                           font="Times 10 bold"))

        update_line(0)

    animate_line(map_canvas, lines_coor)


def show_graph():
    if djk is None:
        graph.visualize_graph()
    else:
        djk.visualize_graph()
        # djk.visualize_path()


show_graph_bt.configure(command=show_graph)

total_cost_lb_rect = None
total_cost_lb_text = None
total_cost_lb_x = None


def remove_total_cost_lb():
    global total_cost_lb_rect, total_cost_lb_text, total_cost_lb_x
    map_canvas.delete(total_cost_lb_rect)
    map_canvas.delete(total_cost_lb_text)
    map_canvas.delete(total_cost_lb_x)
    total_cost_lb_rect = None
    total_cost_lb_text = None
    total_cost_lb_x = None


def show_total_dist():
    global total_cost_lb_rect, total_cost_lb_text, total_cost_lb_x
    if total_cost_lb_rect is not None:
        map_canvas.delete(total_cost_lb_rect)
        map_canvas.delete(total_cost_lb_text)
        map_canvas.delete(total_cost_lb_x)
    total_cost_lb_rect = map_canvas.create_rectangle(0, 0, 300, 40, fill="white", outline="white")
    total_cost_lb_text = map_canvas.create_text(150, 20, text="Total Distance: " + str(path[-1].total_dist) + " m",
                                                fill="green", font="Times 20 bold")
    total_cost_lb_x = map_canvas.create_text(280, 10, text="[X]", fill="red", font="Times 12 bold")

    map_canvas.tag_bind(total_cost_lb_x, "<Button-1>", lambda event: remove_total_cost_lb())


def plot_path():
    # src = vertex_node_mapping[beginning_item_id[0]]
    src = map_canvas.gettags(beginning_item_id)[0]
    # to = vertex_node_mapping[end_item_id[0]]
    to = map_canvas.gettags(end_item_id)[0]
    global djk
    djk = dijkstra2.Dijkstra(graph, src, to)
    # djk.visualize_graph()
    global path
    path = djk.path
    draw_edges()
    show_total_dist()
    make_path_graph()


def stop_animation():
    global animate_flag
    animate_flag = False


def reset_sizes():
    for vertex in vertices:
        # map_canvas.itemconfig(vertex, fill="red", outline="red")
        coords = vertex_coords[vertex]
        map_canvas.coords(vertex, coords)


def reset():
    stop_animation()
    for vertex in vertices:
        map_canvas.itemconfig(vertex, fill="red", outline="red")
        coords = vertex_coords[vertex]
        map_canvas.coords(vertex, coords)
    for line in lines:
        map_canvas.delete(line)
    for label in edge_labels:
        map_canvas.delete(label)
    lines.clear()
    edge_labels.clear()


def enlarge_vertex(event, item_id=None):
    if item_id is None:
        item_id = event.widget.find_withtag(tk.CURRENT)
    x0, y0, x1, y1 = map_canvas.coords(item_id)
    x0 = x0 - 5
    y0 = y0 - 5
    x1 = x1 + 5
    y1 = y1 + 5
    map_canvas.coords(item_id, x0, y0, x1, y1)


def back_small(event):
    item_id = event.widget.find_withtag(tk.CURRENT)
    x0, y0, x1, y1 = map_canvas.coords(item_id)
    coord = vertex_coords[item_id[0]]  # getting original coordinates to compare size
    x0 = x0 + 5
    if x0 > coord[0]:  # comparing shrunk size with original size
        map_canvas.coords(item_id, coord)  # no further shrinking if already at original size
        return
    y0 = y0 + 5
    x1 = x1 - 5
    y1 = y1 - 5
    map_canvas.coords(item_id, x0, y0, x1, y1)


beginning_selected = False


# Called when a vertex is clicked or Return is pressed on the search field
# Checks if the vertex is the beginning or end of the path
# If beginning is already selected checks if the new vertex is the same as the beginning
# If it is the same it makes no changes whereas if different it selects the other vertex as the end
# Takes left click event or return key press event (One or the other can't be both)
# If return key is pressed then an item_id is passed to be selected. The item_id is passed from another function that captures clicks "search_options"
# If left click is pressed then the item_id is None and the current item (clicked item) is selected
def select_vertex(event, selected_item_id=None):
    global beginning_selected
    global beginning_item_id
    global end_item_id
    search_field.delete(0, tk.END)  # Clear search field
    search_options(None)  #

    if beginning_selected:
        if selected_item_id is None:
            selected_item_id = event.widget.find_withtag(tk.CURRENT)
        if beginning_item_id == selected_item_id:
            reset()
            enlarge_vertex(event, selected_item_id)
            # event.widget.itemconfigure("current", fill="green", outline="green")
            map_canvas.itemconfigure(selected_item_id, fill="green", outline="green")
        else:
            reset_sizes()
            x0, y0, x1, y1 = vertex_coords[beginning_item_id[0]]
            enlarge_vertex(event, selected_item_id)
            map_canvas.coords(beginning_item_id, x0 - 5, y0 - 5, x1 + 5, y1 + 5)
            # event.widget.itemconfigure("current", fill="orange", outline="orange")
            map_canvas.itemconfigure(selected_item_id, fill="orange", outline="orange")
            beginning_selected = False
            # end_item_id = event.widget.find_withtag(tk.CURRENT)
            end_item_id = selected_item_id
            plot_path()
    else:
        reset()
        enlarge_vertex(event, selected_item_id)
        if selected_item_id is None:
            selected_item_id = event.widget.find_withtag(tk.CURRENT)
        # beginning_item_id = event.widget.find_withtag(tk.CURRENT)
        beginning_item_id = selected_item_id
        # event.widget.itemconfigure("current", fill="green", outline="green")
        map_canvas.itemconfigure(selected_item_id, fill="green", outline="green")
        beginning_selected = True
    enlarge_vertex(event, selected_item_id)


def map_points_to_image(filename):
    points_num = 0
    edges_num = 0
    global graph
    graph = dijkstra2.UndirGraph()
    file_content = read_file(filename)
    vertix_names = []  # used for checking duplicate nodes names
    coords = []  # used for checking duplicate nodes coordinates
    for indx, i in enumerate(file_content):
        if indx == 0:
            try:
                points_num = int(i.split(" ")[0])
                if len(file_content) <= points_num + 1:
                    CTkMessagebox(title="Data File Error", message="Data file is missing nodes or edges", icon="cancel")
                    return False
                edges_num = int(i.split(" ")[1])
            except:
                CTkMessagebox(title="Data File Error",
                              message="Data file need to have the number of nodes and edges specified at the "
                                      "beginning of the file.",
                              icon="cancel")
                return False
        elif indx <= points_num:
            coor = i.split(" ")
            vertix_name = coor[0].strip()
            if vertix_name in vertix_names:
                CTkMessagebox(title="Data File Error", message="Data file has duplicate nodes.", icon="cancel")
                return False
            vertix_names.append(vertix_name)
            labels.append(vertix_name.replace("_", " "))
            try:
                coor_x = int(int(coor[1]) * x_factor)
                coor_y = int(int(coor[2]) * y_factor)
                if (coor_x, coor_y) in coords:
                    CTkMessagebox(title="Data File Error", message="Data file has duplicate nodes coordinates.",
                                  icon="cancel")
                    return False
                coords.append((coor_x, coor_y))

            except:
                CTkMessagebox(title="Data File Error",
                              message="Please check the data file format and the number of entries.", icon="cancel")
                return False

            node = dijkstra2.Node(vertix_name)
            item_id = map_canvas.create_oval(coor_x - vertex_radius, coor_y - vertex_radius, coor_x + vertex_radius,
                                             coor_y + vertex_radius, fill="red",
                                             outline="red", tags=vertix_name)
            # map_canvas.create_text(coor_x + vertex_radius + 30, coor_y + vertex_radius - 15,
            #                        text=vertix_name.replace("_", " "), fill="blue",
            #                        font="Times 10 bold")
            vertices.append(item_id)
            vertex_coords[int(item_id)] = (coor_x - 5, coor_y - 5, coor_x + 5, coor_y + 5)
        else:
            i = i.strip()
            edge = i.split(" ")
            if len(edge) < 3:
                CTkMessagebox(title="Data File Error", message="Data file has missing edges or edge distances.",
                              icon="cancel")
                return False
            if len(edge) > 3:
                CTkMessagebox(title="Data File Error", message="Data file has extra entries in the edges.",
                              icon="cancel")
                return False
            node1 = edge[0]
            if node1 not in vertix_names:
                CTkMessagebox(title="Data File Error", message="Data file has edges with nodes that are not defined.",
                              icon="cancel")
                return False
            try:
                node2 = edge[1]
            except:
                CTkMessagebox(title="Data File Error", message="Data file has some missing edges.", icon="cancel")
                return False
            if node2 not in vertix_names:
                CTkMessagebox(title="Data File Error",
                              message="Data file has edges with nodes that are not defined or has missing edges.",
                              icon="cancel")
                return False
            try:
                distance = float(edge[2])
                if distance <= 0:
                    CTkMessagebox(title="Data File Error", message="Data file has edges with zero or less distance.",
                                  icon="cancel")
                    return False
            except:
                CTkMessagebox(title="Data File Error", message="Data file has edges with invalid distance.",
                              icon="cancel")
                return False
            dijkstra2.Edge(node1, node2, distance)
    for node in dijkstra2.Node.nodes.values():
        graph.add_node(node)
    for v in vertices:
        map_canvas.tag_bind(v, '<Button-1>', select_vertex)
        map_canvas.tag_bind(v, '<Enter>', enlarge_vertex)
        map_canvas.tag_bind(v, '<Leave>', back_small)
    return True


def prepare_image(filename):
    global og_img
    global map_img
    og_img = Image.open(filename)
    img_width, img_height = og_img.size
    ratio = img_width / img_height
    canvas_width = 1200
    canvas_height = 800
    canvas_ratio = canvas_width / canvas_height
    resized_image = None
    if ratio > canvas_ratio:
        map_canvas.configure(height=int(canvas_width / ratio), width=canvas_width)
        resized_image = og_img.resize((canvas_width, int(canvas_width / ratio)), Image.ANTIALIAS)
    else:
        map_canvas.configure(width=int(canvas_height * ratio), height=canvas_height)
        resized_image = og_img.resize((int(canvas_height * ratio), canvas_height), Image.ANTIALIAS)
    app.geometry(str(resized_image.size[0] + 240 + 40) + "x" + str(resized_image.size[1] + 100))
    new_width, new_height = resized_image.size
    global x_factor, y_factor
    x_factor = new_width / img_width
    y_factor = new_height / img_height
    print(new_width, new_height, img_width, img_height, x_factor, y_factor)
    map_img = ImageTk.PhotoImage(resized_image)
    map_canvas.create_image(0, 0, image=map_img, anchor=ctk.NW)


def make_path_graph():
    global djk
    img_file = djk.visualize_path()
    img = Image.open(img_file)
    width, height = img.size
    if height > 880:
        height = 880
    img = CTkImage(light_image=Image.open(img_file), size=(width, height))
    path_lb.configure(image=img)

def load_files():
    data_file = filedialog.askopenfilename(initialdir="./", title="Select Data File",
                                           filetypes=(("txt files", "*.txt"), ("all files", "*.*")))
    # print(data_file)
    if data_file == "":
        return

    image_file = data_file.replace(".txt", ".png")
    if not os.path.isfile(image_file):
        image_file = filedialog.askopenfilename(initialdir="./", title="Select Image File",
                                                filetypes=(("png files", "*.png"), ("all files", "*.*")))
        if image_file == "":
            return
    data_file_field.configure(state="normal")
    data_file_field.delete(0, tk.END)
    data_file_field.insert(0, data_file.split("/")[-1])
    data_file_field.configure(state="readonly")
    image_field.configure(state="normal")
    image_field.delete(0, tk.END)
    image_field.insert(0, image_file.split("/")[-1])
    image_field.configure(state="readonly")
    reset()
    remove_total_cost_lb()
    map_canvas.delete("all")
    dijkstra2.Node.nodes.clear()
    vertices.clear()
    vertex_coords.clear()
    labels.clear()
    global beginning_selected, beginning_item_id, end_item_id, return_key_item_id
    beginning_selected = False
    beginning_item_id = None
    end_item_id = None
    return_key_item_id = None
    vertex_coords.clear()

    prepare_image(image_file)
    if not map_points_to_image(data_file):
        map_canvas.delete("all")
        dijkstra2.Node.nodes.clear()
        vertices.clear()
        vertex_coords.clear()
        labels.clear()
        vertex_coords.clear()
        return

    show_graph_bt.configure(state="enabled")


data_file_bt.configure(command=load_files)


def search_options(event):
    if event is not None:
        global return_key_item_id
        if re.match(r'^\bReturn\b$', event.keysym):
            if return_key_item_id is not None:
                select_vertex(event, return_key_item_id)
                return_key_item_id = None
            return
        if not re.match(r"^[0-9a-zA-Z]$|\bBackSpace\b", event.keysym):
            # if re.match(r'^\bEscape\b$', event.keysym):
            #     search_field.delete(0, tk.END)
            #     search_field.insert(0, '')
            #     reset()
            return
    global beginning_selected
    reset()
    if beginning_selected:
        map_canvas.itemconfig(beginning_item_id, fill="green", outline="green")
        x0, y0, x1, y1 = map_canvas.coords(beginning_item_id)
        map_canvas.coords(beginning_item_id, x0 - 5, y0 - 5, x1 + 5, y1 + 5)
    search_text = search_field.get()
    filtered_options = [option for option in labels if search_text.lower() in option.lower()]
    # print(filtered_options)
    if len(filtered_options) != len(labels):
        for option in filtered_options:
            # map_canvas.itemconfig(option, state="hidden")
            # option=option.replace(" ", "_")
            x0, y0, x1, y1 = map_canvas.coords(option.replace(" ", "_"))
            # map_canvas.coords(option, x0 + 5, y0 + 5, x1 - 5, y1 -5)
            if len(filtered_options) == 1:
                return_key_item_id = map_canvas.find_withtag(option.replace(" ", "_"))
            else:
                return_key_item_id = None
            map_canvas.coords(option.replace(" ", "_"), x0 - 10, y0 - 10, x1 + 10, y1 + 10)
            map_canvas.itemconfig(option.replace(" ", "_"), fill="yellow", outline="yellow")
            if beginning_item_id is not None and beginning_selected and option == map_canvas.gettags(beginning_item_id)[
                0]:
                map_canvas.itemconfig(option.replace(" ", "_"), fill="green", outline="green")


search_field.bind("<KeyRelease>", search_options)


def escape_reset():
    search_field.delete(0, tk.END)
    search_field.insert(0, '')
    reset()
    global beginning_selected
    beginning_selected = False


app.bind("<Escape>", lambda event: escape_reset())

app.mainloop()
