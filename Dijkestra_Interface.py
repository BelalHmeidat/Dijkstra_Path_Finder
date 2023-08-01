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

image_lb = ctk.CTkLabel(master=file_frame, text="Image: ")
image_lb.pack(side=ctk.LEFT, padx=10, pady=5)

image_field = ctk.CTkEntry(master=file_frame, state="readonly")
image_field.pack(side=ctk.LEFT, padx=2, pady=5, fill="x")

data_file_bt = ctk.CTkButton(master=file_frame, text="Browse", width=70)
data_file_bt.pack(side=ctk.LEFT, padx=10, pady=5)

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

    # getting the lines from the content of the file without redundant spaces in between lines
    def process_file_content():
        file_content_arr = file_content.split("\n")

        # removing redundant spaces in between lines
        def remove_spacing():
            lines_to_remove = []
            for i, line in enumerate(file_content_arr):
                if line.strip() == "":  # if line is empty
                    lines_to_remove.append(i)  # add it to remove list
            new_content = []
            for i in range(len(file_content_arr)):
                if i in lines_to_remove:  # if line index is in remove list the it's empty line index
                    continue  # skipping that line
                else:
                    new_content.append(file_content_arr[i])  # adding non-empty lines to the final list of lines

            return new_content

        file_content_arr = remove_spacing()

        # for i in file_content_arr:
        #     print(i)
        return file_content_arr

    return process_file_content()


x_factor = 1  # used to adjust point positions in the canvas; after the image get resized the coordinates of the points will be adjusted
y_factor = 1

graph = None  # Stores the dijkstra graph
vertex_radius = 5  # the radius of the vertex circles
vertices = []  # stores the vertex items of the canvas
vertex_coords = {}  # stores the coordinates of the vertices (used in resetting the canvas)

labels = []  # stores the names of the vertices
filtered_options = []  # sotres the canvas filtered items of the search field. Used to highlighting search result vertices
filtered_labels = []  # stores the names of the filtered vertices

beginning_item_id = None  # stores the id of the beginning vertex
end_item_id = None  # stores the id of the end vertex

path = []  # stores the path of the dijkstra algorithm
lines = []  # stores the canvas line items of the path
node_labels = []  # stores the canvas label items of the vertices
edge_labels = []  # stores the canvas label items of the edge distances
# vertex_labels = []

animate_flag = True  # used to halt animation before it finishes (only animates if True)
djk = None  # stores the dijkstra object
return_key_item_id = None  # stores the id of the vertex that was selected by pressing the return key after search


# puts the labels above the vertices
# These vertices are ones that are selected for start and end or hovered over or searched for
def put_label_above_vertex(item_id):
    x1, y1, x2, y2 = map_canvas.coords(item_id)  # gets the coordinates of the vertex
    x = (x1 + x2) / 2  # find the center
    y = (y1 + y2) / 2
    name = map_canvas.gettags(item_id)[0]  # gets the name of the vertex
    name = name.replace("_", " ")  # replaces the underscore with space in the name
    label = map_canvas.create_text(x - 20, y - 20, text=name, font="Arial 12 bold", fill="yellow")  # creates the label
    node_labels.append(label)  # adds to the list of labels to be removed later


