
SQUARE = './img/square_placeholder_text.png'
RECTANGLE = './img/rectangular_placeholder_text.png'

IMAGE_INFO = {
    'concat_pre_reg_gray': {
        'pattern': 'DVARS_and_FD_CONCA*.png',
        'placeholder': SQUARE
        },
    'concat_post_reg_gray': {
        'pattern': 'DVARS_and_FD_CONCP*.png',
        'placeholder': SQUARE
        },
    'atlas_in_t1': {
        'pattern': '*atlas_in_t1*.gif',
        'placeholder': SQUARE
        },
    't1_in_atlas': {
        'pattern': '*t1_in_atlas*.gif',
        'placeholder': SQUARE
        },
    'task_pre_reg_gray': {
        'pattern': 'DVARS_and_FD*%s*.png',
        'placeholder': SQUARE
        },
    'task_post_reg_gray': {
        'pattern': 'postreg_DVARS_and_FD*%s*.png',
        'placeholder': SQUARE
        },
    'task_in_t1': {
        'pattern': '*%s*_in_t1*.gif',
        'placeholder': SQUARE
        },
    't1_in_task': {
        'pattern': '*t1_in_*%s*.gif',
        'placeholder': SQUARE
        },
    'ref': {
        'pattern': '*%s*ref.png',
        'placeholder': RECTANGLE
        },
    'bold': {
        'pattern': '*%s*_bold.png',
        'placeholder': RECTANGLE
        }
    }

# HTML constants:
HTML_START = """
<!DOCTYPE html>
<html>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.0/css/all.css"
    integrity="sha384-lZN37f5QGtY3VHgisS14W3ExzMWZxybE1SJSEsQp9S+oqd12jhcu+A56Ebc1zFSJ" crossorigin="anonymous">
<style type="text/css">
    header, footer, section, article, nav, aside { display: block; }
    h1, h2, h3, h4, body, button, p, w3-btn { font-family: Verdana, Helvetica, Arial, Bookman, sans-serif; }
    h1 { text-align: center; font-size: 2.5em; }
    h2{ text-align: center; font-size: 2.00em; }
    h3{ text-align: left; font-size: 1.75em; }
    h4{ text-align: left; font-size: 1.25em; }
    p{ font-size: 1.0em; }
    body{ font-size: 1.0em; }
    img{ width: 100%; padding: 2px; }
    .label1, .label2, .label3 { font-family: Verdana, Helvetica, Arial, Bookman, sans-serif }
    .label1 { font-size: 1.25em; text-align: center; }
    .label2 { font-size: 1.00em; text-align: center; }
    .label3 { font-size: 1.25em; text-align: left; }
    .label4 { font-size: 1.25em; text-align: right; }
    .grid-container { grid-gap: 2px; padding: 2px; }
    .T1pngs, .T2pngs, .Registrations { display: none; }
</style>
<body>
"""

# Make the html 'title' (what will be seen on the tab, etc.),
# as well as the page header.
# Needs the following values:
#    subject, session.
TITLE="""
<title>Executive Summary: %(subject)s %(session)s</title>
<header> <h2>%(subject)s: %(session)s</h2> </header>
"""

HTML_END = """
</body>
</html>
"""

# Make a section for T1 or T2. This will show the brainsprite
# viewer, with a label above it to identify T1 v T2, and a
# button that will open a modal window with a slider for the
# T1 or T2 pngs.
# Needs the following values:
#    tx, brainsprite_label, modal_button, brainsprite_viewer.
TX_SECTION = """
<section id="%(tx)s">
    <div class="w3-container">
        <div class="w3-cell w3-left label3">%(brainsprite_label)s</div>
        <div class="w3-cell w3-right">
            %(pngs_button)s
        </div>
    </div>
    <div class="w3-container">
        %(brainsprite_viewer)s
    </div>
</section>
"""

# Make a section for combined gray ordinates and atlas images.
# Start with the column headings.
# No values needed.
ATLAS_SECTION_START = """
<section id="Atlas">
    <div class="w3-container">
        <div class="w3-row">
            <div class="w3-half w3-center label1">Resting State Grayordinates Plots</div>
            <div class="w3-half w3-center label1"></div>
        </div>
        <div class="w3-cell-row">
            <div class="w3-quarter w3-center label1">Pre-Regression</div>
            <div class="w3-quarter w3-center label1">Post-Regression</div>
            <div class="w3-quarter w3-center label1">Atlas in T1</div>
            <div class="w3-quarter w3-center label1">T1 in Atlas</div>
        </div>
        <div  class="w3-row">
            """

