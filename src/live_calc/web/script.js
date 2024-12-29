let runs = 0;

let input 
let display_text
let display_text_selected
let current_line
let output
let output_holder
let incoming_line_dependencies = []
let outgoing_line_dependencies = []
let dependency_lines
let error_dot
let time_info
let var_info
let line_error_break_container

let LINE_HEIGHT = 1.4;

let file_menu
let file_list
let file_names = []

let save_menu
let save_name

let current_file = null

// After content is loaded
document.addEventListener('DOMContentLoaded', function(event) {
  input = document.getElementById("input");
  display_text = document.getElementById("display-text");
  display_text_selected = document.getElementById("display-text-selected");
  line_display = document.getElementById("line-display");
  dependency_lines = document.getElementById("dependency-lines");
  output = document.getElementById("output");
  output_holder = document.getElementById("output-holder");
  error_dot = document.getElementById("error-dot");
  time_info = document.getElementById("time-info");
  var_info = document.getElementById("var-info");
  file_menu =  document.getElementById("file-menu");
  file_list = document.getElementById("file-list");
  save_menu = document.getElementById("save-menu");
  save_name = document.getElementById("save-name");
  save_dot = document.getElementById("save-dot");
  line_error_break_container = document.getElementById("line-error-break-container");
  line_error = document.getElementById("line-error");
  error_info = document.getElementById("error-info");

  // Start an update timer to recalc at 10Hz
  // let update_timer=setInterval(update, 100);

  // Update text and input box height as text is typed into it
  // input.setAttribute("style", "height:" + (input.scrollHeight) + "px;overflow-y:hidden;");
  input.addEventListener("input", function () {
    // Update the display text
    update();
    update_display_text();
    update_input_height();
  }, false); 

  error_info.style.color = "rgb(0,0,0,0)";
  // On error dot mouseover, show the error message + the line
  error_dot.addEventListener("mouseover", function() {
    error_info.style.color = "rgb(220,220,220)";
    error_info.style.backgroundColor = "rgb(145, 38, 38)";
    line_error.style.backgroundColor = "rgb(145, 38, 38, 1.0)";
  })
  // On mouseout, hide
  error_dot.addEventListener("mouseout", function() {
    error_info.style.color = "rgb(0,0,0,0)";
    error_info.style.backgroundColor = "rgb(0,0,0,0)";
    line_error.style.backgroundColor = "rgb(0,0,0,0)";
  })

  // Update display text as the mouse moves (mainly for highlighting)
  // input.addEventListener("mousemove", function() {
  //   update_display_text();
  // })
  input.addEventListener("mousedown", function() {
    setTimeout(update_display_text, 1);
  })
  // input.addEventListener("mouseup", function() {
  //   update_display_text();
  //   // update_dependency_display();
  // })

  input.addEventListener("keydown", function() {
    setTimeout(update_display_text, 1);
  })
  // input.addEventListener("keyup", function() {
  //   update_display_text();
  // })
  

  // Update the file list
  update_file_list();
  // Focus the input textarea
  input.focus();
})


// function update_dependency_display(){
//   current_line = input.value.substr(0, input.selectionStart).split("\n").length;

//   console.log(current_line)
// }

