#! /home/exacloud/lustre1/fnl_lab/code/external/utilities/anaconda2/bin/python

"""
Call this program with -s, pointing to a subject-summary_tools path, to build the Executive Summary for that subject's
processed data.
-o for optional output_directory; (default = user's home directory)

__author__ = 'Shannon Buckley', 2/20/16
"""

import os
from os import path
import re
import argparse
import image_summary
from image_summary import _logger
import glob
import shutil
import logging
import sys
from helpers import shenanigans

PROG = 'Layout Builder'
VERSION = '1.4.2'
LAST_MOD = '7-11-17'

program_desc = """%(prog)s v%(ver)s:
Builds the layout for the Executive Summary by writing-out chunks of html with some help from image_summary methods.
Use -s /path/to/subjectfolder/with/summary_subfolder to launch and build a summary page.
Has embedded css & jquery elements.
""" % {'prog': PROG, 'ver': VERSION}


def get_parser():

    parser = argparse.ArgumentParser(description=program_desc, prog=PROG, version=VERSION)

    parser.add_argument('-s', '--subject_path', dest='subject_path', action='append',
                        help='''Expects path to a subject-level directory of processed data, which should have a
                        'summary' folder within (e.g./remote_home/bucklesh/Projects/TestData/ABCDPILOT_MSC02/)''')

    parser.add_argument('-o', '--output_path', dest='output_path', action='store',
                        help='''Expects path to a folder you can write to in order to copy final outputs there. Final
                        goodies will be inside a directory on the output_path: date_stamp/SUBJ_ID.''')

    parser.add_argument('-l', '--list_file', dest='list_file', required=False, help="""Optional: path to file containing
    list of processed-subject-paths, e.g. /scratch/HCP/processed/ASD-blah/subjCode/VisitID/subjCode .""")

    parser.add_argument('--verbose', dest="verbose", action="store_true", help="Tell me all about it.")

    parser.add_argument('-vv', '--very_verbose', dest="very_verbose", action="store_true", help="Tell me all about it.")

    return parser

# HTML BUILDING BLOCKS
html_header = """<!DOCTYPE html>
<html lang = "en">
    <head>
        <meta charset = "utf-8">
        <title>Executive Summary: CODE_VISIT</title>
        <style type="text/css">.epi,.grayords,.params{position:relative}.header,button,table,td{text-align:center}body{background-color:#c3c4c3}span{font-size:10px}img{border-radius:5px}.header{font-family:Garamond;margin-top:25px;margin-bottom:15px}table,td{border:1px dashed #70b8ff}.epi td,.params td,.top-left-panel table,td{border:none}.top-left-panel{float:left;width:50%}.top-left-panel img{width:250px;height:200px}.epi{float:right}.epi img{width:175px;height:150px}.raw_rest_img img {width: 300px;height: 110px}.params{float:left;width:40%}.params th{border-bottom:1px #70b8ff solid}.params .column-names{border-bottom:1px #00f solid;font-weight:700}.grayords{float:right}.grayords img{width:525px;height:450px}.out-of-range{color:red}button{cursor:pointer;display:inline-block;height:20px;width:70px;font-family:arial;font-weight:700;margin-top:2px}
        </style>
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

    </head>
    <body>
        <div class="header">
            <h1>CODE_VISIT</h1>
            <p>VERSION</p>
            </div>
        </div>"""

param_table_html_header = """
        <div class="bottom-row">
            <div class="params">
                <table id="param_table">
                    <thead>
                        <th colspan="8">
                            Acquisition Parameters
                        </th>
                    </thead>
                    <tbody>
                        <tr class="column-names">
                            <td>Modality</td>
                            <td>x <span>(mm)</span></td>
                            <td>y <span>(mm)</span></td>
                            <td>z <span>(mm)</span></td>
                            <td>TE <span>(ms)</span></td>
                            <td>TR <span>(ms)</span></td>
                            <td>Frames <span>(n)</span></td>
                            <td>TI <span>(ms)</span></td>
                        </tr>"""

param_table_footer = """
                    </tbody>
                </table>
            </div>"""

series_panel_header = """
            <div class="epi">
                <table id="epi">
                    <thead>
                        <th colspan="4">
                            Resting State and Task Data
                        </th>
                    </thead>
                    <tbody>"""

series_panel_footer = """
                    </tbody>
                </table>
            </div>
        </div>"""

html_footer = """
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
        <script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.9.1/jquery-ui.min.js"></script>
        <script>$(document).ready(function(){$("img[src*=SBRef]").width(300).height(110),$('img').filter('.raw_rest_img').width(300).height(110),$(".t1_tr").each(function(t,a){"2400.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t1_te").each(function(t,a){"4.97"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t1_x").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t1_y").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t1_z").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_frames").each(function(t,a){"120"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_x").each(function(t,a){"3.8"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_y").each(function(t,a){"3.8"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_z").each(function(t,a){"3.8"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_tr").each(function(t,a){"2100.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_te").each(function(t,a){"5.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t2_x").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t2_y").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t2_z").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t2_tr").each(function(t,a){"3200.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t2_te").each(function(t,a){"4.97"!=$(a).text()&&$(a).addClass("out-of-range")}),$("div.params").draggable(),$("div.grayords").draggable(),$("div.epi").draggable()});
        </script>
        <script>
           $( window ).load(function() {
               var brain = brainsprite({
                 canvas: "viewer",
                 sprite: "spriteImg",
                 nbSlice: { 'Y':218 , 'Z':218 },
                 flagCoordinates: true,
               });
           });           
       </script>
    </body>
</html>
"""