# defines the line start and end points of each edge in the path and draws the lines animated
def draw_edges():
    global animate_flag
    animate_flag = True
    lines_coor = []  # stores the coordinates of the lines of the path
    path_items = []  # stores the canvas line items of the path to be removed later
    path_dists = []  # stores the distances of the edges in the path
    for entry1, entry2 in zip(path, path[
                                    1:]):  # iterates through the path and takes pairs of vertices (begin and end of each edge)
        # item1_id = node_vertex_mapping[entry1.node.name]
        item1_id = map_canvas.find_withtag(entry1.node.name)[0]  # fetches the item id of the vertex with that name
        path_items.append(item1_id)
        item2_id = map_canvas.find_withtag(entry2.node.name)[0]
        # item2_id = node_vertex_mapping[entry2.node.name]
        x0, y0, x1, y1 = map_canvas.coords(item1_id)  # gets the coordinates of the vertex
        if item1_id == beginning_item_id[
            0]:  # if it's the beginning vertex then the start point of the line is the center of the vertex and since the begginning vertex is bigger than the others we need to add 5 to the coordinates
            x0 = x0 + vertex_radius + 5
            y0 = y0 + vertex_radius + 5
            start = (x0, y0)
        else:  # all other vertices on the path will be small intially so the line start point will be the center of the small vertex
            x0 = x0 + vertex_radius
            y0 = y0 + vertex_radius
            start = (x0, y0)
        if item2_id == end_item_id[0]:  # same as start of the line for the end of the line
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
        path_dists.append(
            entry2.total_dist - entry1.total_dist)  # edge distance is the difference between total distances of two successive vertices in the path

    # animates the line
    def animate_line(lines_coor, index=0,
                     steps=100):  # takes list of line begin and end coords, index of line, and number of steps to animate
        if index >= len(lines_coor):  # recursive function end condition when the index is at the end of the list
            return
        start = lines_coor[index][0]  # start point of the line
        end = lines_coor[index][1]  # end point of the line
        x1, y1 = start
        x2, y2 = end
        center_line_x = (x1 + x2) / 2  # center of the line for edge label
        center_line_y = (y1 + y2) / 2  # center of the line for edge label

        dx = (x2 - x1) / steps  # change in x and y for each step
        dy = (y2 - y1) / steps

        line = map_canvas.create_line(x1, y1, x1, y1, fill="red", width=5)  # Initial line with no length
        lines.append(line)
        item_id = path_items[index]
        map_canvas.tag_raise(item_id)  # raising vertices above the lines
        if path_items[index + 1] == path_items[-1]:  # loop doesn't work for last item, so we need to raise it manually
            map_canvas.tag_raise(path_items[-1])
        if index > 0:  # skipping first node as it's already enlarged due to selection last item is already not in the
            # loop so it's skipped as well
            item_id = path_items[index]
            map_canvas.coords(item_id, x1 - 10, y1 - 10, x1 + 10, y1 + 10)
            # put_label_above_vertex(item_id)

        # recursive function that does the animation of the line
        def update_line(step):
            nonlocal x1, y1
            x1 += dx
            y1 += dy
            map_canvas.coords(line, start[0], start[1], x1, y1)
            if step < steps and animate_flag:  # if the animation is not stopped and the line is not finished drawing
                map_canvas.after(1, update_line, step + 1)  # Update every 1 millisecond (not stable)
            elif animate_flag:  # if the animation is not stopped and finished it addes the edge label and calls the function again for the next edge
                animate_line(lines_coor, index + 1)
                edge_labels.append(
                    map_canvas.create_text(center_line_x, center_line_y, text=str(path_dists[index]), fill="yellow",
                                           font="Ariel 12 bold"))

        update_line(0)  # starts the animation at step 0

    animate_line(lines_coor)


# Shows the graph when the show graph button is pressed
def show_graph():
    if djk is None:
        graph.visualize_graph()
    else:
        djk.visualize_graph()
        # djk.visualize_path()


show_graph_bt.configure(command=show_graph)

total_cost_lb_rect = None  # rectangle for the total cost label
total_cost_lb_text = None  # text for the total cost label
total_cost_lb_x = None  # exit button for the total cost label


# removes the total cost label
def remove_total_cost_lb():
    global total_cost_lb_rect, total_cost_lb_text, total_cost_lb_x
    map_canvas.delete(total_cost_lb_rect)
    map_canvas.delete(total_cost_lb_text)
    map_canvas.delete(total_cost_lb_x)
    total_cost_lb_rect = None
    total_cost_lb_text = None
    total_cost_lb_x = None


