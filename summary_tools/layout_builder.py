#! /usr/bin/env python

"""
Call this program with:
    -u full path to the root of the directory containing unprocessed files (root = parent of sub-<subject_id>)
    -p full path to the root of the directory containing derivatives (root = parent of sub-<subject_id>)
    -s subject - id without sub- prefix
    -e executive summary directory (e.g., summary_DCANBOLDProc_v4.0.0)

__author__ = 'Shannon Buckley', 2/20/16
"""

import os
from os import path
import re
import argparse
import subprocess
import image_summary
import glob
import shutil
import logging
import sys
import time # For debugging.
from helpers import shenanigans

PROG = 'Layout Builder'
LAST_MOD = '11-13-18'

program_desc = """%(prog)s:
Builds the layout for the Executive Summary by writing-out chunks of html with some help from image_summary methods.
Use -u <unproc_root> -d <deriv_root> -s <subject> -e <sum_dir> to launch and build a summary page.
Has embedded css & jquery elements.
""" % {'prog': PROG}


def get_parser():

    parser = argparse.ArgumentParser(description=program_desc, prog=PROG)

    parser.add_argument('-u', '--unproc_root', dest='unproc_root', action='store',
                        help='Expects the full path to the parent of the sub-<subject> directory of unprocessed files.')

    parser.add_argument('-d', '--deriv_root', dest='proc_root', action='store',
                        help='Expects the full path to the parent of the sub-<subject> directory of derivative files.')

    parser.add_argument('-s', '--subject_id', dest='subject_id', action='store',
                        help='Expects a subject id without sub- prefix.')

    parser.add_argument('-e', '--ex_summ_dir', dest='summ_dir', action='store',
                        help='Expects the name of the subdirectory used for the summary (e.g.: summary_DCANBOLDProc_v4.0.0)')

    parser.add_argument('--ica', action='store_true')

    parser.add_argument('--verbose', dest="verbose", action="store_true", help="Tell me all about it.")

    parser.add_argument('-vv', '--very_verbose', dest="very_verbose", action="store_true", help="Tell me all about it.")

    return parser

# HTML BUILDING BLOCKS
html_header = """<!DOCTYPE html>
<html lang = "en">
    <head>
        <meta charset = "utf-8">
        <title>Executive Summary: CODE_VISIT</title>
        <style type="text/css">.epi,.grayords,.params{position:relative}.header,button,table,td{text-align:center}body{background-color:#c3c4c3}span{font-size:10px}img{border-radius:5px}.header{font-family:Garamond;margin-top:25px;margin-bottom:15px}table,td{border:1px dashed #70b8ff}.epi td,.params td,.top-left-panel table,td{border:none}.top-left-panel{float:left;width:50%}.top-left-panel img{width:250px;height:200px}.epi{float:right}.epi img{width:175px;height:150px}.raw_rest_img img {width: 300px;height: 110px}.params{float:left;width:40%}.params th{border-bottom:1px #70b8ff solid}.params .column-names{border-bottom:1px #00f solid;font-weight:700}.grayords{float:right}.grayords img{width:675px;height:600px}.out-of-range{color:red}button{cursor:pointer;display:inline-block;height:20px;width:70px;font-family:arial;font-weight:700;margin-top:2px}
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
            </div>
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
        <script>$(document).ready(function(){$("img[src*=sbref]").width(300).height(110),$('img').filter('.raw_rest_img').width(300).height(110),$(".t1_tr").each(function(t,a){"2400.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t1_te").each(function(t,a){"4.97"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t1_x").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t1_y").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t1_z").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_frames").each(function(t,a){"120"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_x").each(function(t,a){"3.8"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_y").each(function(t,a){"3.8"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_z").each(function(t,a){"3.8"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_tr").each(function(t,a){"2100.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".epi_te").each(function(t,a){"5.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t2_x").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t2_y").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t2_z").each(function(t,a){"1.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t2_tr").each(function(t,a){"3200.0"!=$(a).text()&&$(a).addClass("out-of-range")}),$(".t2_te").each(function(t,a){"4.97"!=$(a).text()&&$(a).addClass("out-of-range")}),$("div.params").draggable(),$("div.grayords").draggable(),$("div.epi").draggable()});
        </script>
        <script>
           $( window ).load(function() {
               var brain = brainsprite({
                 canvas: "viewer1",
                 sprite: "spriteImg1",
                 nbSlice: { 'Y':218 , 'Z':218 },
                 flagCoordinates: true,
               });
           });
       </script>
       <script>
           $( window ).load(function() {
               var brain = brainsprite({
                 canvas: "viewer2",
                 sprite: "spriteImg2",
                 nbSlice: { 'Y':218 , 'Z':218 },
                 flagCoordinates: true,
               });
           });
       </script>
    </body>
</html>
"""