def write_html(template, dest_dir, title="executive_summary.html"):
    """
    Takes an html template string and a destination, then writes it out to a default title.

    :parameter: template: path to html template
    :parameter: dest_dir: output path for final .html file
    :parameter: title: string to apply to output
    :return: None
    """

    if not title.endswith('.html'):
        title += '.html'

    try:
        f = open(path.join(dest_dir, title), 'w')
        f.writelines(template)
        f.close()
    except IOError:
        print 'cannot write there for some reason...'


def make_brainsprite_viewer(png_path, mosaic_path):
    """
    Builds HTML panel for BrainSprite viewer so users can click through 3d anatomical images.

    :return: string of html containing a div row with a canvas and hidden BrainSprite mosaic image
    """

    image_summary.make_mosaic(png_path, mosaic_path)

    structural_html_panel = """
    <div class="top-row">
            <div class="structural">
                <div style="max-width:100%;height:auto;">
                    <p>BrainSprite Viewer: T1</p>
                    <canvas id="viewer" style="max-width:100%;">
                    <img id="spriteImg" class="hidden" src="./img/mosaic.jpg">
                </div>
            </div>
    </div>"""
    return structural_html_panel


def edit_html_chunk(html_string, thing_to_find, thing_that_replaces_it):
    """
    Takes some html string, does a find/replace on it.

    :parameter: html_string: any string, really
    :parameter: thing_to_find: any string
    :parameter: thing_that_replaces_it: replacement string
    :return: new string with replacement
    """

    new_html_string = html_string.replace(thing_to_find, thing_that_replaces_it)

    return new_html_string


def write_param_table_row(list_of_data):
    """
    Takes a list of data and fills in one row in the parameter table per datum

    :parameter: list_of_data: list of data with 8 elements
    :return: param_table_row with specific metrics (8 columns)
    """

#    if len(list_of_data) != 8 or list_of_data[5] == '' or list_of_data[0] == '':
#        _logger.error('list of data is incomplete:\n%s' % list_of_data)
#        print 'list of data is incomplete:\n%s' % list_of_data
#        return

    param_table_html_row = """
                        <tr class="%(class_prefix)s_data">
                            <td>%(modality)s</td>
                            <td id="%(class_prefix)s_x" class="%(class_prefix)s_x">%(x_dim)s</td>
                            <td id="%(class_prefix)s_y" class="%(class_prefix)s_y">%(y_dim)s</td>
                            <td id="%(class_prefix)s_z" class="%(class_prefix)s_z">%(z_dim)s</td>
                            <td id="%(class_prefix)s_te" class="te">%(te)s</td>
                            <td id="%(class_prefix)s_tr">%(tr)s</td>
                            <td id="%(class_prefix)s_frames" class="%(class_prefix)s_frames">%(frames)s</td>
                            <td id="%(class_prefix)s_ti">%(ti)s</td>
                        </tr>""" % {'modality': list_of_data[0],
                                    'class_prefix': list_of_data[0].lower(),
                                    'x_dim': list_of_data[1],
                                    'y_dim': list_of_data[2],
                                    'z_dim': list_of_data[3],
                                    'te': list_of_data[4],
                                    'tr': list_of_data[5],
                                    'frames': list_of_data[6],
                                    'ti': list_of_data[7]
                                    }

    return param_table_html_row


def write_series_panel_row(list_of_img_paths):
    """
    Takes a list of image paths and builds one row of series images for the panel.

    :parameter: list_of_img_paths: list of paths
    :return: one row of an html table, <tr> to </tr> with epi or task images for a given series
    """

    series_type_re = r'(REST|SST|MID|nBack)\d+'
    compiled_series_type = re.compile(series_type_re)
    series_type = compiled_series_type.search(list_of_img_paths[5]).group()
    print "Making series panel for " + series_type

    series_panel_row = """
                    <tr>
                        <td><b>%(series_type)s</b></td>
                        <td><a href="%(dvars)s" target="_blank"><img src="%(dvars)s"></a></td>
			<td><a href="%(dvars_postreg)s" target="_blank"><img src="%(dvars_postreg)s"></a></td>
                        <td><a href="%(series_in_t1)s" target="_blank"><img src="%(series_in_t1)s"></a></td>
                        <td><a href="%(t1_in_series)s" target="_blank"><img src="%(t1_in_series)s"></a></td>
                        <td><a href="%(sb_ref)s" target="_blank"><img src="%(sb_ref)s" class="raw_rest_img"></a></td>
                        <td><a href="%(nonlin_norm)s" target="_blank"><img src="%(nonlin_norm)s"
                            class="raw_rest_img"></a></td>
                    </tr>""" % {'series_type'       : series_type,
                                'dvars'             : list_of_img_paths[0],
                                'dvars_postreg'     : list_of_img_paths[1],
                                'series_in_t1'        : list_of_img_paths[2],
                                't1_in_series'        : list_of_img_paths[3],
                                'sb_ref'            : list_of_img_paths[4],
                                'nonlin_norm'  : list_of_img_paths[5]}

    return series_panel_row