// Update the display text
// The visual text is made up of three seperate elements
// - Input (syntax highlighted)
// - Highlight (highlight similar selected)
// - Output (green result text)
function update_display_text(){

  // console.log(input.value)

  // display_text.innerHTML = input_text;

  // Syntax highlighting!
  input_text = input.value + '\n';
  input_text = input_text.replaceAll(/([=\/\*])/g, "<span class = 'equal'>$1</span>")
  input_text = input_text.replaceAll(/(#.*?\n)/ig, "<span class = 'comment'>$1</span>")
  input_text = input_text.replaceAll(/([0-9]+.[0-9]+|[0-9]+)/ig, "<span class = 'number'>$1</span>")
  display_text.innerHTML = input_text;


  current_line = input.value.substr(0, input.selectionStart).split("\n").length - 1;

  line_text = "";
  num_lines = 1;
  input_regex = input.value.match(/\n/g)
  if(input_regex){
    num_lines = input.value.match(/\n/g).length + 1;
  }

  if(current_line < incoming_line_dependencies.length){
    current_incoming_dependencies = incoming_line_dependencies[current_line]
    current_outgoing_dependencies = outgoing_line_dependencies[current_line]
  } else {
    current_incoming_dependencies = []
    current_outgoing_dependencies = []
  }

  for (let i = 0; i < num_lines; i++) {

    if(i == current_line){
      line_text += "<span class = 'active-line-number'>" + String(i) + "</span>\n";
    } else if(current_incoming_dependencies.includes(i)) {
      line_text += "<span class = 'incoming-dependency-line-number'>" + String(i) + "</span>\n";
    } else if(current_outgoing_dependencies.includes(i)) {
      line_text += "<span class = 'outgoing-dependency-line-number'>" + String(i) + "</span>\n";
    } else {
      line_text += String(i) + "\n";
    }
  }

  line_display.innerHTML = line_text;

  
  dependency_lines.innerHTML = "";
  em_size = parseFloat(getComputedStyle(dependency_lines).fontSize);
  
  function generate_curve_path_text(start_line, end_line){
    line_inner_x = 1.5;
    line_outer_x = 0.9;

    return `M 
    ${line_inner_x * em_size} ${(start_line * LINE_HEIGHT + LINE_HEIGHT/2) * em_size} 
    Q
    ${line_outer_x * em_size} ${(start_line * LINE_HEIGHT + LINE_HEIGHT/2) * em_size}
    ,
    ${line_outer_x * em_size} ${(start_line * LINE_HEIGHT) * em_size}
    ,
    ${line_outer_x * em_size} ${((start_line + dep_line)/2 * LINE_HEIGHT) * em_size}
    ,
    ${line_outer_x * em_size} ${(end_line * LINE_HEIGHT + LINE_HEIGHT) * em_size}
    ,
    ${line_outer_x * em_size} ${(end_line * LINE_HEIGHT + LINE_HEIGHT/2) * em_size} 
    ,
    ${line_inner_x * em_size} ${(end_line * LINE_HEIGHT + LINE_HEIGHT/2) * em_size} `;
  }


  for (let i = 0; i < current_outgoing_dependencies.length; i ++){
    var new_path_svg = document.createElementNS('http://www.w3.org/2000/svg','path');

    dep_line = current_outgoing_dependencies[i]

    new_path_svg.setAttribute('d', generate_curve_path_text(dep_line, current_line));
    new_path_svg.setAttribute("class", "dependency-line outgoing-dependency")
    dependency_lines.appendChild(new_path_svg);
  }
  
  for (let i = 0; i < current_incoming_dependencies.length; i ++){
    var new_path_svg = document.createElementNS('http://www.w3.org/2000/svg','path');

    dep_line = current_incoming_dependencies[i]

    new_path_svg.setAttribute('d', generate_curve_path_text(current_line, dep_line));
    new_path_svg.setAttribute("class", "dependency-line incoming-dependency")
    dependency_lines.appendChild(new_path_svg);
  }


  // Selected highlighting
  // var start = input.selectionStart;
  // var finish = input.selectionEnd;
  // var selected_text = input.value.substring(start, finish);
  // regex = new RegExp("("+selected_text+")","g");
  // display_text_selected.innerHTML = input.value.replaceAll(regex, "<span class = 'highlight'>$1</span>")
}

// Update the height of the input box
function update_input_height(){
  input.style.height = "90%";
  input.style.height = (input.scrollHeight + 10) + "px";
  input.style.width = "90%";
  input.style.width = (input.scrollWidth + 10) + "px";
}

// Write the calculator output to the output html element
eel.expose(write_output); // Expose this function to Python
function write_output(output_text, error) {
  if(!error){
    // Error dot transparent
    error_dot.style.backgroundColor = "rgb(145, 38, 38, 0)";
    line_error.style.backgroundColor = "rgb(145, 38, 38, 0.0)";

    // Set output text value
    output.innerHTML = output_text;
  }else{
    // Log error
    console.warn(error);

    // Set correct offset for error line
    line_error_break_container.innerHTML = "";
    line_error_output = ""
    for(let i = 0; i < error[0]; i++){
      line_error_output += "<br>"
    }
    line_error_break_container.innerHTML = line_error_output;

    // Set text in error display
    error_info.innerHTML = error[1];

    // Make the error dot red!
    error_dot.style.backgroundColor = "rgb(200, 45, 45)";
  }
}

// Probably a more efficient way to do this with eel but.... too bad
eel.expose(update_dependency_lists)
function update_dependency_lists(_incoming_line_dependencies, _outgoing_line_dependencies) {
  console.log(_incoming_line_dependencies)
  incoming_line_dependencies = _incoming_line_dependencies
  outgoing_line_dependencies = _outgoing_line_dependencies
}

// Set the value of the timer element
eel.expose(set_timer);
function set_timer(time){
  if(time != 0){
    time_info.innerHTML = time.toString() + "ms"
  }
}

// Set the variable number element
eel.expose(set_var_num)
function set_var_num(num){
  var_info.innerHTML = num.toString();
}

// Send input text to python
function update(){
  eel.send_input(input.value);
}

function open_file_picker(){
  update_file_list();

  file_menu.style.display = "block";
}

function close_file_picker(){
  file_menu.style.display = "none";
}

// Opens file
async function open_file(file_path){
  // New file
  // Very Hacky, I dislike this but I've got like 10 mins to finish this feature so there we go
  if(file_path == "> new file"){
    input.value = "";
    output.value = "";
    current_file = null;
    document.title = "new calc";
    input.focus();

  }else{
    current_file = file_path;
    document.title = file_path;

    // Set text area value to be file text
    input.value = await eel.get_file_text(file_path)();
  }

  // Recalculate and update height
  update();
  update_input_height();
  update_display_text();

  // Hide file dialog
  close_file_picker();
}

function open_save_menu(){
  save_menu.style.display = "block";
  save_name.focus()
}

function close_save_menu(){
  save_menu.style.display = "none";
}

// Saves the current file
function save_file(){
  if(current_file == null){
    open_save_menu();
  }else{
    save_dot.classList.remove("flash-animation");
    save_dot.offsetWidth
    eel.save_file_text(current_file, input.value);

    save_dot.classList.add("flash-animation");
  }
}

async function update_file_list(){
  file_template = document.getElementById("file-template");
  
  // Remove existing files
  file_list.innerHTML = "";

  // Get new filenames and add new file
  file_names = await eel.get_file_names()();
  file_names.unshift("> new file");
  
  // Add html elements to represent each file
  for(let file in file_names){
    
    filename = file_names[file];
    new_file = file_template.content.cloneNode(true);
    button = new_file.querySelector('button');
    button.innerHTML = filename;
    
    // Add open file button to each file
    button.addEventListener('click', () => {
      console.log(file_names[file]);
      open_file(file_names[file]);
    })
    
    file_list.appendChild(button);
  }
}


// A window level keypress function to catch shortcuts
function window_key_press(e) {
  var eventObj = window.event? event : e

  // Toggle open dialog with ctrl or cmd + o 
  // Horray for multi-system support
  if (eventObj.key == "o" && (eventObj.ctrlKey || eventObj.metaKey)){
    console.log(file_menu.style.display)
    if(file_menu.style.display == "block"){
      close_file_picker();
    }else{
      open_file_picker();
    }
  }

  // Save file with ctrl or cmd + s
  if (eventObj.key == "s" && (eventObj.ctrlKey || eventObj.metaKey)){
    e.preventDefault();
    save_file();
  }

  // If save menu is open, enter saves the file
  if(save_menu.style.display == "block" && eventObj.key == "Enter"){
    e.preventDefault();
    current_file = save_name.value
    save_file();
    close_save_menu();
  }

  if(eventObj.key == "Escape"){
    close_file_picker();
    close_save_menu();
  }
}
document.onkeydown = window_key_press;