# end of HTML BUILDING BLOCKS

def write_html(template, dest_dir, title="executive_summary.html"):
    """
    Takes an html template string and a destination, then writes it out to a default title.

    :parameter: template: path to html template
    :parameter: dest_dir: path for final .html file
    :parameter: title: string to apply to html
    :return: None
    """

    if not title.endswith('.html'):
        title += '.html'

    try:
        f = open(path.join(dest_dir, title), 'w')
        f.writelines(template)
        f.close()
        print('\nSummary %s can be found in path %s.\n' % (title, dest_dir))
    except IOError:
        print('\ncannot write %s to %s for some reason...\n' % (title, dest_dir))


def make_brainsprite_viewers(T1_path, T2_path, img_out_path):
    """
    Builds HTML panel for BrainSprite viewer(s) so users can click through 3d anatomical images.

    :return: string of html containing up to 2 div rows, each with a canvas and hidden BrainSprite mosaic image
    """
    structural_html_panel = ''

    # If there are T1 pngs, make a BrainSprite viewer T1.
    # KJS: hardcoding file names, ids, etc. bc this whole thing assumes "./img" and
    # there is no way to make it more general until the redesign. I would just be
    # faking it.
    if (os.path.isdir(T1_path)) and (os.listdir(T1_path)):

        out_path = os.path.join(img_out_path, "T1_mosaic.jpg")
        image_summary.make_mosaic(T1_path, out_path)

        structural_html_panel += """
        <div class="top-row">
                <div class="structural">
                    <div style="max-width:100%;height:auto;">
                        <p>BrainSprite Viewer: T1</p>
                        <canvas id="viewer1" style="max-width:100%;">
                        <img id="spriteImg1" class="hidden" src="./img/T1_mosaic.jpg" >
                    </div>
                </div>
        </div>"""

    # If there are T2 pngs, make a BrainSprite viewer T2.
    if (os.path.isdir(T2_path)) and (os.listdir(T2_path)):

        out_path = os.path.join(img_out_path, "T2_mosaic.jpg")
        image_summary.make_mosaic(T2_path, out_path)

        structural_html_panel += """
        <div class="top-row">
                <div class="structural">
                    <div style="max-width:100%;height:auto;">
                        <p>BrainSprite Viewer: T2</p>
                        <canvas id="viewer2" style="max-width:100%;">
                        <img id="spriteImg2" class="hidden" src="./img/T2_mosaic.jpg" >
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


def write_series_panel_row(list_of_img_paths):
    """
    Takes a list of image paths and builds one row of series images for the panel.

    :parameter: list_of_img_paths: list of paths
    :return: one row of an html table, <tr> to </tr> with epi or task images for a given series
    """

    series_type_re = r'(task-\D+\d+)'
    compiled_series_type = re.compile(series_type_re)

    for path in list_of_img_paths:
        print(path)
        series_type_match = compiled_series_type.search(path)
        if series_type_match is None:
            print('Writing series panel but series type is unknown...')
            series_type = "Unknown"
        else:
            series_type = series_type_match.group()
            break

    print("Making series panel for " + series_type)

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
    :return: html string for the whole epi-panel div (one row of images per rest)
    """

    series_panel_html = header

    for row in series_rows_list:
        series_panel_html += row
    series_panel_html += footer

    return series_panel_html