def make_series_panel(series_rows_list, header=series_panel_header, footer=series_panel_footer):
    """
    Takes a list of panel rows (html_strings), a header and footer to build the full series panel.

    :parameter: series_rows_list: list of data rows (strings)
    :parameter: header: div section opener
    :parameter: footer: dev section closer
    :return: html string for the whole epi-panel div (one row of images per REST)
    """

    series_panel_html = header

    for row in series_rows_list:
        series_panel_html += row
    series_panel_html += footer

    return series_panel_html


def write_dvars_panel(dvars_input_path='img/DVARS_and_FD_CONCA.png', dvars_concp_input_path='img/DVARS_and_FD_CONCP.png'):
    """
    Takes a path to a specific image and writes up a div for it

    :parameter: dvars_input_path: path to DVARS image.png expected
    :return: div section string for DVARS
    """

    dvars_panel_html_string = """
            <div class="grayords">
                <table class="grayords">
                <thead>
                    <th colspan="1">
                        Resting State Grayordinates Plot (pre-regression)
                    </th>
                </thead>
                <tbody>
                    <tr>
                        <td><a href="%(dvars_path)s" target="_blank">
                                <img src="%(dvars_path)s"></a>
                        </td>

                    </tr>
                    <th colspan="1">
                        Resting State Grayordinates Plot (post-regression)
                    </th>
		    <tr>
                        <td><a href="%(dvars_p_path)s" target="_blank">
                                <img src="%(dvars_p_path)s"></a>
                        </td>
		    </tr>
                    </tbody>
                </table>
            </div>""" % {'dvars_path' : dvars_input_path, 'dvars_p_path': dvars_concp_input_path}

    return dvars_panel_html_string


def append_html_with_chunk(existing_html, string_to_insert):
    """
    Takes some html string, appends a chunk to it, returns the new chunk+extension.

    :parameter: existing_html: string
    :parameter: string_to_insert: another string
    :return: appended string
    """

    new_html_string = existing_html + string_to_insert

    return new_html_string


def copy_images(src_dir, list_of_images, dst_dir='./img/'):
    """
    Takes a source dir and a list of images, copies them to a default destination ./img.

    :parameter: src_dir: copy from path
    :parameter: list_of_images: list of image names to copy (full paths not expected)
    :parameter: dst_dir: copy to  path
    :return: None
    """

    if type(list_of_images) == str:
        img_path = path.join(src_dir, list_of_images)
        shutil.copyfile(img_path, dst_dir)

    elif type(list_of_images) == list:
        for image in list_of_images:
            img_path = path.join(src_dir, image)
            shutil.copyfile(img_path, path.join(dst_dir, image))


def natural_sort(l):
    """
    Returns a list of strings sorted in alphanumeric order, with multi-digit
    numbers treated as a single item. e.g. native Python sort() produces this
    order: ['item1', 'item10', 'item2'] whereas natural_sort() produces this
    order: ['item1', 'item2', 'item10'].

    :parameter: l: list of strings
    :return: same list of strings with natural sort
    """ 
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
 
    return sorted(l, key = alphanum_key)


def find_series_numbers(path_list, regex):
    """
    Locates series numbers within a list of image paths.

    :parameter: path_list: list of image paths (strings)
    :paramater: regex: regular expression describing where to find series numbers
    :returns: list of series numbers (natural sort)
    """

#    print 'Doing find_series numbers on...'
#    print 'path_list:'
#    print path_list
#    print 'regex:'
#    print regex

    filtered_list = []
    compiled_regex = re.compile(regex)

    for item in path_list:
        filtered = compiled_regex.search(item)
        if filtered:
            filtered = filtered.group()
            filtered_num = re.search(r'\d+', filtered).group()
            filtered_list.append(filtered_num)

    sorted_list = natural_sort(filtered_list)

    return sorted_list