# Add the actual row of images.
# Needs the following values:
#    pre_reg_gray, post_reg_gray, atlas_in_t1, t1_in_atlas.
ATLAS_ROW = """
            <div class="w3-quarter"><img src="{concat_pre_reg_gray}"></div>
            <div class="w3-quarter"><img src="{concat_post_reg_gray}"></div>
            <div class="w3-quarter"><img src="{atlas_in_t1}" onclick="open_modal_to_index('{modal_id}', {atlas_in_t1_idx})"></div>
            <div class="w3-quarter"><img src="{t1_in_atlas}" onclick="open_modal_to_index('{modal_id}', {t1_in_atlas_idx})"></div>
            """

# End the atlas section by closing up the divisions and the section.
# No values needed.
ATLAS_SECTION_END = """
        </div>
    </div>
</section>
"""

# Start the tasks section and  put in the column headings for the task-specific data.
TASKS_SECTION_START = """
<section id="Tasks">
    <div class="w3-container">
        <div  class="w3-row">
            <div class="w3-col s1 label1">Task</div>
            <div class="w3-col s2 label1">Pre-Reg Gray Plot</div>
            <div class="w3-col s2 label1">Post-Reg Gray Plot</div>
            <div class="w3-col s2 label1">Task in T1</div>
            <div class="w3-col s2 label1">T1 in Task</div>
            <div class="w3-col s3 label2">Reference (top) and BOLD (bottom)</div>
        </div>
"""

# Lays out a single row of 6 images for a task/run.
# Needs the following values:
#    row_label, task_pre_reg_gray, task_post_reg_gray, task_in_t1, t1_in_task, ref, bold.
TASK_ROW = """
        <div class="w3-cell-row">
            <div class="w3-col s1 label4">{row_label}</div>
            <div class="w3-col s2"><img src="{task_pre_reg_gray}"></div>
            <div class="w3-col s2"><img src="{task_post_reg_gray}"></div>
            <div class="w3-col s2"><img src="{task_in_t1}" onclick="open_modal_to_index('{modal_id}', {task_in_t1_idx})"></div>
            <div class="w3-col s2"><img src="{t1_in_task}" onclick="open_modal_to_index('{modal_id}', {t1_in_task_idx})"></div>
            <div class="w3-col s3"><img src="{ref}"></div>
            <br>
            <div class="w3-col s3"><img src="{bold}"></div>
        </div>
        """

# Close up the divisions and section.
TASKS_SECTION_END = """
    </div>
</section>
"""


# MODAL/SLIDER STUFF

# Begin a modal container.
# Needs the following values:
#    modal_id
MODAL_START = """
    <div id="%(modal_id)s" class="w3-modal">
        <div class="w3-modal-content">
            <div class="w3-content w3-display-container">
            """

# Make a button to display a modal container.
# Needs the following values:
#    modal_id, btn_label
DISPLAY_MODAL_BUTTON = """
            <button class="w3-btn w3-teal" onclick="open_modal_to_index('{modal_id}', 1)">{btn_label}</button>
            """

# Add the buttons at the end, so that they don't get covered by
# the images. Every slider needs a left and right button, and
# the modal window needs a close button.
# Then, close up the slider elements.
# Needs the following values:
#    modal_id, image_class
MODAL_SLIDER_END = """
                <button class="w3-button w3-black w3-display-bottomleft w3-xxlarge"
                    onclick="change_%(image_class)s(-1)"><i class="fas fa-angle-left"></i></button>
                <button class="w3-button w3-black w3-display-bottomright w3-xxlarge"
                    onclick="change_%(image_class)s(1)"><i class="fas fa-angle-right"></i></button>
                <button class="w3-btn w3-red w3-display-topright w3-large"
                    onclick="document.getElementById('%(modal_id)s').style.display='none'"><i class="fa fa-close"></i></button>
            </div>
        </div>
    </div>
"""

# Add an image in a container with its filename displayed in the
# upper left corner. The filename is 'w3-black' so that the text
# will be white and show up against the fMRI image without being
# too obtrusive.
# We assign a specific class so that scripts can find the images
# by calling getElementsByClassName().
# Needs the following values:
#    image_class, image_file, image_name.
IMAGE_WITH_NAME = """
                <div class="w3-display-container %(image_class)s">
                    <img src="%(image_file)s">
                    <div class="w3-display-topleft w3-black"><p>%(image_name)s</p></div>
                </div>
                """