def write_dvars_panel(dvars_input_path, dvars_concp_input_path):
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


def copy_image(src_path, dest_dir):
    """
    Copies a file to a destination directory.

    :parameter: src_path: full path to original file.
    :parameter: dest_dir: full path to destination directory.
    :return: path to copied file.
    """
    return shutil.copy(src_path, dest_dir)



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

    filtered_list = []
    compiled_regex = re.compile(regex)

    for item in path_list:
        filtered = compiled_regex.search(item)
        if filtered:
            filtered_num = filtered.group(1)
            filtered_list.append(filtered_num)

    sorted_list = natural_sort(set(filtered_list))

    return sorted_list


def insert_placeholders(image_path_lists, fmri_type='rest'):
    """
    Fills in any gaps (missing series) in lists of image paths with placeholder
    images.

    :parameter: image_path_lists: list of image path lists that need to be altered
    :parameter: fmri_type: indicates whether images are rest, ferumoxytol, or task, and if task, which one
    :returns: list of image path lists with paths to placeholder images where needed
    """

    corrected_lists = []

    # Make these more flexible. Names may or may not have ses-* before _task-,
    # and task-* may or may not have _run- before the number.
    dvars_re         = r'DVARS_and_FD_.*task-\D+(\d+)'
    postreg_dvars_re = r'postreg_DVARS_and_FD_.*task-\D+(\d+)'
    series_t1_re     = r'task-\D+(\d+)_in_t1'
    t1_series_re     = r't1_in_.*task-\D+(\d+)'
    sbref_re         = r'task-\D+(\d+)_sbref'
    rest_re          = r'task-\D+(\d+)'

    dvars_nums = find_series_numbers(image_path_lists[0], dvars_re)
    postreg_dvars_nums = find_series_numbers(image_path_lists[1], postreg_dvars_re)
    series_t1_nums = find_series_numbers(image_path_lists[2], series_t1_re)
    t1_series_nums = find_series_numbers(image_path_lists[3], t1_series_re)
    sbref_nums = find_series_numbers(image_path_lists[4], sbref_re)
    rest_nums = find_series_numbers(image_path_lists[5], rest_re)

    numbers_lists = [dvars_nums, postreg_dvars_nums, series_t1_nums, t1_series_nums, sbref_nums, rest_nums]

    # Check if there are any gaps in image sequence that need to be filled by placeholders
    missing = []
    for x in range(0, len(numbers_lists)):
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
        if missing:
            last_missing = int(missing[-1]) + 1

            for x in range(int(missing[0]), last_missing):
                sequence_num = '%02d' % x
                sequence_task = 'task-%s' % fmri_type
                if list_index == 0:
                    sequence_text = 'DVARS_and_FD_'
                elif list_index == 1:
                    sequence_text = 'postreg_DVARS_and_FD_'
                elif list_index == 2:
                    sequence_text = '_in_t1'
                elif list_index == 3:
                    sequence_text = 't1_in_'
                elif list_index == 4:
                    sequence_text = '_sbref'
                elif list_index == 5:
                    sequence_text = ''

                match = [s for s in l if sequence_task and sequence_text and sequence_num in s]
                if match:
                    new_l.append(match[0])
                else:
                    new_l.append(placeholder_path)
                    print('\nNot found in summary directory: image with these strings '
                          'in its name: %s, %s, and %s\n' % (sequence_task, sequence_num, sequence_text))
            corrected_lists.append(new_l)

    # If ffmri images exist, deal with those separately

    flattened_image_paths = [p for sublist in image_path_lists for p in sublist]

    if any("ffMRI" in path for path in flattened_image_paths):

        for l in image_path_lists:
            new_l = []
            list_index = image_path_lists.index(l)
            if list_index in [0, 1, 2, 3]:
                placeholder_path = './img/square_placeholder_text.png'
            else:
                placeholder_path = './img/rectangular_placeholder_text.png'

            if missing:
                for x in range(int(missing[0]), last_missing):
                    sequence_task = 'task-%s' % fmri_type
                    sequence_num = str(x)
                    if list_index == 0:
                        sequence_text = 'DVARS_and_FD'
                    elif list_index == 1:
                        sequence_text = 'postreg_DVARS_and_FD'
                    elif list_index == 2:
                        sequence_text = '_in_t1'
                    elif list_index == 3:
                        sequence_text = 't1_in_'
                    elif list_index == 4:
                        sequence_text = '_sbref'
                    elif list_index == 5:
                        sequence_text = ''

                    match = [s for s in l if sequence_task and sequence_text and sequence_num in s]
                    if match:
                        new_l.append(match[0])
                    else:
                        new_l.append(placeholder_path)
                        print('\nNot found in summary directory: image with these strings in its name: %s, %s, and %s\n' % (sequence_task, sequence_num, sequence_text))
                corrected_lists[list_index] += new_l

    if corrected_lists:
        return corrected_lists
    else:
        return image_path_lists