# shows the total cost on the cost label on the left top corner of the map
# gets called whenever a new path selected
def show_total_dist():
    global total_cost_lb_rect, total_cost_lb_text, total_cost_lb_x
    if total_cost_lb_rect is not None: # deletes the old one if it exists
        map_canvas.delete(total_cost_lb_rect)
        map_canvas.delete(total_cost_lb_text)
        map_canvas.delete(total_cost_lb_x)
    # creates a new cost label with the new distance
    total_cost_lb_rect = map_canvas.create_rectangle(0, 0, 300, 40, fill="white", outline="white")
    total_cost_lb_text = map_canvas.create_text(150, 20, text="Total Distance: " + str(path[-1].total_dist) + " m",
                                                fill="green", font="Times 20 bold")
    total_cost_lb_x = map_canvas.create_text(280, 10, text="[X]", fill="red", font="Times 12 bold")

    map_canvas.tag_bind(total_cost_lb_x, "<Button-1>", lambda event: remove_total_cost_lb())

# gets the source and destination from the selected vertices and finds the shortest path between them through dijkstra it then calls the draw edges function to draw the path
def plot_path():
    global beginning_item_id
    # src = vertex_node_mapping[beginning_item_id[0]]
    src = map_canvas.gettags(beginning_item_id)[0]
    # to = vertex_node_mapping[end_item_id[0]]
    to = map_canvas.gettags(end_item_id)[0]
    global djk
    djk = dijkstra2.Dijkstra(graph, src, to)
    if not djk.find_path(djk.source, djk.dest): # in case dijkstra returned no path (False)
        CTkMessagebox(title="No Path!", message="Node is unreachable from that start point!", icon="cancel")
        beginning_item_id = None
        reset() # resets the canvas to its original state
        return
    # djk.visualize_graph()
    global path
    path = djk.path
    draw_edges()
    show_total_dist()
    make_path_graph() # creates the path graph at the right side of the map

# stops the animation of the path when interrupted
def stop_animation():
    global animate_flag
    animate_flag = False

# only resets the sizes of the vertices to their original size
def reset_sizes():
    for vertex in vertices:
        # map_canvas.itemconfig(vertex, fill="red", outline="red")
        # It adjusts with coordinates
        coords = vertex_coords[vertex]
        map_canvas.coords(vertex, coords)

# Resets the canvas to its original state when escape key pressed or a new path initiated
def reset():
    stop_animation()
    for vertex in vertices:
        map_canvas.itemconfig(vertex, fill="red", outline="red")
        coords = vertex_coords[vertex]
        map_canvas.coords(vertex, coords)
    # deletes all canvas lines and labels
    for line in lines:
        map_canvas.delete(line)
    for label in edge_labels:
        map_canvas.delete(label)
    for label in node_labels:
        map_canvas.delete(label)
    # clears all the lists
    lines.clear()
    edge_labels.clear()
    node_labels.clear()
    global end_item_id
    end_item_id = None
    # for vertex in vertices:
    #     put_label_above_vertex(vertex)

# enlarges the vertex like in the case of vertex mouse hover or selection
# takes the item id of the vertex from the mouse hover/ select event or the passed item_id (default none) if it's not none
# item_id comes from the search function
def enlarge_vertex(event, item_id=None):
    if item_id is None:
        item_id = event.widget.find_withtag(tk.CURRENT)
    x0, y0, x1, y1 = map_canvas.coords(item_id)
    x0 = x0 - 5
    y0 = y0 - 5
    x1 = x1 + 5
    y1 = y1 + 5
    map_canvas.coords(item_id, x0, y0, x1, y1)

# clears the labels of the nodes
# called when the mouse leaves the vertex
def reset_node_labels():
    for label in node_labels:
        map_canvas.delete(label)
    node_labels.clear()