# The slider scripts that will show the next or previous image
# in a given class.
# TODO: someday, try hiding JUST n, and then showing += n!
# Needs the following values:
#    image_class.
SLIDER_SCRIPTS = """
<script>
    var %(image_class)sIdx = 1;
    show_%(image_class)s(%(image_class)sIdx)

    function change_%(image_class)s(n) {
        show_%(image_class)s(%(image_class)sIdx += n)
    }

    function show_%(image_class)s(n) {
        var i;
        var x = document.getElementsByClassName("%(image_class)s");
        if (n > x.length) { %(image_class)sIdx = 1 }
        if (n < 1) { %(image_class)sIdx = x.length }
        for (i = 0; i < x.length; i++) {
            x[i].style.display = "none";
        }
        x[%(image_class)sIdx-1].style.display = "block";
    }

    function open_modal_to_index(modal_id, idx) {
        show_%(image_class)s(%(image_class)sIdx = idx)
        document.getElementById(modal_id).style.display='block'
    }
</script>
"""

# BRAINSPRITE STUFF

# The brainsprite canvas. Put this in the layout where you want the
# brainsprite to be seen.
# Needs the following values:
#    width, viewer, spriteImg, mosaic_path.
SPRITE_VIEWER_HTML = """
        <div w3-row w3-hide-small>
           <canvas id="%(viewer)s" style="max-width: %(width)s">
           <img id="%(spriteImg)s" class="hidden" src="%(mosaic_path)s">
        </div>
        """

# The loader script to be run when then window loads. Put this
# with other scripts.
# Needs the following values:
#    tx, viewer, spriteImg.
SPRITE_LOAD_SCRIPT = """
<script>
   $( window ).load(function() {
       var brain%(tx)s = brainsprite({
         canvas: "%(viewer)s",
         sprite: "%(spriteImg)s",
         nbSlice: { 'Y':218 , 'Z':218 },
         flagCoordinates: true,
       });
   });
</script>
"""