def bids_dir_exists(bids_path):
    if os.path.isdir(bids_path):
        return 1
    else:
        print('\nRequired BIDS directory does not exist or is not a directory:\n\t%s\nExiting...' % bids_path)
        return 0


def get_args():

    parser = get_parser()
    args = parser.parse_args()

    passing = 1;

    # Make sure all required arguments were specified. If any is missing,
    # keep checking so user knows *all* of what is missing.
    if not args.unproc_root:
        print('\nRequired path to the root of unprocessed files was not specified.\n')
        passing = 0

    if not args.proc_root:
        print('\nRequired path to the root of derivative files was not specified.\n')
        passing = 0

    if not args.subject_id:
        print('\nRequired subject id was not specified.\n')
        passing = 0

    if not args.summ_dir:
        print('\nRequired executive summary directory was not specified.\n')
        passing = 0

    # If we have all of the required arguments, return them.
    if 1 == passing:
        return args
    else:
        print('\nFailed to get all required arguments.\nExiting....\n')
        sys.exit()

def write_summ_file(out_path, args):
    unproc_root = args.unproc_root
    proc_root = args.proc_root
    sub_id = args.subject_id
    ex_sum = args.summ_dir

    date = image_summary.date_stamp

    try:
        summ_file = os.path.join(out_path, 'Summary_Report.txt')
        with open(summ_file, 'w') as f:

            info = '''
                    Executive Summary ran on %s
                    Unprocessed Data Path provided: \n%s
                    Derivative Files Path provided: \n%s
                    Subject Code: %s
                    Executive summary subdir: %s
                    Args: \n%s
                    ''' % (date, unproc_root, proc_root, sub_id, ex_sum, args)

            f.write(info)
            f.close()

        print('\nInitial summary report can be found in:\n\t%s' % summ_file)

        # All good!
        return

    except OSError:
        # path is not writable?
        print('\nCannot write to path; check permissions.\n\tPath: %s\nExiting....' % out_path)
        sys.exit()