def insert_placeholders(image_path_lists, rest_or_task='REST'):
    """
    Fills in any gaps (missing series) in lists of image paths with placeholder
    images.

    :parameter: image_path_lists: list of image path lists that need to be altered
    :parameter: rest_or_task: indicates whether images are rest or task, and if task, which one
    :returns: list of image path lists with paths to placeholder images where needed
    """
    
    corrected_lists = []


    dvars_re         = r'DVARS_and_FD_(?:[rt]fMRI_)?(REST|SST|MID|nBack)\d+'
    postreg_dvars_re = r'_DVARS_and_FD_(?:[rt]fMRI_)?(REST|SST|MID|nBack)\d+'
    series_t1_re     = r'(REST|SST|MID|nBack)\d+_'
    t1_series_re     = r'_in_(?:[rt]fMRI_)?(REST|SST|MID|nBack)\d+'
    sbref_re         = r'SBRef_(REST|SST|MID|nBack)\d+'
    rest_re          = r'(REST|SST|MID|nBack)\d+'

    dvars_nums = find_series_numbers(image_path_lists[0], dvars_re)
    postreg_dvars_nums = find_series_numbers(image_path_lists[1], postreg_dvars_re)
    series_t1_nums = find_series_numbers(image_path_lists[2], series_t1_re)
    t1_series_nums = find_series_numbers(image_path_lists[3], t1_series_re)
    sbref_nums = find_series_numbers(image_path_lists[4], sbref_re)
    rest_nums = find_series_numbers(image_path_lists[5], rest_re)

    numbers_lists = [dvars_nums, postreg_dvars_nums, series_t1_nums, t1_series_nums, sbref_nums, rest_nums]
 
    # Check if there are any gaps in image sequence that need to be filled by placeholders
    missing = []
    for x in xrange(0, len(numbers_lists)):
        for l in numbers_lists:
            missing += [obj for obj in l if obj not in numbers_lists[x]]
        missing = natural_sort(list(set(missing)))

    for l in image_path_lists:
        new_l = []
        list_index = image_path_lists.index(l)
        if list_index in [0, 1, 2, 3]:
            placeholder_path = './img/square_placeholder_text.png'
        else:
            placeholder_path = './img/rectangular_placeholder_text.png'

        # Fill in gaps with placeholder images if necessary
        if (rest_or_task == 'REST'):
            r_or_t = 'r'
        else:
            r_or_t = 't'
        if missing:
            for x in xrange(int(missing[0]), int(missing[-1]) + 1):
                if list_index == 0:
                    sequence_text = 'DVARS_and_FD_' + r_or_t + 'fMRI_' + rest_or_task + str(x)
                elif list_index == 1:
                    sequence_text = 'postreg_DVARS_and_FD_' + r_or_t + 'fMRI_' + rest_or_task + str(x)
                elif list_index == 2:
                    sequence_text = str(x) + '_in_t1'
                elif list_index == 3:
                    sequence_text = 't1_in_' + r_or_t + 'fMRI_' + rest_or_task + str(x)
                elif list_index == 4:
                    sequence_text = 'SBRef_' + rest_or_task + str(x)
                elif list_index == 5:
                    sequence_text = rest_or_task + str(x)

                match = [s for s in l if sequence_text in s]
                if match:
                    new_l.append(match[0])
                else:
                    new_l.append(placeholder_path)
                    _logger.error('\n%s image expected and not found in summary folder\n' % (sequence_text))
            corrected_lists.append(new_l)

    if corrected_lists:
        return corrected_lists
    else:
        return image_path_lists