# The rest of this is scripts for brainsprite. Since brainsprite is no
# longer supported, and since this is working, leave as is!
# This contant is only needed once (thank goodness) and does not need
# any values inserted. Just include it in the HTML whereever you have
# your scripts.
BRAINSPRITE_SCRIPTS = """
<script>
function brainsprite(params) {

  // Function to add nearest neighbour interpolation to a canvas
  function setNearestNeighbour(context,flag){
    context.imageSmoothingEnabled = flag;
    return context;
  }

  // Initialize the brain object
  var brain = {};

  // Flag for "NaN" image values, i.e. unable to read values
  brain.nanValue = false;

  // Smoothing of the main slices
  brain.smooth = typeof params.smooth !== 'undefined' ? params.smooth: false;

  // drawing mode
  brain.fastDraw = typeof params.fastDraw !== 'undefined' ? params.fastDraw: false;

  // The main canvas, where the three slices are drawn
  brain.canvas = document.getElementById(params.canvas);
  brain.context = brain.canvas.getContext('2d');
  brain.context = setNearestNeighbour(brain.context,brain.smooth);

  // An in-memory canvas to draw intermediate reconstruction
  // of the coronal slice, at native resolution
  brain.canvasY = document.createElement('canvas');
  brain.contextY = brain.canvasY.getContext('2d');

  // An in-memory canvas to draw intermediate reconstruction
  // of the axial slice, at native resolution
  brain.canvasZ = document.createElement('canvas');
  brain.contextZ = brain.canvasZ.getContext('2d');

  // An in-memory canvas to read the value of pixels
  brain.canvasRead = document.createElement('canvas');
  brain.contextRead = brain.canvasRead.getContext('2d');
  brain.canvasRead.width = 1;
  brain.canvasRead.height = 1;

  // Onclick events
  brain.onclick = typeof params.onclick !== 'undefined' ? params.onclick : "";

  // Background color for the canvas
  brain.colorBackground = typeof params.colorBackground !== 'undefined' ? params.colorBackground : "#000000";

  // Flag to turn on/off slice numbers
  brain.flagCoordinates = typeof params.flagCoordinates !== 'undefined' ? params.flagCoordinates : false;

  // Origins and voxel size
  brain.origin = typeof params.origin !== 'undefined' ? params.origin : {X: 0, Y: 0, Z: 0};
  brain.voxelSize = typeof params.voxelSize !== 'undefined' ? params.voxelSize : 1;

  // Colorbar size parameters
  brain.heightColorBar = 0.04;

  // Font parameters
  brain.sizeFont = 0.075;
  brain.colorFont = typeof params.colorFont !== 'undefined' ? params.colorFont : "#FFFFFF";
  if (brain.flagCoordinates) {
    brain.spaceFont = 0.1;
  } else {
    brain.spaceFont = 0;
  };

  //******************//
  // The sprite image //
  //******************//
  brain.sprite = document.getElementById(params.sprite);

  // Number of columns and rows in the sprite
  brain.nbCol = brain.sprite.width/params.nbSlice.Y;
  brain.nbRow = brain.sprite.height/params.nbSlice.Z;
  // Number of slices
  brain.nbSlice = {
    X: brain.nbCol*brain.nbRow,
    Y: params.nbSlice.Y,
    Z: params.nbSlice.Z
  };
  // width and height for the canvas
  brain.widthCanvas  = {'X':0 , 'Y':0 , 'Z':0 };
  brain.heightCanvas = {'X':0 , 'Y':0 , 'Z':0 , 'max':0};
  // Default for current slices
  brain.numSlice = {
    'X': Math.floor(brain.nbSlice.X/2),
    'Y': Math.floor(brain.nbSlice.Y/2),
    'Z': Math.floor(brain.nbSlice.Z/2)
  };
  // Coordinates for current slices - these will get updated when drawing the slices
  brain.coordinatesSlice = {'X': 0, 'Y': 0, 'Z': 0 };

  //*************//
  // The planes  //
  //*************//
  brain.planes = {};
  // A series of canvas to represent the sprites along the three possible
  // plane X: sagital;
  brain.planes.canvasX = document.createElement('canvas');
  brain.planes.contextX = brain.planes.canvasX.getContext('2d');

  //*************//
  // The overlay //
  //*************//
  params.overlay = typeof params.overlay !== 'undefined' ? params.overlay : false;
  if (params.overlay) {
      // Initialize the overlay
      brain.overlay = {};
      // Get the sprite
      brain.overlay.sprite = document.getElementById(params.overlay.sprite);
      // Ratio between the resolution of the foreground and background
      // Number of columns and rows in the overlay
      brain.overlay.nbCol = brain.overlay.sprite.width/params.overlay.nbSlice.Y;
      brain.overlay.nbRow = brain.overlay.sprite.height/params.overlay.nbSlice.Z;
      // Number of slices in the overlay
      brain.overlay.nbSlice = {
        X: brain.overlay.nbCol*brain.overlay.nbRow,
        Y: params.overlay.nbSlice.Y,
        Z: params.overlay.nbSlice.Z
      };
      // opacity
      brain.overlay.opacity = typeof params.overlay.opacity !== 'undefined' ? params.overlay.opacity : 1;
  };

  //**************//
  // The colormap //
  //**************//
  params.colorMap = typeof params.colorMap !== 'undefined' ? params.colorMap: false;
  if (params.colorMap) {
      // Initialize the color map
      brain.colorMap = {};
      // Get the sprite
      brain.colorMap.img = document.getElementById(params.colorMap.img);
      // Set min / max
      brain.colorMap.min = params.colorMap.min;
      brain.colorMap.max = params.colorMap.max;
      // Set visibility
      params.colorMap.hide = typeof params.colorMap.hide !== 'undefined' ? params.colorMap.hide: false;
      // An in-memory canvas to store the colormap
      brain.colorMap.canvas = document.createElement('canvas');
      brain.colorMap.context = brain.colorMap.canvas.getContext('2d');
      brain.colorMap.canvas.width  = brain.colorMap.img.width;
      brain.colorMap.canvas.height = brain.colorMap.img.height;

      // Copy the color map in an in-memory canvas
      brain.colorMap.context.drawImage(brain.colorMap.img,
                0,0,brain.colorMap.img.width, brain.colorMap.img.height,
                0,0,brain.colorMap.img.width, brain.colorMap.img.height);
  };

  //*******************************************//
  // Extract the value associated with a voxel //
  //*******************************************//
  brain.getValue = function(rgb,colorMap) {
    if (!colorMap) {
      return NaN;
    }
    var cv, dist, nbColor, ind, val, voxelValue;
    nbColor = colorMap.canvas.width;
    ind = NaN;
    val = Infinity;
    for (xx=0; xx<nbColor; xx++) {
      cv = colorMap.context.getImageData(xx,0,1,1).data;
      dist = Math.pow(cv[0]-rgb[0],2)+Math.pow(cv[1]-rgb[1],2)+Math.pow(cv[2]-rgb[2],2);
      if (dist<val) {
        ind = xx;
        val = dist;
      }
    }
    voxelValue = (ind*(colorMap.max - colorMap.min)/(nbColor-1)) + colorMap.min;
    return voxelValue;
  };


  //***********************//
  // Initialize the viewer //
  //***********************//
  brain.init = function() {

    // Update the width of the X, Y and Z slices in the canvas, based on the width of its parent
    brain.widthCanvas.X = Math.floor(brain.canvas.parentElement.clientWidth*(brain.nbSlice.Y/(2*brain.nbSlice.X+brain.nbSlice.Y)));
    brain.widthCanvas.Y = Math.floor(brain.canvas.parentElement.clientWidth*(brain.nbSlice.X/(2*brain.nbSlice.X+brain.nbSlice.Y)));
    brain.widthCanvas.Z = Math.floor(brain.canvas.parentElement.clientWidth*(brain.nbSlice.X/(2*brain.nbSlice.X+brain.nbSlice.Y)));

    // Update the height of the slices in the canvas, based on width and image ratio
    brain.heightCanvas.X = Math.floor(brain.widthCanvas.X * brain.nbSlice.Z / brain.nbSlice.Y );
    brain.heightCanvas.Y = Math.floor(brain.widthCanvas.Y * brain.nbSlice.Z / brain.nbSlice.X );
    brain.heightCanvas.Z = Math.floor(brain.widthCanvas.Z * brain.nbSlice.Y / brain.nbSlice.X );
    brain.heightCanvas.max = Math.max(brain.heightCanvas.X,brain.heightCanvas.Y,brain.heightCanvas.Z);

    // Apply the width/height to the canvas, if necessary
    if (brain.canvas.width!=(brain.widthCanvas.X+brain.widthCanvas.Y+brain.widthCanvas.Z)) {
      brain.canvas.width = brain.widthCanvas.X+brain.widthCanvas.Y+brain.widthCanvas.Z;
      brain.canvas.height = Math.round((1+brain.spaceFont)*(brain.heightCanvas.max));
      brain.context = setNearestNeighbour(brain.context,brain.smooth);
    };

    // Size for fonts
    brain.sizeFontPixels = Math.round(brain.sizeFont*(brain.heightCanvas.max));

    // fonts
    brain.context.font = brain.sizeFontPixels + "px Arial";

    // Draw the X canvas
    brain.planes.canvasX.width = brain.sprite.width;
    brain.planes.canvasX.height = brain.sprite.height;
    brain.planes.contextX.globalAlpha = 1;
    brain.planes.contextX.drawImage(brain.sprite,
            0, 0, brain.sprite.width, brain.sprite.height,0, 0, brain.sprite.width, brain.sprite.height );
    if (brain.overlay) {
        // Draw the overlay on a canvas
        brain.planes.contextX.globalAlpha = brain.overlay.opacity;
        brain.planes.contextX.drawImage(brain.overlay.sprite,
            0, 0, brain.overlay.sprite.width, brain.overlay.sprite.height,0,0,brain.sprite.width,brain.sprite.height);
    };

    // Draw the Y canvas
    brain.planes.canvasY = document.createElement('canvas');
    brain.planes.contextY = brain.planes.canvasY.getContext('2d');
    if (brain.fastDraw) {
      brain.planes.canvasY.width  = brain.nbSlice.X * brain.nbCol;
      brain.planes.canvasY.height = brain.nbSlice.Z * Math.ceil(brain.nbSlice.Y/brain.nbCol);
      var pos = {};
      for (yy=0; yy<brain.nbSlice.Y; yy++) {
        for (xx=0; xx<brain.nbSlice.X; xx++) {
          pos.XW = (xx%brain.nbCol);
          pos.XH = (xx-pos.XW)/brain.nbCol;
          pos.YW = (yy%brain.nbCol);
          pos.YH = (yy-pos.YW)/brain.nbCol;
          brain.planes.contextY.globalAlpha = 1;
          brain.planes.contextY.drawImage(brain.sprite,
            pos.XW*brain.nbSlice.Y + yy, pos.XH*brain.nbSlice.Z, 1, brain.nbSlice.Z, pos.YW*brain.nbSlice.X + xx, pos.YH*brain.nbSlice.Z, 1, brain.nbSlice.Z );
          // Add the Y overlay
          if (brain.overlay) {
            brain.planes.contextY.globalAlpha = brain.overlay.opacity;
            brain.planes.contextY.drawImage(brain.overlay.sprite,
              pos.XW*brain.nbSlice.Y + yy, pos.XH*brain.nbSlice.Z, 1, brain.nbSlice.Z, pos.YW*brain.nbSlice.X + xx, pos.YH*brain.nbSlice.Z, 1, brain.nbSlice.Z );
          }
        }
      }
    } else {
      brain.planes.canvasY.width  = brain.nbSlice.X;
      brain.planes.canvasY.height = brain.nbSlice.Z;
    }

    // Draw the Z canvas
    brain.planes.canvasZ = document.createElement('canvas');
    brain.planes.contextZ = brain.planes.canvasZ.getContext('2d');
    if (brain.fastDraw) {
      brain.planes.canvasZ.height = Math.max(brain.nbSlice.X * brain.nbCol , brain.nbSlice.Y * Math.ceil(brain.nbSlice.Z/brain.nbCol));
      brain.planes.canvasZ.width  = brain.planes.canvasZ.height;
      brain.planes.contextZ.rotate(-Math.PI/2);
      brain.planes.contextZ.translate(-brain.planes.canvasZ.width,0);
      var pos = {};
      for (zz=0; zz<brain.nbSlice.Z; zz++) {
        for (xx=0; xx<brain.nbSlice.X; xx++) {
          pos.XW = (xx%brain.nbCol);
          pos.XH = (xx-pos.XW)/brain.nbCol;
          pos.ZH = zz%brain.nbCol;
          pos.ZW = Math.ceil(brain.nbSlice.Z/brain.nbCol)-1 -((zz-pos.ZH)/brain.nbCol);
          brain.planes.contextZ.globalAlpha = 1;
          brain.planes.contextZ.drawImage(brain.sprite,
            pos.XW*brain.nbSlice.Y , pos.XH*brain.nbSlice.Z + zz, brain.nbSlice.Y, 1, pos.ZW*brain.nbSlice.Y , pos.ZH*brain.nbSlice.X + xx , brain.nbSlice.Y , 1);
          // Add the Z overlay
          if (brain.overlay) {
            brain.planes.contextZ.globalAlpha = brain.overlay.opacity;
            brain.planes.contextZ.drawImage(brain.overlay.sprite,
              pos.XW*brain.nbSlice.Y , pos.XH*brain.nbSlice.Z + zz, brain.nbSlice.Y, 1, pos.ZW*brain.nbSlice.Y , pos.ZH*brain.nbSlice.X + xx , brain.nbSlice.Y , 1);
          }
        }
      }
    } else {
      brain.planes.canvasZ.width = brain.nbSlice.X;
      brain.planes.canvasZ.height = brain.nbSlice.Y;
      brain.planes.contextZ.rotate(-Math.PI/2);
      brain.planes.contextZ.translate(-brain.nbSlice.Y,0);
    }
  }

  //***************************************//
  // Draw a particular slice in the canvas //
  //***************************************//
  brain.draw = function(slice,type) {

    // Init variables
    var pos={}, coord, coordWidth;

    // Update the slice number
    brain.numSlice[type] = slice;

    // Update slice coordinates
    brain.coordinatesSlice.X = (brain.numSlice.X * brain.voxelSize) - brain.origin.X;
    brain.coordinatesSlice.Y = (brain.numSlice.Y * brain.voxelSize) - brain.origin.Y;
    brain.coordinatesSlice.Z = ((brain.nbSlice.Z-brain.numSlice.Z-1) * brain.voxelSize) - brain.origin.Z;

    // Update voxel value
    if (brain.overlay && !brain.nanValue) {
      try {
        pos.XW = ((brain.numSlice.X)%brain.nbCol);
        pos.XH = (brain.numSlice.X-pos.XW)/brain.nbCol;
        brain.contextRead.drawImage(brain.overlay.sprite,pos.XW*brain.nbSlice.Y+brain.numSlice.Y, pos.XH*brain.nbSlice.Z+brain.numSlice.Z, 1, 1,0, 0, 1, 1 );
        rgb = brain.contextRead.getImageData(0,0,1,1).data;
        brain.voxelValue = brain.getValue(rgb,brain.colorMap);
      }
      catch(err) {
        console.warn(err.message);
        rgb = 0;
        brain.nanValue = true;
        brain.voxelValue = NaN;
      }
    } else {
      brain.voxelValue = NaN;
    };
    // Now draw the slice
    switch(type) {
      case 'X':
        // Draw a sagital slice
        pos.XW = ((brain.numSlice.X)%brain.nbCol);
        pos.XH = (brain.numSlice.X-pos.XW)/brain.nbCol;
        // Set fill color for the slice
        brain.context.fillStyle=brain.colorBackground;
        brain.context.fillRect(0, 0, brain.widthCanvas.X , brain.canvas.height);
        brain.context.drawImage(brain.planes.canvasX,
                pos.XW*brain.nbSlice.Y, pos.XH*brain.nbSlice.Z, brain.nbSlice.Y, brain.nbSlice.Z,0, (brain.heightCanvas.max-brain.heightCanvas.X)/2, brain.widthCanvas.X, brain.heightCanvas.X );

        // Add X coordinates on the slice
        if (brain.flagCoordinates) {
          coord = "x="+brain.coordinatesSlice.X;
          coordWidth = brain.context.measureText(coord).width;
          brain.context.fillStyle = brain.colorFont;
          brain.context.fillText(coord,brain.widthCanvas.X/2-coordWidth/2,Math.round(brain.canvas.height-(brain.sizeFontPixels/2)));
        }
      break;
      case 'Y':
        // Draw a single coronal slice at native resolution
        brain.context.fillStyle=brain.colorBackground;
        brain.context.fillRect(brain.widthCanvas.X, 0, brain.widthCanvas.Y, brain.canvas.height);
        if (brain.fastDraw) {
          pos.YW = (brain.numSlice.Y%brain.nbCol);
          pos.YH = (brain.numSlice.Y-pos.YW)/brain.nbCol;
          brain.context.drawImage(brain.planes.canvasY,
            pos.YW*brain.nbSlice.X, pos.YH*brain.nbSlice.Z, brain.nbSlice.X, brain.nbSlice.Z, brain.widthCanvas.X, (brain.heightCanvas.max-brain.heightCanvas.Y)/2, brain.widthCanvas.Y, brain.heightCanvas.Y );
        } else {
          for (xx=0; xx<brain.nbSlice.X; xx++) {
            posW = (xx%brain.nbCol);
            posH = (xx-posW)/brain.nbCol;
            brain.planes.contextY.drawImage(brain.planes.canvasX,
                posW*brain.nbSlice.Y + brain.numSlice.Y, posH*brain.nbSlice.Z, 1, brain.nbSlice.Z, xx, 0, 1, brain.nbSlice.Z );
          }
          // Redraw the coronal slice in the canvas at screen resolution
          brain.context.drawImage(brain.planes.canvasY,
            0, 0, brain.nbSlice.X, brain.nbSlice.Z, brain.widthCanvas.X, (brain.heightCanvas.max-brain.heightCanvas.Y)/2, brain.widthCanvas.Y, brain.heightCanvas.Y );
        }

        // Add colorbar
        if ((brain.colorMap)&&(!brain.colorMap.hide)) {
          // draw the colorMap on the coronal slice at screen resolution
          brain.context.drawImage(brain.colorMap.img,
                0, 0, brain.colorMap.img.width, 1, Math.round(brain.widthCanvas.X + brain.widthCanvas.Y*0.2) , Math.round(brain.heightCanvas.max * brain.heightColorBar / 2), Math.round(brain.widthCanvas.Y*0.6) , Math.round(brain.heightCanvas.max * brain.heightColorBar));
          brain.context.fillStyle = brain.colorFont;
          brain.context.fillText(brain.colorMap.min,brain.widthCanvas.X+(brain.widthCanvas.Y*0.2),Math.round( (brain.heightCanvas.max*brain.heightColorBar*2) + (3/4)*(brain.sizeFontPixels) ));
          brain.context.fillText(brain.colorMap.max,brain.widthCanvas.X+(brain.widthCanvas.Y*0.8)-brain.context.measureText(brain.colorMap.max).width,Math.round( (brain.heightCanvas.max*brain.heightColorBar*2) + (3/4)*(brain.sizeFontPixels) ));
        }

        // Add Y coordinates on the slice
        if (brain.flagCoordinates) {
          brain.context.font = brain.sizeFontPixels + "px Arial";
          brain.context.fillStyle = brain.colorFont;
          coord = "y="+brain.coordinatesSlice.Y;
          coordWidth = brain.context.measureText(coord).width;
          brain.context.fillText(coord,brain.widthCanvas.X+(brain.widthCanvas.Y/2)-coordWidth/2,Math.round(brain.canvas.height-(brain.sizeFontPixels/2)));
        }

      case 'Z':
        // Draw a single axial slice at native resolution
        brain.context.fillStyle=brain.colorBackground;
        brain.context.fillRect(brain.widthCanvas.X+brain.widthCanvas.Y, 0, brain.widthCanvas.Z, brain.canvas.height);

        if (brain.fastDraw) {
          pos.ZW = (brain.numSlice.Z%brain.nbCol);
          pos.ZH = (brain.numSlice.Z-pos.ZW)/brain.nbCol;
          brain.context.drawImage(brain.planes.canvasZ,
                pos.ZW*brain.nbSlice.X, pos.ZH*brain.nbSlice.Y, brain.nbSlice.X, brain.nbSlice.Y, brain.widthCanvas.X+brain.widthCanvas.Y, (brain.heightCanvas.max-brain.heightCanvas.Z)/2, brain.widthCanvas.Z, brain.heightCanvas.Z );
        } else {
          for (xx=0; xx<brain.nbSlice.X; xx++) {
            posW = (xx%brain.nbCol);
            posH = (xx-posW)/brain.nbCol;
            brain.planes.contextZ.drawImage(brain.planes.canvasX,
                posW*brain.nbSlice.Y , posH*brain.nbSlice.Z + brain.numSlice.Z, brain.nbSlice.Y, 1, 0, xx, brain.nbSlice.Y, 1 );

          }
          // Redraw the axial slice in the canvas at screen resolution
          brain.context.drawImage(brain.planes.canvasZ,
            0, 0, brain.nbSlice.X, brain.nbSlice.Y, brain.widthCanvas.X+brain.widthCanvas.Y, (brain.heightCanvas.max-brain.heightCanvas.Z)/2, brain.widthCanvas.Z, brain.heightCanvas.Z );
        }
        // Add Z coordinates on the slice
        if (brain.flagCoordinates) {
          coord = "z="+brain.coordinatesSlice.Z;
          coordWidth = brain.context.measureText(coord).width;
          brain.context.fillStyle = brain.colorFont;
          brain.context.fillText(coord,brain.widthCanvas.X+brain.widthCanvas.Y+(brain.widthCanvas.Z/2)-coordWidth/2,Math.round(brain.canvas.height-(brain.sizeFontPixels/2)));
        }
    }
  };

  // In case of click, update brain slices
  brain.clickBrain = function(e){
    var rect = brain.canvas.getBoundingClientRect();
    var xx = e.clientX - rect.left;
    var yy = e.clientY - rect.top;
    var sy, sz;

    if (xx<brain.widthCanvas.X){
      sy = Math.round(brain.nbSlice.Y*(xx/brain.widthCanvas.X));
      sz = Math.round(brain.nbSlice.Z*(yy-((brain.heightCanvas.max-brain.heightCanvas.X)/2))/brain.heightCanvas.X);
      brain.draw(Math.max(Math.min(sy,brain.nbSlice.Y-1),0),'Y');
      brain.draw(Math.max(Math.min(sz,brain.nbSlice.Z-1),0),'Z');
    } else if (xx<(brain.widthCanvas.X+brain.widthCanvas.Y)) {
      xx = xx-brain.widthCanvas.X;
      sx = Math.round(brain.nbSlice.X*(xx/brain.widthCanvas.Y));
      sz = Math.round(brain.nbSlice.Z*(yy-((brain.heightCanvas.max-brain.heightCanvas.Y)/2))/brain.heightCanvas.Y);
      brain.draw(Math.max(Math.min(sx,brain.nbSlice.X-1),0),'X');
      brain.draw(Math.max(Math.min(sz,brain.nbSlice.Z-1),0),'Z');
    } else {
      xx = xx-brain.widthCanvas.X-brain.widthCanvas.Y;
      sx = Math.round(brain.nbSlice.X*(xx/brain.widthCanvas.Z));
      sy = Math.round(brain.nbSlice.Y*(1-((yy-((brain.heightCanvas.max-brain.heightCanvas.Z)/2))/brain.heightCanvas.Z)));
      brain.draw(Math.max(Math.min(sx,brain.nbSlice.X-1),0),'X');
      brain.draw(Math.max(Math.min(sy,brain.nbSlice.Y-1),0),'Y');
      brain.draw(brain.numSlice.Z,'Z');
    };
    if (brain.onclick) {
      brain.onclick(e);
    };
  };

  brain.drawAll = function(){
    brain.draw(brain.numSlice.X,'X');
    brain.draw(brain.numSlice.Y,'Y');
    brain.draw(brain.numSlice.Z,'Z');
  };

  // Attach a listener for clicks
  brain.canvas.addEventListener('click', brain.clickBrain, false);

  // Attach a listener on mouse down
  brain.canvas.addEventListener('mousedown', function(e) {
    brain.canvas.addEventListener('mousemove', brain.clickBrain, false);
  }, false);

  // Detach the listener on mouse up
  brain.canvas.addEventListener('mouseup', function(e) {
      brain.canvas.removeEventListener('mousemove', brain.clickBrain, false);
    }, false);

  // Draw all slices when background/overlay are loaded
  brain.sprite.addEventListener('load', function(){
    brain.init();
    brain.drawAll();
  });
  if (brain.overlay) {
    brain.overlay.sprite.addEventListener('load', function(){
      brain.init();
      brain.drawAll();
    });
  }

  // Init the viewer
  brain.init();

  // Draw all slices
  brain.drawAll();

  return brain;
};
</script>
<script src="http://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
<script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.9.1/jquery-ui.min.js"></script>
"""