def get_paths(args):

    unprocessed_files = args.unproc_root
    processed_files = args.proc_root
    sub_id = args.subject_id
    ex_sum = args.summ_dir

    # Currently, assume pipeline is HCP. (May need to specify in future.)

    # Check that unprocessed data are available to us.
    if (bids_dir_exists(unprocessed_files)):
        print('\nUnprocessed data will be found in path:\n\t%s' % unprocessed_files)

    else:
        print('\nPath to unprocessed data does not exist.\n\tPath: %s\nExiting....\n' % unprocessed_files)
        sys.exit()


    # The summary dir lives in the processed_files dir; it should already be there; if not, create it.
    summary_path = os.path.join(processed_files, ex_sum)
    mni_path = os.path.join(processed_files, 'MNINonLinear/Results')

    if os.path.isdir(summary_path):
        print( '\nData will be processed in path:\n\t%s' % processed_files)
    else:
        try:
            os.makedirs(summary_path)

        except OSError:
            print('\nUnable to make dir %s in path; check path and permissions.\n %s' % (ex_sum, processed_files))
            print('\nExiting....\n')
            sys.exit()

    if os.path.isdir(mni_path):
        print( '\nProcessed tasks will be found in path:\n\t%s' % mni_path)
    else:
        print('\nPath to task data does not exist.\n\tPath: %s\nExiting....\n' % mni_path)
        sys.exit()

    # Subdirectories within the summary directory:

    # There will need to be a subdirectory, called executivesummary, where the html (and eventually images) will live.
    execsumm_subdir_name = 'executivesummary'
    execsumm_path = os.path.join(summary_path, execsumm_subdir_name)

    # Also, a subdirectory for the images the html will use. During processing, this lives in the outer summary
    # folder. Later it will be moved into the executivesummary folder where the html lives. Sigh.
    img_path = os.path.join(summary_path, 'img')

    if os.path.exists(img_path):
        shutil.rmtree(img_path, ignore_errors=True)

    if path.exists(execsumm_path):
        shutil.rmtree(execsumm_path, ignore_errors=True)

    try:
        os.makedirs(img_path)
        os.makedirs(execsumm_path)

    except OSError as err:
        print('cannot make img or executivesummary folder within path... permissions? \nPath: %s' % summary_path)
        print('OSError: %s' % err)
        print('\nExiting....\n')
        sys.exit()

    # And subdirectories for the T1 and T2 pngs. These might or might not already exist.
    t1_path = os.path.join(summary_path, 'T1_pngs')
    t2_path = os.path.join(summary_path, 'T2_pngs')

    write_summ_file(summary_path, args)

    paths = {
            'unprocessed' : unprocessed_files,
            'processed' : processed_files,
            'summary' : summary_path,
            'mni': mni_path,
            't1' : t1_path,
            't2' : t2_path,
            'img' : img_path,
            'execsumm' : execsumm_path
    }

    return paths


def copy_gifs(source_dir, target_dir):

    # Find .gif files in source directory; copy to target directory.
    # Return the list of gif filenames (no paths).
    try:
        gifs = [gif for gif in os.listdir(source_dir) if gif.endswith('gif')]

        if len(gifs) > 0:
            copy_images(source_dir, gifs, target_dir)
            return gifs

        else:
            print('no .gifs in summary directory %s', source_dir)
            sys.exit()

    except OSError as err:
            print('\nOS Error trying to locate gifs in path:\n\t %s...' % source_dir)
            print('\nOS Error: %s...' % err)
            print('\nExiting....\n')
            sys.exit()

def img_path(filepath):
    """
    Turns a file path into the relative path used by executive summary.
    That is, prepends ./img/ to the file's name.

    :parameter: filepath: path to file
    :return: relative path
    """

    return os.path.join('./img/', os.path.basename(filepath))

def nifti_root(filename):
    """
    Gets the root filename from a nifti file. That is, strips off both
    the dirname and extension(s).

    :parameter: filename.
    :return: filename with no dirname or extensions.
    """

    # File may be either .nii or .nii.gz.
    root, ext = os.path.splitext(os.path.basename(filename))
    if ext == '.gz':
        root, ext = os.path.splitext(root)

    return root


def find_and_copy_image(seek_dir, pattern, image_path):
    """
    Finds a file using pattern within the directory specified as
    seek_dir. If found, copies the file to the directory of images.

    :parameter: seek_dir: directory to be searched.
    :parameter: pattern: Unix shell pattern for finding files.
    :return: relative path to copied file, or None.
    """

    found_path = find_one_file(seek_dir, pattern)

    if found_path:
        # Copy the file to the path for the images.
        filename = os.path.basename(found_path)
        shutil.copyfile(found_path, os.path.join(image_path, filename))
        return img_path(filename)

    else:
        return None



def find_one_file(seek_dir, pattern):

    one_file = None

    # Try to find a file with the pattern given in the directory given.
    glob_pattern = path.join(seek_dir, pattern)
    filelist = glob.glob(glob_pattern)

    # Make sure we got exactly one file.
    numfiles=len(filelist)
    if numfiles is 1:
        one_file = filelist[0]
    else:
        # TODO: Log an error
        print('\nFound %s files with pattern: %s' % (numfiles, glob_pattern))

    return one_file