def main():

    parser = get_parser()

    script_dir = os.path.dirname(os.path.realpath(__file__))
    program_dir = os.path.abspath(os.path.join(script_dir, os.pardir))

    args = parser.parse_args()

    if args.verbose:
        _logger.setLevel(logging.INFO)
    elif args.very_verbose:
        _logger.setLevel(logging.DEBUG)
    else:
        _logger.setLevel(logging.ERROR)

    if args.list_file:

        file_we_read_in = path.join(args.list_file)

        if not path.exists(file_we_read_in) or not file_we_read_in.endswith('.txt'):
            shenanigans.update_user('List FILE (.txt) does not exist, please verify your path to: \n%s' %
                                    file_we_read_in)

        if path.exists(file_we_read_in):

            paths_to_process = shenanigans.read_list_file(file_we_read_in)

            # print paths_to_process

            for path_to_proc in paths_to_process:

                path_to_proc = path_to_proc.strip('\n')

                command = 'python %s -s %s' % (sys.argv[0], path.join(path_to_proc))

                shenanigans.submit_command(command)

    if args.subject_path:

        for sub in args.subject_path:

            sub_root = path.join(sub)

            if path.exists(sub_root):

                sub_root = shenanigans.handle_trailing_slash(sub_root)

                # ------------------------- > GATHER BASIC INFO < ------------------------- #

                summary_path, data_path = image_summary.get_paths(sub_root)

                if sub_root.endswith('/'):
                    sub_root = sub_root[:-1]

                subj_id = sub_root.split('/')[-1]

                visit_id = sub_root.split('/')[-3]

                print '\nSubjID and Visit: %s %s: \n\n' % (subj_id, visit_id)

                pipeline_version = sub_root.split('/')[-2]

                date = image_summary.date_stamp

                if 'release' not in pipeline_version:
                    print '\nthis may or may not workout if this is not a standard HCP_release! *fingers crossed*'

                print '\npipeline_version is: %s\n' % pipeline_version

                shenanigans.update_user('SubjID and Visit: \n%s %s\nPipeline: %s' % (subj_id, visit_id,
                                                                                     pipeline_version))

                date = image_summary.date_stamp

                # ------------------------- > WRITE OUT SUMMARY REPORT < ------------------------- #
                with open(path.join(sub_root, 'Summary_Report.txt'), 'w') as f:

                    info = '''
                            Executive Summary ran on %s
                            pipeline %s was detected
                            Subject Path provided: \n%s
                            Subject Code: %s
                            Visti_ID: %s
                            Args: \n%s
                            ''' % (date, pipeline_version, sub_root, subj_id, visit_id, args)

                    f.write(info)
                    f.close()

            else:

                print '\nNo subject directory found within %s \nexiting...' % sub
                _logger.error('\nNo subject directory within %s \nexiting...' % sub)

                continue

            # --------------------------------- > SETUP PATHS < --------------------------------- #
            if path.exists(summary_path):

		if 'v2' or 'infant' in summary_path:

		    img_out_path = path.join(summary_path, 'img')
		    T1_path = path.join(summary_path, 'T1_pngs')

		else:

		    img_out_path = path.join(sub_root, 'summary', 'img')
		    T1_path = path.join(sub_root, 'summary', 'T1_pngs')

                img_in_path = summary_path
                subject_code_folder = path.join(summary_path, subj_id + '_' + visit_id)

            else:

                print '\nMake sure a "summary" folder exists or this will not work...\n\tcheck in here: %s' % sub_root
                _logger.error('\nno Summary folder exists within %s\n' % sub_root)

                continue
            # ------------------------- > MAKE /img or quit ... CHECK IMAGES < ------------------------- #
            if path.exists(img_out_path):

                shutil.rmtree(img_out_path,ignore_errors=True)

            try:

                os.makedirs(img_out_path)

            except OSError:

                print '\nCheck permissions to write to that path? \npath: %s' % summary_path
                _logger.error('cannot make /img within /summary... permissions? \nPath: %s' % summary_path)

                return

            try:
                gifs = [gif for gif in os.listdir(img_in_path) if gif.endswith('gif')]

                if len(gifs) == 0:

                    print img_in_path

                    _logger.error('no .gifs in summary folder')
                    print '\nNo summary .gifs were found! There should be some .gifs and I do not make those! '\
                        'Check to make sure FNL_preproc has been ran? '

                    return

                else:

                    copy_images(img_in_path, gifs, img_out_path)

                    data = image_summary.get_list_of_data(data_path)

                    _logger.debug('data are: %s' % data)


            except OSError:

                    print '\n\tUnable to locate image sources...'

                    return

            # Copy DVARS pngs to /img folder

            dvars = [img for img in os.listdir(img_in_path) if (img.endswith('png')) and 'DVARS' in img]
            copy_images(img_in_path, dvars, img_out_path)

            # Copy placeholder images to /img folder
            placeholders = ['square_placeholder_text.png', 'rectangular_placeholder_text.png']
            placeholder_path = os.path.join(program_dir, 'placeholder_pictures')

            copy_images(placeholder_path, placeholders, img_out_path)

            # ------------------------- > Make lists of paths to be used in the series panel < -------------------------- #
            real_data = []
            rest_in_t1_gifs = natural_sort([path.join('./img', path.basename(gif)) for gif in gifs if ('_in_t1.gif' in gif) and ('REST' in gif) and ('atlas' not in gif)])
            mid_in_t1_gifs = natural_sort([path.join('./img', path.basename(gif)) for gif in gifs if ('_in_t1.gif' in gif) and ('MID' in gif) and ('atlas' not in gif)])
            nback_in_t1_gifs = natural_sort([path.join('./img', path.basename(gif)) for gif in gifs if ('_in_t1.gif' in gif) and ('nBack' in gif) and ('atlas' not in gif)])
            sst_in_t1_gifs = natural_sort([path.join('./img', path.basename(gif)) for gif in gifs if ('_in_t1.gif' in gif) and ('SST' in gif) and ('atlas' not in gif)])


            t1_in_rest_gifs = natural_sort([path.join('./img', path.basename(gif)) for gif in gifs if ('_t1_in_' in gif) and ('REST' in gif)])
            t1_in_mid_gifs = natural_sort([path.join('./img', path.basename(gif)) for gif in gifs if ('_t1_in_' in gif) and ('MID' in gif)])
            t1_in_nback_gifs = natural_sort([path.join('./img', path.basename(gif)) for gif in gifs if ('_t1_in_' in gif) and ('nBack' in gif)])
            t1_in_sst_gifs = natural_sort([path.join('./img', path.basename(gif)) for gif in gifs if ('_t1_in_' in gif) and ('SST' in gif)])


            # setup an output directory
            if path.exists(subject_code_folder):
                shutil.rmtree(subject_code_folder,ignore_errors=True)

            os.makedirs(subject_code_folder)

            # ------------------------- > Check list of epi-data to ensure even numbers of files... < ---------------- #
            # TODO: improve this section with a more specific test