# shrinks the vertices by 5 pixels when the mouse left the hover area or the vertex is deselected takes t
# also removes the hover labels on top of the hovered vertex
def back_small(event):
    item_id = event.widget.find_withtag(tk.CURRENT)
    x0, y0, x1, y1 = map_canvas.coords(item_id)
    coord = vertex_coords[item_id[0]]  # getting original coordinates to compare size
    x0 = x0 + 5
    if x0 > coord[0]:  # comparing shrunk size with original size (one coordinate is enough)
        map_canvas.coords(item_id, coord)  # no further shrinking if already at original size
        return
    y0 = y0 + 5
    x1 = x1 - 5
    y1 = y1 - 5
    map_canvas.coords(item_id, x0, y0, x1, y1)
    reset_node_labels() #
    # removes hovered over labels everything except the selected vertices (beginning and end) or the vertices of the search result it puts them back up
    if beginning_item_id is not None:
        put_label_above_vertex(beginning_item_id)
    if end_item_id is not None:
        put_label_above_vertex(end_item_id)
    global filtered_options
    if len(filtered_options) != len(vertices): # if the search field is empty then filtered options has all the vertices names this prevents
        # print(filtered_options)
        for option in filtered_options:
            option = option.replace(" ", "_")
            put_label_above_vertex(option)


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

    if beginning_selected: # if beginning is already selected
        if selected_item_id is None: # takes the item_id from the mouse event if no item_id from keyboard search function is passed
            selected_item_id = event.widget.find_withtag(tk.CURRENT)
        if beginning_item_id == selected_item_id: # if selected item is the same as the formly selected beginning then does nothing
            reset()
            enlarge_vertex(event, selected_item_id)
            # event.widget.itemconfigure("current", fill="green", outline="green")
            map_canvas.itemconfigure(selected_item_id, fill="green", outline="green")
            put_label_above_vertex(selected_item_id)
        else: # if selected item is different from the formly selected beginning then selects it as the end
            reset_sizes() # resets the sizes of all vertices
            x0, y0, x1, y1 = vertex_coords[beginning_item_id[0]] # except the beginning and end vertices
            map_canvas.coords(beginning_item_id, x0 - 5, y0 - 5, x1 + 5, y1 + 5)
            put_label_above_vertex(beginning_item_id)
            enlarge_vertex(event, selected_item_id) # enlarges the end vertex
            # event.widget.itemconfigure("current", fill="orange", outline="orange")
            map_canvas.itemconfigure(selected_item_id, fill="orange", outline="orange")
            put_label_above_vertex(selected_item_id)
            beginning_selected = False
            # end_item_id = event.widget.find_withtag(tk.CURRENT)
            end_item_id = selected_item_id
            plot_path()
    else: # if beginning is not selected then selects the vertex as the beginning
        reset()
        enlarge_vertex(event, selected_item_id)
        if selected_item_id is None: # takes the item_id from the mouse event if no item_id from keyboard search function is passed
            selected_item_id = event.widget.find_withtag(tk.CURRENT)
        # beginning_item_id = event.widget.find_withtag(tk.CURRENT)
        beginning_item_id = selected_item_id
        # event.widget.itemconfigure("current", fill="green", outline="green")
        map_canvas.itemconfigure(selected_item_id, fill="green", outline="green")
        beginning_selected = True
        put_label_above_vertex(selected_item_id)
    enlarge_vertex(event, selected_item_id)

# puts label on top of the vertex and enlarges the vertex
def vertex_hover(event):
    item_id = event.widget.find_withtag(tk.CURRENT)
    put_label_above_vertex(item_id)
    enlarge_vertex(event, item_id)


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
        map_canvas.tag_bind(v, '<Enter>', vertex_hover)
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

    # image_file = data_file.replace(".txt", ".png")
    # if not os.path.isfile(image_file):
    #     image_file = filedialog.askopenfilename(initialdir="./", title="Select Image File",
    #                                             filetypes=(("png files", "*.png"), ("all files", "*.*")))
    #     if image_file == "":
    #         return

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
    global filtered_options
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
            put_label_above_vertex(option.replace(" ", "_"))
            map_canvas.itemconfig(option.replace(" ", "_"), fill="yellow", outline="yellow")
            if beginning_item_id is not None and beginning_selected and option == map_canvas.gettags(beginning_item_id)[
                0]:  # if one of the searched for items is the beginning item it keeps it green
                map_canvas.itemconfig(option.replace(" ", "_"), fill="green", outline="green")


search_field.bind("<KeyRelease>", search_options)


def escape_reset():
    global beginning_item_id
    beginning_item_id = None
    search_field.delete(0, tk.END)
    search_field.insert(0, '')
    reset()
    global beginning_selected
    beginning_selected = False


app.bind("<Escape>", lambda event: escape_reset())

app.mainloop()