def main():

    # Initialization:
    script_dir = os.path.dirname(os.path.realpath(__file__))
    program_dir = os.path.abspath(os.path.join(script_dir, os.pardir))


    # Get arguments.
    args = get_args()

    subj_id = 'sub-' + args.subject_id


    # Use arguments to get paths. Make sure required paths are in place.
    paths = get_paths(args)

    nifti_path = paths['unprocessed']
    sub_root = paths['processed']
    summary_path = paths['summary']
    mni_path = paths['mni']
    img_out_path = paths['img']
    T1_path = paths['t1']
    T2_path = paths['t2']
    executivesummary_path = paths['execsumm']


    # Set up placeholders in case of missing files.
    placeholder_path = os.path.join(program_dir, 'placeholder_pictures')
    placeholders = ['square_placeholder_text.png', 'rectangular_placeholder_text.png']
    copy_images(placeholder_path, placeholders, img_out_path)
    square_path = './img/square_placeholder_text.png'
    rectangle_path = './img/rectangular_placeholder_text.png'


    # Information for images to be found in processed files.
    image_info = {
            'concat_pre_reg_gray': {
                'pattern': 'DVARS_and_FD_CONCA*.png',
                'source_dir': summary_path
                },
            'concat_post_reg_gray': {
                'pattern': 'DVARS_and_FD_CONCP*.png',
                'source_dir': summary_path
                },
            'atlas_in_t1': {
                'pattern': '*atlas_in_t1*.gif',
                'source_dir': summary_path
                },
            't1_in_atlas': {
                'pattern': '*t1_in_atlas*.gif',
                'source_dir': summary_path
                },
            'task_pre_reg_gray': {
                'pattern': 'DVARS_and_FD*%s*.png',
                'source_dir': summary_path,
                'placeholder': square_path
                },
            'task_post_reg_gray': {
                'pattern': 'postreg_DVARS_and_FD*%s*.png',
                'source_dir': summary_path,
                'placeholder': square_path
                },
            'task_in_t1': {
                'pattern': '*%s*_in_t1*.gif',
                'source_dir': summary_path,
                'placeholder': square_path
                },
            't1_in_task': {
                'pattern': '*t1_in_*%s*.gif',
                'source_dir': summary_path,
                'placeholder': square_path
                },
            'sbref': {
                'pattern': '*%s*_sbref.nii*',
                'source_dir': nifti_path,
                'placeholder': rectangle_path
                },
            'scout': {
                'pattern': '*%s*/Scout_orig.nii*',
                'source_dir': sub_root,
                'placeholder': rectangle_path
                },
            'bold': {
                'pattern': '*%s*_bold.nii*',
                'source_dir': nifti_path,
                'placeholder': rectangle_path
                }
            }

    # -------------------------> START TO BUILD THE LAYOUT <------------------------- #

    head = html_header


    # BUILD & WRITE THE STRUCTURAL PANEL

    body = ''
    # Make BrainSprite viewer(s).
    body = make_brainsprite_viewers(T1_path, T2_path, img_out_path)

    # Get T1 in atlas and atlas in T1.
    """
    NEXT:
    values = image_info['atlas_in_t1']
    atlas_in_t1 = find_and_copy_image(values['source_dir'], values['pattern'], img_out_path)
    values = image_info['t1_in_atlas']
    t1_in_atlas = find_and_copy_image(values['source_dir'], values['pattern'], img_out_path)
    """

    # Get a list of tasks processed for this subject from the mni_path.
    # Each entry is a tuple of the task-name and number (without run-).
    task_entries = image_summary.get_list_of_tasks(mni_path)

    if len(task_entries) is not 0:

        # The subject has at least one task; add the header.
        body += series_panel_header

        # Add a row for each task.
        for task_name, task_num in task_entries:
            row_label = 'task-%s_run-%s' % (task_name, task_num)

            # Find each of the files needed for this task.
            task_files = []

            # Using glob patterns to find the files for this task;
            # make glob pattern for the task itself.
            task_pattern = task_name + '*' + task_num

            for key in [ 'task_pre_reg_gray', 'task_post_reg_gray', 'task_in_t1', 't1_in_task' ]:
                pattern = image_info[key]['pattern'] % task_pattern
                task_file = find_and_copy_image(image_info[key]['source_dir'], pattern, img_out_path)
                if task_file:
                    task_files.append(task_file)
                else:
                    task_files.append(image_info[key]['placeholder'])

            # Find and slice the bids input files for this task: sbref and bold.
            pattern = image_info['sbref']['pattern'] % task_pattern
            ref_file = find_one_file(image_info['sbref']['source_dir'], pattern)
            if ref_file is None:
                # Run # is not required by BIDS when there is only 1 run for a task.
                pattern = image_info['sbref']['pattern'] % task_name
                ref_file = find_one_file(image_info['sbref']['source_dir'], pattern)

            # If reference file was found in bids input, just replace the extension(s)
            # with .png to make the name of the output file.
            if ref_file:
                png_file = nifti_root(ref_file) + '.png'
            else:
                # Next best thing: try to find a scout file.
                pattern = image_info['scout']['pattern'] % task_pattern
                ref_file = find_one_file(image_info['scout']['source_dir'], pattern)
                if ref_file:
                    # Use the name of the file's parent directory to make a name
                    # for the output file. Else we would have name collisions.
                    parent_path = os.path.dirname(ref_file)
                    parent = os.path.basename(parent_path)
                    png_file = parent + '_sbref.png'

            # Slice the .nii to get the .png.
            if ref_file is not None:
                dest_file = os.path.join(img_out_path, png_file)
                image_summary.slice_image_to_ortho_row(ref_file, dest_file)
                task_files.append(img_path(png_file))
            else:
                task_files.append(image_info['sbref']['placeholder'])

            pattern = image_info['bold']['pattern'] % task_pattern
            bold_file = find_one_file(image_info['bold']['source_dir'], pattern)
            if bold_file is None:
                # Run # is not required by BIDS when there is only 1 run for a task.
                pattern = image_info['bold']['pattern'] % task_name
                bold_file = find_one_file(image_info['bold']['source_dir'], pattern)

            # Slice the .nii to get the .png.
            if bold_file:
                png_file = nifti_root(bold_file) + '.png'
                dest_file = os.path.join(img_out_path, png_file)
                image_summary.slice_image_to_ortho_row(bold_file, dest_file)
                task_files.append(img_path(png_file))
            else:
                task_files.append(image_info['bold']['placeholder'])

            body += write_series_panel_row(task_files)

        # Add the footer for the task panels.
        body += series_panel_footer


    # FILL-IN THE CODE INFO
    new_html_header = edit_html_chunk(head, 'CODE_VISIT', '%s' % (subj_id))

    # ASSEMBLE THE WHOLE DOC, THEN WRITE IT!

    # Get concatenated gray plots.
    values = image_info['concat_pre_reg_gray']
    concat_pre_reg_gray = find_and_copy_image(values['source_dir'], values['pattern'], img_out_path)
    values = image_info['concat_post_reg_gray']
    concat_post_reg_gray = find_and_copy_image(values['source_dir'], values['pattern'], img_out_path)

    html_doc = new_html_header + body + write_dvars_panel(concat_pre_reg_gray, concat_post_reg_gray)

    html_doc += html_footer

    write_html(html_doc, summary_path, title='executive_summary_%s.html' % (subj_id))

    # -------------------------> END LAYOUT <------------------------- #

    # -------------------------> PREPARE QC PACKET <------------------------- #
    # Move the img subdirectory into the directory where the html was created.
    move_cmd = "mv %(img_in_path)s/*.html %(executivesummary_path)s; mv %(img_in_path)s/img %(executivesummary_path)s" % {
                'executivesummary_path' : executivesummary_path,
                'img_in_path'           : summary_path}

    image_summary.submit_command(move_cmd)


if __name__ == '__main__':

    main()

    print('\nall done!')