#            if len(data['epi-data']) == len(glob.glob(path.join(sub_root,'REST*'))):  # we should have at least 1 raw REST and 1 SBRef per subject (pairs)
#
#                _logger.warning('odd number of epi files were found...')
#                print '\nLooking for SBRef images...\n'
#
#                # locate an alternative source for SBRef images -> MNINonLinear/Results/REST*
#
#                # alt_sbref_path = path.join(sub_root, 'MNINonLinear', 'Results')
#                # pattern = alt_sbref_path + '/REST*/REST*_SBRef.nii.gz'
#                # more_epi = glob.glob(pattern)
#                #
#                # for sbref in more_epi:
#                #     data['epi-data'].append(sbref)
#
#                # TODO: TEST: LOCATE ANOTHER ALTERNATIVE SBRef SOURCE
#                alternate_sbref_path = path.join(sub_root)
#                sbref_pattern = alternate_sbref_path + '/REST*/Scout_orig.nii.gz'
#
#                more_sbref = glob.glob(sbref_pattern)
#                # print 'found additional SBRef files: %s' % more_sbref
#
#                for sbref in more_sbref:
#                    data['epi-data'].append(sbref)

            print '\nLooking for SBRef images...\n'
            alternate_sbref_path = path.join(sub_root)
            sbref_pattern = alternate_sbref_path + '/*REST*/Scout_orig.nii.gz'
            task_sbref_pattern = alternate_sbref_path + '/*tfMRI*/Scout_orig.nii.gz'
            more_task_sbref = glob.glob(task_sbref_pattern)
            more_sbref = glob.glob(sbref_pattern)
            all_sbref = more_sbref + more_task_sbref            
            for sbref in all_sbref:
                data['epi-data'].append(sbref)

            # ------------------------- > SLICING UP IMAGES FOR EPI DATA LIST < ------------------------- #

            for list_entry in data['epi-data']:

                info = image_summary.get_subject_info(list_entry)

                # get modality / series so we can know how to slice & label ...
                modality, series = info[1], info[2]
                print '\nPROCESSING subject_code: %s, modality: %s ' % (subj_id, modality)
                print 'slicing images for: \n%s' % list_entry

                if 'REST' or 'SST' or 'MID' or 'nBack' in modality and 'SBRef' not in modality:

                    image_summary.slice_list_of_data([list_entry], subject_code=subj_id, modality=modality,
                                                     dest_dir=img_out_path, also_xyz=True)

                elif 'SBRef' in modality and 'REST' in modality:

                    image_summary.slice_image_to_ortho_row(list_entry, path.join(img_out_path, '%s.png' % modality))

                elif 'SBRef' in modality and 'SST' or 'MID' or 'nBack' in modality:

                    image_summary.slice_image_to_ortho_row(list_entry, path.join(img_out_path, '%s.png' % modality))

                elif 'SBRef' in modality:

                    image_summary.slice_image_to_ortho_row(list_entry, path.join(img_out_path, '%s%s.png' % (modality,
                                                                                                             series)))
                                                                                                             
            # ITERATE through data dictionary keys, sort the list (value), then iterate through each list for params
            for list_entry in data.values():

                list_entry = sorted(list_entry)

                for item in list_entry:

                    information = image_summary.get_subject_info(item)

                    modality, series = information[1], information[2]

#                    dicom_for_te_grabber = shenanigans.get_airc_dicom_path_from_nifti_info(sub_root, modality)

                    dicom_root_dir = path.join(sub_root, 'unprocessed/DICOM/')

                    dicom_for_te_grabber = shenanigans.get_dicom_path_from_nifti_info(dicom_root_dir, modality)

#                    if dicom_for_te_grabber is not None:

#                        nifti_te = shenanigans.grab_te_from_dicom(dicom_for_te_grabber)

#                    else:
#                        nifti_te = 0.0

