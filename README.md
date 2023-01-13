# py-script-director

A simple Flask frontend for modular Python plugins.

UI utilises bootstrap, and plugins use abstract classes. See hello_world.py for a simple example of a plugin

## Purpose / Why to use

Sometimes you write a script for colleagues, and they don't quite know how to modify python code, or how to run things from the command line.

This tool is designed with this situation in mind. You can give them a zip with your custom plugin included, and they can run the script from a web browser with variable inputs.

## Requirements

You will need flask installed
 > pip install Flask
 
 
 # Usage
 Clone the repo, and run the app.py file. This will load a Flask web server (debug mode) on localhost, port 5000.
 
 Take a look at the hello_world.py plugin for an example of how to create an input+output plugin