#                    print '\nTE for this file was: %s\n' % nifti_te

                    print '\nadding %s to list of data, for which we need parameters...\n' % item

                    _logger.debug('data_list is: %s' % data)

                    print "Item: " + item

                    if dicom_for_te_grabber:
                        alt_params_row = shenanigans.get_dcm_info(dicom_for_te_grabber, item, modality)
                        print alt_params_row
                        real_data.append(alt_params_row)

                    else:
                        params_row = image_summary.get_nii_info(item)
                        real_data.append(params_row)

                    #print '\nTESTING PARAMS GETTER.....\n'
                    #print '\nOld Way params_row = %s\n' % params_row
                    #print '\nNew Way alt_params_row = %s\n' % alt_params_row

                    


            # -------------------------> START TO BUILD THE LAYOUT <------------------------- #

            head = html_header

            html_params_panel = param_table_html_header

            # BUILD PARAM PANEL

            for data_row in real_data:
                html_row = write_param_table_row(data_row)
                html_params_panel += html_row

            html_params_panel += param_table_footer

            # BUILD & WRITE THE STRUCTURAL PANEL

            # If there are T1 pngs, make the BrainSprite viewer
            if os.listdir(T1_path):
                body = make_brainsprite_viewer(T1_path, img_out_path)
            else:
                body = ''

            # APPEND WITH PARAMS PANEL

            new_body = body + html_params_panel

            pngs = [png for png in os.listdir(img_out_path) if png.endswith('png')]

            # BUILD THE LISTS NEEDED FOR SERIES PANEL

            raw_rest_img_pattern = path.join(img_out_path, 'REST*.png')
            raw_rest_img_list = glob.glob(raw_rest_img_pattern)

            
            raw_mid_img_pattern = path.join(img_out_path, 'MID*.png')
            raw_mid_img_list = glob.glob(raw_mid_img_pattern)            

            raw_nback_img_pattern = path.join(img_out_path, 'nBack*.png')
            raw_nback_img_list = glob.glob(raw_nback_img_pattern)

            raw_sst_img_pattern = path.join(img_out_path, 'SST*.png')
            raw_sst_img_list = glob.glob(raw_sst_img_pattern)

            raw_rest_paths = natural_sort([path.join('./img', path.basename(img)) for img in raw_rest_img_list if '_' not in path.basename(img)])
            raw_mid_paths = natural_sort([path.join('./img', path.basename(img)) for img in raw_mid_img_list if '_' not in path.basename(img)])
            raw_nback_paths = natural_sort([path.join('./img', path.basename(img)) for img in raw_nback_img_list if '_' not in path.basename(img)])
            raw_sst_paths = natural_sort([path.join('./img', path.basename(img)) for img in raw_sst_img_list if '_' not in path.basename(img)])

            sb_ref_rest_paths = natural_sort([path.join('./img', img) for img in pngs if ('SBRef' in img) and ('REST' in img) and ('-' not in img)])  # Last condition excludes x, y, and z images
            sb_ref_mid_paths = natural_sort([path.join('./img', img) for img in pngs if ('SBRef' in img) and ('MID' in img) and ('-' not in img)])
            sb_ref_nback_paths = natural_sort([path.join('./img', img) for img in pngs if ('SBRef' in img) and ('nBack' in img) and ('-' not in img)])
            sb_ref_sst_paths = natural_sort([path.join('./img', img) for img in pngs if ('SBRef' in img) and ('SST' in img) and ('-' not in img)])

            rest_dvars = natural_sort([path.join('./img', img) for img in pngs if ('DVARS' in img) and ('CONC' not in img) and ('postreg' not in img) and ('tfMRI' not in img)])
            mid_dvars = natural_sort([path.join('./img', img) for img in pngs if ('DVARS' in img) and ('CONC' not in img) and ('postreg' not in img) and ('MID' in img)])
            nback_dvars = natural_sort([path.join('./img', img) for img in pngs if ('DVARS' in img) and ('CONC' not in img) and ('postreg' not in img) and ('nBack' in img)])
            sst_dvars = natural_sort([path.join('./img', img) for img in pngs if ('DVARS' in img) and ('CONC' not in img) and ('postreg' not in img) and ('SST' in img)])

            rest_dvars_postreg = natural_sort([path.join('./img', img) for img in pngs if ('DVARS' in img) and ('CONC' not in img) and ('postreg' in img) and ('tfMRI' not in img)])
            mid_dvars_postreg = natural_sort([path.join('./img', img) for img in pngs if ('DVARS' in img) and ('CONC' not in img) and ('postreg' in img) and ('MID' in img)]) 
            nback_dvars_postreg = natural_sort([path.join('./img', img) for img in pngs if ('DVARS' in img) and ('CONC' not in img) and ('postreg' in img) and ('nBack' in img)]) 
            sst_dvars_postreg = natural_sort([path.join('./img', img) for img in pngs if ('DVARS' in img) and ('CONC' not in img) and ('postreg' in img) and ('SST' in img)]) 


            # INITIALIZE AND BUILD NEW LIST WITH MATCHED SERIES CODES FOR EACH SERIES TYPE
            print '\nAssembling series images to build panel...'

            rest_image_paths = [rest_dvars, rest_dvars_postreg, rest_in_t1_gifs, t1_in_rest_gifs, sb_ref_rest_paths, raw_rest_paths]
            mid_image_paths = [mid_dvars, mid_dvars_postreg, mid_in_t1_gifs, t1_in_mid_gifs, sb_ref_mid_paths, raw_mid_paths]
            nback_image_paths = [nback_dvars, nback_dvars_postreg, nback_in_t1_gifs, t1_in_nback_gifs, sb_ref_nback_paths, raw_nback_paths]
            sst_image_paths = [sst_dvars, sst_dvars_postreg, sst_in_t1_gifs, t1_in_sst_gifs, sb_ref_sst_paths, raw_sst_paths]

            rest_dvars, rest_dvars_postreg, rest_in_t1_gifs, t1_in_rest_gifs, sb_ref_rest_paths, raw_rest_paths = insert_placeholders(rest_image_paths)
            mid_dvars, mid_dvars_postreg, mid_in_t1_gifs, t1_in_mid_gifs, sb_ref_mid_paths, raw_mid_paths = insert_placeholders(mid_image_paths, rest_or_task='MID')
            nback_dvars, nback_dvars_postreg, nback_in_t1_gifs, t1_in_nback_gifs, sb_ref_nback_paths, raw_nback_paths = insert_placeholders(nback_image_paths, rest_or_task='nBack')
            sst_dvars, sst_dvars_postreg, sst_in_t1_gifs, t1_in_sst_gifs, sb_ref_sst_paths, raw_sst_paths = insert_placeholders(sst_image_paths, rest_or_task='SST')

            num_rest_dvars = len(rest_dvars)
            num_mid_dvars = len(mid_dvars)
            num_nback_dvars = len(nback_dvars)
            num_sst_dvars = len(sst_dvars)

            # APPEND NEW SERIES PANEL SECTIONS
            series_rows = []
            newer_body = new_body + series_panel_header
            for i in range(0, num_rest_dvars):
                if rest_dvars:
                    series_rows.append(rest_dvars.pop(0))
                if rest_dvars_postreg:
                    series_rows.append(rest_dvars_postreg.pop(0))
                if rest_in_t1_gifs:
                    series_rows.append(rest_in_t1_gifs.pop(0))
                if t1_in_rest_gifs:
                    series_rows.append(t1_in_rest_gifs.pop(0))
                if sb_ref_rest_paths:
                    series_rows.append(sb_ref_rest_paths.pop(0))
                if raw_rest_paths:
                    series_rows.append(raw_rest_paths.pop(0))

                series_panel = write_series_panel_row(series_rows[:6])

                if series_panel:
                    newer_body += series_panel
                _logger.debug('\nrest_rows were: %s' % series_rows)

                series_rows = []

            for i in range(0, num_mid_dvars):
                if mid_dvars:
                    series_rows.append(mid_dvars.pop(0))
                if mid_dvars_postreg:
                    series_rows.append(mid_dvars_postreg.pop(0))
                if mid_in_t1_gifs:
                    series_rows.append(mid_in_t1_gifs.pop(0))
                if t1_in_mid_gifs:
                    series_rows.append(t1_in_mid_gifs.pop(0))
                if sb_ref_mid_paths:
                    series_rows.append(sb_ref_mid_paths.pop(0))
                if raw_mid_paths:
                    series_rows.append(raw_mid_paths.pop(0))

                series_panel = write_series_panel_row(series_rows[:6])

                if series_panel:
                    newer_body += series_panel
                _logger.debug('\mid_rows were: %s' % series_rows)
                series_rows = []
                
            for i in range(0, num_nback_dvars):
                if nback_dvars:
                    series_rows.append(nback_dvars.pop(0))
                if nback_dvars_postreg:
                    series_rows.append(nback_dvars_postreg.pop(0))
                if nback_in_t1_gifs:
                    series_rows.append(nback_in_t1_gifs.pop(0))
                if t1_in_nback_gifs:
                    series_rows.append(t1_in_nback_gifs.pop(0))
                if sb_ref_nback_paths:
                    series_rows.append(sb_ref_nback_paths.pop(0))
                if raw_nback_paths:
                    series_rows.append(raw_nback_paths.pop(0))

                series_panel = write_series_panel_row(series_rows[:6])

                if series_panel:
                    newer_body += series_panel
                _logger.debug('\nback_rows were: %s' % series_rows)
                series_rows = []

            for i in range(0, num_sst_dvars):
                if sst_dvars:
                    series_rows.append(sst_dvars.pop(0))
                if sst_dvars_postreg:
                    series_rows.append(sst_dvars_postreg.pop(0))
                if sst_in_t1_gifs:
                    series_rows.append(sst_in_t1_gifs.pop(0))
                if t1_in_sst_gifs:
                    series_rows.append(t1_in_sst_gifs.pop(0))
                if sb_ref_sst_paths:
                    series_rows.append(sb_ref_sst_paths.pop(0))
                if raw_sst_paths:
                    series_rows.append(raw_sst_paths.pop(0))

                series_panel = write_series_panel_row(series_rows[:6])

                if series_panel:
                    newer_body += series_panel
                _logger.debug('\sst_rows were: %s' % series_rows)
                series_rows = []


            # COMPLETE EPI PANEls

            newer_body += series_panel_footer

            _logger.debug('newer_body is : %s' % newer_body)

#            try:

#                copy_images(img_in_path, structural_img_labels, img_out_path)  # out: /summary/img/<blah>

#            except IOError:

#                _logger.warning('\nUnable to locate some structural images. Do they exist?')
#                print '\nMake sure you have all 6 structural .png and DVARS available for this subject: %s_%s' % (
#                    subj_id, visit_id)

#                print '\nExpected path to required images: %s' % img_in_path

            # FILL-IN THE CODE / VERSION INFO
            new_html_header = edit_html_chunk(head, 'CODE_VISIT', '%s' % (subj_id))

            new_html_header = edit_html_chunk(new_html_header, 'VERSION', 'Executive Summary_v' + VERSION)

            # ASSEMBLE THE WHOLE DOC, THEN WRITE IT!

            html_doc = new_html_header + newer_body + write_dvars_panel()

            html_doc += html_footer

            write_html(html_doc, summary_path, title='executive_summary_%s.html' % (subj_id))

            # -------------------------> END LAYOUT <------------------------- #

            # -------------------------> PREPARE QC PACKET <------------------------- #
            move_cmd = "mv %(img_in_path)s/*.html %(sub_code_folder)s; mv %(img_in_path)s/img %(sub_code_folder)s" % {
                        'sub_code_folder'  : subject_code_folder,
                        'img_in_path'      : img_in_path}

            image_summary.submit_command(move_cmd)

            if args.output_path:

                user_out_path = path.join(args.output_path)

                if path.exists(user_out_path):

                    print 'found path: %s, using this to copy for QC' % user_out_path

                    qc_folder_out = path.join(user_out_path, image_summary.date_stamp, subj_id)

                    print '\nFind your images here: \n\t%s' % qc_folder_out

            else:

                user_home = os.path.expanduser('~')

                qc_folder_out = path.join(user_home, image_summary.date_stamp, subj_id)

                print '\nusing default output path to copy images for QC: \n%s' % qc_folder_out

            if not path.exists(qc_folder_out):

                print '\ncopying to QC_folder\n\n'

                shutil.copytree(subject_code_folder, qc_folder_out)  # only works if the des_dir doesn't already exist

    else:
        print '\nNo subject path provided!'
        _logger.error('No subject path provided!')

if __name__ == '__main__':

    main()

    print '\nall done!'
